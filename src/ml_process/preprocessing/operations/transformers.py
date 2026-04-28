import polars as pl 

class TransformationOperation: 
    @staticmethod
    def log1p(col: str) -> pl.Expr: 
        return pl.col(col).log1p().alias(col)
    
    @staticmethod
    def sqrt(col: str) -> pl.Expr: 
        return pl.col(col).sqrt().alias(col)
    
    @staticmethod
    def square(col: str) -> pl.Expr: 
        return pl.col(col).pow(2).alias(col)







