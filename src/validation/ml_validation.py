from pydantic import BaseModel, Field

class ml_training_val(BaseModel): 
    target: str
    
    train_temp: float= Field(gt=0.0, le=1.0)
    test_val: float= Field(gt=0.0, le=1.0)
    random_state: int 
    
    encoder: None
    scaler: None


