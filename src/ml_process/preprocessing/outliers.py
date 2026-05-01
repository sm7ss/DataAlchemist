from ...strategies.strategies import analysis_outliers
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
        return pl.col(col).clip(lower, upper).alias(col)
    
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

class OutlierPreprocessingPipeline: 
    def __init__(self, frame: pl.DataFrame, config_outlier: BaseModel, config: BaseModel):
        self.frame= frame.with_row_index()
        
        self.config= config
        self.o_config= config_outlier
        
        self.numeric_frame= self.frame.select(pl.selectors.numeric())
        
        self.value= ImputeOutlierValue(frame=self.frame)
        self.filter= FilterOutliersExpr()
    
    def input_expr(self, col: str, method: OutlierImpute, list_index_out: List[int]) -> pl.Expr: 
        value= self.value.get_value(col=col, method=method)
        
        return  pl.when(pl.col('index').is_in(list_index_out)).then(pl.lit(value)).otherwise(pl.col(col)).alias(col)
    
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
    
    def iqr_method(self, col) -> Dict[str, Any]: 
        q1= self.numeric_frame[col].quantile(0.25)
        q3= self.numeric_frame[col].quantile(0.75)
        
        iqr= q3 - q1
        
        lower= q1 - iqr *1.5
        upper= q3 + iqr *1.5
        
        outlier_frame= self.numeric_frame.filter((pl.col(col) < lower) | (pl.col(col) > upper))
        list_index_out= outlier_frame.get_column('index').to_list()
        
        return {
            'lower': lower, 
            'upper': upper, 
            'list': list_index_out
        }
    
    def iqr_auto_expr_method(self, outlier_dict: Dict[str, Any]) -> List[pl.Expr]:
        list_iqr_expr= []
        
        for col in self.numeric_frame.columns:
            dict_iqr_method= self.iqr_method(col=col)
            list_index_out= dict_iqr_method['list']
            
            lower= dict_iqr_method['lower']
            upper= dict_iqr_method['upper']
            
            if list_index_out: 
                logger.info(f'The total outliers detected were {len(list_index_out)} for column {col}')
                
                percent= outlier_dict[col].get('percent_outliers')
                sugg= outlier_dict[col].get('suggestion')
                
                for type_op, operation in sugg.items(): 
                    if percent < self.o_config.filter_percent: 
                        if type_op == 'filter' and operation: 
                            logger.info(f'Column {col} was filtered into type {type_op} with operation {operation}')
                            expr= self.filter_expr(
                                method=operation, 
                                col=col, 
                                out_index=list_index_out, 
                                upper=upper, 
                                lower=lower
                            )
                            list_iqr_expr.append(expr)
                            break
                    elif percent < self.o_config.impute_percent: 
                        if type_op == 'impute' and operation: 
                            logger.info(f'Column {col} was imputed in type {type_op} with operation {operation}')
                            expr= self.input_expr(
                                col=col, 
                                method=operation, 
                                list_index_out=list_index_out
                            )
                            list_iqr_expr.append(expr)
                            break
                    elif percent > self.o_config.transform_percent: 
                        if type_op == 'transform' and operation: 
                            logger.info(f'Column {col} was transformed into the type {type_op} with the transformer {operation}')
                            expr= self.transform_expr(col=col, method=operation)
                            list_iqr_expr.append(expr)
                            break
                    elif percent > self.o_config.flag_percent: 
                        if type_op == 'flag' and True: 
                            logger.info(f'Column {col} was flagged')
                            expr= self.flag_expr(col=col, list_index_outlier=list_index_out)
                            list_iqr_expr.append(expr)
                            break
                        else: 
                            logger.info(f'Column {col} was not flagged')
            else: 
                logger.info(f'No outliers were detected for {col}')
        
        return list_iqr_expr
    
    def iqr_manual_expr_method(self) -> List[pl.Expr]: 
        list_iqr_expr= []
        
        filter= self.config.ml_preprocessing.outlier.filter
        i_outlier= self.config.ml_preprocessing.outlier.impute_outliers
        flag= self.config.ml_preprocessing.outlier.flag
        transform= self.config.ml_preprocessing.outlier.transform
        
        for col in self.numeric_frame.columns: 
            dict_method= self.iqr_method(col=col)
            
            if filter: 
                logger.info(f'Column {col} was filtered with operation {filter}')
                expr= self.filter_expr(
                    method=filter, 
                    col=col, 
                    out_index=dict_method['list'], 
                    lower=dict_method['lower'], 
                    upper=dict_method['upper']
                )
                list_iqr_expr.append(expr)
            elif i_outlier: 
                logger.info(f'Column {col} was imputed with operation {i_outlier}')
                expr= self.input_expr(
                    col=col, 
                    method=i_outlier, 
                    list_index_out=dict_method['list']
                )
                list_iqr_expr.append(expr)
            elif transform: 
                logger.info(f'Column {col} was transformed with the transformer {transform}')
                expr= self.transform_expr(
                    col=col, 
                    method=transform
                )
                list_iqr_expr.append(expr)
            elif flag == True: 
                logger.info(f'Column {col} was flagged')
                expr= self.flag_expr(
                    col=col, 
                    list_index_outlier=dict_method['list']
                )
                list_iqr_expr.append(expr)
        
        return list_iqr_expr
    
    def pipeline(self, 
            method_anal: analysis_outliers, 
            auto: bool, 
            outlier_dict: Optional[Dict[str, Any]]= None
        ) -> pl.DataFrame: 
        
        match method_anal: 
            case analysis_outliers.IQR: 
                if auto:
                    list_expr= self.iqr_auto_expr_method(outlier_dict=outlier_dict)
                else: 
                    list_expr= self.iqr_manual_expr_method()
        
        frame= self.frame.with_columns(list_expr)
        
        return frame.drop('index')








