from ...strategies.pre_processing_strategies import OutlierImpute, OutlierFilter, OutlierTransform
from .operations.transformers import TransformationOperation

from pydantic import BaseModel
from typing import List, Union, Optional, Dict, Any

import logging
import polars as pl 

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

class ImputeOutlierValue: 
    def __init__(self, frame: pl.DataFrame):
        self.frame= frame
    
    def median(self, col: str) -> float: 
        return self.frame[col].median()
    
    def mean(self, col: str) -> float: 
        return self.frame[col].mean()
    
    def get_value(self, col: str, method: OutlierImpute) -> float: 
        match method: 
            case OutlierImpute.MEDIAN: 
                value= self.median(col=col)
            case OutlierImpute.MEAN: 
                value= self.mean(col=col)
        return value

class FilterOutliersExpr: 
    @staticmethod
    def trim(out_index: List[int]) -> pl.Expr: 
        return ~pl.col('index').is_in(out_index)
    
    @staticmethod
    def capping(col: str, upper: Union[int, float], lower: Union[int, float]) -> pl.Expr: 
        return pl.col(col).clip(lower, upper).alias(col).alias(col)
    
    @classmethod
    def get_expr(cls, 
            method: OutlierFilter, 
            col: Optional[str]=None,
            out_index: Optional[List[int]]= None, 
            upper: Optional[Union[int, float]]= None, 
            lower: Optional[Union[int, float]]= None
        ) -> pl.Expr: 
        
        match method: 
            case OutlierFilter.TRIM: 
                expression= cls.trim(out_index=out_index)
            case OutlierFilter.CAPPING: 
                expression= cls.capping(col=col, upper=upper, lower=lower)
        
        return expression

class Outlier: 
    def __init__(self, frame: pl.DataFrame, config: BaseModel, outlier_dict: Dict[str, Any]):
        self.frame= frame
        
        self.o_config= config.preprocessing.preprocessing_outlier_rules
        self.outlier_dict= outlier_dict
        
        self.numeric_frame= self.frame.select(pl.selectors.numeric())
        
        self.value= ImputeOutlierValue(frame=self.frame)
        self.filter= FilterOutliersExpr()
    
    def input_expr(self, col: str, method: OutlierImpute, list_index_out: List[int]) -> pl.Expr: 
        value= self.value.get_value(col=col, method=method)
        
        return pl.when(pl.col('index').is_in(list_index_out)).then(pl.lit(value)).otherwise(pl.col(col)).alias(col)
    
    def filter_expr(self, 
        method: OutlierFilter, 
        col: Optional[str]=None,
        out_index: Optional[List[int]]= None, 
        upper: Optional[Union[int, float]]= None, 
        lower: Optional[Union[int, float]]= None
        ) -> pl.Expr: 
        
        return self.filter.get_expr(
            method=method, 
            col=col, 
            out_index=out_index, 
            upper=upper, 
            lower=lower
        )
    
    def flag_expr(self, col: str, list_index_outlier: List[int]) -> pl.Expr: 
        return pl.when(pl.col('index').is_in(list_index_outlier)).then(pl.lit(1)).otherwise(pl.lit(0)).alias(f'{col}_outlier_flag')
    
    def transform_expr(self, col: str, method: OutlierTransform) -> pl.Expr: 
        transformer= TransformationOperation()
        
        match method: 
            case OutlierTransform.LOG1P: 
                expression= transformer.log1p(col= col)
            case OutlierTransform.SQRT: 
                expression= transformer.sqrt(col=col)
        
        return expression
    
    def iqr_expr(self) -> Dict[str, pl.Expr]:
        dict_expr= {}
        
        dict_expr['filter']= {}
        dict_expr['expr']= {}
        
        for col in self.numeric_frame.columns:
            if col != 'index': 
                q1= self.numeric_frame[col].quantile(0.25)
                q3= self.numeric_frame[col].quantile(0.75)
                
                iqr= q3 - q1
                
                lower= q1 - iqr *1.5
                upper= q3 + iqr *1.5
                
                outlier_frame= self.numeric_frame.filter((pl.col(col) < lower) | (pl.col(col) > upper))
                list_index_out= outlier_frame.get_column('index').to_list()
                
                if list_index_out: 
                    percent= self.outlier_dict[col].get('percent_outliers')
                    sugg= self.outlier_dict[col].get('suggestion')
                    
                    for type_op, operation in sugg.items(): 
                        if percent < self.o_config.filter_percent: 
                            if type_op == 'filter' and operation: 
                                expr= self.filter_expr(
                                    method=operation, 
                                    col=col, 
                                    out_index=list_index_out, 
                                    upper=upper, 
                                    lower=lower
                                )
                                
                                if operation == 'trim': 
                                    logger.info(f'Column {col} will be trimmed')
                                    dict_expr['filter'][col]= expr
                                else: 
                                    logger.info(f'Column {col} will be capped')
                                    dict_expr['expr'][col]= expr
                                break
                        elif percent < self.o_config.impute_percent: 
                            if type_op == 'impute' and operation: 
                                expr= self.input_expr(
                                    col=col, 
                                    method=operation, 
                                    list_index_out=list_index_out
                                )
                                
                                logger.info(f'Column {col} will be imputed')
                                dict_expr['expr'][col]= expr
                                break
                        elif percent > self.o_config.transform_percent: 
                            if type_op == 'transform' and operation: 
                                expr= self.transform_expr(
                                    col=col, 
                                    method=operation
                                )
                                
                                logger.info(f'Column {col} will be transformed')
                                dict_expr['expr'][col]= expr
                                break
                        elif percent > self.o_config.flag_percent: 
                            if type_op == 'flag' and True: 
                                expr= self.flag_expr(
                                    col=col, 
                                    list_index_outlier=list_index_out
                                )
                                
                                logger.info(f'Column {col} will be flagged')
                                dict_expr['expr'][col]= expr
                                break
                            else: 
                                continue
            else: 
                logger.info(f'No outliers were detected for {col}')
        
        return dict_expr
    
    def fit_expressions(self, x_train: pl.DataFrame) -> pl.DataFrame: 
        dict_expr= self.iqr_expr()
        
        self.filter_expr= dict_expr['filter']
        self.expr= dict_expr['expr']
        
        if self.filter_expr: 
            x_train= x_train.filter(self.filter_expr)
            logger.info('Frame was filtered')
        if self.expr: 
            x_train= x_train.with_columns(self.expr)
            logger.info('Frame expressions were applied')
        
        return x_train
    
    def transform_expressions(self, x_test: pl.DataFrame) -> pl.DataFrame: 
        if self.filter_expr: 
            x_test= x_test.filter(self.filter_expr)
            logger.info('Frame was filtered')
        if self.expr: 
            x_test= x_test.with_columns(self.expr)
            logger.info('Frame expressions were applied')
        
        return x_test





