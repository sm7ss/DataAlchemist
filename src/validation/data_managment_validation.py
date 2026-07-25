from pydantic import BaseModel, Field, model_validator
from pathlib import Path
import logging

from ..strategies.strategies import ProtectionData

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

class clean_data_val(BaseModel): 
    enable: bool
    name: str
    
    @model_validator(mode='after')
    def name_val(self): 
        if self.enable:
            path= Path(__file__).parent.parent.parent / 'config' / 'data'
            self.name= path / self.name
            logger.info('The path for the output of the cleaning file is in place')
        
        return self

class preprocessing_data_val(BaseModel): 
    enable: bool
    name: str
    
    @model_validator(mode='after')
    def name_val(self): 
        if self.enable:
            path= Path(__file__).parent.parent.parent / 'config' / 'data'
            self.name= path / self.name
            logger.info('The path for the output of the preprocessing file is in place')
        
        return self

class output_val(BaseModel): 
    clean_data: clean_data_val
    data_protection: preprocessing_data_val

class data_protection_val(BaseModel): 
    enable: bool
    method: ProtectionData
    delete_original_after: bool

class data_managment_val(BaseModel): 
    output: output_val
    data_protection: data_protection_val
    
    overhead_percent: float= Field(ge=1.0, le=3.0)
    sample_data_percent: float= Field(gt=0.0, lt=1.0)

