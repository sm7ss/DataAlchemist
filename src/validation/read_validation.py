import yaml 
import logging
from pathlib import Path
from typing import Dict, Any, Callable
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

from .validation_cleaning.cleaning_validation import cleaning_val
from .validation_preprocessing.preprocessing_validation import ml_preprocessing_val

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
    def read_config(cls) -> Dict[str, Any]: 
        preprocessing= Path(__file__).resolve().parent.parent.parent / 'config' / 'preprocessing' / 'preprocessing.yaml'
        cleaning= Path(__file__).resolve().parent.parent.parent / 'config' / 'cleaning' / 'cleaning.yaml'
        
        dict_configs= {}
        
        dict_configs['cleaning']= cls.yaml_read(config=cleaning, callable=cleaning_val)
        dict_configs['preprocessing']= cls.yaml_read(config=preprocessing, callable=ml_preprocessing_val)
        
        return dict_configs


