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
        path= self.path.data
        analysis= self.eda.basic_analysis_data
        
        if path.suffix == '.csv': 
            frame= pl.read_csv(path, n_rows=1000, null_values=['tbd', 'TBD', 'N/A', 'nan'])
        elif path.suffix == '.parquet': 
            frame= pl.read_parquet(path, n_rows=1000)
        else: 
            frame= pl.read_json(path, n_rows=1000)
        
        num_columns= frame.select(pl.selectors.numeric()).columns
        cat_columns= frame.select(pl.selectors.string()).columns
        
        for analysis_data in analysis: 
            columns= analysis[analysis_data]['columns']
            enable= analysis[analysis_data]['enable']
            
            if not columns: 
                if (analysis_data == 'distribution') and (enable == True): 
                    if len(num_columns) < 1: 
                        logger.warning(f'There are no columns available, {analysis_data} will be desactivated')
                        self.eda.basic_analysis_data[analysis_data]['enable']= False
                    else: 
                        logger.info(f'{analysis_data} analysis will change their columns to be all columns, cause there are no columns available and the analysis is activated')
                        self.eda.basic_analysis_data[analysis_data]['columns']= num_columns
                elif (analysis_data == 'outliers') and (enable == True): 
                    if len(num_columns) < 1: 
                        logger.warning(f'There are no numric columns available, {analysis_data} will be desactivated')
                        self.eda.basic_analysis_data[analysis_data]['enable']= False
                    else: 
                        logger.info(f'{analysis_data} analysis will change their columns to be all numeric columns, cause there are no columns available and the analysis is activated')
                        self.eda.basic_analysis_data[analysis_data]['columns']= num_columns
                elif (analysis_data == 'correlation') and (enable == True): 
                    if len(num_columns) < 1: 
                        logger.warning(f'There are no numeric columns available, {analysis_data} will be desactivated')
                        self.eda.basic_analysis_data[analysis_data]['enable']= False
                    else: 
                        if len(num_columns) < 2: 
                            logger.warning(f'{analysis_data} analysis cannot have less than 2 numeric columns. This analysis will be desactivated')
                            self.eda.basic_analysis_data[analysis_data]['enable']= False
                        else: 
                            logger.info(f'{analysis_data} analysis will change their columns to be all numeric columns, cause there are no columns available and the analysis is activated')
                            self.eda.basic_analysis_data[analysis_data]['columns']= num_columns
                elif (analysis_data == 'category_dominance') and (enable == True): 
                    if len(cat_columns) < 1: 
                        logger.warning(f'There are no categoric columns available, {analysis_data} will be desactivated')
                        self.eda.basic_analysis_data[analysis_data]['enable']= False
                    else: 
                        logger.info(f'{analysis_data} analysis will change their columns to be all categorical columns, cause there are no columns available and the analysis is activated')
                        self.eda.basic_analysis_data[analysis_data]['columns']= cat_columns 
                else: 
                    continue
            elif isinstance(columns, list): 
                for col in columns: 
                    if (analysis_data == 'distribution') and (enable == True): 
                        if col not in num_columns: 
                            logger.error(f'The column {col} doesnt exist on the frame.\nThe available columns are: {num_columns}')
                    elif (analysis_data == 'outliers') and (enable == True): 
                        if col not in num_columns: 
                            logger.error(f'Th column {col} should be a numerical column.\nNumerical columns available: {num_columns}')
                            raise ValueError(f'Th column {col} should be a numerical column.\nNumerical columns available: {num_columns}')
                    elif (analysis_data == 'correlation') and (enable == True): 
                        if col not in num_columns: 
                            logger.error(f'The column {col} should be a numerical column.\nNumerical columns available: {num_columns}')
                            raise ValueError(f'The column {col} should be a numerical column.\nNumerical columns available: {num_columns}')
                    elif (analysis_data == 'category_dominance') and (enable == True): 
                        if col not in cat_columns: 
                            logger.error(f'The column {col} is not a categorical column.\nCateorical columns available: {cat_columns}')
                            raise ValueError(f'The column {col} is not a categorical column.\nCateorical columns available: {cat_columns}')
                    else: 
                        continue
            elif isinstance(columns, str): 
                if (analysis_data == 'distribution') and (enable == True): 
                    if columns not in num_columns: 
                        logger.error(f'The column {columns} doesnt exist on the frame.\nThe available columns are: {num_columns}')
                        raise ValueError(f'The column {columns} doesnt exist on the frame.\nThe available columns are: {num_columns}')
                elif (analysis_data == 'outliers') and (enable == True): 
                    if columns not in num_columns: 
                        logger.error(f'Th column {columns} should be a numerical column.\nNumerical columns available: {num_columns}')
                        raise ValueError(f'Th column {columns} should be a numerical column.\nNumerical columns available: {num_columns}')
                elif (analysis_data == 'correlation') and (enable == True): 
                    
                    if columns not in num_columns: 
                        logger.error(f'The column {columns} should be a numerical column.\nNumerical columns available: {num_columns}')
                        raise ValueError(f'The column {columns} should be a numerical column.\nNumerical columns available: {num_columns}')
                elif (analysis_data == 'category_dominance') and (enable == True): 
                    
                    if columns not in cat_columns: 
                        logger.error(f'The column {columns} is not a categorical column.\nCateorical columns available: {cat_columns}')
                        raise ValueError(f'The column {columns} is not a categorical column.\nCateorical columns available: {cat_columns}')
                else: 
                    continue
            else: 
                logger.error('The columns should be on a list or should be a string')
                raise ValueError('The columns should be on a list or should be a string')
        
        return self



