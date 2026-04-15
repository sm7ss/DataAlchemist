from ..strategies.strategies_analysis_data import correlation_config, correlation_sampling
from ..io.folder_file_manager import FolderAndFile

from pathlib import Path
from typing import Dict, Any, Union, List, Optional
from pydantic import BaseModel

import polars as pl 
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
        self.config_values= config_vars
        
        self.outlier_decision= OutlierDecisionMaker(config_vars=self.config_values)
        self.correlation_decision= CorrelationDecisionMaker(config_vars=self.config_values)
    
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
    
    def outliers_analysis(self) -> Dict[str, Any]: 
        column= self.analysis['outliers']['columns']
        method= self.analysis['outliers']['method']
        
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
        threshold= self.config_values.correlation_decision_maker.threshold/100
        
        old_frame= self.frame.select(column)
        frame= self.correlation_decision.correlation_decision_maker(frame=old_frame, column=column)
        corr= frame.corr()
        
        correlation= []
        multicollinearity= []
        
        for i in range(len(corr)): 
            for j in range(i+1, len(column)):
                col_1= column[i]
                col_2= column[j]
                corr_value= corr[col_2][i]
                
                correlation.append([col_1, col_2, corr_value])
                if corr_value > threshold: 
                    multicollinearity.append([col_1, col_2, corr_value])
        
        dict_corr= {
            'correlations': correlation,
            'high_correlations': multicollinearity if multicollinearity else None,
            'threshold': threshold, 
            'note': 'values with high correlation were found, it is recommended to either remove, join or filter values from the columns for model training' if multicollinearity else None
        }
        
        return dict_corr
    
    def category_dominance_analysis(self) -> Dict[str, Any]:
        column= self.analysis['category_dominance']['columns']
        top_n= self.analysis['category_dominance']['top_n']
        rare_threshold= self.analysis['category_dominance']['rare_threshold_percent']
        
        frame= self.frame.select(column)
        total_rows= frame.height
        
        dict_cat_dom= {}
        rare_threshold_limit= self.config_values.category_decision_maker.rare_threshold_limit
        
        for col in frame.columns: 
            rare_limit_count= 0
            rare_values= []
            top= []
            
            total_unique_values= frame[col].n_unique()
            unique= frame[col].value_counts()
            top_hight_frecuency= unique.sort(by='count' , descending=True).limit(top_n)
            
            for i in range(len(unique)): 
                value= unique[col][i]
                count= unique['count'][i]
                percent= count/total_rows
                
                if percent < rare_threshold: 
                    rare_values_dict= {
                        'value': value, 
                    'count': count, 
                    'percent': round(percent*100, 3)
                    }
                    rare_values.append(rare_values_dict)
                    rare_limit_count+=1
                    if rare_limit_count == rare_threshold_limit: 
                        break
            
            for i in range(len(top_hight_frecuency)): 
                value= top_hight_frecuency[col][i]
                count= top_hight_frecuency['count'][i]
                percent= count/total_rows
                
                top_dict= {
                    'value': value, 
                    'count': count, 
                    'percent': round(percent*100, 3)
                }
                top.append(top_dict)
            
            dict_cat_dom[col]= {
                'unique_count': total_unique_values, 
                'top_values': top,
                'rare_values':  rare_values if rare_values else None, 
                'rare_threshold': 0.01, 
                'suggestion': 'Group rare categories' if rare_values else None
            }
        return dict_cat_dom
    
    def analysis_data(self) -> Optional[Path]: 
        distribution= self.analysis['distribution']['enable']
        outlier= self.analysis['outliers']['enable']
        correlation= self.analysis['correlation']['enable']
        category= self.analysis['category_dominance']['enable']
        
        analysis_dict= {}
        
        if distribution: 
            dict_distribution= self.distribution_analysis()
            analysis_dict['distribution']= dict_distribution
        if outlier: 
            dict_outlier= self.outliers_analysis()
            analysis_dict['outliers']= dict_outlier
        if correlation:
            dict_correlation= self.correlation_analysis()
            analysis_dict['correlation']= dict_correlation
        if category: 
            dict_category= self.category_dominance_analysis()
            analysis_dict['category_dominance']= dict_category
        
        if not analysis_dict: 
            logger.warning('The JSON file was not created for exploratory analysis since no analysis was enabled')
            return None
        
        path= FolderAndFile().create_json(json_dict=analysis_dict)
        return path


