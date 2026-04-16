from pydantic import BaseModel
from typing import Dict, Any

import polars as pl 
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s-&(levelname)s-%(message)s')
logger= logging.getLogger(__name__)

class EdaNullValues: 
    def __init__(self, frame: pl.DataFrame, config_eda: BaseModel):
        self.frame= frame
        self.column_percentage= config_eda.null_values_percent_column
        self.row_percentage= config_eda.null_values_percent_row
    
    def null_horizontal(self, col: str) -> int: 
        umbral= (self.frame.width*self.row_percentage)
        
        frame_nulls= self.frame.filter(pl.col(col).is_null())
        return frame_nulls.with_columns(
            sum_nulls= pl.sum_horizontal(pl.col('*').is_null().cast(pl.Int32))
        ).filter(pl.col('sum_nulls') > umbral).height
    
    def null_column(self, col: str) -> int: 
        return self.frame.filter(pl.col(col).is_null()).height
    
    def total_nulls_values(self) -> Dict[str, Any]: 
        columns= self.frame.columns
        total_height= self.frame.height
        col_per= self.column_percentage*100
        row_per= self.row_percentage*100
        
        nulls_dict={}
        total_nulls= 0
        
        for col in columns: 
            null_count_col= self.null_column(col=col)
            null_count_row= self.null_horizontal(col=col)
            
            nulls_dict[col]= {}
            nulls_dict[col]= {}
            
            null_percent= (null_count_col/total_height)*100
            
            #TOTAL 
            total_nulls+=null_count_col
            #COLUMN
            if null_count_col > 0: 
                row_null_percent= (null_count_row/null_count_col)*100
                if null_percent < col_per:
                    nulls_dict[col]['total_nulls_column']= null_count_col
                    nulls_dict[col]['total_nulls_row']= null_count_row
                    nulls_dict[col]['nulls_percent']= round((null_count_col/total_height)*100, 3)
                    if row_null_percent < row_per: 
                        nulls_dict[col]['action'] = 'analyse'
                    else: 
                        nulls_dict[col]['action'] = 'delete'
                else: 
                    nulls_dict[col]['total_nulls_column']= null_count_col
                    nulls_dict[col]['total_nulls_row']= null_count_row
                    nulls_dict[col]['nulls_percent']= round((null_count_col/total_height)*100, 3)
                    nulls_dict[col]['action'] = 'delete'
            else: 
                nulls_dict[col]['total_nulls_column']= null_count_col
                nulls_dict[col]['total_nulls_row']= null_count_row
                nulls_dict[col]['action'] = 'keep'
        
        nulls_dict['total_nulls']= total_nulls
        return nulls_dict



