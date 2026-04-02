from pydantic import BaseModel, Field, field_validator, model_validator
from pathlib import Path
import polars as pl 
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

from .eda_validation import eda_val

class path_validation(BaseModel): 
    data: str
    sample_data_percent: float= Field(gt=0.0, lt=1.0)
    
    @field_validator('data')
    def data_validation(cls, v): 
        path= Path(__file__).parent.parent.parent / 'data' / v
        if not path.exists(): 
            logger.error(f'The path for file {v} doesnt exists')
            raise FileNotFoundError(f'The path for file {v} doesnt exists')
        if path.suffix not in ['.csv', '.parquet', '.json']: 
            logger.error(f'The file {v} should be a csv, parquet or json')
            raise ValueError(f'The file {v} should be a csv, parquet or json')
        return path

class validation(BaseModel): 
    path: path_validation
    eda: eda_val
    
    @model_validator(mode='after')
    def columns_analysis_val(self): 
        path= self.path
        analysis= self.eda.basic_analysis_data
        
        if path.suffix == '.csv': 
            frame= pl.scan_csv(path, n_rows=1000)
            schema= frame.collect_schema()
        elif path.suffix == '.parquet': 
            frame= pl.scan_parquet(path, n_rows=1000)
            schema= frame.collect_schema()
        else: 
            frame= pl.read_json(path, n_rows=1000)
            schema= frame.schema
        
        
        
        
    



