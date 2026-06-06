import polars as pl 
from typing import List, Dict, Any
import logging

from .operations.transformers import TransformationOperation
from ...strategies.pre_processing_strategies import DistributionTransformer

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

class DistributionListExpr: 
    def __init__(self, frame: pl.DataFrame):
        self.num_frame= frame.select(pl.selectors.numeric())
    
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
    
    def auto_distribution(self, distribution_dict: Dict[str, Any]) -> List[pl.Expr]: 
        list_expr= []
        
        for col in self.num_frame.columns: 
            if col == 'index': 
                continue
            
            transform= distribution_dict[col]['suggestion'].get('transformer')
            
            if transform: 
                logger.info(f'The column {col} has the transformer {transform}')
                expr= self.transform(col=col, method=transform)
                list_expr.append(expr)
            else: 
                logging.info(f'Column {col} doesnt have transform suggestion')
        
        return list_expr


















