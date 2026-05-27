from ..strategies.cleaning_strategies import DataTypes

from pydantic import BaseModel
from typing import List

import polars as pl
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

class DataTypeExpr: 
    @staticmethod
    def cast_float_32(col: str) -> pl.Expr: 
        return pl.col(col).cast(pl.Float32).alias(col)
    
    @staticmethod
    def cast_int_32(col: str) -> pl.Expr: 
        return pl.col(col).cast(pl.Int32).alias(col)
    
    @staticmethod
    def cast_int_64(col: str) -> pl.Expr: 
        return pl.col(col).cast(pl.Int64).alias(col)
    
    @staticmethod
    def cast_utf(col: str) -> pl.Expr: 
        return pl.col(col).cast(pl.Utf8).alias(col)

class DataTypeListExpr:
    def __init__(self, frame: pl.DataFrame, config: BaseModel):
        self.frame= frame
        self.c_datatypes= config.cleaning.change_datatypes
        
        self.dt_expr= DataTypeExpr()
    
    def expr(self, col: str, type_dt: DataTypes) -> pl.Expr: 
        match type_dt: 
            case DataTypes.FLOAT32: 
                logger.info('Expression for floating type was obtained ')
                expr= self.dt_expr.cast_float_32(col=col)
            case DataTypes.INT32: 
                logger.info('Expression for int type was obtained ')
                expr= self.dt_expr.cast_int_32(col=col)
            case DataTypes.INT64: 
                logger.info('Expression for int type was obtained ')
                expr= self.dt_expr.cast_int_64(col=col)
            case DataTypes.UTF8: 
                logger.info('Expression for string type was obtained ')
                expr= self.dt_expr.cast_utf(col=col)
        
        return expr
    
    def list_expr_cast(self) -> List[pl.Expr]:
        list_expr= []
        
        for col, method in self.c_datatypes.items(): 
            expr= self.expr(col=col, type_dt=method)
            list_expr.append(expr)
        
        return list_expr


