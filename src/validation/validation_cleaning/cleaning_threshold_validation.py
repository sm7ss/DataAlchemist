from pydantic import BaseModel, model_validator
from typing import Optional

from datetime import datetime
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

class output_val(BaseModel): 
    name: Optional[str]
    enable: Optional[bool]
    
    @model_validator(mode='after')
    def name_val(self): 
        if self.enable:
            date= datetime.now().strftime('%d-%m-%Y')
            path= Path(__file__).parent.parent.parent/'data_output'/'cleaned'/date/self.name
            self.name= path / self.name
            logger.info('The path for the output of the cleaned file is in place')
        
        return self

class cleaning_val(BaseModel): 
    output: output_val
