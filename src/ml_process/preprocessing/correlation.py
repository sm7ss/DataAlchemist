import polars as pl 
import logging 
from pydantic import BaseModel
from typing import Union, Dict, Any, List

from ...strategies.pre_processing_strategies import HighCorrelationActions

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

class CorrelationExpr: 
    def __init__(self, frame: pl.DataFrame):
        self.frame= frame
    
    def remove(self, col: Union[str, List[str]]) -> pl.DataFrame: 
        return self.frame.drop(col)
    
    def join(self, col_1: str, col_2: str) -> pl.Expr: 
        return ((pl.col(col_1) + pl.col(col_2)) / 2).alias(f'{col_1}_{col_2}_avg')

class CorrelationPreprocessing: 
    def __init__(self, frame: pl.DataFrame, corr_dict: Dict[str, Any], config: BaseModel):
        self.frame= frame
        
        self.corr_config= config.correlation
        
        self.corr= corr_dict.get('high_correlations')
        self.expr= CorrelationExpr(frame=self.frame)
    
    def auto_correlation(self) -> Dict[List[pl.Expr], List[str]]: 
        if not self.corr:
            logger.info('No high correlation was found') 
            return None
        
        list_expr= []
        list_col_drop= []
        
        for i in range(len(self.corr)): 
            col_1= self.corr[i][0]
            col_2= self.corr[i][1]
            
            logger.info(f'Column {col_1} and column {col_2} were joined')
            
            expr= self.expr.join(col_1=col_1, col_2=col_2)
            list_expr.append(expr)
            list_col_drop.append(col_1)
            list_col_drop.append(col_2)
        
        return {
            'drop': list_col_drop, 
            'expr': list_expr
        }




