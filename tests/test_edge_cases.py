"""
Comprehensive edge case tests for cfgone printing functionality.
"""

import unittest
import tempfile
import os
from pathlib import Path
from cfgone.core import DictToObj, ConfigError, _discover_config_path, load_config


class TestDictToObjEdgeCases(unittest.TestCase):
    """Test edge cases and error handling for DictToObj"""

    def test_empty_dictionary(self):
        """Test handling of empty dictionaries"""
        obj = DictToObj({})
        self.assertEqual(str(obj), "{}")
        self.assertEqual(obj._to_dict(), {})

    def test_none_values(self):
        """Test handling of None values"""
        obj = DictToObj({"key": None})
        self.assertIsNone(obj.key)
        result_dict = obj._to_dict()
        self.assertIsNone(result_dict["key"])

    def test_invalid_initialization(self):
        """Test that DictToObj raises error for non-dict input"""
        with self.assertRaises(TypeError):
            DictToObj("not a dict")

        with self.assertRaises(TypeError):
            DictToObj(123)

        with self.assertRaises(TypeError):
            DictToObj(None)

    def test_missing_attribute_access(self):
        """Test that accessing missing attributes raises AttributeError"""
        obj = DictToObj({"existing": "value"})

        with self.assertRaises(AttributeError) as cm:
            _ = obj.nonexistent

        self.assertIn("has no attribute 'nonexistent'", str(cm.exception))

    def test_very_deep_nesting(self):
        """Test handling of deeply nested structures"""
        # Create a deeply nested dictionary
        deep_dict = {}
        current = deep_dict
        for i in range(50):  # Create 50 levels deep
            current[f"level_{i}"] = {}
            current = current[f"level_{i}"]
        current["final_value"] = "deep"

        obj = DictToObj(deep_dict)

        # Should not crash and should handle the depth
        result_str = str(obj)
        self.assertIsInstance(result_str, str)

        # Should be able to access deeply
        current_obj = obj
        for i in range(50):
            current_obj = getattr(current_obj, f"level_{i}")
        self.assertEqual(current_obj.final_value, "deep")

    def test_extremely_deep_nesting_protection(self):
        """Test protection against extremely deep nesting (>100 levels)"""
        # Create a dictionary deeper than the max depth limit
        deep_dict = {}
        current = deep_dict
        for i in range(150):  # Exceed the 100 level limit
            current[f"level_{i}"] = {}
            current = current[f"level_{i}"]
        current["final_value"] = "too_deep"

        obj = DictToObj(deep_dict)
        result_dict = obj._to_dict()

        # Should contain depth protection message at some point
        def contains_depth_exceeded(d, depth=0):
            if depth > 120:  # Avoid infinite recursion in test
                return False
            for v in d.values():
                if v == "<Max depth exceeded>":
                    return True
                if isinstance(v, dict):
                    if contains_depth_exceeded(v, depth + 1):
                        return True
            return False

        # The depth protection should kick in
        self.assertTrue(contains_depth_exceeded(result_dict))

    def test_circular_reference_protection(self):
        """Test protection against circular references"""
        # Create circular reference manually
        obj1 = DictToObj({"name": "obj1"})
        obj2 = DictToObj({"name": "obj2"})

        # Create circular reference
        obj1.ref = obj2
        obj2.ref = obj1

        # Should not cause infinite recursion
        result_str = str(obj1)
        self.assertIsInstance(result_str, str)
        self.assertIn("Circular reference", result_str)

    def test_non_json_serializable_objects(self):
        """Test handling of objects that can't be JSON serialized"""
        import datetime

        # Create object with non-serializable content
        obj = DictToObj({
            "date": datetime.datetime.now(),
            "function": lambda x: x,
            "normal": "value"
        })

        # Should not crash, should handle gracefully
        result_str = str(obj)
        self.assertIsInstance(result_str, str)

        # Should contain the normal value
        self.assertIn("normal", result_str)
        self.assertIn("value", result_str)

    def test_list_with_mixed_types(self):
        """Test lists containing mixed types including non-serializable"""
        import datetime

        obj = DictToObj({
            "mixed_list": [
                "string",
                123,
                {"nested": "dict"},
                datetime.datetime.now(),
                None
            ]
        })

        result_str = str(obj)
        self.assertIsInstance(result_str, str)
        self.assertIn("string", result_str)
        self.assertIn("123", result_str)
        self.assertIn("nested", result_str)

    def test_repr_vs_str_difference(self):
        """Test that repr and str return different formats"""
        obj = DictToObj({"key": "value"})

        obj_str = str(obj)
        obj_repr = repr(obj)

        # str should be JSON formatted
        self.assertIn("{\n", obj_str)  # Pretty printed JSON

        # repr should start with class name
        self.assertTrue(obj_repr.startswith("DictToObj("))

    def test_error_handling_in_str(self):
        """Test error handling when str() encounters problems"""
        obj = DictToObj({"key": "value"})

        # Simulate an error by corrupting the object
        original_to_dict = obj._to_dict

        def broken_to_dict(*args, **kwargs):
            raise Exception("Simulated error")

        obj._to_dict = broken_to_dict

        result_str = str(obj)
        self.assertIn("serialization error", result_str)

        # Restore original method
        obj._to_dict = original_to_dict

    def test_error_handling_in_repr(self):
        """Test error handling when repr() encounters problems"""
        obj = DictToObj({"key": "value"})

        # Simulate an error
        original_to_dict = obj._to_dict

        def broken_to_dict(*args, **kwargs):
            raise Exception("Simulated error")

        obj._to_dict = broken_to_dict

        result_repr = repr(obj)
        self.assertIn("repr error", result_repr)

        # Restore original method
        obj._to_dict = original_to_dict

    def test_dynamic_attribute_assignment(self):
        """Test that users can add new attributes after initialization"""
        obj = DictToObj({"initial": "value"})

        # Should be able to add new attributes
        obj.new_attr = "new_value"
        self.assertEqual(obj.new_attr, "new_value")

        # Should appear in string representation
        result_str = str(obj)
        self.assertIn("new_attr", result_str)
        self.assertIn("new_value", result_str)

    def test_dict_style_operations(self):
        """Test dictionary-style operations work correctly"""
        obj = DictToObj({"key1": "value1", "key2": {"nested": "value"}})

        # Test __getitem__
        self.assertEqual(obj["key1"], "value1")
        self.assertEqual(obj["key2"]["nested"], "value")

        # Test __setitem__
        obj["key3"] = "value3"
        self.assertEqual(obj.key3, "value3")

        # Test __contains__
        self.assertTrue("key1" in obj)
        self.assertFalse("nonexistent" in obj)

        # Test get method
        self.assertEqual(obj.get("key1"), "value1")
        self.assertEqual(obj.get("nonexistent", "default"), "default")


