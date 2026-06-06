import polars as pl 
import logging
from typing import List, Optional, Union, Dict, Any
from pydantic import BaseModel

from ...strategies.pre_processing_strategies import CorrSampling
from .operations.null import NullNumHandler, NullCatHandler

from .distribution import DistributionListExpr
from .outliers import OutlierCleanFrame
from .correlation import CorrelationPreprocessing

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

class SamplingData: 
    def __init__(self, frame: pl.DataFrame, config: BaseModel):
        self.frame= frame
        self.config_sample= config.sample_data
    
    def percent_files(self) -> int: 
        size= self.frame.height
        
        min_sample= self.config_sample.min_sample.max_files
        
        medium_sample= self.config_sample.medium_sample.max_files
        medium_percent= self.config_sample.medium_sample.percent
        
        many_sample= self.config_sample.many_sample.max_files
        many_percent= self.config_sample.many_sample.percent
        
        too_much_percent= self.config_sample.many_sample.percent
        
        if size < min_sample: 
            new_size= size
        elif size < medium_sample: 
            new_size= int(size* medium_percent)
        elif size < many_sample: 
            new_size= int(size*many_percent)
        else: 
            new_size= int(size*too_much_percent)
        
        return new_size
    
    def random_sample(self) -> pl.DataFrame: 
        files= self.percent_files()
        return self.frame.sample(n=files, seed=42)
    
    def representative(self, r_columns: Union[str, List[str]]) -> pl.DataFrame: 
        files= self.percent_files
        return self.frame.select(r_columns).sample(n=files, seed=42)
    
    def sampling(self, decision: CorrSampling, r_columns: Union[str, List[str]]=None) -> pl.DataFrame: 
        match decision: 
            case CorrSampling.RANDOM: 
                self.frame= self.random_sample()
            case CorrSampling.REPRESENTATIVE: 
                self.frame= self.representative(r_columns=r_columns)
        
        return self.frame

class NullHandler: 
    def __init__(self, frame: pl.DataFrame, config: BaseModel):
        self.config= config.ml_preprocessing
        
        self.frame= frame
        self.num_cols= frame.select(pl.selectors.numeric()).columns
        self.cat_cols= frame.select(pl.selectors.string()).columns
        
        self.num_handle= NullNumHandler()
        self.cat_handle= NullCatHandler()
    
    def get_columns_with_nulls(self, null_dict: Dict[str, Any]) -> Optional[List[str]]: 
        null= null_dict.get('null_analysis', None)
        
        if not null: 
            logger.info('No null analysis were detected')
            return None
        
        list_nulls= []
        
        for col in null: 
            if col != 'total_nulls': 
                nulls= null[col].get('total_nulls_column', None)
                if nulls > 0: 
                    list_nulls.append(col)
        
        if list_nulls: 
            return list_nulls
        else: 
            logger.info(f'Any column have outliers')
            return None
    
    def get_expr(self, null_analysis: Dict[str, Any]) -> Optional[List[pl.Expr]]: 
        list_expr= []
        cols= self.get_columns_with_nulls(null_dict=null_analysis)
        
        if not cols: 
            logger.info('No nulls were found')
            return None
        
        cat_handle= self.config.null_cat_handler
        const_value= self.config.null_cat_handler_value
        
        num_handle= self.config.null_num_handler
        
        for col in cols: 
            if col in self.num_cols:
                expr= self.num_handle.get_null_num_handler_expr(col=col, null_method=num_handle)
                list_expr.append(expr)
                logger.info(f'Expression for column {col} numeric was created')
            elif col in self.cat_cols: 
                expr= self.cat_handle.get_null_cat_handler_expr(col=col, null_method=cat_handle, constant_value=const_value)
                list_expr.append(expr)
                logger.info(f'Expression for column {col} categorical was created')
            else: 
                logger.info(f'Column {col} has no expression for its data type')
                continue
        
        if not list_expr:
            logger.info('No nulls were found')
            return None
        
        return list_expr

