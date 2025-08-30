#!/usr/bin/env python3

import shutil
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class DatasetCleaner:
    def __init__(self):
        self._raw_data_dir = Path("data/raw/datasets")
        
    def run(self, action, dataset_name=None):
        """Execute cleanup action"""
        match action:
            case "list":
                return self._list_datasets()
            case "delete_specific":
                if not dataset_name:
                    logger.error("Dataset name required for specific deletion")
                    return False
                return self._delete_specific(dataset_name)
            case "delete_all":
                return self._delete_all()
            case _:
                logger.error("Invalid action. Use: list, delete_specific, delete_all")
                return False
                
    def _list_datasets(self):
        """List available datasets"""
        if not self._raw_data_dir.exists():
            logger.info("No datasets directory found")
            return True
            
        datasets = [d.name for d in self._raw_data_dir.iterdir() if d.is_dir()]
        
        if not datasets:
            logger.info("No datasets found")
        else:
            logger.info("Available datasets:")
            for dataset in datasets:
                logger.info(f"  - {dataset}")
        return True
        
    def _delete_specific(self, dataset_name):
        """Delete specific dataset with confirmation"""
        dataset_folder = self._get_dataset_folder(dataset_name)
        
        if not dataset_folder.exists():
            logger.warning(f"Dataset {dataset_name} not found")
            return False
            
        confirmation = input(f"Are you sure you want to delete dataset '{dataset_name}'? (y/N): ")
        if confirmation.lower() != 'y':
            logger.info("Deletion cancelled")
            return False
            
        self._remove_dataset(dataset_folder, dataset_name)
        logger.info(f"Dataset {dataset_name} successfully deleted")
        return True
        
    def _delete_all(self):
        """Delete all datasets with confirmation"""
        if not self._raw_data_dir.exists():
            logger.info("No datasets directory found")
            return True
            
        datasets = [d for d in self._raw_data_dir.iterdir() if d.is_dir()]
        
        if not datasets:
            logger.info("No datasets found to delete")
            return True
            
        logger.info(f"Found {len(datasets)} datasets to delete:")
        for dataset in datasets:
            logger.info(f"  - {dataset.name}")
            
        confirmation = input(f"Are you sure you want to delete ALL {len(datasets)} datasets? (y/N): ")
        if confirmation.lower() != 'y':
            logger.info("Deletion cancelled")
            return False
            
        for dataset_folder in datasets:
            self._remove_dataset(dataset_folder, dataset_folder.name)
            
        logger.info("All datasets successfully deleted")
        return True
        
    def _get_dataset_folder(self, dataset_name):
        """Get dataset folder path"""
        return self._raw_data_dir / dataset_name
        
    def _remove_dataset(self, dataset_folder, dataset_name):
        """Remove dataset folder and all contents"""
        logger.info(f"Deleting dataset {dataset_name}...")
        shutil.rmtree(dataset_folder)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        logger.error("Usage: python dataset.py <action> [dataset_name]")
        logger.error("Actions: list, delete_specific, delete_all")
        sys.exit(1)
    
    action = sys.argv[1]
    dataset_name = sys.argv[2] if len(sys.argv) > 2 else None
    
    cleaner = DatasetCleaner()
    if not cleaner.run(action, dataset_name):
        sys.exit(1)