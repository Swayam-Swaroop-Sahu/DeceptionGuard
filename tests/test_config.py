from deceptionguard.config import Config, LLMConfig, load_config


def test_load_config_default():
    cfg = load_config(load_env=False)
    # The default LLM config model depends on env vars if any, or default empty.
    assert hasattr(cfg.llm, "model")
    assert cfg.risk_thresholds["high"] == 70

def test_load_config_env(monkeypatch):
    monkeypatch.setenv("DG_LLM_MODEL", "custom-model")
    monkeypatch.setenv("DG_LLM_TIMEOUT", "42")
    monkeypatch.setenv("DG_THRESHOLD_HIGH", "80") # We don't support env vars for thresholds easily, but we'll check what works

    cfg = load_config(load_env=True)
    assert cfg.llm.model == "custom-model"
    assert cfg.llm.timeout == 42

def test_config_validation():
    cfg = Config(risk_thresholds={"minimal":0, "low":10, "medium":50, "high":50})
    errors = cfg.validate()
    assert len(errors) > 0

def test_llm_config_is_configured():
    cfg = LLMConfig(api_key="sk-test")
    assert cfg.is_configured
    cfg2 = LLMConfig()
    assert not cfg2.is_configured
