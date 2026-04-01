from enum import Enum

class analysis_outliers(str, Enum): 
    IQR = 'iqr'

class category_dominance_tn(int, Enum):
    MAX = 100
    MIN = 2

class category_dominance_rtp(float, Enum): 
    MAX = 1
    MIN = 0.0



