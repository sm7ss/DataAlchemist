from ..strategies.strategies_analysis_data import correlation_config, correlation_sampling

from typing import Dict, Any, Union, List
from pydantic import BaseModel

import polars as pl 
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s-&(levelname)s-%(message)s')
logger= logging.getLogger(__name__)

# This will change to be lazy later
# HERE # if your outliers analysis detection is another one, please create a new class like OutlierAnalysis

class OutlierDecisionMaker: 
    def __init__(self, config_vars: BaseModel):
        self.scaler= config_vars.outlier_decision_maker.scaler
        self.filter= config_vars.outlier_decision_maker.filter
        self.impute= config_vars.outlier_decision_maker.impute
        self.flag= config_vars.outlier_decision_maker.flag
        self.transform= config_vars.outlier_decision_maker.transform
    
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
            suggest_filter= None
        elif percent_outlier < self.filter.trim: 
            suggest_filter= 'trim'
        else: 
            suggest_filter= 'capping'
        
        return suggest_filter
    
    def impute_model_option(self, percent_outlier: float) -> str: 
        if percent_outlier > self.impute.none: 
            suggest_impute= None
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
            suggest_transform= None
        
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

class CorrelationHandleNulls: 
    def __init__(self, frame: pl.DataFrame):
        self.frame= frame
    
    def filter(self, col:List[str]) -> pl.DataFrame: 
        expression= []
        
        for column in col: 
            expression.append(~pl.col(column).is_null())
        
        return self.frame.filter(expression)
    
    def median(self, col:List[str]) -> pl.DataFrame: 
        expression=[]
        
        for column in col: 
            expression.append(pl.col(column).fill_null(pl.median(column)))
        
        return self.frame.with_columns(expression)
    
    def zero(self, col:List[str]) -> pl.DataFrame: 
        expression=[]
        
        for column in col: 
            expression.append(pl.col(column).fill_null(0))
        
        return self.frame.with_columns(expression)
    
    def mean(self, col:List[str]) -> pl.DataFrame: 
        expression=[]
        
        for column in col: 
            expression.append(pl.col(column).fill_null(pl.mean(column)))
        
        return self.frame.with_columns(expression)
    
    def correlation_config_decision(self, handle_nulls: correlation_config, col: List[str]) -> pl.DataFrame: 
        match handle_nulls: 
            case correlation_config.FILTER: 
                frame= self.filter(col=col)
            case correlation_config.MEDIAN: 
                frame= self.median(col=col)
            case correlation_config.ZERO: 
                frame= self.zero(col=col)
            case correlation_config.MEAN: 
                frame= self.mean(col=col)
        
        return frame

class CorrelationSampling: 
    def __init__(self, frame: pl.DataFrame, percent: float):
        self.frame= frame
        self.percent= percent/100
    
    def random_sample(self) -> pl.DataFrame: 
        return self.frame.sample(fraction=self.percent, seed=42)
    
    def representative(self, r_columns: Union[str, List[str]]) -> pl.DataFrame: 
        return self.frame.select(r_columns).sample(fraction=self.percent, seed=42)
    
    def correlation_sampling_decision(self, decision: correlation_sampling, r_columns: Union[str, List[str]]) -> pl.DataFrame: 
        match decision: 
            case correlation_sampling.RANDOM: 
                frame= self.random_sample()
            case correlation_sampling.REPRESENTATIVE: 
                frame= self.representative(r_columns=r_columns)
        
        return frame

class CorrelationDecisionMaker: 
    def __init__(self, config_vars: BaseModel):
        self.sampling= config_vars.correlation_decision_maker.sampling
        self.handle_nulls= config_vars.correlation_decision_maker.handle_nulls
        self.threshold= config_vars.correlation_decision_maker.threshold
    
    def correlation_null_hanlder(self, frame: pl.DataFrame, col: List[str]) -> pl.DataFrame: 
        return CorrelationHandleNulls(frame=frame).correlation_config_decision(
            handle_nulls=self.handle_nulls, 
            col=col
        )
    
    def correlation_sampling(self, frame: pl.DataFrame) -> pl.DataFrame: 
        percent= self.sampling.percent
        decision= self.sampling.method
        r_columns= self.sampling.representative_columns
        return CorrelationSampling(frame=frame, percent=percent).correlation_sampling_decision(
            decision=decision, 
            r_columns=r_columns
        )
    
    def correlation_decision_maker(self, frame: pl.DataFrame, column: Union[str, List[str]]) -> pl.DataFrame: 
        sample_frame= self.correlation_sampling(frame=frame)
        columns_with_nulls= []
        
        for col in column: 
            nulls= sample_frame.filter(pl.col(col).is_null()).height
            if nulls > 0: 
                columns_with_nulls.append(col)
        
        if columns_with_nulls:
            frame= self.correlation_null_hanlder(frame=sample_frame, col=column)
        
        return frame

class AnalysisData: 
    def __init__(self, frame: pl.DataFrame, analysis: Dict[str, Any], config_vars: BaseModel):
        self.frame= frame
        self.analysis= analysis
        
        self.outlier_decision= OutlierDecisionMaker(config_vars=config_vars)
        self.correlation_decision= CorrelationDecisionMaker(config_vars=config_vars)
    
    def distribution_analysis(self) -> Dict[str, Any]: 
        columns= self.analysis['distribution']['columns']
        frame= self.frame.select(columns)
        
        distribution_dict= {}
        
        for col in columns: 
            statistics= frame[col].describe()
            
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
        column= self.analysis['outliers']['columns']
        frame= self.frame.select(column)
        
        outliers_dict= {}
        
        for col in column: 
            describe= frame[col].describe()
            
            mean= describe.filter(pl.col('statistic')=='mean')['value'].item()
            median= describe.filter(pl.col('statistic')=='50%')['value'].item()
            q1= describe.filter(pl.col('statistic')=='25%')['value'].item()
            q3= describe.filter(pl.col('statistic')=='75%')['value'].item()
            min_val= describe.filter(pl.col('statistic')=='min')['value'].item()
            max_val= describe.filter(pl.col('statistic')=='max')['value'].item()
            
            iqr= q3 - q1 
            
            lower= q1 - 1.5*iqr
            upper= q3 + 1.5*iqr
            
            outliers= frame.filter((pl.col(col) < lower) | (pl.col(col) > upper))
            n_out= outliers.height 
            pct_outlier= (n_out/ frame.height) *100
            
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
        column= self.analysis['correlation']['columns']
        frame= self.frame.select(column)
        
        frame= self.correlation_decision.correlation_decision_maker(frame=frame, column=column)
        
        return frame
    
    def category_dominance(self): 
        pass
    
    def analysis_data(self) -> Dict[str, Any]: 
        pass
    
    
    
    
    
    
    



