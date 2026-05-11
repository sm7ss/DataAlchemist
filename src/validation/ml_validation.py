from pydantic import BaseModel, Field

class ml_training_val(BaseModel): 
    target: str
    
    train_test_search: float= Field(gt=0.0, le=1.0)
    train_test_final: float= Field(gt=0.0, le=1.0)
    random_state: int 
    
    encoder: None
    scaler: None


