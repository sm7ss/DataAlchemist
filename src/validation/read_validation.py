import yaml 
import tomli
import logging
from pathlib import Path
from typing import Dict, Any, Callable

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

from .validation import validation
from .validation_analysis_values.validation import validator_analysis_values

class ReadConfigOptions: 
    @staticmethod
    def yaml_read(config: Path, callable: Callable) -> Dict[str, Any]: 
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
    def toml_config(config: Path, callable: Callable) -> Dict[str, Any]: 
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

class ReadConfig: 
    def __init__(self):
        self.config= Path(__file__).resolve().parent.parent.parent / 'config' / 'config.yml'
        self.config_vars= Path(__file__).resolve().parent.parent.parent / 'config' / 'config_analysis_values.yml'
        
        self.config_val= ReadConfigOptions()
    
    def read_config(self) -> Dict[str, Any]: 
        suff_config= self.config.suffix
        suff_config_var= self.config_vars.suffix
        
        dict_configs= {}
        
        if suff_config in ['.yml', '.yaml']: 
            dict_configs['config']= self.config_val.yaml_read(config=self.config, callable=validation)
        else: 
            dict_configs['config'] = self.config_val.toml_config(config=self.config, callable=validation)
        
        if suff_config_var in ['.yml', '.yaml']: 
            dict_configs['config_vars']= self.config_val.yaml_read(config=self.config_vars, callable=validator_analysis_values)
        else: 
            dict_configs['config_vars']= self.config_val.toml_config(config=self.config_vars, callable=validator_analysis_values)
        
        return dict_configs


