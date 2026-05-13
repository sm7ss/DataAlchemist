from .scaler import SelectScaler
from .models import DictModelRegressor

from sklearn.model_selection import GridSearchCV, train_test_split, cross_val_score
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score, root_mean_squared_error

from pydantic import BaseModel
from typing import Tuple, Optional, Callable

import polars as pl 
import numpy as np
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(mesagge)s')
logger= logging.getLogger(__name__)

class BestRegressorModel: 
    def __init__(self, frame: pl.DataFrame, config: BaseModel, config_ml: BaseModel):
        self.frame= frame
        
        self.config= config.ml_training
        self.config_ml= config_ml
        self.random_state= self.config.random_state
        
        self.scaler= SelectScaler(frame=self.frame, config_ml=self.config_ml)
        self.model_reg= DictModelRegressor(config_model=self.config_ml)
    
    def get_scaler(self) -> Optional[Callable]: 
        scaler_object= self.scaler.auto()
        if not scaler_object: 
            return None
        
        return scaler_object
    
    def x_y(self) -> Tuple[np.ndarray]: 
        target= self.config.target
        
        x= self.frame.drop(target).to_numpy(use_pyarrow=True)
        y= self.frame[target].to_numpy(use_pyarrow=True)
        
        logger.info('X/Y was transformed into an ndarray for numpy and obtained')
        return (x, y)
    
    def x_y_split(self) -> Tuple[np.ndarray]: 
        x, y= self.x_y()
        scaler= self.get_scaler()
        
        x_train, x_search, y_train, y_search= train_test_split(
            x, y, test_size=self.config.train_test_search, random_state=self.random_state
        )
        
        if scaler: 
            logging.info('x was scaled')
            x_train= scaler.fit_transform(x_train)
            x_search= scaler.transform(x_search)
        
        return (x_train, x_search, y_train, y_search)
    
    def best_hyper(self) : 
        pass
    
    def best_model(self): 
        """y_pred= grid_search.predict(x_search)
        
        mse= mean_squared_error(y_search, y_pred)
        rmse= root_mean_squared_error(y_search, y_pred)
        mae= mean_absolute_error(y_search, y_pred)
        r2= r2_score(y_search, y_pred)
        
        dict_sbh[model_type]['metrics']= {
            'MSE': mse, 
            'RMSE': rmse,
            'MAE': mae,
            'R2': r2
        }"""
        pass
    
    def generalization(self): 
        pass
    
    def report(self): 
        pass
    
    def searching_best_hyper_and_model(self) : 
        dict_sbh= {}
        
        dict_model= self.model_reg.get_dict(random_state=self.random_state)
        
        if not dict_model: 
            logging.warning('No models were found enable')
            return None
        
        x_train, x_search, y_train, y_search= self.x_y_split()
        scores= self.config_ml.grid_search_cv.scoring
        cv= self.config_ml.grid_search_cv.cv
        n_jobs= self.config_ml.grid_search_cv.n_jobs
        
        for model_type, config in dict_model.items(): 
            dict_sbh[model_type]= {}
            
            model= config['model']
            params= config['params']
            
            grid_search= GridSearchCV(
                model, 
                params, 
                cv=cv, 
                scoring=scores, 
                n_jobs=n_jobs, 
                refit=False,
                verbose=1, 
                return_train_score=True
            )
            
            grid_search.fit(x_train, y_train)
            
            dict_sbh[model_type]['cv_result']= grid_search.cv_results_
        
        return dict_sbh

















