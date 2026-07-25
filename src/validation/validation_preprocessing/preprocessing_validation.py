from ...strategies.pre_processing_strategies import NullCategoricHandler, NullNumericHandler, DistributionTransformer, OutlierFilter, OutlierImpute, OutlierTransform, CorrSampling, HighCorrelationActions, CategoryOperation

from ...strategies.strategies import AnalysisOutliers

from pydantic import BaseModel, model_validator, field_validator
from typing import List, Union, Optional

import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

class distribution_val(BaseModel): 
    transformer: Optional[DistributionTransformer]

class outlier_val(BaseModel): 
    strategy: Optional[AnalysisOutliers]
    filter: Optional[OutlierFilter]
    impute_outliers: Optional[OutlierImpute]
    flag: Optional[bool]
    transform: Optional[OutlierTransform]
    
    @field_validator('strategy')
    def strategy_val(cls, v): 
        if not v: 
            v= 'iqr'
            logger.warning('As None value was given to "strategy" then the method IQR will be used')
        
        return v

class correlation_val(BaseModel): 
    high_correlation: Optional[HighCorrelationActions]
    remove_column: Union[str, List[str], None]
    
    @model_validator(mode='after')
    def correlation_val(self): 
        hc= self.high_correlation
        rc= self.remove_column
        
        if not hc: 
            self.high_correlation= 'join'
            logger.warning('The value for "high_correlation" is now "join" because "high_correlation" was a None value')
        
        if rc and not hc: 
            self.remove_column= None
            logger.warning('The value for "remove_column" was deleated cause "remove" operation in "high_correlation" was not found. "high_correlation" now will be "join"')
        
        return self

class category_val(BaseModel): 
    operation: Optional[CategoryOperation]
    name_operation_value: Optional[str]
    
    @field_validator('operation')
    def operation_val(cls, v): 
        if not v: 
            v= 'group'
            logger.warning('As no value was given to "operation" then the new value will be "group"')
        
        return v 
    
    @field_validator('name_operation_value')
    def name_operation_value_val(cls, v): 
        if not v: 
            v= 'Unknown'
            logger.warning('As no value was given to "name_operation_value" the new value will be "Unknown"')
        
        return v

class ml_preprocessing_val(BaseModel): 
    columns: Union[List[str], str, None]
    
    representative_column: Union[str, List[str], None]
    sampling: Optional[CorrSampling]
    
    null_num_handler: Optional[NullNumericHandler]
    null_cat_handler: Optional[NullCategoricHandler]
    null_cat_handler_value: Optional[str]
    
    distribution: distribution_val
    outlier: outlier_val
    correlation: correlation_val
    category: category_val
    
    @field_validator('sampling')
    def sampling_val(cls, v): 
        if not v: 
            logger.warning('As no value was found for sampling, "random" will be used')
            return 'random'
        else: 
            return v
    
    @field_validator('null_num_handler')
    def null_num_handler_val(cls, v): 
        if not v: 
            logger.warning('As no value was found for null_num_handler, "median" will be used')
            return 'median'
        else: 
            return v
    
    @field_validator('null_cat_handler')
    def null_cat_handler_val(cls, v): 
        if not v: 
            logger.warning('As no value was found for null_cat_handler, "constantValue" will be used')
            return 'constantValue'
        else: 
            return v
    
    @field_validator('null_cat_handler_value')
    def null_cat_handler_value_val(cls, v): 
        if not v: 
            logger.warning('As no value was found for null_cat_handler_value, "Unknown" will be used')
            return 'Unknown'
        else: 
            return v

