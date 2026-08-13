import polars as pl 
import logging
from typing import List, Union, Dict, Any, Tuple
from pydantic import BaseModel

from ...strategies.pre_processing_strategies import CorrSampling
from .operations.null import NullNumHandler, NullCatHandler

from .nulls import Nulls
from .distribution import Distribution
from .outliers import Outlier
from .correlation import Correlation

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

class SamplingData: 
    def __init__(self, config: BaseModel):
        self.config_sample= config.sample_data
    
    def percent_files(self, x: pl.DataFrame) -> int: 
        size= x.height
        
        min_sample= self.config_sample.min_sample.max_files
        
        medium_sample= self.config_sample.medium_sample.max_files
        medium_percent= self.config_sample.medium_sample.percent
        
        many_sample= self.config_sample.many_sample.max_files
        many_percent= self.config_sample.many_sample.percent
        
        too_much_percent= self.config_sample.many_sample.percent
        
        if size < min_sample: 
            new_size= size
        elif size < medium_sample: 
            new_size= int(size* medium_percent)
        elif size < many_sample: 
            new_size= int(size*many_percent)
        else: 
            new_size= int(size*too_much_percent)
        
        return new_size
    
    def random_sample(self, x: pl.DataFrame, y: pl.DataFrame) -> Tuple[pl.DataFrame]: 
        files= self.percent_files(x=x)
        
        x= x.sample(n=files, seed=42)
        y= y.sample(n=files, seed=42)
        
        return x, y
    
    def representative(self, x: pl.DataFrame, y: pl.DataFrame, r_columns: Union[str, List[str]]) -> Tuple[pl.DataFrame]: 
        files= self.percent_files(x=x)
        
        x= x.select(r_columns).sample(n=files, seed=42)
        y= y.select(r_columns).sample(n=files, seed=42)
        
        return x, y
    
    def sampling(self, x: pl.DataFrame, y: pl.DataFrame, decision: CorrSampling, r_columns: Union[str, List[str]]=None) -> Tuple[pl.DataFrame]: 
        match decision: 
            case CorrSampling.RANDOM: 
                x, y= self.random_sample(x=x, y=y)
            case CorrSampling.REPRESENTATIVE: 
                x, y= self.representative(x=x, y=y, r_columns=r_columns)
        
        return x, y

class NullHandler: 
    def __init__(self, frame: pl.DataFrame, config: BaseModel):
        self.config= config
        
        self.frame= frame
        self.num_cols= frame.select(pl.selectors.numeric()).columns
        self.cat_cols= frame.select(pl.selectors.string()).columns
        
        self.nulls= False
    
    def get_expr(self, x_train: pl.DataFrame) -> List[str]: 
        expr= []
        
        num_method= self.config.null_num_handler
        cat_method= self.config.null_cat_handler
        const_value= self.config.null_cat_handler_value
        
        cat= NullCatHandler()
        num= NullNumHandler()
        
        for col in x_train.columns: 
            if col == 'index': 
                continue
            
            num_nulls= x_train.filter(pl.col(col).is_null()).height
            
            if num_nulls > 0:
                if col in self.num_cols: 
                    expression= num.get_null_num_handler_expr(col=col, null_method=num_method)
                    expr.append(expression)
                
                if col in self.cat_cols: 
                    expression= cat.get_null_cat_handler_expr(col=col, null_method=cat_method, constant_value=const_value)
                    expr.append(expression)
        
        return expr
    
    def fit_expression(self, x_train: pl.DataFrame) -> pl.DataFrame: 
        expressions= self.get_expr(x_train=x_train)
        
        if not expressions: 
            return x_train
        
        self.nulls= True
        self.impute_values= {}
        
        for expr in expressions: 
            value= x_train.select(expr).item(0,0)
            col= expr.meta.root_names()[0]
            
            self.impute_values[col]= value
        
        x_train= x_train.with_columns(expressions)
        logger.info('All nulls were imputed')
        
        return x_train
    
    def transform_expression(self, x_test: pl.DataFrame) -> pl.DataFrame: 
        if not self.nulls: 
            return x_test
        
        expressions= []
        
        for col in self.impute_values: 
            value= self.impute_values[col]
            
            expr= pl.col(col).fill_null(value)
            expressions.append(expr)
        
        x_test= x_test.with_columns(expressions)
        logger.info('All nulls were imputed')
        
        return x_test

