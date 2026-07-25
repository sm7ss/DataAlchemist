from pydantic import BaseModel
from typing import Literal, Union, List

class decision_tree_regressor_val(BaseModel): 
    name: Literal['decision_tree_regressor']= 'decision_tree_regressor'
    max_depth: Union[int, List[int], None]
    min_sample_split: Union[int, List[int], None]
    min_sample_leaf: Union[int, List[int], None]

