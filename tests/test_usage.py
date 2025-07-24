"""
Simple tests demonstrating real usage of cfgone package.
These tests assume a config.yaml file exists in the current directory.
"""

import unittest
import cfgone as cfg


class TestCfgoneUsage(unittest.TestCase):
    """Test the package as it would be used by end users"""

    def test_basic_config_access(self):
        """Test basic configuration access patterns"""
        # Test basic access patterns - these should come from extends + overrides
        self.assertEqual(cfg.app.name, "MyApp")  # Overridden in main config
        self.assertEqual(cfg.app.version, "1.0.0")  # Overridden in main config
        self.assertTrue(cfg.app.debug)  # Overridden in main config (base has false)
        self.assertEqual(cfg.app.port, 8080)  # Added in main config

    def test_extends_inheritance(self):
        """Test that values are properly inherited from extended configs"""
        # Values that should come from base.yaml
        self.assertEqual(cfg.database.host, "localhost")  # From base.yaml
        self.assertEqual(cfg.database.port, 5432)  # From base.yaml

        # Values that should be overridden by main config
        self.assertEqual(cfg.database.ssl, False)  # Overridden in main config (base.yaml & database.yaml had true)

        # Values from database.yaml that should be inherited (not overridden)
        self.assertEqual(cfg.database.pool_size, 20)  # From database.yaml (not in main config)

        # Values from database.yaml that should merge but are overridden
        self.assertEqual(cfg.cache.redis.host, "redis.example.com")  # Overridden in main config (database.yaml had redis.production.com)
        self.assertEqual(cfg.cache.redis.port, 6379)  # From database.yaml (same in main config)        # Values from api.yaml
        self.assertEqual(cfg.api.rate_limit, 1000)  # From api.yaml

        # Features should be replaced by api.yaml, then by main config
        self.assertIn("feature_a", cfg.features)  # From main config
        self.assertIn("feature_b", cfg.features)  # From main config
        self.assertIn("feature_c", cfg.features)  # From main config    def test_nested_config_access(self):
        """Test accessing nested configuration"""
        # Test database configuration - mix of inherited and overridden values
        self.assertEqual(cfg.database.host, "localhost")  # From base.yaml
        self.assertEqual(cfg.database.port, 5432)  # From base.yaml
        self.assertEqual(cfg.database.name, "mydb")  # Overridden in main config
        self.assertEqual(cfg.database.user, "admin")  # Overridden in main config
        self.assertFalse(cfg.database.ssl)  # Overridden in main config (base & database had true)

    def test_api_configuration(self):
        """Test API configuration access"""
        # Overridden values from main config
        self.assertEqual(cfg.api.base_url, "https://api.example.com")  # Overridden in main
        self.assertEqual(cfg.api.timeout, 30)  # Overridden in main (api.yaml has 60)
        self.assertEqual(cfg.api.retries, 3)  # Overridden in main (api.yaml has 5)

        # Inherited values from api.yaml
        self.assertEqual(cfg.api.rate_limit, 1000)  # From api.yaml

        # Test nested endpoints - these are from main config
        self.assertEqual(cfg.api.endpoints.users, "/users")
        self.assertEqual(cfg.api.endpoints.posts, "/posts")
        self.assertEqual(cfg.api.endpoints.comments, "/comments")

    def test_list_configuration(self):
        """Test accessing list configurations"""
        # Test features list
        self.assertIn("feature_a", cfg.features)
        self.assertIn("feature_b", cfg.features)
        self.assertIn("feature_c", cfg.features)
        self.assertEqual(len(cfg.features), 3)

    def test_deeply_nested_access(self):
        """Test deeply nested configuration access"""
        self.assertEqual(cfg.nested.level1.level2.level3.value, "deep_value")
        self.assertEqual(cfg.nested.level1.level2.level3.number, 42)

    def test_list_with_objects(self):
        """Test lists containing objects"""
        items = cfg.nested.level1.level2.items
        self.assertEqual(len(items), 2)

        # Test first item
        self.assertEqual(items[0].name, "item1")
        self.assertEqual(items[0].value, 100)

        # Test second item
        self.assertEqual(items[1].name, "item2")
        self.assertEqual(items[1].value, 200)

    def test_cache_configuration(self):
        """Test cache configuration"""
        # Redis cache
        self.assertEqual(cfg.cache.redis.host, "redis.example.com")
        self.assertEqual(cfg.cache.redis.port, 6379)
        self.assertEqual(cfg.cache.redis.db, 0)

        # Memory cache
        self.assertEqual(cfg.cache.memory.max_size, 1000)

    def test_logging_configuration(self):
        """Test logging configuration"""
        self.assertEqual(cfg.logging.level, "INFO")
        self.assertIsInstance(cfg.logging.format, str)
        self.assertTrue(cfg.logging.format.startswith("%(asctime)s"))

        # Test handlers
        self.assertEqual(len(cfg.logging.handlers), 2)
        self.assertEqual(cfg.logging.handlers[0].type, "console")
        self.assertEqual(cfg.logging.handlers[1].type, "file")
        self.assertEqual(cfg.logging.handlers[1].filename, "app.log")

    def test_dict_style_access(self):
        """Test dictionary-style access"""
        # Test __getitem__
        self.assertEqual(cfg["app"]["name"], "MyApp")
        self.assertEqual(cfg["database"]["host"], "localhost")

        # Test mixed access
        self.assertEqual(cfg.app.name, cfg["app"]["name"])
        self.assertEqual(cfg.database.port, cfg["database"]["port"])

    def test_get_method(self):
        """Test the get method"""
        self.assertEqual(cfg.get("app").name, "MyApp")
        self.assertEqual(cfg.app.get("name"), "MyApp")
        self.assertEqual(cfg.app.get("nonexistent", "default"), "default")

    def test_contains_operator(self):
        """Test the 'in' operator"""
        self.assertTrue("app" in cfg)
        self.assertTrue("database" in cfg)
        self.assertTrue("api" in cfg)
        self.assertFalse("nonexistent" in cfg)

    def test_runtime_modification(self):
        """Test modifying configuration at runtime"""
        # Test modifying existing values
        original_debug = cfg.app.debug
        cfg.app.debug = not original_debug
        self.assertEqual(cfg.app.debug, not original_debug)

        # Restore original value to avoid affecting other tests
        cfg.app.debug = original_debug

        # Test adding new configuration
        cfg.app.new_setting = "test_value"
        self.assertEqual(cfg.app.new_setting, "test_value")

        # Test dict-style assignment
        cfg["app"]["another_setting"] = "another_value"
        self.assertEqual(cfg.app.another_setting, "another_value")


