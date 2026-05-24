from ..strategies.cleaning_strategies import NumericNulls, CategoricNulls

from typing import List, Optional, Tuple, Dict, Any
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
    def delete_row_expr(frame: pl.DataFrame) -> pl.Expr: 
        columna = frame.get_column('index').to_list()
        return ~pl.col('index').is_in(columna)

class NullAnalyseDelete: 
    def __init__(self, frame: pl.DataFrame, JSON: Dict[str, Any], model: BaseModel, model_cleaning: BaseModel):
        self.frame= frame
        
        self.JSON= JSON.get('null_analysis', None)
        self.model= model
        
        self.cat= CatNullExpr(model=self.model)
        self.num= NumNullExpr(model=model)
        self.delete= DeleteData()
    
    def cat_impute(self, col: str) -> pl.Expr: 
        return self.cat.input_cat_col(cat_col=col)
    
    def num_impute(self, col: str) -> pl.Expr: 
        return self.num.input_num_data(col_num=col)
    
    def delete(self, col: str) -> pl.Expr: 
        frame= self.frame.with_row_index()
        
        # AQUI AGREGAR LA LOGICA DE INDEX PARA ELIMINAR SEA COLUMNA O ROW 
        # AGREGARELO A UNA LISTA O DICCIONARIO Y PASARLO A OBTAIN_NULL_ACTION
        
        
        
    
    def obtain_null_actions(self) -> Optional[Tuple[List[str]]]: 
        if not self.JSON: 
            logger.info('No nulls were found')
            return None
        
        delete_columns_or_row= []
        analyse_columns= []
        
        for col in self.JSON: 
            if col != 'total_nulls': 
                action= self.JSON[col]['action']
                
                if action == 'delete': 
                    logger.info(f'Column or row {col} will be deleated')
                    delete_columns_or_row.append(col)
                elif action == 'analyse': 
                    logger.info(f'Column {col} will be analysed')
                    analyse_columns.append(col)
                else: 
                    logger.info(f'Column {col} will be keeped')
                    continue
        
        return (delete_columns_or_row, analyse_columns)