class PreProcessinAuto: 
    def __init__(self, frame: pl.DataFrame, config: BaseModel, config_prep: BaseModel, analysis_dict: Dict[str, Any]):
        self.frame= frame
        
        self.config= config
        self.config_prep= config_prep
        self.analysis_dict= analysis_dict.get('analysis_data', None)
    
    def distribution(self) -> Optional[List[str]]: 
        distribution_dict= self.analysis_dict.get('distribution', None)
        if not distribution_dict: 
            logger.info('No distribution analysis were detected or enabled')
            return None
        
        distribution_expr= DistributionListExpr(frame=self.frame)
        distribution_list= distribution_expr.auto_distribution(distribution_dict=distribution_dict)
        
        if distribution_list: 
            logger.info('List of expresions for distribution were added into principal list expressions')
            return distribution_list
        else: 
            logger.info('No expressions for distribution analisys were found')
    
    def outliers(self) -> Optional[List[str]]: 
        outlier_dict= self.analysis_dict.get('outliers', None)
        if not outlier_dict: 
            logger.info(f'No outlier analysis were detected or enabled')
            return None
        
        outlier_frame= OutlierCleanFrame(frame=self.frame, config=self.config_prep)
        frame= outlier_frame.iqr_auto_expr_method(outlier_dict=outlier_dict)
        
        return frame
    
    def correlation(self) -> Optional[List[pl.Expr]]: 
        corr_dict= self.analysis_dict.get('correlation', None)
        if not corr_dict: 
            logger.info(f'No correlation analysis were detected or enabled')
            return None
        
        correlation_op= CorrelationPreprocessing(frame=self.frame, corr_dict=corr_dict, config=self.config)
        correlation_dict= correlation_op.auto_correlation()
        
        if correlation_dict: 
            logger.info('List of expresions for correlation were added into principal list expressions')
            return correlation_dict
        else: 
            logger.info('No expressions for correlation analisys were found')
    
    def get_frame(self) -> Optional[pl.DataFrame]:
        frame= self.frame
        
        change= 0
        
        d_expr= self.distribution()
        o_expr= self.outliers()
        c_expr= self.correlation()
        
        if d_expr: 
            frame= frame.with_columns(d_expr)
            logger.info('DataFrame with changes to the distribution data')
            change+=1
        if o_expr is not None: 
            frame= o_expr
            logger.info('DataFrame with changes to the data for outliers')
            change+=1
        if c_expr: 
            if isinstance(c_expr, list):
                frame= frame.with_columns(c_expr)
                logger.info('DataFrame with changes to the correlation data')
                change+=1
            else: 
                drop= c_expr['drop']
                expr= c_expr['expr']
                
                frame= frame.with_columns(expr).drop(drop)
                logger.info('DataFrame with changes to the correlation data')
                change+=1
        
        if change > 0: 
            return frame
        else: 
            logger.info(f'No expressions were found')
            return None

class AutoPipeline: 
    def __init__(self, frame: pl.DataFrame, analysis: Dict[str, Any], config: BaseModel, config_pre: BaseModel):
        self.config= config
        self.config_pre= config_pre
        
        column= self.config.ml_preprocessing.columns
        if column: 
            self.frame= frame.select(column).with_row_index()
        else: 
            self.frame= frame.with_row_index()
        
        self.analysis= analysis
    
    def frame_sampling(self) -> pl.DataFrame: 
        sampling= self.config.ml_preprocessing.sampling
        r_columns= self.config.ml_preprocessing.representative_column
        
        sample_data= SamplingData(frame=self.frame, config=self.config_pre).sampling(decision=sampling, r_columns=r_columns)
        
        logger.info('Sampled frame were obtained')
        
        return sample_data
    
    def nulls_frame(self, frame: pl.DataFrame) -> Optional[pl.DataFrame]: 
        list_null_handler= NullHandler(frame=frame, config=self.config).get_expr(null_analysis=self.analysis)
        
        if list_null_handler: 
            logger.info('Null expressions were added')
            return frame.with_columns(list_null_handler)
        else:
            return None
    
    def analysis_frame(self, frame: pl.DataFrame) -> Optional[pl.DataFrame]: 
        frame= PreProcessinAuto(frame=frame, config=self.config, config_prep=self.config_pre, analysis_dict=self.analysis).get_frame()
        
        if frame is None: 
            return None
        else: 
            return frame
    
    def auto_frame_tests(self) -> Dict[str, pl.DataFrame]: 
        sample_frame= self.frame_sampling()
        frame= self.frame
        
        nulls= self.nulls_frame(frame=sample_frame)
        frame_nulls= self.nulls_frame(frame=frame)
        if frame_nulls is not None: 
            analysis= self.analysis_frame(frame=nulls)
            analysis_frame= self.analysis_frame(frame=frame)
            if analysis_frame is not None: 
                logger.info('Frame was obtained correctly')
                analysis= self.analysis_frame(frame=sample_frame)
                analysis_frame= self.analysis_frame(frame=frame)
                if analysis_frame is not None: 
                    logger.info('Frame was obtained correctly')
                    return {
                        'sample': analysis.drop('index'), 
                        'frame': analysis_frame.drop('index')
                    }
        
        analysis= self.analysis_frame(frame=sample_frame)
        analysis_frame= self.analysis_frame(frame=frame)
        if analysis_frame is not None: 
            logger.info('Frame was obtained correctly')
            return {
                'sample': analysis.drop('index'), 
                'frame': analysis_frame.drop('index')
            }
        else: 
            return {
                'sample': sample_frame.drop('index'),
                'frame': frame.drop('index')
            }

