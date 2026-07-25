from pydantic import BaseModel
from typing import Literal, Union, List

class random_forest_regressor_val(BaseModel): 
    name: Literal['random_forest_regressor']= 'random_forest_regressor'
    n_estimators: Union[int, List[int], None]
    max_depth: Union[int, List[int], None]
    min_samples_split: Union[int, List[int], None]



