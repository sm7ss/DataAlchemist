from .eda_general_info import EdaGeneralInfo
from .eda_null_val import EdaNullValues
from .eda_analysis_data import AnalysisData
from ..io.folder_file_manager import FolderAndFile
from ..get_frame import get_frame

from pydantic import BaseModel
from pathlib import Path
from typing import Dict, Any

import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

class EdaPipeline: 
    def __init__(self, config: BaseModel, config_var: BaseModel):
        frame= get_frame(file=config.path.data, overhead=config.path.overhead_percent)
        
        self.config_eda= config.eda
        
        self.eda_general= EdaGeneralInfo(frame=frame)
        self.eda_null= EdaNullValues(frame=frame, config_eda=self.config_eda)
        self.eda_analysis= AnalysisData(
            frame= frame, 
            analysis= self.config_eda.basic_analysis_data, 
            config_vars= config_var
        )
    
    def eda_general_info(self) -> Dict[str, Any]:
        return self.eda_general.eda_general_info_format()
    
    def eda_null_info(self) -> Dict[str, Any]: 
        return self.eda_null.total_nulls_values()
    
    def eda_analysis_info(self) -> Dict[str, Any]: 
        return self.eda_analysis.analysis_data()
    
    def pipeline_eda_json_file(self) -> Path: 
        enable_general_eda= self.config_eda.general_information
        enable_null_analysis= self.config_eda.null_values
        
        dict_eda={}
        
        if enable_general_eda: 
            general_eda= self.eda_general_info()
            dict_eda['general_eda']= general_eda
        
        if enable_null_analysis: 
            null_analysis= self.eda_null_info()
            dict_eda['null_analysis']= null_analysis
        
        analysis_data= self.eda_analysis_info()
        dict_eda['analysis_data']= analysis_data
        
        path= FolderAndFile().create_json(json_dict=dict_eda)
        
        return path



