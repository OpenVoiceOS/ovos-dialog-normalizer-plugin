import unittest
import sys
import os

# Add the project root to the Python path to import the version module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Import the version constants from the actual location
from ovos_dialog_normalizer_plugin.version import VERSION_MAJOR, VERSION_MINOR, VERSION_BUILD, VERSION_ALPHA


class TestVersionConstants(unittest.TestCase):
    """Test suite for version constants validation."""
    
    def test_version_major_is_integer(self):
        """Test that VERSION_MAJOR is an integer."""
        self.assertIsInstance(VERSION_MAJOR, int, "VERSION_MAJOR must be an integer")
    
    def test_version_minor_is_integer(self):
        """Test that VERSION_MINOR is an integer."""
        self.assertIsInstance(VERSION_MINOR, int, "VERSION_MINOR must be an integer")
    
    def test_version_build_is_integer(self):
        """Test that VERSION_BUILD is an integer."""
        self.assertIsInstance(VERSION_BUILD, int, "VERSION_BUILD must be an integer")
    
    def test_version_alpha_is_integer(self):
        """Test that VERSION_ALPHA is an integer."""
        self.assertIsInstance(VERSION_ALPHA, int, "VERSION_ALPHA must be an integer")
    
    def test_version_major_non_negative(self):
        """Test that VERSION_MAJOR is non-negative."""
        self.assertGreaterEqual(VERSION_MAJOR, 0, "VERSION_MAJOR must be non-negative")
    
    def test_version_minor_non_negative(self):
        """Test that VERSION_MINOR is non-negative."""
        self.assertGreaterEqual(VERSION_MINOR, 0, "VERSION_MINOR must be non-negative")
    
    def test_version_build_non_negative(self):
        """Test that VERSION_BUILD is non-negative."""
        self.assertGreaterEqual(VERSION_BUILD, 0, "VERSION_BUILD must be non-negative")
    
    def test_version_alpha_non_negative(self):
        """Test that VERSION_ALPHA is non-negative."""
        self.assertGreaterEqual(VERSION_ALPHA, 0, "VERSION_ALPHA must be non-negative")
    
    def test_current_version_values(self):
        """Test the current specific version values."""
        self.assertEqual(VERSION_MAJOR, 0, "Expected VERSION_MAJOR to be 0")
        self.assertEqual(VERSION_MINOR, 0, "Expected VERSION_MINOR to be 0")
        self.assertEqual(VERSION_BUILD, 1, "Expected VERSION_BUILD to be 1")
        self.assertEqual(VERSION_ALPHA, 0, "Expected VERSION_ALPHA to be 0")
    
    def test_version_consistency(self):
        """Test version consistency rules."""
        # Alpha versions should typically have a build number
        if VERSION_ALPHA > 0:
            self.assertGreaterEqual(VERSION_BUILD, 0, "Alpha versions should have a valid build number")
        
        # Major version 0 indicates pre-release
        if VERSION_MAJOR == 0:
            self.assertGreaterEqual(VERSION_MINOR, 0, "Pre-release versions should have valid minor version")
    
    def test_version_string_formation(self):
        """Test that version components can form a valid version string."""
        version_string = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_BUILD}"
        
        # Basic format validation
        parts = version_string.split('.')
        self.assertEqual(len(parts), 3, "Version string should have 3 parts")
        
        # Each part should be numeric
        for part in parts:
            self.assertTrue(part.isdigit(), f"Version part '{part}' should be numeric")
    
    def test_version_string_with_alpha(self):
        """Test version string formation including alpha designation."""
        if VERSION_ALPHA > 0:
            alpha_version = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_BUILD}-alpha.{VERSION_ALPHA}"
            self.assertIn("alpha", alpha_version, "Alpha version should contain 'alpha' designation")
        else:
            stable_version = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_BUILD}"
            self.assertNotIn("alpha", stable_version, "Stable version should not contain 'alpha'")
    
    def test_semantic_versioning_compliance(self):
        """Test compliance with semantic versioning principles."""
        # Test that the version follows semantic versioning format
        version = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_BUILD}"
        
        # Should be parseable as semantic version
        parts = [int(x) for x in version.split('.')]
        self.assertEqual(len(parts), 3, "Should have exactly 3 version components")
        self.assertTrue(all(x >= 0 for x in parts), "All version components should be non-negative")
    
    def test_version_comparison_logic(self):
        """Test version comparison scenarios."""
        current_version = (VERSION_MAJOR, VERSION_MINOR, VERSION_BUILD, VERSION_ALPHA)
        
        # Test against some hypothetical versions
        newer_major = (VERSION_MAJOR + 1, 0, 0, 0)
        newer_minor = (VERSION_MAJOR, VERSION_MINOR + 1, 0, 0)
        newer_build = (VERSION_MAJOR, VERSION_MINOR, VERSION_BUILD + 1, 0)
        
        self.assertLess(current_version, newer_major, "Current version should be less than newer major")
        self.assertLess(current_version, newer_minor, "Current version should be less than newer minor")
        self.assertLess(current_version, newer_build, "Current version should be less than newer build")
    
    def test_version_constants_immutable(self):
        """Test that version constants maintain their expected immutability."""
        # This tests that the constants are defined and accessible
        original_major = VERSION_MAJOR
        original_minor = VERSION_MINOR
        original_build = VERSION_BUILD
        original_alpha = VERSION_ALPHA
        
        # Verify they haven't changed during test execution
        self.assertEqual(VERSION_MAJOR, original_major)
        self.assertEqual(VERSION_MINOR, original_minor)
        self.assertEqual(VERSION_BUILD, original_build)
        self.assertEqual(VERSION_ALPHA, original_alpha)
    
    def test_version_range_validity(self):
        """Test that version numbers are within reasonable ranges."""
        # Version components should be reasonable (not absurdly large)
        self.assertLessEqual(VERSION_MAJOR, 99, "VERSION_MAJOR should be reasonable (<=99)")
        self.assertLessEqual(VERSION_MINOR, 999, "VERSION_MINOR should be reasonable (<=999)")
        self.assertLessEqual(VERSION_BUILD, 9999, "VERSION_BUILD should be reasonable (<=9999)")
        self.assertLessEqual(VERSION_ALPHA, 99, "VERSION_ALPHA should be reasonable (<=99)")
    
    def test_development_version_indicators(self):
        """Test development version indicators."""
        # Version 0.0.1 typically indicates early development
        if VERSION_MAJOR == 0 and VERSION_MINOR == 0:
            self.assertGreater(VERSION_BUILD, 0, "Development versions should have positive build number")


