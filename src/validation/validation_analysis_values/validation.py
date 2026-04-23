from pydantic import BaseModel, Field, model_validator
from ...strategies.pre_processing_strategies import NullHandler, CorrSampling
from typing import List, Union

import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

class distribution_decision_maker_val(BaseModel): 
    tail_length: int= Field(ge=50, le=1000)
    scaler_concentration: float= Field(ge=0.1, le=100) 

class out_scaler_val(BaseModel): 
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

class out_filter_val(BaseModel): 
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

class out_impute_val(BaseModel): 
    none: float= Field(ge=0.0, le=100.0)

class out_flag_val(BaseModel): 
    flag_true: float= Field(ge=0.0, le=100.0)

class out_transform_val(BaseModel): 
    log1p: float= Field(ge=0.0, le=100.0)

class outlier_decision_maker_val(BaseModel): 
    scaler: out_scaler_val
    filter: out_filter_val
    impute: out_impute_val
    flag: out_flag_val
    transform: out_transform_val

class corr_sampling(BaseModel): 
    percent: float= Field(ge=0.001, le=100.0)
    method: CorrSampling
    representative_columns: Union[List[str], str, None]
    
    @model_validator(mode='after')
    def type_operation(self): 
        percent= self.percent
        method= self.method
        representative_columns= self.representative_columns
        
        match method: 
            case CorrSampling.RANDOM: 
                if not percent: 
                    logger.error('A percent should be given for random sample')
                    raise ValueError('A percent should be given for random sample')
            case CorrSampling.REPRESENTATIVE: 
                if not representative_columns: 
                    logger.error('You need to asign a column or a list of columns, because you choose i method a representative sample')
                    raise ValueError('You need to asign a column or a list of columns, because you choose i method a representative sample')
        
        return self

class correlation_decision_maker_val(BaseModel): 
    sampling: corr_sampling
    handle_nulls: NullHandler
    threshold: float= Field(gt=0.0, le=100.0)

class category_threshold_ml_analysis_val(BaseModel): 
    few_categories: int = Field(ge=1, le=10)
    many_categories: int= Field(ge=10, le=100)
    high_cardinality: int= Field(ge=10)
    no_rare_values_and_reasonable_categories: int= Field(ge=1, le=10)

class category_decision_maker_val(BaseModel): 
    rare_threshold_limit: int= Field(ge=1, le=100)
    threshold_ml_analysis: category_threshold_ml_analysis_val

class validator_analysis_values(BaseModel): 
    distribution_decision_maker: distribution_decision_maker_val
    outlier_decision_maker: outlier_decision_maker_val
    correlation_decision_maker: correlation_decision_maker_val
    category_decision_maker: category_decision_maker_val
