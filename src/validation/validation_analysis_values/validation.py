from pydantic import BaseModel, Field, model_validator
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

class scaler_val(BaseModel): 
    robust_scaler_percent: float= Field(ge=0.0, le=100.0)
    standard_scaler_percent: float= Field(ge=0.0, le=100.0)
    
    @model_validator(mode='after')
    def difference_val(self): 
        robust= self.robust_scaler_percent
        standard= self.standard_scaler_percent
        
        if robust == standard: 
            logger.error(f'The value percent for RobustScaler and StandardScaler cant be the same.\nStandard percent: {standard}, Robust percent: {robust}')
            raise ValueError(f'The value percent for RobustScaler and StandardScaler cant be the same.\nStandard percent: {standard}, Robust percent: {robust}')
        
        return self

class filter_val(BaseModel): 
    none: float= Field(ge=0.0, le=100.0)
    trim: float= Field(ge=0.0, le=100.0)
    
    @model_validator(mode='after')
    def difference_val(self): 
        none= self.none
        trim= self.trim
        
        if none == trim: 
            logger.error(f'The value percent for None and Trim cant be the same.\nNone percent: {none}, Trim percent: {trim}')
            raise ValueError(f'The value percent for None and Trim cant be the same.\nNone percent: {none}, Trim percent: {trim}')
        
        return self

class impute_val(BaseModel): 
    none: float= Field(ge=0.0, le=100.0)

class flag_val(BaseModel): 
    flag_true: float= Field(ge=0.0, le=100.0)

class transform_val(BaseModel): 
    log1p: float= Field(ge=0.0, le=100.0)
    sqrt: float= Field(ge=0.0, le=100.0)

class outlier_decision_maker(BaseModel): 
    scaler: scaler_val
    filter: filter_val
    impute: impute_val
    flag: flag_val
    transform: transform_val

