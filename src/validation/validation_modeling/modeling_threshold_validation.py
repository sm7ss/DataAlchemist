from pydantic import BaseModel, Field
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

class modeling_val(BaseModel): 
    scaler_rules: sacler_rules_val
    best_model_rules: best_model_rules
