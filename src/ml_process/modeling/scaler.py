from sklearn.preprocessing import MinMaxScaler, StandardScaler, RobustScaler

from typing import Callable, Optional
from pydantic import BaseModel

import polars as pl
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(mesagge)s')
logger= logging.getLogger(__name__)

class SelectScaler: 
    def __init__(self, frame: pl.DataFrame, config_ml: BaseModel):
        self.frame= frame
        self.config_ml= config_ml.scaler_rules
    
    def robust_scaler(self) -> Callable: 
        return RobustScaler()
    
    def standard_scaler(self) -> Callable: 
        return StandardScaler()
    
    def min_max_scaler(self) -> Callable: 
        return MinMaxScaler()
    
    def total_mean_outliers(self) -> Optional[float]: 
        total= 0
        
        for col in self.frame.columns:
            q1= self.frame[col].quantile(0.25)
            q3= self.frame[col].quantile(0.75)
            
            iqr= q3-q1
            
            lower= q1 - iqr*1.5
            upper= q3 + iqr*1.5
            
            total_outlier= self.frame.filter((pl.col(col) < lower) | (pl.col(col) > upper))
            total+= total_outlier.height
        
        if total == 0: 
            return None
        else: 
            return total/self.frame.height
    
    def auto(self) -> Optional[Callable]: 
        mean_percent= self.total_mean_outliers()
        
        if not mean_percent: 
            logger.info('No outliers were detected')
            return None
        
        rs_percent= self.config_ml.robust_scaler_percent
        ss_percent= self.config_ml.standard_scaler_percent
        
        if mean_percent < ss_percent: 
            return self.standard_scaler()
        elif mean_percent > rs_percent: 
            return self.robust_scaler()
        else: 
            return self.min_max_scaler()
    
    # 🚨🚨🚨 the manual way is being tested, it is not stable 🚨🚨🚨
    def manual(self, config: BaseModel) -> Callable: 
        raise ValueError('MANUAL WAY NOT AVAILABLE')



