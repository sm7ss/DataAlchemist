from pydantic import BaseModel
from typing import Literal, Union, List

class linear_regression_val(BaseModel): 
    name: Literal['linear_regression']= 'linear_regression'
    fit_intercept: Union[bool, List[bool], None]

