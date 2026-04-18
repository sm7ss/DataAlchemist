from enum import Enum

class DistributionTransformer(str, Enum): 
    LOG1P= 'log1p'
    SQRT= 'sqrt'
    SQUARE= 'square'

class DistributionScaler(str, Enum): 
    ROBUSTSCALER= 'robustScaler'
    STANDARDSCALER= 'standarScaler'
    MINMAXSCALER= 'minMaxScaler'

class OutlierScaler(str, Enum): 
    ROBUSTSCALER= 'robustScaler'
    STANDARDSCALER= 'standarScaler'
    MINMAXSCALER= 'minMaxScaler'

class OutlierFilter(str, Enum): 
    TRIM= 'trim'
    CAPPING= 'capping'

class OutlierImpute(str, Enum): 
    MEDIAN= 'median'

class OutlierTransform(str, Enum): 
    LOG1P= 'lop1p'
    SQRT= 'sqrt'

class CategoryTransform(str, Enum): 
    ORDINALENCODER= 'ordinalEncoder'
    TARGETENCODER= 'targetEncoder'
    ONEHOTENCODER= 'oneHotEncoder'

class CategoryImpute(str, Enum): 
    SIMPLEIMPUTER= 'simpleImputer'








