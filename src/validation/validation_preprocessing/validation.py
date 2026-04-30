from pydantic import BaseModel, Field
from typing import Union

class preprocessing_outlier_rules(BaseModel): 
    filter_percent: Union[int, float]= Field(ge=0.01, le=20)
    impute_percent: Union[int, float]= Field(ge=0.1, le= 50)
    transform_percent: Union[int, float]= Field(ge=0.1, le= 50)
    flag_percent: Union[int, float]= Field(ge=1, le=100)




