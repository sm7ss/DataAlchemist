import polars as pl 
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

def duplicated_rows(frame: pl.DataFrame) -> pl.DataFrame: 
    new_frame= frame.filter(~frame.is_duplicated())
    
    if new_frame.height != frame.height: 
        logger.info(f'Duplicate rows were removed. Total rows {frame.height}, total duplicate rows deleted {new_frame.height}')
        return new_frame
    else: 
        logger.info('There are no duplicate rows')
        return frame

