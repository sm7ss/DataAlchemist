"""from ...strategies.strategies import AnalysisOutliers

from typing import Optional, List, Union
from pydantic import BaseModel, Field, field_validator

class ml_training_val(BaseModel): 
    target: Union[List[str], str]
    
    train_test_search: float= Field(gt=0.0, le=1.0)
    train_test_final: float= Field(gt=0.0, le=1.0)
    random_state: int 
    
    encoder: None
    scaler: None
    scaler_outlier_method: Optional[AnalysisOutliers]
    
    @field_validator('scaler_outlier_method')
    def scaler_outlier_method_val(cls, v): 
        if not v: 
            return AnalysisOutliers.IQR
        else: 
            return v"""
