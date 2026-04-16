from typing import Optional
from pathlib import Path

import polars as pl 
import psutil
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

#Right now, no streaming or lazy mode will be added, just eager mode
def get_frame(file: Path, overhead: float) -> Optional[pl.DataFrame]: 
    file_size= file.stat().st_size
    memory= psutil.virtual_memory().available * overhead
    
    ratio= file_size/memory
    
    if ratio > 0.65: #The 0.65 will change to a yaml file later
        logger.error(f'The file {file.name} is too big for process in local form')
        raise ValueError(f'The file {file.name} is too big for process in local form')
    else: 
        if file.suffix == '.csv': 
            frame= pl.read_csv(file, null_values=['tbd', 'TBD', 'N/A', 'nan'])
        elif file.suffix == '.parquet': 
            frame= pl.read_parquet(file)
        else: 
            frame= pl.read_json(file)
    logger.info(f'The frame for file {file.name} was obtained succesfully')
    
    return frame

