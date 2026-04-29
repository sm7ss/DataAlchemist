from ...strategies.strategies import analysis_outliers
from ...strategies.pre_processing_strategies import OutlierImpute, OutlierFilter

from typing import List, Union, Optional

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

# CHANGE HERE
class InputOutliersExpr: 
    def __init__(self, frame: pl.DataFrame):
        self.frame= frame.with_row_index()
        self.numeric_frame= self.frame.select(pl.selectors.numeric())
        
        self.value= ImputeOutlierValue(frame=self.frame)
    
    def iqr_method(self, col: str, method: OutlierImpute) -> pl.Expr:
        value= self.value.get_value(col=col, method=method)
        
        q1= self.numeric_frame[col].quantile(0.25)
        q3= self.numeric_frame[col].quantile(0.75)
        
        iqr= q3 - q1
        
        lower= q1 - iqr *1.5
        upper= q3 + iqr *1.5
        
        outlier_frame= self.numeric_frame.filter((pl.col(col) < lower) | (pl.col(col) > upper))
        list_index_out= outlier_frame.get_column('index').to_list()
        
        if list_index_out: 
            logger.info(f'The total outliers detected were {len(list_index_out)} for column {col}')
            return pl.when(pl.col('index').is_in(list_index_out)).then(pl.lit(value)).otherwise(pl.col(col)).alias(col)
        else: 
            logger.info(f'No outliers were detected for {col}')
    
    #This will be deleated
    def get_list_expr(self, method_anal: analysis_outliers, method_op: OutlierImpute) -> pl.DataFrame: 
        match method_anal: 
            case analysis_outliers.IQR: 
                list_expr= self.iqr_method(method=method_op)
        
        frame= self.frame.with_columns(list_expr)
        
        return frame.drop('index')

# TENGO QUE ABSTRAER LA LOGICA DE OUTLIERS Y EN BASE A ESO OBTENER SUS OPERACIONES

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

class FlagOutliersExpr: 
    pass

# THIS WILL BE CALLED FROM .transformers for expressions
class TransfrormOutliersExpr: 
    pass







