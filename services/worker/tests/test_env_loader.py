import os
from pathlib import Path

from services.common.env_loader import load_repo_env


def test_load_repo_env_prefers_env_local_and_skips_blank_placeholders(monkeypatch, tmp_path: Path) -> None:
    env_path = tmp_path / ".env"
    env_local_path = tmp_path / ".env.local"
    env_path.write_text("OPENAI_API_KEY=from-env\nHF_TOKEN=hf-from-env\n", encoding="utf-8")
    env_local_path.write_text(
        "OPENAI_API_KEY=from-local\nHF_TOKEN=hf-from-local\nGEMINI_API_KEY=\n",
        encoding="utf-8",
    )

    monkeypatch.setenv("OPENAI_API_KEY", "machine-value")
    monkeypatch.setenv("GEMINI_API_KEY", "machine-gemini")
    monkeypatch.delenv("HF_TOKEN", raising=False)

    load_repo_env((env_path, env_local_path))

    assert os.environ["OPENAI_API_KEY"] == "from-local"
    assert os.environ["HF_TOKEN"] == "hf-from-local"
    assert os.environ["HUGGINGFACE_HUB_TOKEN"] == "hf-from-local"
    assert os.environ["GEMINI_API_KEY"] == "machine-gemini"


def test_load_repo_env_populates_langfuse_host_alias(monkeypatch, tmp_path: Path) -> None:
    env_local_path = tmp_path / ".env.local"
    env_local_path.write_text('LANGFUSE_BASE_URL="https://us.cloud.langfuse.com"\n', encoding="utf-8")

    monkeypatch.delenv("LANGFUSE_BASE_URL", raising=False)
    monkeypatch.delenv("LANGFUSE_HOST", raising=False)

    load_repo_env((env_local_path,))

    assert os.environ["LANGFUSE_BASE_URL"] == "https://us.cloud.langfuse.com"
    assert os.environ["LANGFUSE_HOST"] == "https://us.cloud.langfuse.com"