class TestVersionUtilities(unittest.TestCase):
    """Test suite for version utility functions."""
    
    def test_get_version_string(self):
        """Test version string generation utility."""
        def get_version_string():
            if VERSION_ALPHA > 0:
                return f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_BUILD}-alpha.{VERSION_ALPHA}"
            return f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_BUILD}"
        
        version_str = get_version_string()
        self.assertIsInstance(version_str, str, "Version string should be a string")
        self.assertGreater(len(version_str), 0, "Version string should not be empty")
    
    def test_version_tuple(self):
        """Test version as tuple representation."""
        version_tuple = (VERSION_MAJOR, VERSION_MINOR, VERSION_BUILD, VERSION_ALPHA)
        
        self.assertEqual(len(version_tuple), 4, "Version tuple should have 4 components")
        self.assertTrue(all(isinstance(x, int) for x in version_tuple), "All components should be integers")
    
    def test_version_dict(self):
        """Test version as dictionary representation."""
        version_dict = {
            'major': VERSION_MAJOR,
            'minor': VERSION_MINOR,
            'build': VERSION_BUILD,
            'alpha': VERSION_ALPHA
        }
        
        self.assertEqual(len(version_dict), 4, "Version dict should have 4 keys")
        self.assertTrue(all(isinstance(v, int) for v in version_dict.values()), "All values should be integers")
    
    def test_is_prerelease(self):
        """Test prerelease version detection."""
        def is_prerelease():
            return VERSION_MAJOR == 0 or VERSION_ALPHA > 0
        
        prerelease_status = is_prerelease()
        
        # Current version 0.0.1 with alpha=0 should be considered prerelease due to major=0
        self.assertTrue(prerelease_status, "Version 0.0.1 should be considered prerelease")
    
    def test_is_stable(self):
        """Test stable version detection."""
        def is_stable():
            return VERSION_MAJOR > 0 and VERSION_ALPHA == 0
        
        stable_status = is_stable()
        
        # Current version should not be stable since major=0
        self.assertFalse(stable_status, "Version 0.0.1 should not be considered stable")


