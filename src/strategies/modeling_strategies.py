from enum import Enum

# 🚨 NOT AVAILABLE 🚨
class Scaler(str, Enum): 
    ROBUSTSCALER= 'robustScaler'
    STANDARDSCALER= 'standarScaler'
    MINMAXSCALER= 'minMaxScaler'

# 🚨 NOT AVAILABLE CAUSE CATEGORICS 🚨
class Encoder(str, Enum): 
    ORDINALENCODER= 'ordinalEncoder'
    TARGETENCODER= 'targetEncoder'
    ONEHOTENCODER= 'oneHotEncoder'






