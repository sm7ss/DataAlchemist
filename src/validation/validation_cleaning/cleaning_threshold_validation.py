from pydantic import BaseModel

class config_cleaning(BaseModel): 
    rows_percent: int
    columns_percent: int