class TestVersionEdgeCases(unittest.TestCase):
    """Test suite for version edge cases and boundary conditions."""
    
    def test_zero_version_handling(self):
        """Test handling of zero version components."""
        # Test that zero values are handled correctly
        if VERSION_MAJOR == 0:
            self.assertTrue(True, "Zero major version is valid for development")
        if VERSION_MINOR == 0:
            self.assertTrue(True, "Zero minor version is valid")
        if VERSION_ALPHA == 0:
            self.assertTrue(True, "Zero alpha version indicates stable release")
    
    def test_version_string_parsing(self):
        """Test that version strings can be parsed back to components."""
        version_str = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_BUILD}"
        
        # Parse back to components
        parts = version_str.split('.')
        parsed_major = int(parts[0])
        parsed_minor = int(parts[1])
        parsed_build = int(parts[2])
        
        self.assertEqual(parsed_major, VERSION_MAJOR)
        self.assertEqual(parsed_minor, VERSION_MINOR)
        self.assertEqual(parsed_build, VERSION_BUILD)
    
    def test_version_ordering(self):
        """Test version ordering logic."""
        current = (VERSION_MAJOR, VERSION_MINOR, VERSION_BUILD)
        
        # Test some ordering scenarios
        self.assertLessEqual((0, 0, 0), current, "Current version should be >= 0.0.0")
        self.assertLessEqual(current, (99, 99, 99), "Current version should be <= 99.99.99")
        
        # Test equality
        same_version = (VERSION_MAJOR, VERSION_MINOR, VERSION_BUILD)
        self.assertEqual(current, same_version, "Version should equal itself")
    
    def test_version_block_integrity(self):
        """Test that version block structure is maintained."""
        # This test ensures the version block format is preserved
        # Read the actual file to verify the block structure
        version_file_path = os.path.join(
            os.path.dirname(__file__), 
            '..', 
            'ovos_dialog_normalizer_plugin', 
            'version.py'
        )
        
        if os.path.exists(version_file_path):
            with open(version_file_path, 'r') as f:
                content = f.read()
            
            # Check for version block markers
            self.assertIn('START_VERSION_BLOCK', content, "START_VERSION_BLOCK marker should be present")
            self.assertIn('END_VERSION_BLOCK', content, "END_VERSION_BLOCK marker should be present")
            
            # Check that all version constants are defined
            self.assertIn('VERSION_MAJOR', content, "VERSION_MAJOR should be defined in file")
            self.assertIn('VERSION_MINOR', content, "VERSION_MINOR should be defined in file")
            self.assertIn('VERSION_BUILD', content, "VERSION_BUILD should be defined in file")
            self.assertIn('VERSION_ALPHA', content, "VERSION_ALPHA should be defined in file")


