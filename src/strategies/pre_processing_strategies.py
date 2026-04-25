from enum import Enum

class Scaler(str, Enum): 
    ROBUSTSCALER= 'robustScaler'
    STANDARDSCALER= 'standarScaler'
    MINMAXSCALER= 'minMaxScaler'

class Encoder(str, Enum): 
    

class NullHandler(str, Enum): 
    FILTER= 'filter'
    MEDIAN= 'median'
    ZERO= 'zero'
    MEAN= 'mean'

class DistributionTransformer(str, Enum): 
    LOG1P= 'log1p'
    SQRT= 'sqrt'
    SQUARE= 'square'

class OutlierFilter(str, Enum): 
    TRIM= 'trim'
    CAPPING= 'capping'

class OutlierImpute(str, Enum): 
    MEDIAN= 'median'

class OutlierTransform(str, Enum): 
    LOG1P= 'log1p'
    SQRT= 'sqrt'

class CorrSampling(str, Enum): 
    RANDOM= 'random'
    REPRESENTATIVE= 'representative'

class HighCorrelationActions(str, Enum): 
    REMOVE= 'remove'
    JOIN= 'join'
    FILTER= 'filter'

class CategoryOperation(str, Enum): 
    GROUP= 'group'

class CategoryImpute(str, Enum): 
    SIMPLEIMPUTER= 'simpleImputer'








