from sklearn.linear_model import LinearRegression
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor

from pydantic import BaseModel
from typing import Callable, Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(mesagge)s')
logger= logging.getLogger(__name__)

class ModelRegressor: 
    @staticmethod
    def linear_regression() -> Callable: 
        return LinearRegression()
    
    @staticmethod
    def decision_tree(random_state: int) -> Callable: 
        return DecisionTreeRegressor(random_state=random_state)
    
    @staticmethod
    def random_forest(random_state: int) -> Callable: 
        return RandomForestRegressor(random_state=random_state)

class DictModelRegressor: 
    def __init__(self, config_model: BaseModel):
        self.config= config_model.models_hyperparameters
        self.models= ModelRegressor()
    
    def linear(self) -> Optional[Dict[str, Any]]: 
        linear_hyper= self.config.linear_regression
        enable= linear_hyper.enable
        
        if enable: 
            dict_linear= {}
            dict_linear['model']= self.models.linear_regression()
            dict_linear['params']= {
                'fit_intercept': linear_hyper.fit_intercept
            }
            logger.info('Dictionary for the line regression model for grid was created')
            return dict_linear
        else: 
            return None
    
    def decision(self, random_state: int) -> Optional[Dict[str, Any]]: 
        decision_hyper= self.config.decision_tree
        enable= decision_hyper.enable
        
        if enable: 
            dict_decision= {}
            dict_decision['model']= self.models.decision_tree(random_state=random_state)
            dict_decision['params']= {
                'max_depth': decision_hyper.max_depth, 
                'min_samples_split': decision_hyper.min_samples_split
            }
            logger.info('Dictionary for the decision tree model for grid was created')
            return dict_decision
        else: 
            return None
    
    def forest(self, random_state: int) -> Optional[Dict[str, Any]]: 
        forest_hyper= self.config.random_forest
        enable= forest_hyper.enable
        
        if enable: 
            dict_forest= {}
            dict_forest['model']= self.models.random_forest(random_state=random_state)
            dict_forest['params']= {
                'n_estimators': forest_hyper.n_estimators, 
                'max_depth': forest_hyper.max_depth, 
                'min_samples_split': forest_hyper.min_samples_split
            }
            logger.info('Dictionary for the random forest model for grid was created')
            return dict_forest
        else: 
            return None
    
    def get_dict(self, random_state: int) -> Dict[str, Any]: 
        dict_general= {}
        
        linear= self.linear()
        if linear: 
            dict_general['linear_regression']= linear
        
        decision= self.decision(random_state=random_state)
        if decision: 
            dict_general['decision_tree']= decision
        
        forest= self.forest(random_state=random_state)
        if forest:
            dict_general['random_forest']= forest
        
        return dict_general

