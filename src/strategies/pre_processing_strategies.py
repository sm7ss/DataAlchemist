from enum import Enum

class Scaler(str, Enum): 
    ROBUSTSCALER= 'robustScaler'
    STANDARDSCALER= 'standarScaler'
    MINMAXSCALER= 'minMaxScaler'

class Encoder(str, Enum): 
    ORDINALENCODER= 'ordinalEncoder'
    TARGETENCODER= 'targetEncoder'
    ONEHOTENCODER= 'oneHotEncoder'

# THIS IS DONE
class NullNumericHandler(str, Enum): 
    FILTER= 'filter'
    MEDIAN= 'median'
    ZERO= 'zero'
    MEAN= 'mean'

# THIS IS DONE
class NullCategoricHandler(str, Enum): 
    FILTER= 'filter'
    CONSTANTVALUE= 'constantValue'

# THIS IS DONE
class DistributionTransformer(str, Enum): 
    LOG1P= 'log1p'
    SQRT= 'sqrt'
    SQUARE= 'square'

class OutlierFilter(str, Enum): 
    TRIM= 'trim'
    CAPPING= 'capping'

# THIS IS DONE
class OutlierImpute(str, Enum): 
    MEDIAN= 'median'
    MEAN= 'mean'

# THIS IS DONE
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