class TestConfigLoadingEdgeCases(unittest.TestCase):
    """Test edge cases in config loading"""

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.test_dir)

    def create_test_config(self, filename, content):
        """Helper to create test config files"""
        filepath = os.path.join(self.test_dir, filename)
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'w') as f:
            f.write(content)
        return filepath

    def test_empty_config_file(self):
        """Test loading empty config file"""
        from cfgone.core import _load_config_file

        self.create_test_config('empty.yaml', '')
        result = _load_config_file('empty.yaml')
        self.assertEqual(result, {})

    def test_config_with_only_extends(self):
        """Test config file with only extends and no other content"""
        from cfgone.core import _load_config_file

        base_content = "key: value"
        self.create_test_config('base.yaml', base_content)

        main_content = """
extends:
  - "base.yaml"
"""
        self.create_test_config('main.yaml', main_content)

        result = _load_config_file('main.yaml')
        self.assertEqual(result['key'], 'value')

    def test_invalid_yaml_syntax(self):
        """Test handling of invalid YAML syntax"""
        from cfgone.core import _load_config_file

        invalid_content = """
key: value
invalid: [unclosed list
another: value
"""
        self.create_test_config('invalid.yaml', invalid_content)

        with self.assertRaises(ConfigError) as cm:
            _load_config_file('invalid.yaml')

        self.assertIn("Invalid YAML", str(cm.exception))

    def test_extends_with_invalid_type(self):
        """Test extends with invalid type (not list)"""
        from cfgone.core import _load_config_file

        content = """
extends: "single_file.yaml"  # Should be a list
key: value
"""
        self.create_test_config('invalid_extends.yaml', content)

        with self.assertRaises(ConfigError) as cm:
            _load_config_file('invalid_extends.yaml')

        self.assertIn("'extends' must be a list", str(cm.exception))

    def test_extends_with_non_string_paths(self):
        """Test extends with non-string paths in list"""
        from cfgone.core import _load_config_file

        # First create the valid.yaml that's referenced
        self.create_test_config('valid.yaml', 'key: value')

        content = """
extends:
  - "valid.yaml"
  - 123  # Invalid: not a string
key: value
"""
        self.create_test_config('invalid_path_type.yaml', content)

        with self.assertRaises(ConfigError) as cm:
            _load_config_file('invalid_path_type.yaml')

        self.assertIn("All paths in 'extends' must be strings", str(cm.exception))


class TestConfigDiscovery(unittest.TestCase):
    """Test locating configuration files relative to project markers"""

    def test_finds_config_in_project_root(self):
        """Config should be discovered in project root when cwd lacks it"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir).resolve()
            (root / "pyproject.toml").write_text("", encoding="utf-8")
            (root / "config.yaml").write_text("app:\n  name: root-app\n", encoding="utf-8")

            nested = root / "pkg" / "module"
            nested.mkdir(parents=True)

            discovered = _discover_config_path(start_dir=nested)
            self.assertEqual(discovered, root / "config.yaml")

            original_cwd = os.getcwd()
            try:
                os.chdir(nested)
                config = load_config()
                self.assertEqual(config.app.name, "root-app")
            finally:
                os.chdir(original_cwd)


if __name__ == "__main__":
    unittest.main(verbosity=2)
