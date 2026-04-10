import yaml 
import tomli
import logging
from pathlib import Path
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

from .validation import validation
from .validation_analysis_values.validation import outlier_decision_maker

class ReadConfigYaml: 
    @staticmethod
    def yaml_config(config: Path) -> Dict[str, Any]: 
        try: 
            with open(config, 'r') as c: 
                read= yaml.safe_load(c)
                logger.info(f'The file {config.name} was readed correctly')
            val= validation(**read)
            logger.info(f'The file {config.name} was validated correctly')
            return val
        except yaml.YAMLError: 
            logger.error(f'The yaml file {config.name} is corrupted')
            raise ValueError(f'The yaml file {config.name} is corrupted')
        except Exception as e: 
            logger.error(f'There is an error:\n{e}')
            raise ValueError(f'There is an error:\n{e}')
    
    @staticmethod
    def yaml_config_vars(config: Path) -> Dict[str, Any]: 
        try: 
            with open(config, 'r') as c: 
                read= yaml.safe_load(c)
                logger.info(f'The file {config.name} was readed correctly')
            val= outlier_decision_maker(**read['outlier_decision_maker'])
            logger.info(f'The file {config.name} was validated correctly')
            return val
        except yaml.YAMLError: 
            logger.error(f'The yaml file {config.name} is corrupted')
            raise ValueError(f'The yaml file {config.name} is corrupted')
        except Exception as e: 
            logger.error(f'There is an error:\n{e}')
            raise ValueError(f'There is an error:\n{e}')

class ReadConfigToml: 
    @staticmethod
    def toml_config(config: Path) -> Dict[str, Any]: 
        try: 
            with open(config, 'rb') as c: 
                read= tomli.load(c)
                logger.info(f'The file {config.name} was readed correctly')
            val= validation(**read)
            logger.info(f'The file {config.name} was validated correctly')
            return val
        except tomli.TOMLDecodeError: 
            logger.error(f'The toml file {config.name} is corrupted')
            raise ValueError(f'The toml file {config.name} is corrupted')
        except Exception as e: 
            logger.error(f'There is an error:\n{e}')
            raise ValueError(f'There is an error:\n{e}')
    
    @staticmethod
    def toml_config_vars(config: Path) -> Dict[str, Any]: 
        try: 
            with open(config, 'rb') as c: 
                read= tomli.load(c)
                logger.info(f'The file {config.name} was readed correctly')
            val= outlier_decision_maker(**read['outlier_decision_maker'])
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
        
        self.yaml_config= ReadConfigYaml()
        self.toml_config= ReadConfigToml()
    
    def read_config(self) -> Dict[str, Any]: 
        suff_config= self.config.suffix
        suff_config_var= self.config_vars.suffix
        
        dict_configs= {}
        
        if suff_config in ['.yml', '.yaml']: 
            dict_configs['config']= self.yaml_config.yaml_config(config=self.config)
        else: 
            dict_configs['config'] = self.toml_config.toml_config(config=self.config)
        
        if suff_config_var in ['.yml', '.yaml']: 
            dict_configs['config_vars']= self.yaml_config.yaml_config_vars(config=self.config_vars)
        else: 
            dict_configs['config_vars']= self.toml_config.toml_config_vars(config=self.config_vars)
        
        return dict_configs


