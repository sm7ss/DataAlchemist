from pydantic import BaseModel, field_validator, model_validator, Field
from ..strategies.strategies import analysis_outliers, category_dominance_rtp, category_dominance_tn
from typing import Dict, Any, Optional

import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

class eda_val(BaseModel): 
    general_information: Optional[bool]
    null_values: Optional[bool]
    null_values_percent: Optional[float] = Field(gt=0.0, le=90.0)
    basic_analysis_data: Dict[str, Any]
    
    @model_validator(mode='after')
    def bool_analysis_val(self): 
        #This is for general information
        self.general_information= False if not self.general_information else self.general_information
        self.null_values= False if not self.null_values else self.null_values
        
        #This is for analysis basic information
        distribution= self.basic_analysis_data['distribution']['enable']
        outliers= self.basic_analysis_data['outliers']['enable']
        correlation= self.basic_analysis_data['correlation']['enable']
        cat_dominance= self.basic_analysis_data['category_dominance']['enable']
        
        self.basic_analysis_data['distribution']['enable']= False if not distribution else distribution
        self.basic_analysis_data['outliers']['enable']= False if not outliers else outliers
        self.basic_analysis_data['correlation']['enable']= False if not correlation else correlation
        self.basic_analysis_data['category_dominance']['enable']= False if not cat_dominance else cat_dominance
        
        return self
    
    @field_validator('basic_analysis_data')
    def outlier_val(cls, v): 
        outliers= v['outliers']['method']
        if not outliers:
            logger.info(f'The value for the outlier method cant be a None, the new value is {analysis_outliers.IQR.value}')
            v['outliers']['method']= analysis_outliers.IQR.value
            return v
        
        if not isinstance(outliers, str): 
            logger.error('The outlier method should be an string')
            raise ValueError('The outlier method should be an string')
        
        outlier_enums= [v.value for v in analysis_outliers]
        if outliers not in outlier_enums: 
            logger.error(f'The outlier method should be: {outlier_enums}')
            raise ValueError(f'The outlier method should be: {outlier_enums}')
        
        return v
    
    @field_validator('basic_analysis_data')
    def category_dominance_val(cls, v): 
        top_n= v['category_dominance']['top_n']
        rare_threshold_percent= v['category_dominance']['rare_threshold_percent']
        
        if not top_n: 
            logger.info(f'The value of top_n cant be a None, so the new value is: {category_dominance_tn.MIN.value}')
            v['category_dominance']['top_n']= category_dominance_tn.MIN.value
        elif top_n <= category_dominance_tn.MIN.value or top_n >= category_dominance_tn.MAX.value: 
            logger.error(f'Top_n cant be less or equal than {category_dominance_tn.MIN.value} and greater or equal than {category_dominance_tn.MAX.value}')
            raise ValueError(f'Top_n cant be less or equal than {category_dominance_tn.MIN.value} and greater or equal than {category_dominance_tn.MAX.value}')
        
        if not rare_threshold_percent: 
            logger.info(f'The value of the percent threshold cant be a None, so the new value is: {0.01}')
            v['category_dominance']['rare_threshold_percent']= 0.01
        elif rare_threshold_percent <= category_dominance_rtp.MIN.value or rare_threshold_percent >= category_dominance_rtp.MAX.value: 
            logger.error(f'Top_n cant be less or equal than {category_dominance_rtp.MIN.value} and greater or equal than {category_dominance_rtp.MAX.value}')
            raise ValueError(f'Top_n cant be less or equal than {category_dominance_rtp.MIN.value} and greater or equal than {category_dominance_rtp.MAX.value}')
        
        return v

