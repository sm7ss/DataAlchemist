from .eda_general_info import EdaGeneralInfo
from .eda_null_val import EdaNullValues
from .eda_analysis_data import AnalysisData

from pydantic import BaseModel
from typing import Dict, Any

import polars as pl
import json 
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

class EdaPipeline: 
    def __init__(self):
        pass
    
    def eda_general_info(self) -> Dict[str, Any]:
        pass
    
    def eda_null_info(self) -> Dict[str, Any]: 
        pass
    
    def eda_analysis_info(self) -> Dict[str, Any]: 
        pass
    
    def pipeline_eda(self) -> None: 
        pass
    



