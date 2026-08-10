import hydra
from omegaconf import DictConfig, OmegaConf
from src.validation.read_validation import ReadConfig
from src.validation.validation import validation

from src.get_frame import get_frame
from src.eda.pipeline import EdaPipeline

from src.cleaning.pipeline import CleanDataFrame
from src.ml_process.preprocessing.pipeline import Pipeline

from pathlib import Path
import json
import logging

from sklearn.model_selection import train_test_split

logging.basicConfig(level=logging.INFO, format='%(levelname)s-%(asctime)s-%(message)s')
logger= logging.getLogger(__name__)

@hydra.main(
    version_base=None, 
    config_path="config",
    config_name="config"
)
def main(cfg: DictConfig) -> None:
    dict_config= OmegaConf.to_container(cfg, resolve=True)
    
    try: 
        config= validation(**dict_config)
        logger.info('Sucess validation')
    except Exception as e:
        raise ValueError(f'There are problems in validating fields:\n{e}')
    
    # DataFrame
    frame= get_frame(file=config.data.path)
    
    # EDA JSON and TXT files
    dict_eda_files= EdaPipeline(
        frame=frame,
        config=config
        ).pipeline_eda()
    json_path= dict_eda_files['JSON_path']
    
    # Open JSON File
    with open(json_path, 'r', encoding='utf-8') as f: 
        file= json.load(f)
    
    path_cleaning= Path(__file__).parent/'config'/'cleaning'/'cleaning.yaml'
    cleaning_config= ReadConfig().read_config(
        frame=frame, 
        config=config, 
        path_config=path_cleaning
    )
    
    X, Y= CleanDataFrame(
        frame=frame, 
        config_cleaning=cleaning_config, 
        config=config,
        JSON=file
    ).clean_dataframe()
    
    test_size= config.data.training.test_size
    random_state= config.data.training.random_state
    shuffle= config.data.training.shuffle
    
    path_preprocessing= Path(__file__).parent/'config'/'preprocessing'/'preprocessing.yaml'
    preprocessing= ReadConfig().read_config(
        frame=X, 
        config=config, 
        path_config=path_preprocessing
    )
    
    x_train, x_test, y_train, y_test= train_test_split(
        X, Y, random_state=random_state, test_size=test_size, shuffle=shuffle
    )
    
    c_preprocessing= Pipeline(
        frame=X, 
        analysis=file, 
        config=preprocessing, 
        config_threshold_preprocessing=config
    )
    
    preprocessing_dict= c_preprocessing.fit_transform_expression(
        x_train= x_train, 
        y_train= y_train, 
        x_test=x_test
    )
    
    print(preprocessing_dict)
    


if __name__ == '__main__':
    main()


