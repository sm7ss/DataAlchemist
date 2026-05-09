from enum import Enum

class NullNumericHandler(str, Enum): 
    FILTER= 'filter'
    MEDIAN= 'median'
    ZERO= 'zero'
    MEAN= 'mean'

class NullCategoricHandler(str, Enum): 
    FILTER= 'filter'
    CONSTANTVALUE= 'constantValue'

class DistributionTransformer(str, Enum): 
    LOG1P= 'log1p'
    SQRT= 'sqrt'
    SQUARE= 'square'

class OutlierFilter(str, Enum): 
    TRIM= 'trim'
    CAPPING= 'capping'

class OutlierImpute(str, Enum): 
    MEDIAN= 'median'
    MEAN= 'mean'

class OutlierTransform(str, Enum): 
    LOG1P= 'log1p'
    SQRT= 'sqrt'

class CorrSampling(str, Enum): 
    RANDOM= 'random'
    REPRESENTATIVE= 'representative'

class HighCorrelationActions(str, Enum): 
    REMOVE= 'remove'
    JOIN= 'join'

# 🚨🚨🚨 
class CategoryOperation(str, Enum): 
    GROUP= 'group'

