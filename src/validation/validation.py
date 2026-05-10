from pydantic import BaseModel, Field, field_validator, model_validator
from pathlib import Path
import polars as pl 
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

from .eda_validation import eda_val
from .pre_processing_validation import ml_preprocessing_val
from .ml_validation import ml_training_val

class path_validation(BaseModel): 
    data: str
    overhead_percent: float= Field(ge=1.0, le=3.0)
    sample_data_percent: float= Field(gt=0.0, lt=1.0)
    
    @field_validator('data')
    def data_validation(cls, v): 
        path= Path(__file__).parent.parent.parent / 'data' / v
        if not path.exists(): 
            logger.error(f'The path for file {v} doesnt exists')
            raise FileNotFoundError(f'The path for file {v} doesnt exists')
        if path.suffix not in ['.csv', '.parquet']: 
            logger.error(f'The file {v} should be a csv, parquet')
            raise ValueError(f'The file {v} should be a csv, parquet')
        return path

class validation(BaseModel): 
    path: path_validation
    eda: eda_val
    ml_preprocessing: ml_preprocessing_val
    ml_training: ml_training_val
    
    @model_validator(mode='after')
    def columns_analysis_val(self): 
        path= self.path.data
        analysis= self.eda.basic_analysis_data
        
        if path.suffix == '.csv': 
            frame= pl.read_csv(path, n_rows=1000, null_values=['tbd', 'TBD', 'N/A', 'nan'])
        else: 
            frame= pl.read_parquet(path, n_rows=1000)
        
        num_columns= frame.select(pl.selectors.numeric()).columns
        cat_columns= frame.select(pl.selectors.string()).columns
        
        for analysis_data in analysis: 
            if not num_columns: 
                if analysis_data == 'distribution': 
                    self.eda.basic_analysis_data[analysis_data]['enable']= False
                if analysis_data == 'outliers': 
                    self.eda.basic_analysis_data[analysis_data]['enable']= False
                if analysis_data == 'correlation': 
                    self.eda.basic_analysis_data[analysis_data]['enable']= False
            
            if not cat_columns: 
                if analysis_data == 'category_dominance': 
                    self.eda.basic_analysis_data[analysis_data]['enable']= False
            
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
                        if len(num_columns) < 2: 
                            logger.warning(f'{analysis_data} analysis cannot have less than 2 numeric columns. This analysis will be desactivated')
                            self.eda.basic_analysis_data[analysis_data]['enable']= False 
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
                    if len(num_columns) < 2: 
                        logger.warning(f'{analysis_data} analysis cannot have less than 2 numeric columns. This analysis will be desactivated')
                        self.eda.basic_analysis_data[analysis_data]['enable']= False
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
    
    @model_validator(mode='after')
    def column_ml_preprocessing_val(self): 
        path= self.path.data
        
        if path.suffix == '.csv': 
            frame= pl.read_csv(path, n_rows=1000, null_values=['tbd', 'TBD', 'N/A', 'nan'])
        else: 
            frame= pl.read_parquet(path, n_rows=1000)
        
        frame_columns= frame.columns
        
        # COLUMNS ML VALIDATION
        columns_ml= self.ml_preprocessing.columns
        if not columns_ml: 
            self.ml_preprocessing.columns= frame_columns
            logger.warning('As the columns for ML pre-processing wasnt selected then all columns will be selected')
        if columns_ml: 
            if isinstance(columns_ml, str): 
                if columns_ml not in frame_columns: 
                    logger.error(f'Column {columns_ml} was not found in the frame columns.\nAvailable columns: {frame_columns}')
                    raise ValueError(f'Column {columns_ml} was not found in the frame columns.\nAvailable columns: {frame_columns}')
            elif isinstance(columns_ml, list): 
                for col in columns_ml: 
                    if col not in frame_columns: 
                        logger.error(f'Column {col} was not found in the frame columns.\nAvailable columns: {frame_columns}')
                        raise ValueError(f'Column {col} was not found in the frame columns.\nAvailable columns: {frame_columns}')
        
        # COLUMNS REMOVE VALIDATION 
        columns_correlation= self.ml_preprocessing.correlation.remove_column
        if isinstance(columns_correlation, str): 
            if columns_correlation not in frame_columns: 
                logger.error(f'Column {columns_correlation} was not found in the frame columns.\nAvailable columns: {frame_columns}')
                raise ValueError(f'Column {columns_correlation} was not found in the frame columns.\nAvailable columns: {frame_columns}')
        elif isinstance(columns_correlation, list): 
            for col in columns_correlation: 
                if col not in frame_columns: 
                    logger.error(f'Column {col} was not found in the frame columns.\nAvailable columns: {frame_columns}')
                    raise ValueError(f'Column {col} was not found in the frame columns.\nAvailable columns: {frame_columns}')
        
        # REPRESENTATIVE COLUMNS 
        sample_data= self.ml_preprocessing.sampling
        if sample_data == 'representative': 
            columns_representative= self.ml_preprocessing.representative_column
            if isinstance(columns_representative, str): 
                if columns_representative not in frame_columns: 
                    logger.error(f'Column {columns_representative} were not found in available columns.\nAvailable columns: {frame_columns}')
                    raise ValueError(f'Column {columns_representative} were not found in available columns.\nAvailable columns: {frame_columns}')
            elif isinstance(columns_representative, list): 
                for col in columns_representative: 
                    if col not in frame_columns: 
                        logger.error(f'Column {columns_representative} were not found in available columns.\nAvailable columns: {frame_columns}')
                        raise ValueError(f'Column {columns_representative} were not found in available columns.\nAvailable columns: {frame_columns}')
            else: 
                logger.error(f'Column/s should be selected to be representative')
        
        return self
    
    @model_validator(mode='after')
    def column_ml_training(self): 
        path= self.path.data
        
        if path.suffix == '.csv': 
            frame_columns= pl.read_csv(path, n_rows=1000, null_values=['tbd', 'TBD', 'N/A', 'nan']).columns
        else: 
            frame_columns= pl.read_parquet(path, n_rows=1000).columns
        
        target= self.ml_training.target
        
        if target not in frame_columns: 
            logger.error(f'The target column "{target}" must be in the Frame. Available columns:\n{frame_columns}')
            raise ValueError(f'The target column "{target}" must be in the Frame. Available columns:\n{frame_columns}')
        
        return self



