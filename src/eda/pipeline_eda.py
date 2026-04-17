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

class InfoGeneralEdaReport: 
    def __init__(self, eda_general_dict: Dict[str, Any]):
        self.dict= eda_general_dict
    
    def available_columns(self) -> str: 
        available_columns= self.dict['general_eda']['available_columns']
        return ', '.join(map(str, available_columns))
    
    def datatype_unique(self, type: Dict[str, Any]) -> str: 
        text= ''
        
        for key, val in type.items(): 
            text+= f'    - {key}: {val}\n'
        
        return text
    
    def statistics(self) -> str: 
        statistics= self.dict['general_eda']['statistics']
        text= ''
        
        for col in statistics: 
            values= statistics[col]
            mean= values['mean']
            median= values['50']
            std= values['std']
            min= values['min']
            max= values['max']
            text+= f'''    
        {col} 
            - Mean: {mean} 
            - Median: {median}
            - Std: {std}
            - Min:  {min}
            - Max: {max}
        '''
        
        return text
    
    def get_text(self) -> str: 
        datatype= self.dict['general_eda']['datatype']
        unique= self.dict['general_eda']['unique_values']
        return f'''
GENERAL INFO
-----------------------------------------------------------------------
Available Columns: {self.available_columns()}

Column Type: 
{self.datatype_unique(type=datatype)}
Numeric Statistics: {self.statistics()} 
Unique Categoric Values: 
{self.datatype_unique(type=unique)} 
'''

class InfoNullEda: 
    pass

class InfoAnalysisEda: 
    pass

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
    
    def pipeline_eda(self) -> Dict[str, Path]: 
        enable_general_eda= self.config_eda.general_information
        enable_null_analysis= self.config_eda.null_values
        report= ''
        
        dict_eda={}
        
        if enable_general_eda: 
            general_eda= self.eda_general_info()
            general_report= ''
            dict_eda['general_eda']= general_eda
        
        if enable_null_analysis: 
            null_analysis= self.eda_null_info()
            null_report= ''
            dict_eda['null_analysis']= null_analysis
        
        analysis_data= self.eda_analysis_info()
        if analysis_data: 
            analysis_report= ''
        dict_eda['analysis_data']= analysis_data
        
        json_path= FolderAndFile().create_json(json_dict=dict_eda)
        txt_path= FolderAndFile().create_txt(report=report)
        
        return {
            'JSON_path': json_path, 
            'TXT_path': txt_path
        }



