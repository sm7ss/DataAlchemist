import yaml 
import logging
import polars as pl

from pathlib import Path
from typing import Dict, Any, Callable, List
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

from .validation_cleaning.cleaning_validation import cleaning_val
from .validation_preprocessing.preprocessing_validation import ml_preprocessing_val
from ..strategies.cleaning_strategies import DataTypes

class ValidateExternData: 
    def __init__(self, frame: pl.DataFrame):
        self.cols= frame.columns
        self.cat_cols= frame.select(pl.selectors.string()).columns
    
    def existing_columns(self, columns: List[str]) -> None: 
        for col in columns: 
            if col not in self.cols: 
                logger.error(f'The column {col} doesnt exist in DataFrame. Available columns:\n{self.cols}')
                raise ValueError(f'The column {col} doesnt exist in DataFrame. Available columns:\n{self.cols}')
    
    def cleaning_validation(self, config: BaseModel, config_cleaning: BaseModel): 
        cleaning_columns_name= config_cleaning.rename_columns
        change_datatypes= config_cleaning.change_datatypes
        drop_columns= config_cleaning.drop_columns
        
        if cleaning_columns_name: 
            self.existing_columns(columns=cleaning_columns_name)
        
        if change_datatypes: 
            try: 
                for key, value in change_datatypes.items(): 
                    if key not in self.cols: 
                        logger.error(f'The column {key} doesnt exist in DataFrame. Available columns:\n{self.cols}')
                        raise ValueError(f'The column {key} doesnt exist in DataFrame. Available columns:\n{self.cols}')
                    if value in [DataTypes.INT32, DataTypes.INT64, DataTypes.FLOAT32] and key in self.cat_cols: 
                        frame= frame.with_columns(pl.col(key).cast(pl.Utf8))
                        logger.info(f'Column "{key}" that is a string type can be a numeric type')
            except: 
                logger.error(f'The "{key}" column cannot be changed from string to numeric')
                raise TypeError(f'The "{key}" column cannot be changed from string to numeric')
        
        if drop_columns: 
            self.existing_columns(columns=drop_columns)
            y= config.data.target
            
            if y in drop_columns: 
                logger.error('The target column cannot be deleted')
                raise ValueError('The target column cannot be deleted')
    
    def preprocessing_validation(self, config_preprocessing: BaseModel): 
        columns_remove_correlation= config_preprocessing.correlation.remove_column
        
        if isinstance(columns_remove_correlation, str): 
            if columns_remove_correlation not in self.cols: 
                logger.error(f'The column {columns_remove_correlation} doesnt exist in DataFrame. Available columns:\n{self.cols}')
                raise ValueError(f'The column {columns_remove_correlation} doesnt exist in DataFrame. Available columns:\n{self.cols}')
        elif isinstance(columns_remove_correlation, list): 
            self.existing_columns(columns=columns_remove_correlation)
        
        sample_data= config_preprocessing.sampling
        columns_representative= config_preprocessing.representative_column
        
        if sample_data == 'representative': 
            if isinstance(columns_representative, str): 
                if columns_representative not in self.cols: 
                    logger.error(f'The column {columns_representative} doesnt exist in DataFrame. Available columns:\n{self.cols}')
                    raise ValueError(f'The column {columns_representative} doesnt exist in DataFrame. Available columns:\n{self.cols}')
            elif isinstance(columns_representative, list): 
                self.existing_columns(columns=columns_representative)
            else: 
                logger.error(f'A representative column/s should be selected to be representative')
                raise ValueError(f'A representative column/s should be selected to be representative')

class ReadConfig: 
    @staticmethod
    def yaml_read(config: Path, callable: Callable) -> BaseModel: 
        try: 
            with open(config, 'r') as c: 
                read= yaml.safe_load(c)
                logger.info(f'The file {config.name} was readed correctly')
            val= callable(**read)
            logger.info(f'The file {config.name} was validated correctly')
            return val
        except yaml.YAMLError: 
            logger.error(f'The yaml file {config.name} is corrupted')
            raise ValueError(f'The yaml file {config.name} is corrupted')
        except Exception as e: 
            logger.error(f'There is an error:\n{e}')
            raise ValueError(f'There is an error:\n{e}')
    
    @classmethod
    def read_config(cls, frame: pl.DataFrame, config: BaseModel, path_config: Path) -> Dict[str, Any]: 
        validate= ValidateExternData(frame=frame)
        
        if path_config.name == 'cleaning.yaml': 
            cleaning_config= cls.yaml_read(config=path_config, callable=cleaning_val)
            validate.cleaning_validation(config_cleaning=cleaning_config, config=config)
            logger.info('Cleaning config was validated correctly')
            return cleaning_config
        else: 
            preprocessing_config= cls.yaml_read(config=path_config, callable=ml_preprocessing_val)
            validate.preprocessing_validation(config_preprocessing=preprocessing_config)
            logger.info('Preprocessing config was validated correctly')
            return preprocessing_config