class TestVersionIntegration(unittest.TestCase):
    """Test suite for version integration scenarios."""
    
    def test_version_import_from_module(self):
        """Test that version constants can be imported correctly."""
        # Test direct import
        from ovos_dialog_normalizer_plugin.version import VERSION_MAJOR, VERSION_MINOR, VERSION_BUILD, VERSION_ALPHA
        
        self.assertIsNotNone(VERSION_MAJOR)
        self.assertIsNotNone(VERSION_MINOR)
        self.assertIsNotNone(VERSION_BUILD)
        self.assertIsNotNone(VERSION_ALPHA)
    
    def test_version_module_attributes(self):
        """Test that version module has expected attributes."""
        import ovos_dialog_normalizer_plugin.version as version_module
        
        required_attrs = ['VERSION_MAJOR', 'VERSION_MINOR', 'VERSION_BUILD', 'VERSION_ALPHA']
        for attr in required_attrs:
            self.assertTrue(hasattr(version_module, attr), f"Version module should have {attr} attribute")
    
    def test_version_for_packaging(self):
        """Test version formatting for packaging systems."""
        # Test PEP 440 compatible version string
        def get_pep440_version():
            base_version = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_BUILD}"
            if VERSION_ALPHA > 0:
                return f"{base_version}a{VERSION_ALPHA}"
            return base_version
        
        pep440_version = get_pep440_version()
        
        # Basic PEP 440 validation
        import re
        pep440_pattern = r'^([1-9][0-9]*!)?(0|[1-9][0-9]*)(\.(0|[1-9][0-9]*))*((a|b|rc)(0|[1-9][0-9]*))?(\.post(0|[1-9][0-9]*))?(\.dev(0|[1-9][0-9]*))?$'
        self.assertIsNotNone(re.match(pep440_pattern, pep440_version), 
                           f"Version {pep440_version} should be PEP 440 compatible")
    
    def test_version_for_semantic_versioning(self):
        """Test version formatting for semantic versioning."""
        # Test semantic versioning format
        def get_semver():
            base = f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_BUILD}"
            if VERSION_ALPHA > 0:
                return f"{base}-alpha.{VERSION_ALPHA}"
            return base
        
        semver = get_semver()
        
        # Basic semver validation
        import re
        semver_pattern = r'^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$'
        self.assertIsNotNone(re.match(semver_pattern, semver), 
                           f"Version {semver} should be semantic version compatible")


class TestVersionBoundaryConditions(unittest.TestCase):
    """Test suite for version boundary conditions and stress tests."""
    
    def test_version_component_boundaries(self):
        """Test version components at their boundaries."""
        # Test that current values are within expected boundaries
        self.assertGreaterEqual(VERSION_MAJOR, 0)
        self.assertLess(VERSION_MAJOR, 1000)  # Reasonable upper bound
        
        self.assertGreaterEqual(VERSION_MINOR, 0)
        self.assertLess(VERSION_MINOR, 1000)  # Reasonable upper bound
        
        self.assertGreaterEqual(VERSION_BUILD, 0)
        self.assertLess(VERSION_BUILD, 10000)  # Reasonable upper bound
        
        self.assertGreaterEqual(VERSION_ALPHA, 0)
        self.assertLess(VERSION_ALPHA, 1000)  # Reasonable upper bound
    
    def test_version_arithmetic_operations(self):
        """Test arithmetic operations on version components."""
        # Test that version components can be used in arithmetic
        total = VERSION_MAJOR + VERSION_MINOR + VERSION_BUILD + VERSION_ALPHA
        self.assertIsInstance(total, int)
        
        # Test multiplication (useful for version hashing)
        version_hash = (VERSION_MAJOR * 1000000 + 
                       VERSION_MINOR * 10000 + 
                       VERSION_BUILD * 100 + 
                       VERSION_ALPHA)
        self.assertIsInstance(version_hash, int)
        self.assertGreater(version_hash, 0)
    
    def test_version_string_operations(self):
        """Test string operations on version components."""
        # Test string formatting with different formats
        formats = [
            f"{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_BUILD}",
            f"v{VERSION_MAJOR}.{VERSION_MINOR}.{VERSION_BUILD}",
            f"{VERSION_MAJOR:02d}.{VERSION_MINOR:02d}.{VERSION_BUILD:02d}",
        ]
        
        for fmt in formats:
            self.assertIsInstance(fmt, str)
            self.assertGreater(len(fmt), 0)


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)