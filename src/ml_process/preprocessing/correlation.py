import polars as pl 
import logging 
from pydantic import BaseModel
from typing import Union, Optional, Dict, Any, List

from ...strategies.pre_processing_strategies import HighCorrelationActions

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

class CorrelationExpr: 
    @staticmethod
    def remove(frame: pl.DataFrame, col: Union[str, List[str]]) -> pl.DataFrame: 
        return frame.drop(col)
    
    @staticmethod
    def join(col_1: str, col_2: str) -> pl.Expr: 
        return (pl.col(col_1) + pl.col(col_2) / 2).alias(f'{col_1}_{col_2}_avg')

class CorrelationPreprocessing: 
    def __init__(self, frame: pl.DataFrame, corr_dict: Dict[str, Any], config: BaseModel):
        self.frame= frame
        self.num_frame= frame.select(pl.selectors.numeric())
        
        self.method= config.ml_preprocessing.correlation.high_correlation
        self.column= config.ml_preprocessing.correlation.remove_column
        
        self.corr= corr_dict.get('high_correlations')
        self.expr= CorrelationExpr()
    
    def auto_correlation(self) -> Union[str, List[pl.Expr]]: 
        list_expr= []
        
        if not self.corr: 
            return 'No high correlation was found'
        
        for i in range(len(self.corr)): 
            col_1= self.corr[i][0]
            col_2= self.corr[i][1]
            
            logger.info(f'Column {col_1} and column {col_2} were joined')
            
            expr= self.expr.join(col_1=col_1, col_2=col_2)
            
            list_expr.append(expr)
        
        return list_expr
    
    def manual_correlation(self) -> Union[pl.DataFrame, List[pl.Expr]]: 
        if not self.corr: 
            return 'No high correlation was found'
        
        list_expr= []
        
        match self.method: 
            case HighCorrelationActions.REMOVE: 
                self.frame= self.expr.remove(frame=self.frame, col=self.column)
                logger.info(f'Column {self.column} was deleated')
            case HighCorrelationActions.JOIN: 
                for i in range(len(self.corr)): 
                    col_1= self.corr[i][0]
                    col_2= self.corr[i][1]
                    expr= self.expr.join(col_1=col_1, col_2=col_2)
                    list_expr.append(expr)
                    list_expr.append(f'Column {col_1} and {col_2} were joined')
        
        if list_expr: 
            return list_expr
        
        return self.frame