class TestRealWorldScenarios(unittest.TestCase):
    """Test real-world usage scenarios"""

    def test_database_connection_string(self):
        """Test building database connection string from config"""
        # Simulate building a database URL
        db_url = f"postgresql://{cfg.database.user}@{cfg.database.host}:{cfg.database.port}/{cfg.database.name}"
        expected_url = "postgresql://admin@localhost:5432/mydb"
        self.assertEqual(db_url, expected_url)

    def test_api_client_configuration(self):
        """Test configuring an API client"""
        # Simulate API client configuration
        api_config = {
            "base_url": cfg.api.base_url,
            "timeout": cfg.api.timeout,
            "retries": cfg.api.retries,
            "endpoints": {
                "users": cfg.api.endpoints.users,
                "posts": cfg.api.endpoints.posts
            }
        }

        self.assertEqual(api_config["base_url"], "https://api.example.com")
        self.assertEqual(api_config["timeout"], 30)
        self.assertEqual(api_config["endpoints"]["users"], "/users")

    def test_feature_flags(self):
        """Test using configuration as feature flags"""
        # Simulate feature flag checking
        enabled_features = cfg.features

        if "feature_a" in enabled_features:
            feature_a_enabled = True
        else:
            feature_a_enabled = False

        self.assertTrue(feature_a_enabled)

    def test_web_server_configuration(self):
        """Test web server configuration"""
        # Simulate web server setup
        server_config = {
            "host": cfg.app.get("host", "127.0.0.1"),
            "port": cfg.app.port,
            "debug": cfg.app.debug
        }

        self.assertEqual(server_config["host"], "127.0.0.1")  # default value
        self.assertEqual(server_config["port"], 8080)
        self.assertTrue(server_config["debug"])


