from ....strategies.pre_processing_strategies import OutlierImpute
import polars as pl

class ImputeOutlier: 
    def __init__(self, frame: pl.DataFrame):
        self.frame= frame
    
    def median(self, col: str) -> float: 
        return self.frame[col].median()
    
    def mean(self, col: str) -> float: 
        return self.frame[col].mean()
    
    def get_value(self, col: str, method: OutlierImpute) -> float: 
        match method: 
            case OutlierImpute.MEDIAN: 
                value= self.median(col=col)
            case OutlierImpute.MEAN: 
                value= self.mean(col=col)
        return value





