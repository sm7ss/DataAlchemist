from pydantic import BaseModel, Field
from typing import Union

class min_sample(BaseModel): 
    max_files: int= Field(ge=5000, le=10000)

class medium_sample(BaseModel): 
    max_files: int= Field(ge=10000, le=100000)
    percent: float= Field(ge=0.2, le=0.5)

class many_sample(BaseModel): 
    max_files: int= Field(ge=100000, le=1000000)
    percent: float= Field(ge=0.05, le=0.1)

class too_much_sample(BaseModel): 
    percent: float= Field(ge=0.01, le=0.05)

class sample_data_val(BaseModel): 
    min_sample: min_sample
    medium_sample: medium_sample
    many_sample: many_sample
    too_much_sample: too_much_sample

class preprocessing_outlier_rules(BaseModel): 
    filter_percent: Union[int, float]= Field(ge=0.01, le=20)
    impute_percent: Union[int, float]= Field(ge=0.1, le= 50)
    transform_percent: Union[int, float]= Field(ge=0.1, le= 50)
    flag_percent: Union[int, float]= Field(ge=1, le=100)

class preprocessing_validation(BaseModel): 
    sample_data: sample_data_val
    preprocessing_outlier_rules: preprocessing_outlier_rules


