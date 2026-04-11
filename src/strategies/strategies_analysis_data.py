from enum import Enum

class correlation_config(str, Enum): 
    FILTER= 'filter'
    MEDIAN= 'median'
    ZERO= 'zero'
    MEAN= 'mean'

class correlation_sampling(str, Enum): 
    RANDOM= 'random'
    REPRESENTATIVE= 'representative'


