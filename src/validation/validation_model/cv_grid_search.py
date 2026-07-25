from pydantic import BaseModel, field_validator
from typing import Literal, Optional, Union, List

from sklearn.metrics import get_scorer_names
import psutil
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

class grid_search_cv_val(BaseModel):
    name: Literal['grid_search_cv']= 'grid_search_cv'
    cv: Optional[int] 
    scoring: Union[List[str], str] 
    n_jobs: Optional[int]
    
    @field_validator('scoring')
    def scoring_val(cls, v): 
        scores= get_scorer_names()
        
        if isinstance(v, str):
            if v not in scores:
                logger.error(f'Metric given {v}, is not available. Available metrics:\n{scores}')
                raise ValueError(f'Metric given {v}, is not available. Available metrics:\n{scores}')
        else: 
            for i in v: 
                if i not in scores:
                    logger.error(f'Metric given {i}, is not available. Available metrics:\n{scores}')
                    raise ValueError(f'Metric given {i}, is not available. Available metrics:\n{scores}')
        
        return v
    
    @field_validator('n_jobs')
    def n_jobs_val(cls, v): 
        cpu_count= psutil.cpu_count(logical=True)
        
        if not v: 
            v= cpu_count-1
            logger.info(f'New number of cpus will be used: {v}')
            return v
        else: 
            new_njobs= cpu_count - v
            if new_njobs < 0: 
                logger.warning(f'The number of cpus left to system cant be larger than the real number of cpus ({new_njobs}/{cpu_count}), so one will be letf to system.')
                logger.info(f'New number of cpus will be used: {new_njobs}')
                return cpu_count - 1
            else: 
                logger.info(f'New number of cpus will be used: {new_njobs}')
                return new_njobs

