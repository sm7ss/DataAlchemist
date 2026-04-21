from src.validation.read_validation import ReadConfig
from src.eda.pipeline_eda import EdaPipeline

config= ReadConfig().read_config()

config_var= config['config_vars']
config= config['config']

EdaPipeline(config=config, config_var=config_var).pipeline_eda()
