"""Config loading tests."""

from pathlib import Path
import yaml

import pytest

from wheels.config import (
    Config,
    get_config,
    load_config,
    reset_config,
)


class TestConfigAttributes:
    def test_config_has_output_mode(self, mock_config):
        assert hasattr(mock_config, "output_mode")

    def test_config_has_pdf_engine(self, mock_config):
        assert hasattr(mock_config, "pdf_engine")

    def test_config_has_max_file_size(self, mock_config):
        assert hasattr(mock_config, "max_file_size")

    def test_config_has_concurrency(self, mock_config):
        assert hasattr(mock_config, "concurrency")

    def test_config_has_retry_count(self, mock_config):
        assert hasattr(mock_config, "retry_count")

    def test_config_output_mode_is_valid(self, mock_config):
        assert mock_config.output_mode in ("fast", "quality")

    def test_config_pdf_engine_is_valid(self, mock_config):
        assert mock_config.pdf_engine in ("light", "heavy")

    def test_config_max_file_size_is_positive(self, mock_config):
        assert mock_config.max_file_size > 0

    def test_config_concurrency_is_positive(self, mock_config):
        assert mock_config.concurrency > 0

    def test_config_retry_count_is_positive(self, mock_config):
        assert mock_config.retry_count > 0


class TestConfigFromYaml:
    def test_loads_config_yaml_correctly(self, tmp_path: Path):
        config_content = {
            "output_mode": "quality",
            "pdf_engine": "heavy",
            "max_file_size": 100,
            "concurrency": 8,
            "retry_count": 5,
        }
        config_file = tmp_path / "config.yaml"
        config_file.write_text(yaml.dump(config_content), encoding="utf-8")

        config = Config.from_yaml(config_file)

        assert config.output_mode == "quality"
        assert config.pdf_engine == "heavy"
        assert config.max_file_size == 100
        assert config.concurrency == 8
        assert config.retry_count == 5

    def test_config_from_yaml_with_defaults(self, tmp_path: Path):
        config_file = tmp_path / "config.yaml"
        config_file.write_text("", encoding="utf-8")

        config = Config.from_yaml(config_file)

        assert config.output_mode == "fast"
        assert config.pdf_engine == "light"
        assert config.max_file_size == 50
        assert config.concurrency == 4
        assert config.retry_count == 3

    def test_config_from_yaml_file_not_found(self):
        with pytest.raises(FileNotFoundError):
            Config.from_yaml("/nonexistent/config.yaml")


class TestGetConfig:
    def test_get_config_returns_config(self):
        reset_config()
        config = get_config()
        assert isinstance(config, Config)

    def test_get_config_returns_same_instance(self):
        reset_config()
        config1 = get_config()
        config2 = get_config()
        assert config1 is config2


class TestConfigValidation:
    def test_invalid_output_mode_raises(self):
        data = {"output_mode": "invalid"}
        with pytest.raises(ValueError):
            Config._from_dict(data)

    def test_invalid_pdf_engine_raises(self):
        data = {"pdf_engine": "invalid"}
        with pytest.raises(ValueError):
            Config._from_dict(data)

    def test_invalid_max_file_size_type_raises(self):
        data = {"max_file_size": "not_an_int"}
        with pytest.raises(TypeError):
            Config._from_dict(data)

    def test_invalid_max_file_size_zero_raises(self):
        data = {"max_file_size": 0}
        with pytest.raises(ValueError):
            Config._from_dict(data)

    def test_invalid_max_file_size_negative_raises(self):
        data = {"max_file_size": -1}
        with pytest.raises(ValueError):
            Config._from_dict(data)

    def test_invalid_concurrency_type_raises(self):
        data = {"concurrency": "not_an_int"}
        with pytest.raises(TypeError):
            Config._from_dict(data)

    def test_invalid_retry_count_type_raises(self):
        data = {"retry_count": "not_an_int"}
        with pytest.raises(TypeError):
            Config._from_dict(data)

    def test_invalid_log_level_raises(self):
        data = {"log_level": "invalid"}
        with pytest.raises(ValueError):
            Config._from_dict(data)


class TestConfigToDict:
    def test_to_dict_returns_dict(self, mock_config):
        result = mock_config.to_dict()
        assert isinstance(result, dict)

    def test_to_dict_contains_all_fields(self, mock_config):
        result = mock_config.to_dict()
        expected_keys = {
            "output_mode",
            "pdf_engine",
            "max_file_size",
            "concurrency",
            "retry_count",
            "output_dir",
            "log_level",
        }
        assert set(result.keys()) == expected_keys
