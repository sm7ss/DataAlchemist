import yaml 
import tomli
import logging
from pathlib import Path
from typing import Dict, Any

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

from .validation import validation

class ReadConfigFile: 
    def __init__(self):
        self.config= Path(__file__).parent.parent.parent / 'config' / 'config.yml'
    
    def yaml_config(self) -> Dict[str, Any]: 
        try: 
            with open(self.config, 'r') as c: 
                read= yaml.safe_load(c)
                logger.info(f'The file {self.config.name} was readed correctly')
            val= validation(**read)
            logger.info(f'The file {self.config.name} was validated correctly')
            return val
        except yaml.YAMLError: 
            logger.error(f'The yaml file {self.config.name} is corrupted')
            raise ValueError(f'The yaml file {self.config.name} is corrupted')
        except Exception as e: 
            logger.error(f'There is an error:\n{e}')
            raise ValueError(f'There is an error:\n{e}')
    
    def toml_config(self) -> Dict[str, Any]: 
        try: 
            with open(self.config, 'rb') as c: 
                read= tomli.load(c)
                logger.info(f'The file {self.config.name} was readed correctly')
            val= validation(**read)
            logger.info(f'The file {self.config.name} was validated correctly')
            return val
        except tomli.TOMLDecodeError: 
            logger.error(f'The toml file {self.config.name} is corrupted')
            raise ValueError(f'The toml file {self.config.name} is corrupted')
        except Exception as e: 
            logger.error(f'There is an error:\n{e}')
            raise ValueError(f'There is an error:\n{e}')
    
    def read_config(self) -> Dict[str, Any]: 
        suff = self.config.suffix
        if suff in ['.yml', '.yaml']: 
            return self.yaml_config()
        else: 
            return self.toml_config()




