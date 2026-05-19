from typing import List

import polars as pl 
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

def drop_columns(frame: pl.DataFrame, list_drop: List[str]) -> pl.DataFrame: 
    logger.info(f'DataFrame {list_drop} columns were removed')
    return frame.drop(list_drop)

