from typing import Dict, Any

import polars as pl 
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s-&(levelname)s-%(message)s')
logger= logging.getLogger(__name__)

# HERE # if your outliers analysis detection is another one, please create a new class like OutlierAnalysis
# HERE it could be a good idea to have another config that can optimize the values like the quantile, to make this more dinamic

class OutlierDecisionMaker: 
    @staticmethod
    def scaler_model_option() -> str: 
        pass
    
    @staticmethod 
    def filter_model_option() -> str: 
        pass
    
    @staticmethod
    def impute_model_option() -> str: 
        pass
    
    @staticmethod
    def flag_model_option() -> str: 
        pass
    
    @staticmethod
    def transform_model_option() -> str: 
        pass
    
    
    
    

class AnalysisData: 
    def __init__(self, frame: pl.DataFrame, analysis: Dict[str, Any]):
        self.analysis= analysis
        
        self.cat_frame= frame.select(pl.selectors.string())
        self.num_frame= frame.select(pl.selectors.numeric())
    
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
            q1= self.num_frame[col].quantile(0.25)
            q3= self.num_frame[col].quantile(0.75)
            iqr= q3 - q1 
            
            lower= q1 - 1.5*iqr
            upper= q3 + 1.5*iqr
            
            outliers= self.num_frame.filter((pl.col(col) < lower) | (pl.col(col) > upper))
            n_out= outliers.height 
            pct_outlier= (n_out/ self.num_frame.height) *100
            
            
            
            decisions= {
                'scaler': , 
                'filter': ,
                'method': method
            }
            
            outliers_dict[col] = {
                'iqr': round(iqr, 3), 
                'n_outliers': n_out, 
                'percent_outliers': round(pct_outlier, 3), 
                'decision': decisions
            }
        
        return outliers_dict
    
    def correlation_analysis(self): 
        pass
    
    def category_dominance(self): 
        pass
    
    def analysis_data(self) -> Dict[str, Any]: 
        pass
    
    
    
    
    
    
    



