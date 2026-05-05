import yaml 
import tomli
import logging
from pathlib import Path
from typing import Dict, Any, Callable
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

from .validation import validation
from .validation_analysis_values.validation import validator_analysis_values
from .validation_preprocessing.validation import preprocessing_validation

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
    
    @staticmethod
    def toml_read(config: Path, callable: Callable) -> BaseModel: 
        try: 
            with open(config, 'rb') as c: 
                read= tomli.load(c)
                logger.info(f'The file {config.name} was readed correctly')
            val= callable(**read)
            logger.info(f'The file {config.name} was validated correctly')
            return val
        except tomli.TOMLDecodeError: 
            logger.error(f'The toml file {config.name} is corrupted')
            raise ValueError(f'The toml file {config.name} is corrupted')
        except Exception as e: 
            logger.error(f'There is an error:\n{e}')
            raise ValueError(f'There is an error:\n{e}')
    
    @classmethod
    def read_config(cls) -> Dict[str, Any]: 
        config= Path(__file__).resolve().parent.parent.parent / 'config' / 'config.yml'
        config_var= Path(__file__).resolve().parent.parent.parent / 'config' / 'config_analysis_values.yml'
        config_preprocessing= Path(__file__).resolve().parent.parent.parent / 'config' / 'config_preprocessing.yml'
        
        dict_configs= {}
        
        if config.suffix in ['.yml', '.yaml']: 
            dict_configs['config']= cls.yaml_read(config=config, callable=validation)
        else: 
            dict_configs['config'] = cls.toml_read(config=config, callable=validation)
        
        if config_var.suffix in ['.yml', '.yaml']: 
            dict_configs['config_vars']= cls.yaml_read(config=config_var, callable=validator_analysis_values)
        else: 
            dict_configs['config_vars']= cls.toml_read(config=config_var, callable=validator_analysis_values)
        
        if config_preprocessing.suffix in ['.yml', '.yaml']: 
            dict_configs['preprocessing']= cls.yaml_read(config=config_preprocessing, callable=preprocessing_validation)
        else:
            dict_configs['preprocessing']= cls.toml_read(config=config_preprocessing, callable=preprocessing_validation)
        
        return dict_configs


