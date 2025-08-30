#!/usr/bin/env python3

import sys
import zipfile
import logging
from pathlib import Path
import kaggle

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class KaggleDatasetDownloader:
    def __init__(self):
        self._raw_data_dir = Path("data/raw/datasets")
        
    def run(self, dataset_name):
        """Download, unzip, and organize Kaggle dataset"""
        self._create_directories(dataset_name)
        self._download_dataset(dataset_name)
        self._extract_dataset(dataset_name)
        self._cleanup_zip(dataset_name)
        logger.info(f"Dataset {dataset_name} successfully downloaded to {self._get_dataset_folder(dataset_name)}")
        return True
        
    def _create_directories(self, dataset_name):
        """Create necessary directories"""
        self._raw_data_dir.mkdir(parents=True, exist_ok=True)
        self._get_dataset_folder(dataset_name).mkdir(exist_ok=True)
        
    def _download_dataset(self, dataset_name):
        """Download dataset from Kaggle"""
        logger.info(f"Downloading {dataset_name} dataset...")
        kaggle.api.competition_download_files(dataset_name, path=str(self._get_dataset_folder(dataset_name)), quiet=False)
        
    def _extract_dataset(self, dataset_name):
        """Extract downloaded zip file"""
        zip_file = self._get_zip_file(dataset_name)
        if not zip_file.exists():
            logger.error(f"{zip_file} not found!")
            return False
            
        logger.info(f"Extracting {zip_file}...")
        with zipfile.ZipFile(zip_file, 'r') as zip_ref:
            zip_ref.extractall(self._get_dataset_folder(dataset_name))
            
    def _cleanup_zip(self, dataset_name):
        """Remove zip file after extraction"""
        self._get_zip_file(dataset_name).unlink()
        
    def _get_dataset_folder(self, dataset_name):
        """Get dataset folder path"""
        return self._raw_data_dir / dataset_name
        
    def _get_zip_file(self, dataset_name):
        """Get zip file path"""
        return self._get_dataset_folder(dataset_name) / f"{dataset_name}.zip"


if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.error("Usage: python kaggle.py <dataset_name>")
        sys.exit(1)
    
    dataset_name = sys.argv[1]
    downloader = KaggleDatasetDownloader()
    if not downloader.run(dataset_name):
        sys.exit(1)