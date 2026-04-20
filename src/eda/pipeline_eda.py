from .eda_general_info import EdaGeneralInfo
from .eda_null_val import EdaNullValues
from .eda_analysis_data import AnalysisData
from ..io.folder_file_manager import FolderAndFile
from ..get_frame import get_frame

from pydantic import BaseModel
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List

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
----------------------------------------------------------------------------------------
Available Columns: {self.available_columns()}

Column Type: 
{self.datatype_unique(type=datatype)}
Numeric Statistics: {self.statistics()} 
Unique Categoric Values: 
{self.datatype_unique(type=unique)} 
========================================================================================'''

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
    - {col}: {total_nulls} nulls column ({percent}%), {total_null_row} nulls row -> action: {action}'''
                else: 
                    text+= f'''
    - {col}: {total_nulls} nulls column -> action: {action}'''
        
        return text
    
    def get_text(self) -> str: 
        total_nulls= self.dict['total_nulls']
        
        return f'''
MISSING VALUES ANALYSIS
----------------------------------------------------------------------------------------
Total Nulls in Dataset: {total_nulls}
{self.null_text()}

========================================================================================'''

class InfoAnalysisNumericColumns: 
    def __init__(self, data_analysis: Dict[str, Any]):
        self.dict_distribution= data_analysis['analysis_data']['distribution']
        self.dict_outliers= data_analysis['analysis_data']['outliers']
        self.dict_correlations= data_analysis['analysis_data']['correlation']
    
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
========================================================================================'''
        else: 
            return None
        
        if distribution_enable: 
            dis= self.distribution()
            text+= f'''
DISTRIBUTION 
----------------------------------------------------------------------------------------{dis}
========================================================================================'''
        
        if outliers_enable: 
            out= self.outliers()
            text+= f'''
OUTLIERS
----------------------------------------------------------------------------------------{out}
========================================================================================'''
        
        if correlation_enable: 
            corr= self.correlation()
            text+= f'''
CORRELATION
----------------------------------------------------------------------------------------
{corr}
========================================================================================'''
        
        return text

class InfoAnalysisCategoricColumns: 
    def __init__(self, data_analysis: Dict[str, Any]):
        self.dict_category= data_analysis['analysis_data']['category_dominance']
    
    @staticmethod
    def category_dominance_top_rare_values(list_dicts: List[str]) -> str: 
        text= ''
        
        for i in range(len(list_dicts)): 
            value= list_dicts[i]['value']
            count= list_dicts[i]['count']
            percent= list_dicts[i]['percent']
            text+= f'    - {value} ({percent}%) -> {count} total values\n'
        
        return text
    
    def category_dominance(self) -> str: 
        text= ''
        
        for col in self.dict_category: 
            unique_count= self.dict_category[col]['unique_count']
            
            top_values= self.dict_category[col]['top_values']
            rare_values= self.dict_category[col]['rare_values']
            
            top_categories_text= self.category_dominance_top_rare_values(list_dicts=top_values)
            rare_values_text= self.category_dominance_top_rare_values(list_dicts=rare_values)
            
            text+= f'''
{col}
Total unique values: {unique_count}

    Unique Top Values
{top_categories_text}
    Rare Unique Values
{rare_values_text}
'''
            ml_suggestion= self.dict_category[col]['suggestion']
            
            few_cat= ml_suggestion['few_categories']
            if few_cat: 
                text+= f'    - For few categories: {few_cat}\n'
            
            many_cat= ml_suggestion['many_categories']
            if many_cat: 
                text+= f'    - For many categories: {many_cat}\n'
            
            hight_cardin= ml_suggestion['hight_cardinality']
            if hight_cardin: 
                text+= f'    - For hight cardinality: {hight_cardin}\n'
            
            nrv_cr= ml_suggestion['no_rare_value_categories_reasonable']
            if nrv_cr: 
                text+= f'    - For no rare value categories resonable: {nrv_cr}\n'
            
            many_rare_val= ml_suggestion['many_rare_values']
            if many_rare_val:
                text+= '    Many Rare Values\n'
                many_rare_val_sugg= many_rare_val['suggestion']
                if many_rare_val_sugg: 
                    text+= f'    - Suggestion: {many_rare_val_sugg}\n'
                many_rare_val_encoder= many_rare_val['encoder']
                if many_rare_val_encoder: 
                    text+= f'    - Encoder: {many_rare_val_encoder}\n'
            
            cat_with_nulls= ml_suggestion['categories_with_nulls']
            if cat_with_nulls:
                text+= '    Categories With Nulls\n'
                cat_with_nulls_sugg= cat_with_nulls['suggestion']
                if cat_with_nulls_sugg: 
                    text+= f'    - Suggestion: {cat_with_nulls_sugg}\n'
                cat_with_nulls_encoder= cat_with_nulls['encoder']
                if cat_with_nulls_encoder: 
                    text+= f'    - Encoder: {cat_with_nulls_encoder}\n'
        
        return text
    
    def get_text(self, analysis_data_enable: Dict[str, Any]) -> Optional[str]: 
        text= ''
        
        category_dominance_enable= analysis_data_enable['category_dominance']['enable']
        
        if category_dominance_enable: 
            text+= f'''
