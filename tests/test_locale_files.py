import pytest
import os
import tempfile
import shutil
import json
from unittest.mock import patch
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from ovos_dialog_normalizer_plugin.util import LocaleDataManager, load_locale_file


class TestLocaleFiles:
    """
    Comprehensive unit tests for locale files functionality.
    Testing framework: pytest
    
    Tests cover locale file validation, JSON structure verification,
    locale data loading, and integration with LocaleDataManager.
    """
    
    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.temp_dir = tempfile.mkdtemp()
        self.test_locale_dir = os.path.join(self.temp_dir, 'locale')
        os.makedirs(self.test_locale_dir, exist_ok=True)
        
        # Reference to actual project locale directory
        self.project_locale_dir = os.path.join(
            os.path.dirname(os.path.dirname(__file__)), 
            'ovos_dialog_normalizer_plugin', 
            'locale'
        )
        
        # Existing locales found in the project
        self.existing_locales = ['ca', 'de', 'en', 'es', 'fr', 'gl', 'it', 'nl', 'pt']
        
        # Known file types in the project
        self.known_file_types = ['titles.json', 'units.json', 'contractions.json']
        
    def teardown_method(self):
        """Clean up test fixtures after each test method."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_project_locale_directory_exists(self):
        """Test that the project locale directory exists."""
        assert os.path.exists(self.project_locale_dir), \
            f"Project locale directory should exist at {self.project_locale_dir}"
        assert os.path.isdir(self.project_locale_dir), \
            "Project locale path should be a directory"
    
    def test_existing_locale_directories_structure(self):
        """Test structure of existing locale directories in the project."""
        if os.path.exists(self.project_locale_dir):
            # Get all subdirectories in locale directory
            subdirs = [
                d for d in os.listdir(self.project_locale_dir)
                if os.path.isdir(os.path.join(self.project_locale_dir, d))
            ]
            
            # Verify we have expected locale directories
            assert len(subdirs) > 0, "Should have at least one locale subdirectory"
            
            # Test that subdirectories follow expected naming convention
            for subdir in subdirs:
                assert len(subdir) == 2, f"Locale directory '{subdir}' should be 2 characters"
                assert subdir.islower(), f"Locale directory '{subdir}' should be lowercase"
    
    def test_locale_file_types_validation(self):
        """Test validation of existing locale file types."""
        if os.path.exists(self.project_locale_dir):
            for locale in self.existing_locales:
                locale_path = os.path.join(self.project_locale_dir, locale)
                if os.path.exists(locale_path):
                    files = os.listdir(locale_path)
                    
                    # Check that files follow expected naming patterns
                    for file in files:
                        assert file.endswith('.json'), f"File {file} should be a JSON file"
                        assert file in self.known_file_types, \
                            f"Unknown file type: {file} in locale {locale}"
    
    def test_locale_json_files_validity(self):
        """Test that all existing locale JSON files are valid."""
        if os.path.exists(self.project_locale_dir):
            for locale in self.existing_locales:
                locale_path = os.path.join(self.project_locale_dir, locale)
                if os.path.exists(locale_path):
                    for file_type in self.known_file_types:
                        file_path = os.path.join(locale_path, file_type)
                        if os.path.exists(file_path):
                            with open(file_path, 'r', encoding='utf-8') as f:
                                try:
                                    data = json.load(f)
                                    assert isinstance(data, (dict, list)), \
                                        f"File {file_path} should contain valid JSON data"
                                except json.JSONDecodeError as e:
                                    pytest.fail(f"Invalid JSON in {file_path}: {e}")
    
    def test_titles_json_structure(self):
        """Test structure of titles.json files."""
        if os.path.exists(self.project_locale_dir):
            for locale in self.existing_locales:
                titles_file = os.path.join(self.project_locale_dir, locale, 'titles.json')
                if os.path.exists(titles_file):
                    with open(titles_file, 'r', encoding='utf-8') as f:
                        titles_data = json.load(f)
                    
                    # Titles should be a dictionary or list
                    assert isinstance(titles_data, (dict, list)), \
                        f"titles.json in {locale} should be dict or list"
                    
                    if isinstance(titles_data, dict):
                        # Check that all values are strings
                        for key, value in titles_data.items():
                            assert isinstance(key, str), f"Title key should be string in {locale}"
                            assert isinstance(value, str), f"Title value should be string in {locale}"
    
    def test_units_json_structure(self):
        """Test structure of units.json files."""
        if os.path.exists(self.project_locale_dir):
            for locale in self.existing_locales:
                units_file = os.path.join(self.project_locale_dir, locale, 'units.json')
                if os.path.exists(units_file):
                    with open(units_file, 'r', encoding='utf-8') as f:
                        units_data = json.load(f)
                    
                    # Units should be a dictionary or list
                    assert isinstance(units_data, (dict, list)), \
                        f"units.json in {locale} should be dict or list"
                    
                    if isinstance(units_data, dict):
                        # Check that all values are appropriate types
                        for key, value in units_data.items():
                            assert isinstance(key, str), f"Unit key should be string in {locale}"
                            assert isinstance(value, (str, list, dict)), \
                                f"Unit value should be string, list or dict in {locale}"
    
    def test_contractions_json_structure(self):
        """Test structure of contractions.json files."""
        if os.path.exists(self.project_locale_dir):
            for locale in self.existing_locales:
                contractions_file = os.path.join(self.project_locale_dir, locale, 'contractions.json')
                if os.path.exists(contractions_file):
                    with open(contractions_file, 'r', encoding='utf-8') as f:
                        contractions_data = json.load(f)
                    
                    # Contractions should be a dictionary
                    assert isinstance(contractions_data, dict), \
                        f"contractions.json in {locale} should be dict"
                    
                    # Check that all keys and values are strings
                    for key, value in contractions_data.items():
                        assert isinstance(key, str), f"Contraction key should be string in {locale}"
                        assert isinstance(value, str), f"Contraction value should be string in {locale}"
    
    def test_locale_data_manager_initialization(self):
        """Test LocaleDataManager initialization."""
        manager = LocaleDataManager()
        assert hasattr(manager, 'cache'), "LocaleDataManager should have cache attribute"
        assert isinstance(manager.cache, dict), "Cache should be a dictionary"
    
    def test_locale_data_manager_file_loading(self):
        """Test LocaleDataManager file loading functionality."""
        # Create test data
        test_data = {"test_key": "test_value", "another_key": "another_value"}
        test_file = os.path.join(self.test_locale_dir, 'en', 'test.json')
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        # Mock the RESOURCES_DIR to point to our test directory
        with patch('ovos_dialog_normalizer_plugin.util.RESOURCES_DIR', self.test_locale_dir):
            manager = LocaleDataManager()
            loaded_data = manager.get('en', 'test')
            
            assert loaded_data == test_data, "Loaded data should match original data"
    
    def test_locale_data_manager_caching(self):
        """Test LocaleDataManager caching behavior."""
        # Create test data
        test_data = {"cached_key": "cached_value"}
        test_file = os.path.join(self.test_locale_dir, 'es', 'cache_test.json')
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        with patch('ovos_dialog_normalizer_plugin.util.RESOURCES_DIR', self.test_locale_dir):
            manager = LocaleDataManager()
            
            # First load
            data1 = manager.get('es', 'cache_test')
            
            # Second load should use cache
            data2 = manager.get('es', 'cache_test')
            
            assert data1 == data2, "Cached data should be identical"
            assert ('es', 'cache_test') in manager.cache, "Data should be cached"
    
    def test_load_locale_file_function(self):
        """Test the load_locale_file function directly."""
        # Create test data
        test_data = {"function_test": "value"}
        test_file = os.path.join(self.test_locale_dir, 'fr', 'function_test.json')
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        with patch('ovos_dialog_normalizer_plugin.util.RESOURCES_DIR', self.test_locale_dir):
            loaded_data = load_locale_file('fr', 'function_test')
            assert loaded_data == test_data, "Function should load data correctly"
    
    def test_locale_file_encoding_utf8(self):
        """Test that locale files handle UTF-8 encoding properly."""
        # Create test data with international characters
        test_data = {
            "english": "Hello",
            "spanish": "Hola",
            "french": "Bonjour",
            "german": "Hallo",
            "russian": "Привет",
            "chinese": "你好",
            "japanese": "こんにちは",
            "arabic": "مرحبا"
        }
        
        test_file = os.path.join(self.test_locale_dir, 'multi', 'utf8_test.json')
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        
        # Write with UTF-8 encoding
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        # Read back and verify
        with open(test_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
        
        assert loaded_data == test_data, "UTF-8 characters should be preserved"
    
    def test_locale_file_error_handling(self):
        """Test error handling for missing or invalid locale files."""
        with patch('ovos_dialog_normalizer_plugin.util.RESOURCES_DIR', self.test_locale_dir):
            manager = LocaleDataManager()
            
            # Test missing file
            result = manager.get('nonexistent', 'missing_file')
            assert result == {}, "Missing file should return empty dict"
            
            # Test invalid JSON file
            invalid_file = os.path.join(self.test_locale_dir, 'invalid', 'bad.json')
            os.makedirs(os.path.dirname(invalid_file), exist_ok=True)
            
            with open(invalid_file, 'w') as f:
                f.write('{"invalid": json content}')  # Missing closing brace
            
            result = manager.get('invalid', 'bad')
            assert result == {}, "Invalid JSON should return empty dict"
    
    def test_locale_consistency_across_languages(self):
        """Test consistency of locale file structure across languages."""
        # Create consistent structure for multiple locales
        base_structure = {
            "common_key1": "value1",
            "common_key2": "value2",
            "nested": {
                "sub_key": "sub_value"
            }
        }
        
        test_locales = ['en', 'es', 'fr']
        for locale in test_locales:
            locale_dir = os.path.join(self.test_locale_dir, locale)
            os.makedirs(locale_dir, exist_ok=True)
            
            test_file = os.path.join(locale_dir, 'consistent.json')
            with open(test_file, 'w', encoding='utf-8') as f:
                json.dump(base_structure, f)
        
        # Verify all files have the same structure
        with patch('ovos_dialog_normalizer_plugin.util.RESOURCES_DIR', self.test_locale_dir):
            manager = LocaleDataManager()
            
            reference_keys = None
            for locale in test_locales:
                data = manager.get(locale, 'consistent')
                current_keys = set(data.keys())
                
                if reference_keys is None:
                    reference_keys = current_keys
                else:
                    assert current_keys == reference_keys, \
                        f"Locale {locale} should have same keys as reference"
    
    def test_locale_file_permissions(self):
        """Test that locale files have proper read permissions."""
        if os.path.exists(self.project_locale_dir):
            for root, _dirs, files in os.walk(self.project_locale_dir):
                for file in files:
                    if file.endswith('.json'):
                        file_path = os.path.join(root, file)
                        assert os.access(file_path, os.R_OK), \
                            f"File {file_path} should be readable"
    
    def test_locale_directory_permissions(self):
        """Test that locale directories have proper permissions."""
        if os.path.exists(self.project_locale_dir):
            # Test main locale directory
            assert os.access(self.project_locale_dir, os.R_OK), \
                "Main locale directory should be readable"
            assert os.access(self.project_locale_dir, os.X_OK), \
                "Main locale directory should be executable"
            
            # Test subdirectories
            for locale in self.existing_locales:
                locale_path = os.path.join(self.project_locale_dir, locale)
                if os.path.exists(locale_path):
                    assert os.access(locale_path, os.R_OK), \
                        f"Locale directory {locale} should be readable"
                    assert os.access(locale_path, os.X_OK), \
                        f"Locale directory {locale} should be executable"
    
    def test_locale_file_size_reasonable(self):
        """Test that locale files have reasonable sizes."""
        if os.path.exists(self.project_locale_dir):
            for root, _dirs, files in os.walk(self.project_locale_dir):
                for file in files:
                    if file.endswith('.json'):
                        file_path = os.path.join(root, file)
                        file_size = os.path.getsize(file_path)
                        
                        # Files should not be empty
                        assert file_size > 0, f"File {file_path} should not be empty"
                        
                        # Files should not be unreasonably large (> 1MB)
                        assert file_size < 1024 * 1024, \
                            f"File {file_path} seems unreasonably large ({file_size} bytes)"
    
    def test_locale_data_types_validation(self):
        """Test validation of data types in locale files."""
        # Create test files with various data types
        test_cases = {
            'strings': {"key": "string_value"},
            'numbers': {"count": 42, "price": 19.99},
            'booleans': {"enabled": True, "visible": False},
            'arrays': {"items": ["item1", "item2", "item3"]},
            'nested': {"level1": {"level2": {"value": "nested_value"}}}
        }
        
        for test_name, test_data in test_cases.items():
            test_file = os.path.join(self.test_locale_dir, 'types', f'{test_name}.json')
            os.makedirs(os.path.dirname(test_file), exist_ok=True)
            
            with open(test_file, 'w', encoding='utf-8') as f:
                json.dump(test_data, f)
            
            # Verify data can be loaded and types are preserved
            with open(test_file, 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
            
            assert loaded_data == test_data, f"Data types should be preserved for {test_name}"
    
    def test_locale_backup_and_integrity(self):
        """Test locale file backup and integrity checking."""
        original_data = {"original": "data", "timestamp": "2024-01-01"}
        test_file = os.path.join(self.test_locale_dir, 'backup_test', 'data.json')
        backup_file = test_file + '.bak'
        
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        
        # Create original file
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(original_data, f)
        
        # Create backup
        shutil.copy2(test_file, backup_file)
        
        # Verify backup integrity
        with open(backup_file, 'r', encoding='utf-8') as f:
            backup_data = json.load(f)
        
        assert backup_data == original_data, "Backup should preserve original data"
        
        # Test recovery scenario
        with open(test_file, 'w') as f:
            f.write('corrupted')
        
        # Restore from backup
        shutil.copy2(backup_file, test_file)
        
        # Verify restoration
        with open(test_file, 'r', encoding='utf-8') as f:
            restored_data = json.load(f)
        
        assert restored_data == original_data, "Restored data should match original"


class TestLocaleFileIntegration:
    """
    Integration tests for locale file functionality.
    Tests the complete workflow and real-world usage scenarios.
    """
    
    def setup_method(self):
        """Set up integration test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.integration_locale_dir = os.path.join(self.temp_dir, 'integration_locale')
        os.makedirs(self.integration_locale_dir, exist_ok=True)
    
    def teardown_method(self):
        """Clean up integration test fixtures."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_complete_locale_workflow(self):
        """Test complete workflow from file creation to data usage."""
        # Simulate a complete locale setup
        locales = ['en', 'es', 'fr']
        file_types = ['titles', 'units', 'contractions']
        
        sample_data = {
            'titles': {"mr": "mister", "dr": "doctor", "ms": "miss"},
            'units': {"km": "kilometers", "kg": "kilograms", "l": "liters"},
            'contractions': {"don't": "do not", "can't": "cannot", "won't": "will not"}
        }
        
        # Create locale structure
        for locale in locales:
            locale_path = os.path.join(self.integration_locale_dir, locale)
            os.makedirs(locale_path, exist_ok=True)
            
            for file_type in file_types:
                file_path = os.path.join(locale_path, f'{file_type}.json')
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(sample_data[file_type], f, indent=2)
        
        # Test loading through LocaleDataManager
        with patch('ovos_dialog_normalizer_plugin.util.RESOURCES_DIR', self.integration_locale_dir):
            manager = LocaleDataManager()
            
            # Test data loading for each locale and file type
            for locale in locales:
                for file_type in file_types:
                    loaded_data = manager.get(locale, file_type)
                    assert loaded_data == sample_data[file_type], \
                        f"Data mismatch for {locale}/{file_type}"
    
    def test_locale_fallback_behavior(self):
        """Test fallback behavior when locale files are missing."""
        # Create only English locale
        en_path = os.path.join(self.integration_locale_dir, 'en')
        os.makedirs(en_path, exist_ok=True)
        
        test_data = {"fallback": "english_value"}
        with open(os.path.join(en_path, 'test.json'), 'w') as f:
            json.dump(test_data, f)
        
        with patch('ovos_dialog_normalizer_plugin.util.RESOURCES_DIR', self.integration_locale_dir):
            manager = LocaleDataManager()
            
            # Test existing locale
            en_data = manager.get('en', 'test')
            assert en_data == test_data, "English data should load correctly"
            
            # Test missing locale
            es_data = manager.get('es', 'test')
            assert es_data == {}, "Missing locale should return empty dict"
    
    def test_concurrent_locale_access(self):
        """Test concurrent access to locale files."""
        import threading
        
        # Create test data
        test_data = {"concurrent": "access_test"}
        test_file = os.path.join(self.integration_locale_dir, 'concurrent', 'test.json')
        os.makedirs(os.path.dirname(test_file), exist_ok=True)
        
        with open(test_file, 'w') as f:
            json.dump(test_data, f)
        
        results = []
        errors = []
        
        def load_data():
            try:
                with patch('ovos_dialog_normalizer_plugin.util.RESOURCES_DIR', self.integration_locale_dir):
                    manager = LocaleDataManager()
                    data = manager.get('concurrent', 'test')
                    results.append(data)
            except Exception as e:
                errors.append(e)
        
        # Create multiple threads
        threads = []
        for _ in range(5):
            thread = threading.Thread(target=load_data)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Verify results
        assert len(errors) == 0, f"No errors should occur during concurrent access: {errors}"
        assert len(results) == 5, "All threads should complete successfully"
        
        for result in results:
            assert result == test_data, "All results should be consistent"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])