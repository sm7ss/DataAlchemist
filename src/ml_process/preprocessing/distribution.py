import polars as pl 
from typing import List, Dict, Any
import logging

from .operations.transformers import TransformationOperation
from ...strategies.pre_processing_strategies import DistributionTransformer

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

class Distribution: 
    def __init__(self, frame: pl.DataFrame, distribution_dict: Dict[str, Any]):
        self.num_frame= frame.select(pl.selectors.numeric())
        self.distribution_dict= distribution_dict
    
    def transform(self, col: str, method: DistributionTransformer) -> pl.Expr: 
        transform= TransformationOperation()
        
        match method: 
            case DistributionTransformer.LOG1P: 
                expr= transform.log1p(col=col)
            case DistributionTransformer.SQRT: 
                expr= transform.sqrt(col=col)
            case DistributionTransformer.SQUARE: 
                expr= transform.square(col=col)
        
        return expr
    
    def distribution_expr(self) -> List[pl.Expr]: 
        list_expr= []
        
        for col in self.num_frame.columns: 
            if col == 'index': 
                continue
            
            transform= self.distribution_dict[col]['suggestion'].get('transformer')
            
            if transform: 
                logger.info(f'The column {col} has the transformer {transform}')
                expr= self.transform(col=col, method=transform)
                list_expr.append(expr)
            else: 
                logging.info(f'Column {col} doesnt have transform suggestion')
        
        return list_expr
    
    def fit_expressions(self, x_train: pl.DataFrame) -> pl.DataFrame: 
        distribution_expr= self.distribution_expr()
        
        if not distribution_expr: 
            return x_train
        
        self.distribution= distribution_expr
        
        x_train= x_train.with_columns(distribution_expr)
        logger.info('Distribution expressions were applied')
        
        return x_train
    
    def transform_expressions(self, x_test: pl.DataFrame) -> pl.DataFrame: 
        if not self.distribution: 
            return x_test
        
        x_test= x_test.with_columns(self.distribution)
        logger.info('Distribution expressions were applied')
        
        return x_test


