CATEGORICAL COLUMNS ANALYSIS
----------------------------------------------------------------------------------------{self.category_dominance()}
========================================================================================'''
        else: 
            return None
        
        return text

class InfoAnalysisEda: 
    def __init__(self, data_analysis: Dict[str, Any], dict_analysis: Dict[str, Any]):
        self.enable= dict_analysis
        
        self.data_analysis= data_analysis
        
        self.general_info= InfoGeneralEdaReport(eda_general_dict=self.data_analysis)
        self.null_info= InfoNullEda(eda_null_analysis=self.data_analysis)
        self.numeric_info= InfoAnalysisNumericColumns(data_analysis=self.data_analysis)
        self.categoric_info= InfoAnalysisCategoricColumns(data_analysis=self.data_analysis)
    
    def report_numeric_columns(self) -> Optional[str]: 
        return self.numeric_info.get_text(analysis_data_enable=self.enable)
    
    def report_categoric_columns(self) -> Optional[str]: 
        return self.categoric_info.get_text(analysis_data_enable=self.enable)
    
    def report(self, dataset_name: str, general: bool=False, null: bool=False, analysis: bool=False) -> Optional[str]: 
        date= datetime.now().strftime('%Y-%m-%d')
        rows= self.data_analysis['general_eda']['total_rows']
        columns= self.data_analysis['general_eda']['total_columns']
        
        text= f'''
========================================================================================
                                    DATA ALCHEMIST  
                                ANALYSIS REPORT (TEXT MODE)
========================================================================================
📅 Date: {date}
📁 Dataset: {dataset_name}
📊 Shape: {rows} rows | {columns} columns
========================================================================================'''
        
        if general: 
            text+= self.general_info.get_text()
        
        if null: 
            text+= self.null_info.get_text()
        
        if analysis:
            report_num= self.report_numeric_columns()
            report_cat= self.report_categoric_columns()
            
            if not(report_num) and not (report_cat): 
                logger.warning(f'The analysis report for numeric columns and categoric columns is not available or there are no columns available for numeric and categoric')
            else:
                if report_num: 
                    text+= report_num
                if report_cat: 
                    text+= report_cat
        
        return text

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
            general_report= True
            dict_eda['general_eda']= general_eda
        
        if enable_null_analysis: 
            null_analysis= self.eda_null_info()
            null_report= True
            dict_eda['null_analysis']= null_analysis
        
        analysis_data= self.eda_analysis_info()
        if analysis_data: 
            analysis_report= True
            dict_eda['analysis_data']= analysis_data
        
        return 
        
        json_path= FolderAndFile().create_json(json_dict=dict_eda)
        txt_path= FolderAndFile().create_txt(report=report)
        
        return {
            'JSON_path': json_path, 
            'TXT_path': txt_path
        }



