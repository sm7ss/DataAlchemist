from enum import Enum

class AnalysisOutliers(str, Enum): 
    IQR = 'iqr'

class CategoryDominance(int, Enum):
    MAX = 100
    MIN = 2

class CategoryDominanceRtp(float, Enum): 
    MAX = 1
    MIN = 0.0



