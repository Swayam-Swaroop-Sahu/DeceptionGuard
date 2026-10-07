"""Configuration module for DeceptionGuard.

Loads settings from a TOML config file and environment variables.
Includes a minimal .env file parser using only the standard library.
"""

from __future__ import annotations

import logging
import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Sentinel for missing values
_MISSING = object()

# Default config file locations (searched in order)
_DEFAULT_CONFIG_PATHS = [
    Path("deceptionguard.toml"),
    Path("dg.toml"),
    Path.home() / ".config" / "deceptionguard" / "config.toml",
]

# Default risk factor weights (expert baseline)
DEFAULT_FACTOR_WEIGHTS: dict[str, int] = {
    "claimed_identity_mismatch": 25,
    "urgency_high": 30,
    "authority_spoof": 20,
    "payload_links": 15,
    "action_request": 10,
}

# Default risk thresholds
DEFAULT_RISK_THRESHOLDS: dict[str, int] = {
    "minimal": 0,
    "low": 11,
    "medium": 40,
    "high": 70,
}


def load_dotenv(path: Path | str | None = None) -> dict[str, str]:
    """Parse a .env file and inject values into os.environ.

    Only sets variables that are not already present in the environment
    (environment takes precedence over .env).

    Supports:
    - KEY=VALUE
    - KEY="VALUE" and KEY='VALUE' (quoted values)
    - Comments (lines starting with #)
    - Blank lines
    - export KEY=VALUE prefix

    Args:
        path: Path to .env file. If None, searches for .env in CWD and parents.

    Returns:
        Dict of variables that were loaded (not including already-set ones).
    """
    if path is None:
        # Search for .env in CWD and up to 3 parent levels
        cwd = Path.cwd()
        candidates = [cwd / ".env"] + [p / ".env" for p in list(cwd.parents)[:3]]
        for candidate in candidates:
            if candidate.is_file():
                path = candidate
                break
        if path is None:
            return {}
    else:
        path = Path(path)

    if not path.is_file():
        return {}

    loaded: dict[str, str] = {}

    try:
        with open(path, encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()

                # Skip empty lines and comments
                if not line or line.startswith("#"):
                    continue

                # Strip optional 'export ' prefix
                if line.startswith("export "):
                    line = line[7:].strip()

                # Split on first '='
                if "=" not in line:
                    logger.debug("Skipping malformed line %d in %s", line_num, path)
                    continue

                key, _, value = line.partition("=")
                key = key.strip()
                value = value.strip()

                if not key:
                    continue

                # Remove surrounding quotes
                if len(value) >= 2:
                    if (value[0] == '"' and value[-1] == '"') or (
                        value[0] == "'" and value[-1] == "'"
                    ):
                        value = value[1:-1]

                # Only set if not already in environment
                if key not in os.environ:
                    os.environ[key] = value
                    loaded[key] = value
    except OSError as e:
        logger.warning("Failed to read .env file %s: %s", path, e)

    return loaded


@dataclass(frozen=True)
class LLMConfig:
    """Configuration for the LLM provider (OpenAI-compatible endpoint)."""

    api_key: str = ""
    base_url: str = ""
    model: str = ""
    timeout: int = 30
    max_retries: int = 3
    cache_dir: str = ""

    @property
    def is_configured(self) -> bool:
        """Return True if an API key is set and non-empty."""
        return bool(self.api_key)


@dataclass(frozen=True)
class Config:
    """Typed configuration for DeceptionGuard.

    Loaded from TOML config file and/or environment variables.
    Environment variables take precedence over TOML values.
    """

    # Risk engine
    factor_weights: dict[str, int] = field(default_factory=lambda: dict(DEFAULT_FACTOR_WEIGHTS))
    risk_thresholds: dict[str, int] = field(
        default_factory=lambda: dict(DEFAULT_RISK_THRESHOLDS)
    )

    # LLM provider
    llm: LLMConfig = field(default_factory=LLMConfig)

    # Paths
    data_dir: str = "data"
    results_dir: str = "results"
    cache_dir: str = ".cache"

    # Behavior
    seed: int = 42
    log_level: str = "INFO"

    def validate(self) -> list[str]:
        """Validate configuration and return list of errors (empty if valid)."""
        errors: list[str] = []

        # Validate factor weights are positive integers
        for name, weight in self.factor_weights.items():
            if not isinstance(weight, int) or weight < 0:
                errors.append(f"Factor weight '{name}' must be a non-negative integer, got {weight}")

        # Validate thresholds are in ascending order
        sorted_thresholds = sorted(self.risk_thresholds.items(), key=lambda x: x[1])
        for i in range(1, len(sorted_thresholds)):
            if sorted_thresholds[i][1] <= sorted_thresholds[i - 1][1]:
                errors.append(
                    f"Threshold '{sorted_thresholds[i][0]}' ({sorted_thresholds[i][1]}) "
                    f"must be greater than '{sorted_thresholds[i - 1][0]}' "
                    f"({sorted_thresholds[i - 1][1]})"
                )

        # Validate seed
        if not isinstance(self.seed, int):
            errors.append(f"Seed must be an integer, got {type(self.seed).__name__}")

        return errors


def _deep_get(data: dict[str, Any], *keys: str, default: Any = _MISSING) -> Any:
    """Nested dict lookup."""
    current = data
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        elif default is not _MISSING:
            return default
        else:
            raise KeyError(f"Missing key: {'.'.join(keys)}")
    return current


def load_config(
    config_path: Path | str | None = None,
    *,
    load_env: bool = True,
    env_path: Path | str | None = None,
) -> Config:
    """Load configuration from TOML file and environment variables.

    Priority (highest to lowest):
    1. Environment variables
    2. TOML config file
    3. Defaults

    Args:
        config_path: Explicit path to TOML config file. If None, searches defaults.
        load_env: Whether to load .env file.
        env_path: Explicit path to .env file.

    Returns:
        Validated Config instance.

    Raises:
        ValueError: If configuration validation fails.
    """
    # Step 1: Load .env file if requested
    if load_env:
        load_dotenv(env_path)

    # Step 2: Load TOML config
    toml_data: dict[str, Any] = {}
    if config_path is not None:
        config_path = Path(config_path)
        if config_path.is_file():
            with open(config_path, "rb") as f:
                toml_data = tomllib.load(f)
        else:
            raise FileNotFoundError(f"Config file not found: {config_path}")
    else:
        # Search default locations
        for candidate in _DEFAULT_CONFIG_PATHS:
            if candidate.is_file():
                with open(candidate, "rb") as f:
                    toml_data = tomllib.load(f)
                logger.info("Loaded config from %s", candidate)
                break

    # Step 3: Build config with env overrides
    factor_weights = dict(DEFAULT_FACTOR_WEIGHTS)
    if "factor_weights" in toml_data:
        factor_weights.update(toml_data["factor_weights"])

    risk_thresholds = dict(DEFAULT_RISK_THRESHOLDS)
    if "risk_thresholds" in toml_data:
        risk_thresholds.update(toml_data["risk_thresholds"])

    llm_section = toml_data.get("llm", {})
    llm_config = LLMConfig(
        api_key=os.environ.get(
            "DG_LLM_API_KEY",
            os.environ.get(
                "NVIDIA_API_KEY",
                llm_section.get("api_key", ""),
            ),
        ),
        base_url=os.environ.get(
            "DG_LLM_BASE_URL",
            os.environ.get(
                "NVIDIA_BASE_URL",
                llm_section.get("base_url", ""),
            ),
        ),
        model=os.environ.get(
            "DG_LLM_MODEL",
            os.environ.get(
                "NVIDIA_MODEL",
                llm_section.get("model", ""),
            ),
        ),
        timeout=int(
            os.environ.get(
                "DG_LLM_TIMEOUT",
                llm_section.get("timeout", 30),
            )
        ),
        max_retries=int(
            os.environ.get(
                "DG_LLM_MAX_RETRIES",
                llm_section.get("max_retries", 3),
            )
        ),
        cache_dir=os.environ.get(
            "DG_LLM_CACHE_DIR",
            llm_section.get("cache_dir", ".cache/llm"),
        ),
    )

    config = Config(
        factor_weights=factor_weights,
        risk_thresholds=risk_thresholds,
        llm=llm_config,
        data_dir=os.environ.get("DG_DATA_DIR", toml_data.get("data_dir", "data")),
        results_dir=os.environ.get("DG_RESULTS_DIR", toml_data.get("results_dir", "results")),
        cache_dir=os.environ.get("DG_CACHE_DIR", toml_data.get("cache_dir", ".cache")),
        seed=int(os.environ.get("DG_SEED", toml_data.get("seed", 42))),
        log_level=os.environ.get(
            "DG_LOG_LEVEL", toml_data.get("log_level", "INFO")
        ).upper(),
    )

    # Step 4: Validate
    errors = config.validate()
    if errors:
        raise ValueError(
            "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
        )

    return config


def load_factor_weights(config_path: Path | str | None = None) -> dict[str, int]:
    """Load factor weights from a TOML file or return defaults.

    This is a convenience function for the risk engine that can load
    weights from a standalone TOML file (weights.toml) or fall back
    to the defaults.

    Args:
        config_path: Path to a TOML file containing a [factor_weights] section.
                     If None, returns default weights.

    Returns:
        Dict mapping factor names to integer weights.
    """
    if config_path is not None:
        config_path = Path(config_path)
        if config_path.is_file():
            with open(config_path, "rb") as f:
                data = tomllib.load(f)
            if "factor_weights" in data:
                return data["factor_weights"]
    return dict(DEFAULT_FACTOR_WEIGHTS)
