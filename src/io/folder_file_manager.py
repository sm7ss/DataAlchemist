from typing import Dict, Any
from pathlib import Path
from datetime import datetime

import json
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s-&(levelname)s-%(message)s')
logger= logging.getLogger(__name__)

class FolderAndFile: 
    def __init__(self):
        self.main_path= Path(__file__).resolve().parent.parent.parent
    
    def folder_analysis(self) -> Path: 
        folder= 'eda_analysis'
        path= self.main_path / folder
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def folder_date(self) -> Path: 
        now= datetime.now().strftime('%Y-%m-%d')
        folder= f'analysis_{now}'
        path= self.folder_analysis() / folder
        path.mkdir(parents=True, exist_ok=True)
        return path
    
    def create_json(self, json_dict: Dict[str, Any], json_name: str='JSON_analysis.json') -> Path: 
        file_path= self.folder_date() / json_name
        
        try: 
            with open(file_path, 'w', encoding='utf-8') as f: 
                json.dump(json_dict, f, indent=4, ensure_ascii=False)
                logger.info(f'Json report was written succesfully')
            return file_path
        except json.JSONDecodeError: 
            logger.error(f'The JSON file "{file_path.name}" is corrputed')
            raise ValueError(f'The JSON file "{file_path.name}" is corrputed')
        except Exception as e: 
            logger.error(f'An error ocurred: {e}')
            raise ValueError(f'An error ocurred: {e}')
    
    def create_txt(self, report: str, report_name: str='TXT_report.txt') -> Path: 
        file_path= self.folder_date() / report_name
        
        try: 
            with open(file_path, 'w', encoding='utf-8') as f: 
                f.write(report)
                logger.info(f'The file {file_path.name} was created succesfully')
            return file_path
        except Exception as e: 
            logger.error(f'An error ocurred: {e}')
            raise ValueError(f'An error ocurred: {e}')


