from ..strategies.cleaning_strategies import NumericNulls, CategoricNulls

from typing import List, Optional, Tuple, Dict, Any, Union
from pydantic import BaseModel

import polars as pl 
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

class CatNullExpr: 
    def __init__(self, model: BaseModel):
        self.null_cat = model.cleaning.null_values.null_impute_categorics
    
    def input_value(self, cat_col: str) -> pl.Expr: 
        return pl.col(cat_col).fill_null(self.null_cat)
    
    def input_mode(self, cat_col: str) -> pl.Expr: 
        return pl.col(cat_col).mode().first()
    
    def input_cat_col(self, cat_col: str) -> pl.Expr: 
        match self.null_cat: 
            case CategoricNulls.MODE: 
                expr= self.input_mode(cat_col=cat_col)
            case _: 
                expr= self.input_value(cat_col=cat_col)
        return expr

class NumNullExpr: 
    def __init__(self, model: BaseModel):
        self.null_num = model.cleaning.null_values.null_impute_numerics
    
    def operation_fill(self, col_num: str) -> pl.Expr:
        expr= (getattr(pl.col(col_num), self.null_num)())
        return pl.col(col_num).fill_null(expr)
    
    def input_value(self, col_num: str) -> pl.Expr: 
        return pl.col(col_num).fill_null(self.null_num)
    
    def input_num_data(self, col_num: str) -> pl.Expr: 
        match self.null_num:
            case NumericNulls.MEAN | NumericNulls.MEDIAN: 
                expr= self.operation_fill(col_num=col_num)
            case _:
                expr= self.input_value(col_num=col_num)
        return expr

class DeleteData: 
    @staticmethod
    def delete_column(frame: pl.DataFrame, list_col: List[str]) -> pl.DataFrame: 
        return frame.drop(list_col)
    
    @staticmethod
    def delete_row_expr(index_list: List[Union[int, float]]) -> pl.Expr: 
        return ~pl.col('index').is_in(index_list)

class NullAnalyseDelete: 
    def __init__(self, frame: pl.DataFrame, JSON: Dict[str, Any], model: BaseModel, model_cleaning: BaseModel):
        self.frame= frame
        
        self.JSON= JSON.get('null_analysis', None)
        self.model= model
        self.model_cleaning= model_cleaning.threshold_nulls
        
        self.cat= CatNullExpr(model=self.model)
        self.num= NumNullExpr(model=model)
        self.delete= DeleteData()
    
    def cat_impute(self, col: str) -> pl.Expr: 
        return self.cat.input_cat_col(cat_col=col)
    
    def num_impute(self, col: str) -> pl.Expr: 
        return self.num.input_num_data(col_num=col)
    
    def analyse(self, col: str) -> Union[pl.Expr, str, None]: 
        frame= self.frame.with_row_index()
        
        nulls= frame.filter(pl.col(col).is_null())
        percent_nulls= (nulls.height/ frame.height)*100
        
        if percent_nulls < self.model_cleaning.columns_percent: 
            row_nulls= nulls.with_columns(
                sum_nulls= pl.sum_horizontal(pl.col('*').is_null().cast(pl.Int32))
                .filter(pl.col('sum_nulls') > self.model_cleaning.rows_percent)
            )
            if row_nulls.height < 1: 
                logger.info(f'For column {col} rows will be imputed')
                numeric_cols= self.frame.select(pl.selectors.numeric())
                categoric_cols= self.frame.select(pl.selectors.string())
                
                if col in numeric_cols: 
                    expr= self.num_impute(col=col)
                elif col in categoric_cols: 
                    expr= self.cat_impute(col=col)
                else: 
                    return None
                
                return expr
            else: 
                logger.info(f'For column {col} rows will be removed')
                index_rows= row_nulls.get_column('index').to_list()
                expr= self.delete.delete_row_expr(index_list=index_rows)
                return expr
        else:
            logger.info(f'Column {col} will be removed')
            return col
    
    def obtain_null_actions(self) -> Optional[Tuple[List[str]]]: 
        if not self.JSON: 
            logger.info('No nulls were found')
            return None
        
        columns_removed= []
        list_expr= []
        
        for col in self.JSON: 
            if col != 'total_nulls': 
                action= self.JSON[col]['action']
                analyse= self.analyse(col=col)
                
                if action=='keep': 
                    logger.info(f'Column {col} will be keeped')
                    continue
                else: 
                    if isinstance(analyse, str): 
                        columns_removed.append(col)
                    elif analyse is None:
                        logger.info(f'Datatype for column {col} will not be processed, just strings or numeric types.')
                        continue
                    else:
                        list_expr.append(col)
        
        return list_expr













