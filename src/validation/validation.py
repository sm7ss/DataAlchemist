from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Union, List, Dict, Any
from pathlib import Path

import hydra
from omegaconf import DictConfig, OmegaConf

import polars as pl 
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

from ..strategies.cleaning_strategies import DataTypes

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

def get_frame(path: Path) -> pl.DataFrame: 
    if path.suffix == '.csv': 
        frame= pl.read_csv(path, n_rows=100, null_values=['tbd', 'TBD', 'N/A', 'nan'])
    else: 
        frame= pl.read_parquet(path, n_rows=100)
    
    return frame

class WarningMessages: 
    @staticmethod
    def numeric_columns_available(analysis_data: str) -> None: 
        logger.warning(f'There are no numeric columns available, {analysis_data} will be desactivated')
    
    @staticmethod 
    def all_numeric_columns(analysis_data: str) -> None: 
        logger.warning(f'{analysis_data} analysis will change their columns to be all numeric columns, cause there are no columns available and the analysis is activated')

class ErrorMessages:
    @staticmethod
    def message_available_columns(col: str, columns: List[str]) -> None: 
        logger.error(f'The column {col} doesnt exist on the frame.\nThe available columns are: {columns}')
        raise ValueError(f'The column {col} doesnt exist on the frame.')
    
    @staticmethod
    def message_numeric_columns(col: str, columns: List[str]) -> None: 
        logger.error(f'The column {col} should be a numerical column.\nNumerical columns available: {columns}')
        raise ValueError(f'Th column {col} should be a numerical column.\nNumerical columns available: {columns}')
    
    @staticmethod
    def message_categoric_columns(col: str, columns: List[str]) -> None: 
        logger.error(f'The column {col} is not a categorical column.\nCateorical columns available: {columns}')
        raise ValueError(f'The column {col} is not a categorical column.\nCateorical columns available: {columns}')

class ValidateColumns: 
    def __init__(self):
        self.error= ErrorMessages
    
    def validate_numeric_columns(self) -> None: 
        pass

    def validate_categoric_columns(self) -> None: 
        pass

    def validate_columns(self, columns: Union[Dict[str, Any], List[str]], real_columns: List[str]) -> None: 
        for col in columns: 
            if col not in real_columns: 
                self.error.message_available_columns(col=col, columns=real_columns)

class path_val(BaseModel): 
    data: str
    overhead_percent: float= Field(ge=1.0, le=3.0)
    sample_data_percent: float= Field(gt=0.0, lt=1.0)
    
    @field_validator('data')
    def path_val(cls, v): 
        path= Path(__file__).parent.parent / 'config' / 'data' / v
        
        if path.suffix not in ['.csv', '.parquet']: 
            logger.error(f'File {v} should be a .csv or a .parquet')
            raise ValueError(f'File {v} should be a .csv or a .parquet')
        
        return v

class validation(BaseModel): 
    eda_threshold: eda_threshold_val
    cleaning: config_cleaning
    preprocessing: preprocessing_val
