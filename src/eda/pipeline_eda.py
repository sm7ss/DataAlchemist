from .eda_general_info import EdaGeneralInfo
from .eda_null_val import EdaNullValues
from .eda_analysis_data import AnalysisData
from ..io.folder_file_manager import FolderAndFile
from ..get_frame import get_frame

from pydantic import BaseModel
from pathlib import Path
from typing import Dict, Any, Optional

import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

class InfoGeneralEdaReport: 
    def __init__(self, eda_general_dict: Dict[str, Any]):
        self.dict= eda_general_dict['general_eda']
    
    def available_columns(self) -> str: 
        available_columns= self.dict['available_columns']
        return ', '.join(map(str, available_columns))
    
    def datatype_unique(self, type: Dict[str, Any]) -> str: 
        text= ''
        
        for key, val in type.items(): 
            text+= f'    - {key}: {val}\n'
        
        return text
    
    def statistics(self) -> str: 
        statistics= self.dict['statistics']
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
        datatype= self.dict['datatype']
        unique= self.dict['unique_values']
        return f'''
GENERAL INFO
-----------------------------------------------------------------------
Available Columns: {self.available_columns()}

Column Type: 
{self.datatype_unique(type=datatype)}
Numeric Statistics: {self.statistics()} 
Unique Categoric Values: 
{self.datatype_unique(type=unique)} 

======================================================================='''

class InfoNullEda: 
    def __init__(self, eda_null_analysis: Dict[str, Any]):
        self.dict= eda_null_analysis['null_analysis']
    
    def null_text(self) -> str: 
        text= ''
        null_dict= self.dict
        
        for col in null_dict: 
            if col != 'total_nulls': 
                total_nulls= null_dict[col]['total_nulls_column']
                total_null_row= null_dict[col]['total_nulls_row']
                action= null_dict[col]['action']
                percent= null_dict[col].get('nulls_percent', None)
                if percent: 
                    text+= f'''
{col}: {total_nulls} nulls column ({percent}%), {total_null_row} nulls row -> action: {action}'''
                else: 
                    text+= f'''
{col}: {total_nulls} nulls column -> action: {action}'''
        
        return text
    
    def get_text(self) -> str: 
        total_nulls= self.dict['total_nulls']
        
        return f'''
MISSING VALUES ANALYSIS
-----------------------------------------------------------------------
Total Nulls in Dataset: {total_nulls}
{self.null_text()}

======================================================================='''

class InfoAnalysisNumericColumns: 
    def __init__(self, data_analysis: Dict[str, Any]):
        self.dict_distribution= data_analysis['distribution']
        self.dict_outliers= data_analysis['outliers']
        self.dict_correlations= data_analysis['correlation']
    
    def distribution(self) -> str: 
        text=''
        
        for col in self.dict_distribution: 
            mean= self.dict_distribution[col]['mean']
            median= self.dict_distribution[col]['median']
            skew= self.dict_distribution[col]['form']
            distribution_data= self.dict_distribution[col]['distribution']
            ml_transformer= self.dict_distribution[col]['suggestion']['transformer']
            ml_scaler= self.dict_distribution[col]['suggestion']['scaler']
            
            if skew== 'positive': 
                tail= 'Tail to the left. Higher values'
            elif skew == 'negative': 
                tail= 'Tail to the left. Smaller values'
            else: 
                tail= 'Symmetric values'
            
            text+=f'''
{col}
    - Mean: {mean} | Median: {median} -> skew: {skew} ({tail})
    - Distribution: {distribution_data}
    ML Suggestions: 
        - Transformer: {ml_transformer if ml_transformer else 'Many zeros. Consider a specific model for excess zeros'}
        - Scaler: {ml_scaler}\n'''
        return text
    
    def outliers(self) -> str: 
        text= ''
        
        for col in self.dict_outliers: 
            concentration= self.dict_outliers[col]['iqr']
            n_out= self.dict_outliers[col]['n_outliers']
            percent_out= self.dict_outliers[col]['percent_outliers']
            
            text+= f'''
{col}
    - IQR (distance between 25 and 75: {concentration}
    - Total of Outliers: {n_out}
    - Percent: {percent_out}
    ML Suggestions: 
'''
            scaler_sugg= self.dict_outliers[col]['suggestion']['scaler']
            if scaler_sugg: 
                text+= f'       - Scaler: {scaler_sugg}\n'
            
            filter_sugg= self.dict_outliers[col]['suggestion']['filter']
            if filter_sugg: 
                text+= f'       - Filter: {filter_sugg}\n'
            
            impute_sugg= self.dict_outliers[col]['suggestion']['impute']
            if impute_sugg: 
                text+= f'       - Impute: {impute_sugg}\n'
            
            flag_sugg= self.dict_outliers[col]['suggestion']['flag']
            if flag_sugg: 
                text+= f'       - Flag: {flag_sugg}\n'
            
            transfrom_sugg= self.dict_outliers[col]['suggestion']['transform']
            if transfrom_sugg: 
                text+= f'       - Transform: {transfrom_sugg}\n'
        
        return text
    
    def correlation(self) -> str: 
        text= ''
        
        high_correlation= self.dict_correlations['high_correlations']
        if not high_correlation: 
            return 'No high correlation was detected'
        
        threshold= self.dict_correlations['threshold']
        note= self.dict_correlations['note']
        
        text+= f'High correlation detected (threshold= {threshold})\n'
        
        for i in high_correlation: 
            col_1= i[0] 
            col_2= i[1]
            corr= round(i[2], 3)
            
            text+= f'   - {col_1} <--> {col_2}: {corr}\n'
        
        text+= f'\nNote: {note}\n'
        
        return text
    
    def get_text(self, analysis_data_enable: Dict[str, Any]) -> Optional[str]: 
        text= ''
        
        distribution_enable= analysis_data_enable['distribution']['enable']
        outliers_enable= analysis_data_enable['outliers']['enable']
        correlation_enable= analysis_data_enable['correlation']['enable']
        
        if distribution_enable or outliers_enable or correlation_enable: 
            text+='''
NUMERIC COLUMNS ANALYSIS
======================================================================='''
        else: 
            return None
        
        if distribution_enable: 
            dis= self.distribution()
            text+= f'''
DISTRIBUTION 
-----------------------------------------------------------------------{dis}
======================================================================='''
        
        if outliers_enable: 
            out= self.outliers()
            text+= f'''
OUTLIERS
-----------------------------------------------------------------------{out}
======================================================================='''
        
        if correlation_enable: 
            corr= self.correlation()
            text+= f'''
CORRELATION
-----------------------------------------------------------------------
{corr}
======================================================================='''
        
        return text

class InfoAnalysisCategoricColumns: 
    def __init__(self, data_analysis: Dict[str, Any]):
        self.dict_category= data_analysis['category_dominance']

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
            #PASAR LA CONFIG PARA HABILITAR LOS ANALYSIS
            analysis_report= ''
            dict_eda['analysis_data']= analysis_data
        
        json_path= FolderAndFile().create_json(json_dict=dict_eda)
        txt_path= FolderAndFile().create_txt(report=report)
        
        return {
            'JSON_path': json_path, 
            'TXT_path': txt_path
        }



