from typing import Dict

import polars as pl 
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

def rename_columns(frame: pl.DataFrame, rename_dict: Dict[str, str]) -> pl.DataFrame:
    columns= [*rename_dict]
    logger.info(f'Columns {columns} were renamed')
    return frame.rename(rename_dict)