#    modeling: modeling_val
    
    data: path_val 
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
    ] = Field(discriminator='name')
    
    data_management: data_managment_val
    eda: eda_val
    
    @model_validator(mode='after')
    def columns_analysis_val(self): 
        path= self.path.data
        analysis= self.eda.basic_analysis_data
        
        frame= get_frame(path=path)
        
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
            
            warning_messages= WarningMessages
            error_messages= ErrorMessages
            
            if not columns and not enable: 
                if analysis_data == 'distribution': 
                    if len(num_columns) < 1: 
                        logger.warning(f'There are no columns available, {analysis_data} will be desactivated')
                        self.eda.basic_analysis_data[analysis_data]['enable']= False
                    else: 
                        logger.warning(f'{analysis_data} analysis will change their columns to be all columns, cause there are no columns available and the analysis is activated')
                        self.eda.basic_analysis_data[analysis_data]['columns']= num_columns
                elif analysis_data == 'outliers': 
                    if len(num_columns) < 1: 
                        warning_messages.numeric_columns_available(analysis_data=analysis_data)
                        self.eda.basic_analysis_data[analysis_data]['enable']= False
                    else: 
                        warning_messages.all_numeric_columns(analysis_data=analysis_data)
                        self.eda.basic_analysis_data[analysis_data]['columns']= num_columns
                elif analysis_data == 'correlation': 
                    if len(num_columns) < 1: 
                        warning_messages.numeric_columns_available(analysis_data=analysis_data)
                        self.eda.basic_analysis_data[analysis_data]['enable']= False
                    else: 
                        if len(num_columns) < 2: 
                            logger.warning(f'{analysis_data} analysis cannot have less than 2 numeric columns. This analysis will be desactivated')
                            self.eda.basic_analysis_data[analysis_data]['enable']= False
                        else: 
                            warning_messages.all_numeric_columns(analysis_data=analysis_data)
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
                            error_messages.message_numeric_columns(col=col, columns=num_columns)
                    elif analysis_data == 'outliers': 
                        if col not in num_columns: 
                            error_messages.message_numeric_columns(col=col, columns=num_columns)
                    elif analysis_data == 'correlation':
                        if len(num_columns) < 2: 
                            logger.warning(f'{analysis_data} analysis cannot have less than 2 numeric columns. This analysis will be desactivated')
                            self.eda.basic_analysis_data[analysis_data]['enable']= False 
                        if col not in num_columns: 
                            error_messages.message_numeric_columns(col=col, columns=num_columns)
                    elif analysis_data == 'category_dominance': 
                        if col not in cat_columns: 
                            error_messages.message_categoric_columns(col=col, columns=cat_columns)
                    else: 
                        continue
            elif isinstance(columns, str) and enable: 
                if analysis_data == 'distribution': 
                    if columns not in num_columns: 
                        error_messages.message_numeric_columns(col=columns, columns=num_columns)
                elif analysis_data == 'outliers': 
                    if columns not in num_columns: 
                        error_messages.message_numeric_columns(col=columns, columns=num_columns)
                elif analysis_data == 'correlation': 
                    if len(num_columns) < 2: 
                        logger.warning(f'{analysis_data} analysis cannot have less than 2 numeric columns. This analysis will be desactivated')
                        self.eda.basic_analysis_data[analysis_data]['enable']= False
                    if columns not in num_columns: 
                        error_messages.message_numeric_columns(col=columns, columns=num_columns)
                elif analysis_data == 'category_dominance': 
                    if columns not in cat_columns: 
                        error_messages.message_categoric_columns(col=columns, columns=cat_columns)
                else: 
                    continue
            else: 
                logger.error('The columns should be on a list or should be a string')
                raise ValueError('The columns should be on a list or should be a string')
        
        return self
    
    @model_validator(mode='after')
    def columns_cleaning_val(self): 
        path= self.data
        cleaning_columns_name= self.cleaning.rename_columns
        change_datatypes= self.cleaning.change_datatypes
        drop_columns= self.cleaning.drop_columns
        
        frame= get_frame(path=path)
        frame_cols= frame.columns
        
        message_errors= ValidateColumns()
        
        # COLUMN NAMES
        if cleaning_columns_name:
            message_errors.validate_columns(columns=cleaning_columns_name, real_columns=frame_cols)
        
        categoric_columns= frame.select(pl.selectors.string()).columns
        # CHANGE DATATYPES  
        if change_datatypes:
            try: 
                for key, value in change_datatypes.items(): 
                    if key not in frame_cols: 
                        message_errors.error.message_available_columns(col=key, columns=frame_cols)
                    if value in [DataTypes.INT32, DataTypes.INT64, DataTypes.FLOAT32] and key in categoric_columns: 
                        frame= frame.with_columns(pl.col(key).cast(pl.Utf8))
                        logger.info(f'Column "{key}" that is a string type can be a numeric type')
            except: 
                logger.error(f'The "{key}" column cannot be changed from string to numeric')
                raise TypeError(f'The "{key}" column cannot be changed from string to numeric')
        
        # DROP COLUMNS
        if drop_columns: 
            message_errors.validate_columns(columns=drop_columns, real_columns=frame_cols)
        
        return self
    
    @model_validator(mode='after')
    def column_preprocessing_val(self): 
        path= self.data
        
        frame= get_frame(path=path)
        frame_columns= frame.columns
        
        message_error= ValidateColumns()
        
        # COLUMNS ML VALIDATION
        columns_ml= self.preprocessing.columns
        if not columns_ml: 
            self.preprocessing.columns= frame_columns
            logger.warning('As the columns for ML pre-processing wasnt selected then all columns will be selected')
        if columns_ml: 
            if isinstance(columns_ml, str): 
                if columns_ml not in frame_columns: 
                    message_error.error.message_available_columns(col=columns_ml, columns=frame_columns)
            elif isinstance(columns_ml, list): 
                message_error.validate_columns(columns=columns_ml, real_columns=frame_columns)
        
        # COLUMNS REMOVE VALIDATION 
        columns_correlation= self.preprocessing.correlation.remove_column
        if isinstance(columns_correlation, str): 
            if columns_correlation not in columns_ml: 
                message_error.error.message_available_columns(col=columns_correlation, columns=columns_ml)
        elif isinstance(columns_correlation, list): 
            message_error.validate_columns(columns_correlation, real_columns=columns_ml)
        
        # REPRESENTATIVE COLUMNS 
        sample_data= self.preprocessing.sampling
        if sample_data == 'representative': 
            columns_representative= self.preprocessing.representative_column
            if isinstance(columns_representative, str): 
                message_error.error.message_available_columns(col=columns_representative, columns=columns_ml)
            elif isinstance(columns_representative, list): 
                message_error.validate_columns(columns=columns_representative, real_columns=columns_ml)
            else: 
                logger.error(f'Column/s should be selected to be representative')
        
        return self
    
    """
    ⚠️ NOT AVAILABLE FOR MODELING ⚠️
    
    @model_validator(mode='after')
    def column_ml_training(self): 
        path= self.path.data
        columns_pre= self.ml_preprocessing.columns
        
        if path.suffix == '.csv': 
            frame_columns= pl.read_csv(path, n_rows=1000, null_values=['tbd', 'TBD', 'N/A', 'nan']).columns
        else: 
            frame_columns= pl.read_parquet(path, n_rows=1000).columns
        
        target= self.ml_training.target
        
        if isinstance(target, str):
            if target not in frame_columns: 
                logger.error(f'The target column "{target}" must be in the Frame. Available columns:\n{frame_columns}')
                raise ValueError(f'The target column "{target}" must be in the Frame. Available columns:\n{frame_columns}')
            if target not in columns_pre: 
                logger.info(f'Target column "{target}" must exists in available columns {columns_pre}')
                raise ValueError(f'Target column "{target}" must exists in available columns {columns_pre}')
        else: 
            for col in target: 
                if col not in frame_columns: 
                    logger.error(f'The target column "{col}" must be in the Frame. Available columns:\n{frame_columns}')
                    raise ValueError(f'The target column "{col}" must be in the Frame. Available columns:\n{frame_columns}')
                if col not in columns_pre: 
                    logger.info(f'Target column "{col}" must exists in available columns {columns_pre}')
                    raise ValueError(f'Target column "{col}" must exists in available columns {columns_pre}')
        
        return self"""



