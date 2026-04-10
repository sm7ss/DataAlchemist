from typing import Dict, Any, List
from pydantic import BaseModel

import polars as pl 
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s-&(levelname)s-%(message)s')
logger= logging.getLogger(__name__)

# HERE # if your outliers analysis detection is another one, please create a new class like OutlierAnalysis

class OutlierDecisionMaker: 
    def __init__(self, config_vars: BaseModel):
        self.scaler= config_vars.scaler
        self.filter= config_vars.filter
        self.impute= config_vars.impute
        self.flag= config_vars.flag
        self.transform= config_vars.transform
    
    def scaler_model_option(self, percent_outlier: float) -> str: 
        if percent_outlier > self.scaler.robust_scaler_percent: 
            suggest_scaler= 'robustScaler'
        elif percent_outlier < self.scaler.standard_scaler_percent: 
            suggest_scaler= 'standarScaler'
        else: 
            suggest_scaler= 'minMaxScaler'
        
        return suggest_scaler
    
    def filter_model_option(self, percent_outlier: float) -> str: 
        if percent_outlier > self.filter.none: 
            suggest_filter= 'none'
        elif percent_outlier < self.filter.trim: 
            suggest_filter= 'trim'
        else: 
            suggest_filter= 'capping'
        
        return suggest_filter
    
    def impute_model_option(self, percent_outlier: float) -> str: 
        if percent_outlier > self.impute.none: 
            suggest_impute= 'none'
        else: 
            suggest_impute= 'median'
        
        return suggest_impute
    
    def flag_model_option(self, percent_outlier: float) -> bool: 
        if percent_outlier > self.flag.flag_true: 
            suggest_flag= True
        else: 
            suggest_flag= False
        
        return suggest_flag
    
    def transform_model_option(self, skew: str, min_max_div: float) -> str: 
        if skew == 'positive' and min_max_div > self.transform.log1p: 
            suggest_transform= 'log1p'
        elif skew == 'positive': 
            suggest_transform= 'sqrt'
        else: 
            suggest_transform= 'none'
        
        return suggest_transform
    
    def outlier_decision_maker(self, percent_outlier: float, skew:str, min_max_div:float) -> Dict[str, Any]: 
        scaler= self.scaler_model_option(percent_outlier=percent_outlier)
        fitler= self.filter_model_option(percent_outlier=percent_outlier)
        impute= self.impute_model_option(percent_outlier=percent_outlier)
        flag= self.flag_model_option(percent_outlier=percent_outlier)
        
        if min_max_div is None:
            logger.warning("Min value is 0, we can't divide by 0. So there will be no value option for tranfrom option")
            transform= None
        else: 
            transform= self.transform_model_option(skew=skew, min_max_div=min_max_div)
        
        dict_outlier= {
            'scaler': scaler, 
            'filter': fitler, 
            'impute': impute, 
            'flag': flag, 
            'transform': transform
        }
        
        return dict_outlier

class AnalysisData: 
    def __init__(self, frame: pl.DataFrame, analysis: Dict[str, Any], config_vars: BaseModel):
        self.analysis= analysis
        
        self.cat_frame= frame.select(pl.selectors.string())
        self.num_frame= frame.select(pl.selectors.numeric())
        
        self.outlier_decision= OutlierDecisionMaker(config_vars=config_vars)
    
    def distribution_analysis(self) -> Dict[str, Any]: 
        distribution_dict= {}
        
        for col in self.num_frame.columns: 
            statistics= self.num_frame[col].describe()
            
            mean= statistics.filter(pl.col('statistic')=='mean')['value'].item()
            median= statistics.filter(pl.col('statistic')=='50%')['value'].item()
            p25= statistics.filter(pl.col('statistic')=='25%')['value'].item()
            p75= statistics.filter(pl.col('statistic')=='75%')['value'].item()
            min_val= statistics.filter(pl.col('statistic')=='min')['value'].item()
            max_val= statistics.filter(pl.col('statistic')=='max')['value'].item()
            
            iqr= p75-p25
            range_val= max_val-min_val
            
            if mean > median: 
                sesgo= 'positive (tail to the right)'
            elif mean < median: 
                sesgo= 'negative (tail to the left)'
            else: 
                sesgo= 'symmetrical'
            
            if range_val > 0: 
                concentration= iqr/range_val
                if concentration < 0.3: 
                    distribution= 'very concentrated (75% of the data in less than 30% of the range)'
                elif concentration > 0.7: 
                    distribution= 'very dispersed (75% of data covers more than 70% of the range)'
                else: 
                    distribution= 'moderately dispersed'
            else: 
                distribution= 'range value is 0'
            
            distribution_dict[col]= {
                'range': round(range_val, 3),
                'mean': round(mean, 3),
                'median': round(median, 3),
                'iqr': round(iqr, 3),
                'form': sesgo, 
                'distribution': distribution
            }
        
        return distribution_dict
    
    def outliers_analysis(self, method: str) -> Dict[str, Any]: 
        outliers_dict= {}
        
        for col in self.num_frame.columns: 
            describe= self.num_frame[col].describe()
            
            mean= describe.filter(pl.col('statistic')=='mean')['value'].item()
            median= describe.filter(pl.col('statistic')=='50%')['value'].item()
            q1= describe.filter(pl.col('statistic')=='25%')['value'].item()
            q3= describe.filter(pl.col('statistic')=='75%')['value'].item()
            min_val= describe.filter(pl.col('statistic')=='min')['value'].item()
            max_val= describe.filter(pl.col('statistic')=='max')['value'].item()
            
            iqr= q3 - q1 
            
            lower= q1 - 1.5*iqr
            upper= q3 + 1.5*iqr
            
            outliers= self.num_frame.filter((pl.col(col) < lower) | (pl.col(col) > upper))
            n_out= outliers.height 
            pct_outlier= (n_out/ self.num_frame.height) *100
            
            if min_val == 0:
                min_max_div= None
            else: 
                min_max_div= max_val/min_val
            
            if mean < median:
                skew= 'negative'
            elif mean > median: 
                skew= 'positive'
            else: 
                skew= 'balanced'
            
            decisions= self.outlier_decision.outlier_decision_maker(percent_outlier=pct_outlier, skew=skew, min_max_div=min_max_div)
            
            outliers_dict[col] = {
                'iqr': round(iqr, 3), 
                'n_outliers': n_out, 
                'percent_outliers': round(pct_outlier, 3), 
                'method': method, 
                'decision': decisions
            }
        
        return outliers_dict
    
    def correlation_analysis(self) -> Dict[str, Any]: 
        pass
    
    def category_dominance(self): 
        pass
    
    def analysis_data(self) -> Dict[str, Any]: 
        pass
    
    
    
    
    
    
    