class TestExtendsFunctionality(unittest.TestCase):
    """Test the extends functionality"""

    def setUp(self):
        """Set up test environment"""
        import tempfile
        import shutil
        import os
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """Clean up test environment"""
        import shutil
        import os
        os.chdir(self.original_cwd)
        shutil.rmtree(self.test_dir)

    def create_test_config(self, filename, content):
        """Helper method to create test config files"""
        import os
        filepath = os.path.join(self.test_dir, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath

    def test_deep_merge_basic(self):
        """Test basic deep merge functionality"""
        from cfgone.core import _deep_merge
        base = {
            'a': 1,
            'b': {'c': 2, 'd': 3}
        }
        override = {
            'b': {'c': 4, 'e': 5},
            'f': 6
        }
        result = _deep_merge(base, override)

        expected = {
            'a': 1,
            'b': {'c': 4, 'd': 3, 'e': 5},
            'f': 6
        }
        self.assertEqual(result, expected)

    def test_single_extends(self):
        """Test extending a single config file"""
        from cfgone.core import _load_config_file
        # Create base config
        base_content = """
app:
  name: "BaseApp"
  version: "1.0.0"
database:
  host: "localhost"
"""
        self.create_test_config('base.yaml', base_content)

        # Create config that extends base
        main_content = """
extends:
  - "base.yaml"
app:
  debug: true
  port: 8080
"""
        self.create_test_config('config.yaml', main_content)

        result = _load_config_file('config.yaml')

        self.assertEqual(result['app']['name'], 'BaseApp')
        self.assertEqual(result['app']['version'], '1.0.0')
        self.assertEqual(result['app']['debug'], True)
        self.assertEqual(result['app']['port'], 8080)
        self.assertEqual(result['database']['host'], 'localhost')

    def test_multiple_extends(self):
        """Test extending multiple config files"""
        from cfgone.core import _load_config_file
        # Create base configs
        base1_content = """
app:
  name: "App"
  version: "1.0.0"
database:
  host: "localhost"
"""
        self.create_test_config('base1.yaml', base1_content)

        base2_content = """
app:
  debug: false
database:
  port: 5432
  user: "admin"
api:
  timeout: 30
"""
        self.create_test_config('base2.yaml', base2_content)

        # Create main config
        main_content = """
extends:
  - "base1.yaml"
  - "base2.yaml"
app:
  debug: true
"""
        self.create_test_config('config.yaml', main_content)

        result = _load_config_file('config.yaml')

        # Check merged values
        self.assertEqual(result['app']['name'], 'App')
        self.assertEqual(result['app']['version'], '1.0.0')
        self.assertEqual(result['app']['debug'], True)  # Overridden by main config
        self.assertEqual(result['database']['host'], 'localhost')
        self.assertEqual(result['database']['port'], 5432)
        self.assertEqual(result['database']['user'], 'admin')
        self.assertEqual(result['api']['timeout'], 30)

    def test_circular_dependency_detection(self):
        """Test that circular dependencies are detected"""
        from cfgone.core import _load_config_file, ConfigError
        cfgone_content = """
extends:
  - "config2.yaml"
value: 1
"""
        self.create_test_config('cfg.yaml', cfgone_content)

        config2_content = """
extends:
  - "cfg.yaml"
value: 2
"""
        self.create_test_config('config2.yaml', config2_content)

        with self.assertRaises(ConfigError) as cm:
            _load_config_file('cfg.yaml')

        self.assertIn("Circular dependency detected", str(cm.exception))

    def test_missing_extended_file(self):
        """Test error handling for missing extended files"""
        from cfgone.core import _load_config_file, ConfigError
        main_content = """
extends:
  - "nonexistent.yaml"
app:
  name: "App"
"""
        self.create_test_config('config.yaml', main_content)

        with self.assertRaises(ConfigError) as cm:
            _load_config_file('config.yaml')

        self.assertIn("Config file not found", str(cm.exception))

    def test_no_extends_backward_compatibility(self):
        """Test that configs without extends still work"""
        from cfgone.core import _load_config_file
        main_content = """
app:
  name: "App"
  debug: true
"""
        self.create_test_config('config.yaml', main_content)

        result = _load_config_file('config.yaml')
        self.assertEqual(result['app']['name'], 'App')
        self.assertEqual(result['app']['debug'], True)


if __name__ == "__main__":
    unittest.main(verbosity=2)
