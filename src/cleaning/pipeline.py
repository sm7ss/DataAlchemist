from .columns_name import rename_columns
from .datatypes import DataTypeListExpr
from .duplicated import duplicated_rows
from .drop_columns import drop_columns

from pydantic import BaseModel
from typing import List, Dict, Any, Tuple

import polars as pl 
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

class CleanDataFrame: 
    def __init__(self, frame: pl.DataFrame, config_cleaning: BaseModel, config: BaseModel,  JSON: Dict[str, Any]):
        self.frame= frame
        
        self.config= config
        self.config_threshold= config.cleaning
        self.config_cleaning= config_cleaning
        
        self.JSON= JSON
    
    def _rename_columns(self, frame: pl.DataFrame, rename_dict: Dict[str, str]) -> pl.DataFrame:
        class_rename_columns= rename_columns(frame=frame, rename_dict=rename_dict)
        
        return class_rename_columns
    
    def _change_datatypes(self, frame: pl.DataFrame) -> pl.DataFrame: 
        class_change_datatypes= DataTypeListExpr(frame=frame, config=self.config_threshold)
        
        expr_datatypes= class_change_datatypes.list_expr_cast()
        new_frame= frame.with_columns(expr_datatypes)
        logger.info('Datypes were applied')
        
        return new_frame
    
    def _duplicates(self, frame: pl.DataFrame) -> pl.DataFrame: 
        class_duplicates= duplicated_rows(frame=frame)
        return class_duplicates
    
    def _drop_columns(self, frame: pl.DataFrame, list_drop: List[str]) -> pl.DataFrame: 
        class_drop_columns= drop_columns(frame=frame, list_drop=list_drop)
        return class_drop_columns
    
    def clean_dataframe(self) -> Tuple[pl.DataFrame]: 
        frame= self.frame.with_row_index()
        
        rename_columns= self.config_cleaning.rename_columns
        change_datatypes= self.config_cleaning.change_datatypes
        duplicates= self.config_cleaning.duplicates
        drop_columns= self.config_cleaning.drop_columns
        
        if rename_columns: 
            frame= self._rename_columns(frame=frame, rename_dict=rename_columns)
        
        if change_datatypes: 
            frame= self._change_datatypes(frame=frame)
        
        if duplicates: 
            frame= self._duplicates(frame=frame)
        
        if drop_columns: 
            frame= self._drop_columns(frame=frame, list_drop=drop_columns)
        logger.info('DataFrame is cleaned')
        
        target= self.config.data.target
        x= frame.drop(target, strict=False)
        y= frame[target, 'index']
        
        logger.info('X and Y were obtained')
        
        return x, y



