from pydantic import BaseModel, model_validator
from typing import Union, List

import polars as pl 
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

from .data_managment_validation import data_managment_val

from .validation_cleaning.cleaning_threshold_validation import config_cleaning
#from .validation_modeling.modeling_threshold_validation import modeling_val
from .validation_preprocessing.preprocessing_threshold_validation import preprocessing_val

from .validation_model.cv_grid_search import grid_search_cv_val
from .validation_model.decision_tree_regressor import decision_tree_regressor_val
from .validation_model.linear_regression import linear_regression_val
from .validation_model.random_forest_regressor_validation import random_forest_regressor_val

from .validation_eda.eda_threshold_validation import eda_threshold_val
from .validation_eda.eda_validation import eda_val

class validation(BaseModel): 
    eda_threshold: eda_threshold_val
    cleaning: config_cleaning
    preprocessing: preprocessing_val
#    modeling: modeling_val
    
    data: data_managment_val 
    model: Union[
        grid_search_cv_val,
        decision_tree_regressor_val, 
        linear_regression_val, 
        random_forest_regressor_val,
        List[Union[
            grid_search_cv_val, 
            decision_tree_regressor_val, 
            linear_regression_val, 
            random_forest_regressor_val
            ]
        ]
    ]
    
    eda: eda_val
    
    @model_validator(mode='after')
    def columns_analysis_val(self): 
        path= self.data.path
        analysis= self.eda.basic_analysis_data
        
        if path.suffix == '.csv': 
            frame= pl.read_csv(path, n_rows=100, null_values=['tbd', 'TBD', 'N/A', 'nan'])
        else: 
            frame= pl.read_parquet(path, n_rows=100)
        
        num_columns= frame.select(pl.selectors.numeric()).columns
        cat_columns= frame.select(pl.selectors.string()).columns
        
        for analysis_data in analysis: 
            if not num_columns: 
                if analysis_data == 'distribution': 
                    self.eda.basic_analysis_data[analysis_data]['enable']= False
                if analysis_data == 'outliers': 
                    self.eda.basic_analysis_data[analysis_data]['enable']= False
                if analysis_data == 'correlation': 
                    self.eda.basic_analysis_data[analysis_data]['enable']= False
            
            if not cat_columns: 
                if analysis_data == 'category_dominance': 
                    self.eda.basic_analysis_data[analysis_data]['enable']= False
            
            columns= analysis[analysis_data]['columns']
            enable= analysis[analysis_data]['enable']
            
            if not columns and enable: 
                if analysis_data == 'distribution': 
                    if len(num_columns) < 1: 
                        logger.warning(f'There are no columns available, {analysis_data} will be desactivated')
                        self.eda.basic_analysis_data[analysis_data]['enable']= False
                    else: 
                        logger.warning(f'{analysis_data} analysis will change their columns to be all columns, cause there are no columns available and the analysis is activated')
                        self.eda.basic_analysis_data[analysis_data]['columns']= num_columns
                elif analysis_data == 'outliers': 
                    if len(num_columns) < 1: 
                        logger.warning(f'There are no numeric columns available, {analysis_data} will be desactivated')
                        self.eda.basic_analysis_data[analysis_data]['enable']= False
                    else: 
                        logger.warning(f'{analysis_data} analysis will change their columns to be all numeric columns, cause there are no columns available and the analysis is activated')
                        self.eda.basic_analysis_data[analysis_data]['columns']= num_columns
                elif analysis_data == 'correlation': 
                    if len(num_columns) < 1: 
                        logger.warning(f'There are no numeric columns available, {analysis_data} will be desactivated')
                        self.eda.basic_analysis_data[analysis_data]['enable']= False
                    else: 
                        if len(num_columns) < 2: 
                            logger.warning(f'{analysis_data} analysis cannot have less than 2 numeric columns. This analysis will be desactivated')
                            self.eda.basic_analysis_data[analysis_data]['enable']= False
                        else: 
                            logger.warning(f'{analysis_data} analysis will change their columns to be all numeric columns, cause there are no columns available and the analysis is activated')
                            self.eda.basic_analysis_data[analysis_data]['columns']= num_columns
                elif analysis_data == 'category_dominance': 
                    if len(cat_columns) < 1: 
                        logger.warning(f'There are no categoric columns available, {analysis_data} will be desactivated')
                        self.eda.basic_analysis_data[analysis_data]['enable']= False
                    else: 
                        logger.warning(f'{analysis_data} analysis will change their columns to be all categorical columns, cause there are no columns available and the analysis is activated')
                        self.eda.basic_analysis_data[analysis_data]['columns']= cat_columns 
                else: 
                    continue
            elif isinstance(columns, list) and enable: 
                for col in columns: 
                    if analysis_data == 'distribution': 
                        if col not in num_columns: 
                            logger.error(f'The column {col} should be a numerical column.\nNumerical columns available: {columns}')
                            raise ValueError(f'Th column {col} should be a numerical column.\nNumerical columns available: {columns}')
                    elif analysis_data == 'outliers': 
                        if col not in num_columns: 
                            logger.error(f'The column {col} should be a numerical column.\nNumerical columns available: {columns}')
                            raise ValueError(f'Th column {col} should be a numerical column.\nNumerical columns available: {columns}')
                    elif analysis_data == 'correlation':
                        if len(num_columns) < 2: 
                            logger.warning(f'{analysis_data} analysis cannot have less than 2 numeric columns. This analysis will be desactivated')
                            self.eda.basic_analysis_data[analysis_data]['enable']= False 
                        if col not in num_columns: 
                            logger.error(f'The column {col} should be a numerical column.\nNumerical columns available: {columns}')
                            raise ValueError(f'Th column {col} should be a numerical column.\nNumerical columns available: {columns}')
                    elif analysis_data == 'category_dominance': 
                        if col not in cat_columns: 
                            logger.error(f'The column {col} is not a categorical column.\nCateorical columns available: {columns}')
                            raise ValueError(f'The column {col} is not a categorical column.\nCateorical columns available: {columns}')
                    else: 
                        continue
            elif isinstance(columns, str) and enable: 
                if analysis_data == 'distribution': 
                    if columns not in num_columns: 
                        logger.error(f'The column {col} should be a numerical column.\nNumerical columns available: {columns}')
                        raise ValueError(f'Th column {col} should be a numerical column.\nNumerical columns available: {columns}')
                elif analysis_data == 'outliers': 
                    if columns not in num_columns: 
                        logger.error(f'The column {col} should be a numerical column.\nNumerical columns available: {columns}')
                        raise ValueError(f'Th column {col} should be a numerical column.\nNumerical columns available: {columns}')
                elif analysis_data == 'correlation': 
                    if len(num_columns) < 2: 
                        logger.warning(f'{analysis_data} analysis cannot have less than 2 numeric columns. This analysis will be desactivated')
                        self.eda.basic_analysis_data[analysis_data]['enable']= False
                    if columns not in num_columns: 
                        logger.error(f'The column {col} should be a numerical column.\nNumerical columns available: {columns}')
                        raise ValueError(f'Th column {col} should be a numerical column.\nNumerical columns available: {columns}')
                elif analysis_data == 'category_dominance': 
                    if columns not in cat_columns: 
                        logger.error(f'The column {col} is not a categorical column.\nCateorical columns available: {columns}')
                        raise ValueError(f'The column {col} is not a categorical column.\nCateorical columns available: {columns}')
                else: 
                    continue
            else: 
                logger.error('The columns should be on a list or should be a string')
                raise ValueError('The columns should be on a list or should be a string')
        
        return self



