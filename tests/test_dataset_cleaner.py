import pytest
from pathlib import Path
from unittest.mock import patch
import tempfile
import shutil

from src.cleanup.dataset import DatasetCleaner


class TestDatasetCleaner:
    @pytest.fixture
    def cleaner(self):
        return DatasetCleaner()
    
    @pytest.fixture
    def temp_dir(self):
        temp_dir = Path(tempfile.mkdtemp())
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_cleaner_with_temp_dir(self, temp_dir):
        cleaner = DatasetCleaner()
        cleaner._raw_data_dir = temp_dir / "raw" / "datasets"
        return cleaner
    
    @pytest.fixture
    def setup_test_datasets(self, mock_cleaner_with_temp_dir):
        cleaner = mock_cleaner_with_temp_dir
        # Create test datasets
        cleaner._raw_data_dir.mkdir(parents=True, exist_ok=True)
        (cleaner._raw_data_dir / "titanic").mkdir()
        (cleaner._raw_data_dir / "iris").mkdir()
        return cleaner
    
    def test_init(self, cleaner):
        assert cleaner._raw_data_dir == Path("data/raw/datasets")
    
    def test_run_list_action(self, setup_test_datasets):
        cleaner = setup_test_datasets
        
        result = cleaner.run("list")
        
        assert result is True
    
    def test_run_delete_specific_action(self, setup_test_datasets):
        cleaner = setup_test_datasets
        
        with patch('builtins.input', return_value='y'):
            result = cleaner.run("delete_specific", "titanic")
        
        assert result is True
        assert not (cleaner._raw_data_dir / "titanic").exists()
    
    def test_run_delete_all_action(self, setup_test_datasets):
        cleaner = setup_test_datasets
        
        with patch('builtins.input', return_value='y'):
            result = cleaner.run("delete_all")
        
        assert result is True
        assert not (cleaner._raw_data_dir / "titanic").exists()
        assert not (cleaner._raw_data_dir / "iris").exists()
    
    def test_run_invalid_action(self, cleaner):
        result = cleaner.run("invalid_action")
        
        assert result is False
    
    def test_run_delete_specific_missing_dataset_name(self, cleaner):
        result = cleaner.run("delete_specific")
        
        assert result is False
    
    def test_list_datasets_no_directory(self, mock_cleaner_with_temp_dir):
        cleaner = mock_cleaner_with_temp_dir
        
        result = cleaner._list_datasets()
        
        assert result is True
    
    def test_list_datasets_empty_directory(self, mock_cleaner_with_temp_dir):
        cleaner = mock_cleaner_with_temp_dir
        cleaner._raw_data_dir.mkdir(parents=True, exist_ok=True)
        
        result = cleaner._list_datasets()
        
        assert result is True
    
    def test_list_datasets_with_datasets(self, setup_test_datasets):
        cleaner = setup_test_datasets
        
        result = cleaner._list_datasets()
        
        assert result is True
    
    def test_delete_specific_dataset_not_found(self, mock_cleaner_with_temp_dir):
        cleaner = mock_cleaner_with_temp_dir
        
        result = cleaner._delete_specific("nonexistent")
        
        assert result is False
    
    def test_delete_specific_cancelled(self, setup_test_datasets):
        cleaner = setup_test_datasets
        
        with patch('builtins.input', return_value='n'):
            result = cleaner._delete_specific("titanic")
        
        assert result is False
        assert (cleaner._raw_data_dir / "titanic").exists()  # Should still exist
    
    def test_delete_specific_confirmed(self, setup_test_datasets):
        cleaner = setup_test_datasets
        
        with patch('builtins.input', return_value='y'):
            result = cleaner._delete_specific("titanic")
        
        assert result is True
        assert not (cleaner._raw_data_dir / "titanic").exists()
    
    def test_delete_all_no_directory(self, mock_cleaner_with_temp_dir):
        cleaner = mock_cleaner_with_temp_dir
        
        result = cleaner._delete_all()
        
        assert result is True
    
    def test_delete_all_empty_directory(self, mock_cleaner_with_temp_dir):
        cleaner = mock_cleaner_with_temp_dir
        cleaner._raw_data_dir.mkdir(parents=True, exist_ok=True)
        
        result = cleaner._delete_all()
        
        assert result is True
    
    def test_delete_all_cancelled(self, setup_test_datasets):
        cleaner = setup_test_datasets
        
        with patch('builtins.input', return_value='n'):
            result = cleaner._delete_all()
        
        assert result is False
        assert (cleaner._raw_data_dir / "titanic").exists()
        assert (cleaner._raw_data_dir / "iris").exists()
    
    def test_delete_all_confirmed(self, setup_test_datasets):
        cleaner = setup_test_datasets
        
        with patch('builtins.input', return_value='y'):
            result = cleaner._delete_all()
        
        assert result is True
        assert not (cleaner._raw_data_dir / "titanic").exists()
        assert not (cleaner._raw_data_dir / "iris").exists()
    
    def test_get_dataset_folder(self, cleaner):
        dataset_name = "titanic"
        expected = Path("data/raw/datasets") / dataset_name
        
        result = cleaner._get_dataset_folder(dataset_name)
        
        assert result == expected
    
    @patch('src.cleanup.dataset.shutil.rmtree')
    def test_remove_dataset(self, mock_rmtree, setup_test_datasets):
        cleaner = setup_test_datasets
        dataset_folder = cleaner._raw_data_dir / "titanic"
        
        cleaner._remove_dataset(dataset_folder, "titanic")
        
        mock_rmtree.assert_called_once_with(dataset_folder)