class Pipeline: 
    def __init__(self, frame: pl.DataFrame, analysis: Dict[str, Any], config: BaseModel, config_threshold_preprocessing: BaseModel):
        self.config= config
        self.config_pre= config_threshold_preprocessing.preprocessing
        
        self.frame= frame
        
        self.analysis= analysis
        self.analysis_data= analysis.get('analysis_data', None)
    
    def x_y_sampling(self, x: pl.DataFrame, y: pl.DataFrame) -> Tuple[pl.DataFrame]: 
        sampling= self.config.sampling
        r_columns= self.config.representative_column
        
        x, y= SamplingData(config=self.config_pre).sampling(x=x, y=y, decision=sampling, r_columns=r_columns)
        
        logger.info('Sampled frame were obtained')
        
        return x, y
    
    def null_general(self, x_train: pl.DataFrame, x_test: pl.DataFrame) -> Tuple[pl.DataFrame]: 
        nulls= Nulls(
            frame=self.frame, 
            JSON=self.analysis, 
            model=self.config, 
            model_threshold=self.config_pre
        )
        
        x_train= nulls.fit_expressions(x_train=x_train)
        x_test= nulls.transform_expressions(x_test=x_test)
        
        return x_train, x_test
    
    def left_nulls(self, x_train: pl.DataFrame, x_test: pl.DataFrame) -> Tuple[pl.DataFrame]: 
        left_nulls= NullHandler(frame=self.frame, config=self.config)
        
        x_train= left_nulls.fit_expression(x_train=x_train)
        x_test= left_nulls.transform_expression(x_test=x_test)
        
        return x_train, x_test
    
    def distribution(self, x_train: pl.DataFrame, x_test: pl.DataFrame) -> Tuple[pl.DataFrame]: 
        distribution= self.analysis_data['distribution']
        
        c_distribution= Distribution(frame=self.frame, distribution_dict=distribution)
        
        x_train= c_distribution.fit_expressions(x_train=x_train)
        x_test= c_distribution.transform_expressions(x_test=x_test)
        
        return x_train, x_test
    
    def outliers(self, x_train: pl.DataFrame, x_test: pl.DataFrame) -> Tuple[pl.DataFrame]: 
        outliers= self.analysis_data['outliers']
        
        c_outlier= Outlier(
            frame=self.frame, 
            config=self.config_pre, 
            outlier_dict=outliers
        )
        
        x_train= c_outlier.fit_expressions(x_train=x_train)
        x_test= c_outlier.transform_expressions(x_test=x_test)
        
        return x_train, x_test
    
    def correlation(self, x_train: pl.DataFrame, x_test: pl.DataFrame) -> Tuple[pl.DataFrame]: 
        correlation= self.analysis_data['correlation']
        
        c_correlation= Correlation(
            frame=self.frame, 
            corr_dict=correlation, 
            config=self.config
        )
        
        x_train= c_correlation.fit_expressions(x_train=x_train)
        x_test= c_correlation.transform_expressions(x_test=x_test)
        
        return x_train, x_test
    
    # CATEGORY IS MISSING HERE
    
    def fit_transform_expression(self,  
            x_train: pl.DataFrame, 
            y_train: pl.DataFrame,
            x_test: pl.DataFrame, 
            y_test: pl.DataFrame
        ) -> Dict[str, Dict[str, pl.DataFrame]]: 
        
        distribution_enable= self.config.distribution.enable
        outlier_enable= self.config.outlier.enable
        correlation_enable= self.config.correlation.enable
        
        x_train, x_test= self.null_general(x_train=x_train, x_test=x_test)
        x_train, x_test= self.left_nulls(x_train=x_train, x_test=x_test)
        
        if distribution_enable: 
            x_train, x_test= self.distribution(x_train=x_train, x_test=x_test)
        
        if outlier_enable: 
            x_train, x_test= self.outliers(x_train=x_train, x_test=x_test)
        
        if correlation_enable: 
            x_train, x_test= self.correlation(x_train=x_train, x_test=x_test)
        
        x_train_sample, y_train_sample= self.x_y_sampling(x=x_train, y=y_train)
        x_test_sample, y_test_sample= self.x_y_sampling(x=x_test, y=y_test)
        
        return {
            'train_sample': {
                    'x_train_sample': x_train_sample,
                    'y_train_sample': y_train_sample, 
                    'x_test_sample': x_test_sample, 
                    'y_test_sample': y_test_sample
                },
            'train_test': {
                    'x_train': x_train, 
                    'x_test': x_test
                }
        }

