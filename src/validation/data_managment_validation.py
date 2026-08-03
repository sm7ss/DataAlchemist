from pydantic import BaseModel, Field, field_validator
from pathlib import Path
import logging

from ..strategies.strategies import ProtectionData

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

class data_protection_val(BaseModel): 
    enable: bool
    method: ProtectionData
    delete_original_after: bool

class data_manag_val(BaseModel): 
    data_protection: data_protection_val
    overhead_percent: float= Field(ge=1.0, le=3.0)
    sample_data_percent: float= Field(gt=0.0, lt=1.0)

class data_managment_val(BaseModel): 
    path: str
    target: str
    
    data_management: data_manag_val
    
    @field_validator('path')
    def path_val(cls, v): 
        path= Path(__file__).parent.parent.parent / 'config' / 'data' / v
        
        if path.suffix not in ['.csv', '.parquet']: 
            logger.error(f'File {v} should be a .csv or a .parquet')
            raise ValueError(f'File {v} should be a .csv or a .parquet')
        
        return path

