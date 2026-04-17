from typing import List, Tuple, Dict, Any, Optional

import polars as pl 
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s-&(levelname)s-%(message)s')
logger= logging.getLogger(__name__)

class EdaGeneralInfo: 
    def __init__(self, frame: pl.DataFrame):
        self.frame= frame
    
    def shape(self) -> Tuple[int]: 
        return self.frame.shape
    
    def available_columns(self) -> List[str]: 
        return self.frame.columns
    
    def basic_statistics(self) -> Optional[Dict[str, Any]]: 
        statistics_dict= {}
        numeric_frame= self.frame.select(pl.selectors.numeric())
        if numeric_frame.is_empty(): 
            return None
        
        describe= numeric_frame.describe()
        
        for col in describe.columns: 
            if col != 'statistic': 
                statistics_dict[col]={}
                statistics_dict[col]['mean']= describe.filter(pl.col('statistic')=='mean')[col].item()
                statistics_dict[col]['std']= describe.filter(pl.col('statistic')=='std')[col].item()
                statistics_dict[col]['25']= describe.filter(pl.col('statistic')=='25%')[col].item()
                statistics_dict[col]['50']= describe.filter(pl.col('statistic')=='50%')[col].item()
                statistics_dict[col]['75']= describe.filter(pl.col('statistic')=='75%')[col].item()
                statistics_dict[col]['min']= describe.filter(pl.col('statistic')=='min')[col].item()
                statistics_dict[col]['max']= describe.filter(pl.col('statistic')=='max')[col].item()
        
        return statistics_dict
    
    def datatype(self) -> Dict[str, Any]: 
        datatype_dict= {}
        
        for col, type_col in self.frame.schema.items(): 
            datatype_dict[col]= str(type_col)
        
        return datatype_dict
    
    def unique_values(self) -> Dict[str, Any]: 
        unique_values_dict= {}
        cat_vals= self.frame.select(pl.selectors.string())
        if cat_vals.is_empty(): 
            return None
        
        for col in cat_vals.columns: 
            unique_num= cat_vals[col].n_unique()
            
            unique_values_dict[col]=unique_num
        
        return unique_values_dict
    
    def eda_general_info_format(self) -> Dict[str, Any]:
        shape= self.shape()
        info_eda_dict= {}
        
        info_eda_dict['total_columns']= shape[1]
        info_eda_dict['total_rows']= shape[0]
        
        info_eda_dict['available_columns']= self.available_columns()
        info_eda_dict['datatype']= self.datatype()
        
        info_eda_dict['statistics']= self.basic_statistics()
        info_eda_dict['unique_values']= self.unique_values()
        
        return info_eda_dict



