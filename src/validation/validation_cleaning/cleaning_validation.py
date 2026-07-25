from ...strategies.cleaning_strategies import NumericNulls, CategoricNulls, DataTypes

from typing import Optional, Dict, Union, List
from pydantic import BaseModel, field_validator

import logging 

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

class null_values_val(BaseModel): 
    null_impute_numerics: Union[NumericNulls, int, float, None]
    null_impute_categorics: Union[CategoricNulls, str, None]
    
    @field_validator('null_impute_numerics')
    def null_num_imp_val(cls, v): 
        if not v:
            logger.warning('Because there is no assigned operation for nulls, the "median" will be taken as the operation')
            v= NumericNulls.MEDIAN
        return v
    
    @field_validator('null_impute_categorics')
    def null_cat_imp_val(cls, v): 
        if not v: 
            logger.warning('Because there is no assigned operation for nulls, "fashion" will be taken as an operation')
            v= CategoricNulls.MODE
        return v

class cleaning_val(BaseModel):
    rename_columns: Optional[Dict[str, str]]
    change_datatypes: Optional[Dict[str, DataTypes]]
    duplicates: bool
    drop_columns: Optional[List[str]]
    
    null_values: null_values_val

