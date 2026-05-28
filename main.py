from src.validation.read_validation import ReadConfig
from src.get_frame import get_frame
from src.eda.pipeline_eda import EdaPipeline
from src.cleaning.pipeline import CleanDataFrame
from src.ml_process.preprocessing.pipeline import AutoPipeline

import json

config= ReadConfig().read_config()

config_var= config['config_vars']
config_preprocessing= config['preprocessing']
config_modeling= config['modeling']
config_cleaning= config['cleaning']
config= config['config']

frame= get_frame(file=config.path.data)

dict_eda_files= EdaPipeline(frame=frame, config=config, config_var=config_var).pipeline_eda()
json_path= dict_eda_files['JSON_path']

with open(json_path, 'r', encoding='utf-8') as f: 
    file= json.load(f)

frame_cleaned= CleanDataFrame(
    frame=frame, 
    config=config, 
    config_clean=config_cleaning, 
    JSON=file
).clean_dataframe()

dict_eda_files= EdaPipeline(frame=frame_cleaned, config=config, config_var=config_var).pipeline_eda()
json_path= dict_eda_files['JSON_path']

with open(json_path, 'r', encoding='utf-8') as f: 
    file= json.load(f)

frame= frame.with_row_index()

preprocessing= AutoPipeline(frame=frame, analysis=file, config=config, config_pre=config_preprocessing)

pre_processing_frame= preprocessing.auto_frame_tests()


