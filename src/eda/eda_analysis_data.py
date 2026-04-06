from typing import Dict, Any

import polars as pl 
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s-&(levelname)s-%(message)s')
logger= logging.getLogger(__name__)

# HERE # if your outliers analysis detection is another one, please create a new class like OutlierAnalysis

class AnalysisData: 
    def __init__(self, analysis: Dict[str, Any]):
        self.analysis= analysis
    
    def distribution_analysis(self): 
        pass
    
    def outliers_analysis(self): 
        pass
    
    def correlation_analysis(self): 
        pass
    
    def category_dominance(self): 
        pass
    
    
    
    
    
    
    
    
    



