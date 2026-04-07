from typing import List, Tuple

import polars as pl 
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s-&(levelname)s-%(message)s')
logger= logging.getLogger(__name__)

class EdaGeneralInfo: 
    def __init__(self, frame: pl.DataFrame):
        self.frame= frame
        
        self.info_eda_dict= {}
    
    def shape(self) -> Tuple[int]: 
        return self.frame.shape
    
    def available_columns(self) -> List[str]: 
        return self.frame.columns
    
    def basic_statistics(self) -> pl.DataFrame: 
        return self.frame.describe()
    
    def eda_general_info_format(self) -> str:
        print('SHAPE')
        print(self.shape())
        print('AVAILABLE COLUMNS')
        print(self.available_columns())
        print('BASIC STATISTICS')
        print(self.basic_statistics())
        
        
        
        



