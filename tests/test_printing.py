"""
Simple unit tests for cfgone printing functionality.
"""

import unittest
import json
import cfgone as cfg


class TestCfgonePrinting(unittest.TestCase):
    """Test the printing functionality of cfgone"""

    def test_cfgone_has_string_representation(self):
        """Test that cfgone object can be converted to string"""
        config_str = str(cfg)
        self.assertIsInstance(config_str, str)
        self.assertGreater(len(config_str), 0)

    def test_cfgone_has_repr_representation(self):
        """Test that cfgone object has a proper repr"""
        config_repr = repr(cfg)
        self.assertIsInstance(config_repr, str)
        self.assertGreater(len(config_repr), 0)

    def test_cfgone_prints_valid_json(self):
        """Test that the printed config is valid JSON"""
        config_str = str(cfg)
        try:
            # Should be able to parse the output as JSON
            parsed_config = json.loads(config_str)
            self.assertIsInstance(parsed_config, dict)
        except json.JSONDecodeError:
            self.fail("Config string representation is not valid JSON")

    def test_cfgone_contains_expected_keys(self):
        """Test that the config contains expected top-level keys"""
        config_str = str(cfg)
        parsed_config = json.loads(config_str)

        # Check for some expected keys from the config.yaml
        expected_keys = ['app', 'database', 'api', 'features']
        for key in expected_keys:
            self.assertIn(key, parsed_config, f"Expected key '{key}' not found in config")

    def test_cfgone_app_section(self):
        """Test that the app section contains expected values"""
        config_str = str(cfg)
        parsed_config = json.loads(config_str)

        # Test app section
        self.assertIn('app', parsed_config)
        app_config = parsed_config['app']

        self.assertEqual(app_config['name'], 'MyApp')
        self.assertEqual(app_config['version'], '1.0.0')
        self.assertTrue(app_config['debug'])
        self.assertEqual(app_config['port'], 8080)

    def test_cfgone_nested_objects(self):
        """Test that nested objects are properly represented"""
        config_str = str(cfg)
        parsed_config = json.loads(config_str)

        # Test nested structure
        self.assertIn('api', parsed_config)
        api_config = parsed_config['api']

        self.assertIn('endpoints', api_config)
        endpoints = api_config['endpoints']

        self.assertEqual(endpoints['users'], '/users')
        self.assertEqual(endpoints['posts'], '/posts')
        self.assertEqual(endpoints['comments'], '/comments')

    def test_cfgone_lists(self):
        """Test that lists are properly represented"""
        config_str = str(cfg)
        parsed_config = json.loads(config_str)

        # Test features list
        self.assertIn('features', parsed_config)
        features = parsed_config['features']

        self.assertIsInstance(features, list)
        self.assertIn('feature_a', features)
        self.assertIn('feature_b', features)
        self.assertIn('feature_c', features)

    def test_str_and_repr_are_different(self):
        """Test that str() and repr() return different formats"""
        config_str = str(cfg)
        config_repr = repr(cfg)

        # They should be different formats
        self.assertNotEqual(config_str, config_repr)

        # str should be JSON formatted
        self.assertIn('{\n', config_str)  # Pretty printed JSON

        # repr should start with class name
        self.assertTrue(config_repr.startswith("DictToObj("))

    def test_printing_doesnt_modify_config(self):
        """Test that printing the config doesn't modify the original object"""
        # Get original value
        original_app_name = cfg.app.name

        # Print the config
        _ = str(cfg)

        # Verify the original value hasn't changed
        self.assertEqual(cfg.app.name, original_app_name)

    def test_config_is_formatted_nicely(self):
        """Test that the config output is nicely formatted (multi-line)"""
        config_str = str(cfg)

        # Should contain newlines for readability
        self.assertIn('\n', config_str)

        # Should contain proper indentation (2 spaces)
        self.assertIn('  ', config_str)


if __name__ == "__main__":
    unittest.main(verbosity=2)
