from enum import Enum

class RegressionScoring(str, Enum): 
    MAE = 'neg_mean_absolute_error'
    RMSE= 'neg_root_mean_squared_error'
    R2= 'r2'
    MSE= 'neg_mean_squared_error'

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






