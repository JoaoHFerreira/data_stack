import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
import tempfile
import shutil

from src.ingestion.kaggle import KaggleDatasetDownloader


class TestKaggleDatasetDownloader:
    @pytest.fixture
    def downloader(self):
        return KaggleDatasetDownloader()
    
    @pytest.fixture
    def temp_dir(self):
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_downloader_with_temp_dir(self, temp_dir):
        downloader = KaggleDatasetDownloader()
        downloader._raw_data_dir = temp_dir / "raw" / "datasets"
        return downloader
    
    def test_init(self, downloader):
        assert downloader._raw_data_dir == Path("data/raw/datasets")
    
    @patch('src.ingestion.kaggle.kaggle.api.competition_download_files')
    @patch('src.ingestion.kaggle.zipfile.ZipFile')
    def test_run_success(self, mock_zipfile, mock_download, mock_downloader_with_temp_dir):
        # Setup
        dataset_name = "titanic"
        downloader = mock_downloader_with_temp_dir
        
        # Mock zip file existence and extraction
        zip_path = downloader._get_dataset_folder(dataset_name) / f"{dataset_name}.zip"
        zip_path.parent.mkdir(parents=True, exist_ok=True)
        zip_path.touch()
        
        mock_zip_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
        
        # Execute
        result = downloader.run(dataset_name)
        
        # Assert
        assert result is True
        mock_download.assert_called_once()
        mock_zip_instance.extractall.assert_called_once()
        assert not zip_path.exists()  # Should be cleaned up
    
    def test_create_directories(self, mock_downloader_with_temp_dir):
        dataset_name = "titanic"
        downloader = mock_downloader_with_temp_dir
        
        downloader._create_directories(dataset_name)
        
        assert downloader._raw_data_dir.exists()
        assert downloader._get_dataset_folder(dataset_name).exists()
    
    @patch('src.ingestion.kaggle.kaggle.api.competition_download_files')
    def test_download_dataset(self, mock_download, mock_downloader_with_temp_dir):
        dataset_name = "titanic"
        downloader = mock_downloader_with_temp_dir
        downloader._create_directories(dataset_name)
        
        downloader._download_dataset(dataset_name)
        
        mock_download.assert_called_once_with(
            dataset_name, 
            path=str(downloader._get_dataset_folder(dataset_name)), 
            quiet=False
        )
    
    @patch('src.ingestion.kaggle.zipfile.ZipFile')
    def test_extract_dataset_success(self, mock_zipfile, mock_downloader_with_temp_dir):
        dataset_name = "titanic"
        downloader = mock_downloader_with_temp_dir
        downloader._create_directories(dataset_name)
        
        # Create mock zip file
        zip_path = downloader._get_zip_file(dataset_name)
        zip_path.touch()
        
        mock_zip_instance = MagicMock()
        mock_zipfile.return_value.__enter__.return_value = mock_zip_instance
        
        downloader._extract_dataset(dataset_name)
        
        mock_zip_instance.extractall.assert_called_once()
    
    def test_extract_dataset_file_not_found(self, mock_downloader_with_temp_dir):
        dataset_name = "nonexistent"
        downloader = mock_downloader_with_temp_dir
        
        result = downloader._extract_dataset(dataset_name)
        
        assert result is False
    
    def test_cleanup_zip(self, mock_downloader_with_temp_dir):
        dataset_name = "titanic"
        downloader = mock_downloader_with_temp_dir
        downloader._create_directories(dataset_name)
        
        # Create zip file
        zip_path = downloader._get_zip_file(dataset_name)
        zip_path.touch()
        assert zip_path.exists()
        
        downloader._cleanup_zip(dataset_name)
        
        assert not zip_path.exists()
    
    def test_get_dataset_folder(self, downloader):
        dataset_name = "titanic"
        expected = Path("data/raw/datasets") / dataset_name
        
        result = downloader._get_dataset_folder(dataset_name)
        
        assert result == expected
    
    def test_get_zip_file(self, downloader):
        dataset_name = "titanic"
        expected = Path("data/raw/datasets") / dataset_name / f"{dataset_name}.zip"
        
        result = downloader._get_zip_file(dataset_name)
        
        assert result == expected