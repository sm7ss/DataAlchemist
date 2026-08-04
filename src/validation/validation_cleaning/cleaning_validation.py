from ...strategies.cleaning_strategies import DataTypes

from typing import Optional, Dict, List
from pydantic import BaseModel

import logging 

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

class cleaning_val(BaseModel):
    rename_columns: Optional[Dict[str, str]]
    change_datatypes: Optional[Dict[str, DataTypes]]
    duplicates: bool
    drop_columns: Optional[List[str]]

