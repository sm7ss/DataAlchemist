from enum import Enum

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










