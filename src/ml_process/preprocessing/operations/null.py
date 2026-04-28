from ....strategies.pre_processing_strategies import NullCategoricHandler, NullNumericHandler

from typing import Optional
import polars as pl 

class NullNumHandler: 
    @staticmethod
    def filter(col: str) -> pl.Expr: 
        return ~pl.col(col).is_null().alias(col)
    
    @staticmethod
    def median(col: str) -> pl.Expr: 
        return pl.median(col).alias(col)
    
    @staticmethod
    def zero(col: str) -> pl.Expr: 
        return pl.col(col).fill_null(0)
    
    @staticmethod
    def mean(col: str) -> pl.Expr: 
        return pl.mean(col).alias(col)
    
    @classmethod
    def get_null_num_handler_expr(cls, col: str, null_method: NullNumericHandler) -> pl.Expr: 
        match null_method: 
            case NullNumericHandler.FILTER: 
                expression= cls.filter(col=col)
            case NullNumericHandler.MEDIAN: 
                expression= cls.median(col=col)
            case NullNumericHandler.ZERO: 
                expression= cls.zero(col=col)
            case NullNumericHandler.MEAN: 
                expression= cls.mean(col=col)
        
        return expression

class NullCatHandler: 
    @staticmethod
    def filter(col: str) -> pl.Expr: 
        return ~pl.col(col).is_null().alias(col)
    
    @staticmethod
    def constant_value(col: str, constant_value: str) -> pl.Expr: 
        return pl.col(col).fill_null(constant_value)
    
    @classmethod
    def get_null_cat_handler_expr(cls, col: str, null_method: NullCategoricHandler, constant_value: Optional[str]=None) -> pl.Expr: 
        match null_method: 
            case NullCategoricHandler.FILTER: 
                expression= cls.filter(col=col)
            case NullCategoricHandler.CONSTANTVALUE: 
                expression= cls.constant_value(col=col, constant_value=constant_value)
        
        return expression

