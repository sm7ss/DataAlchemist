from ...strategies.strategies import analysis_outliers
from ...strategies.pre_processing_strategies import OutlierImpute
from .operations.imputer import ImputeOutlier

from typing import List

import logging
import polars as pl 

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

class InputOutliers: 
    def __init__(self, frame: pl.DataFrame):
        self.frame= frame.with_row_index()
        self.numeric_frame= self.frame.select(pl.selectors.numeric())
        
        self.value= ImputeOutlier(frame=self.frame)
    
    def iqr_method(self, method: OutlierImpute) -> List[pl.Expr]:
        list_expr= []
        
        for col in self.numeric_frame.columns: 
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
                list_expr.append(pl.when(pl.col('index').is_in(list_index_out)).then(pl.lit(value)).otherwise(pl.col(col)).alias(col))
            else: 
                logger.info(f'No outliers were detected for {col}')
        
        return list_expr
    
    def get_frame(self, method_anal: analysis_outliers, method_op: OutlierImpute) -> pl.DataFrame: 
        match method_anal: 
            case analysis_outliers.IQR: 
                list_expr= self.iqr_method(method=method_op)
        
        frame= self.frame.with_columns(list_expr)
        
        return frame.drop('index')


