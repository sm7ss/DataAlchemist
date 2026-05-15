from sklearn.metrics import get_scorer_names
from typing import List, Dict, Optional
from pydantic import BaseModel, field_validator, Field

import psutil
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(mesagge)s')
logger= logging.getLogger(__name__)

class sacler_rules_val(BaseModel): 
    robust_scaler_percent: float= Field(ge=0.01, le=1.0)
    standard_scaler_percent: float= Field(ge=0.01, le=1.0)

class best_model_rules(BaseModel): 
    cv_fold: int= Field(ge=0, le=10)
    train_test_difference_percent: float= Field(ge=0.01, le=1.00)
    unstable_cross_validation_percent: float= Field(ge=0.01, le=1.00)

class linear_regression_val(BaseModel): 
    enable: bool
    fit_intercept: List[bool]

class decision_tree_val(BaseModel): 
    enable: bool
    max_depth: Optional[List[int]]
    min_samples_split: List[int]
    
    @field_validator('max_depth')
    def max_depth_val(cls, v): 
        if v is None: 
            return v
        for i in v: 
            if i < 1: 
                logger.error(f'Max depth cant be lower than 1')
                raise ValueError(f'Max depth cant be lower than 1')
        return v
    
    @field_validator('min_samples_split')
    def min_samples_split_val(cls, v): 
        for i in v: 
            if i < 1: 
                logger.error(f'Min sample split cant be lower than 1')
                raise ValueError(f'Min sample split cant be lower than 1')
        return v

class random_forest_val(BaseModel): 
    enable: bool
    n_estimators: List[int]
    max_depth: Optional[List[int]]
    min_samples_split: List[int]
    
    @field_validator('max_depth')
    def max_depth_val(cls, v): 
        if v is None: 
            return v
        for i in v: 
            if i < 1: 
                logger.error(f'Max depth cant be lower than 1')
                raise ValueError(f'Max depth cant be lower than 1')
        return v
    
    @field_validator('min_samples_split')
    def min_samples_split_val(cls, v): 
        for i in v: 
            if i < 1: 
                logger.error(f'Min sample split cant be lower than 1')
                raise ValueError(f'Min sample split cant be lower than 1')
        return v
    
    @field_validator('n_estimators')
    def n_estimators_val(cls, v): 
        for i in v: 
            if i < 1: 
                logger.error(f'N estimators cant be lower than 1')
                raise ValueError(f'N estimators cant be lower than 1')
        return v

class models_hyperparameters_val(BaseModel): 
    linear_regression: linear_regression_val
    decision_tree: decision_tree_val
    random_forest: random_forest_val

class grid_search_cv_val(BaseModel): 
    cv: int= Field(ge=1, le=10)
    scoring: Dict[str, str]
    n_jobs: int= Field(ge=1)
    
    @field_validator('scoring')
    def scoring_val(cls, v): 
        list_metrics= get_scorer_names()
        
        for key, value in v.items(): 
            if key != value: 
                logger.error(f'the key {key} must equal the value {value}')
                raise ValueError(f'the key {key} must equal the value {value}')
            if value not in list_metrics: 
                logger.error(f'Value {value} must be in the available metrics: \n{list_metrics}')
                raise ValueError(f'Value {value} must be in the available metrics: \n{list_metrics}')
        
        return v
    
    @field_validator('n_jobs')
    def n_jobs_val(cls, v): 
        n_cpus= psutil.cpu_count(logical=True)
        logger.info(f'Total of logical cpus: {n_cpus}')
        
        n= n_cpus-v
        logger.warning(f'Total of logical cpus will be used: {n}')
        
        return n

class modeling_val(BaseModel): 
    scaler_rules: sacler_rules_val
    best_model_rules: best_model_rules
    models_hyperparameters: models_hyperparameters_val
    grid_search_cv: grid_search_cv_val
