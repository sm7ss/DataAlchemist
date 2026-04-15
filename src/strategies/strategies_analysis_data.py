from enum import Enum

#This is used on eda_analysis_data.py 
#This also are strategies in cleaning
class correlation_config(str, Enum): 
    FILTER= 'filter'
    MEDIAN= 'median'
    ZERO= 'zero'
    MEAN= 'mean'

class correlation_sampling(str, Enum): 
    RANDOM= 'random'
    REPRESENTATIVE= 'representative'


