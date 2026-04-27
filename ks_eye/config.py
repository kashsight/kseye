"""
ks-eye v2.0 — Simplified Configuration
Online-first research platform
"""

import json
import os
from datetime import datetime

_PACKAGE_DIR = os.path.dirname(os.path.dirname(__file__))
DATA_DIR = os.path.join(_PACKAGE_DIR, "data")
CONFIG_DIR = os.path.join(DATA_DIR, "config")
RESEARCH_DIR = os.path.join(DATA_DIR, "research_history")
SOURCES_DIR = os.path.join(DATA_DIR, "sources")
CACHE_DIR = os.path.join(DATA_DIR, "cache")

for d in [CONFIG_DIR, RESEARCH_DIR, SOURCES_DIR, CACHE_DIR]:
    os.makedirs(d, exist_ok=True)

SETTINGS_FILE = os.path.join(CONFIG_DIR, "settings.json")
AGENT_PROVIDERS_FILE = os.path.join(CONFIG_DIR, "agent_providers.json")

from ks_eye import DEFAULT_AGENT_PROVIDERS, DEFAULT_PROVIDER

DEFAULT_SETTINGS = {
    "default_provider": DEFAULT_PROVIDER,
    "scrape_depth": 2,
    "max_sources": 30,
    "agent_timeout": 120,
    "auto_save_sessions": True,
    "research_sessions": [],
    "created_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat(),
}


class Config:
    """Global configuration manager."""

    DATA_DIR = DATA_DIR
    CONFIG_DIR = CONFIG_DIR
    RESEARCH_DIR = RESEARCH_DIR
    SOURCES_DIR = SOURCES_DIR
    CACHE_DIR = CACHE_DIR

    def __init__(self):
        self.settings = self._load_settings()
        self.agent_providers = self._load_agent_providers()

    def _load_settings(self):
        if os.path.exists(SETTINGS_FILE):
            try:
                with open(SETTINGS_FILE, "r") as f:
                    saved = json.load(f)
                    # Merge with defaults
                    merged = {**DEFAULT_SETTINGS, **saved}
                    return merged
            except (json.JSONDecodeError, IOError):
                pass
        self._save_settings(DEFAULT_SETTINGS)
        return DEFAULT_SETTINGS.copy()

    def _save_settings(self, settings):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        settings["updated_at"] = datetime.now().isoformat()
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)

    def _load_agent_providers(self):
        if os.path.exists(AGENT_PROVIDERS_FILE):
            try:
                with open(AGENT_PROVIDERS_FILE, "r") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        self._save_agent_providers(DEFAULT_AGENT_PROVIDERS)
        return DEFAULT_AGENT_PROVIDERS.copy()

    def _save_agent_providers(self, providers):
        os.makedirs(CONFIG_DIR, exist_ok=True)
        with open(AGENT_PROVIDERS_FILE, "w") as f:
            json.dump(providers, f, indent=2)

    def get(self, key, default=None):
        return self.settings.get(key, default)

    def set(self, key, value):
        self.settings[key] = value
        self._save_settings(self.settings)

    def get_agent_provider(self, agent_type):
        if agent_type in self.agent_providers:
            return self.agent_providers[agent_type].get(
                "provider", self.settings.get("default_provider", DEFAULT_PROVIDER)
            )
        return self.settings.get("default_provider", DEFAULT_PROVIDER)

    def set_agent_provider(self, agent_type, provider):
        if agent_type in self.agent_providers:
            self.agent_providers[agent_type]["provider"] = provider
            self._save_agent_providers(self.agent_providers)

    def save_session(self, session_data):
        """Save a research session to disk."""
        os.makedirs(RESEARCH_DIR, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        topic_slug = "".join(c if c.isalnum() else "_" for c in session_data.get("topic", "untitled"))[:60]
        folder = os.path.join(RESEARCH_DIR, f"{topic_slug}_{ts}")
        os.makedirs(folder, exist_ok=True)

        session_file = os.path.join(folder, "session.json")
        with open(session_file, "w") as f:
            json.dump(session_data, f, indent=2, default=str)

        if "research_sessions" not in self.settings:
            self.settings["research_sessions"] = []
        self.settings["research_sessions"].append({
            "timestamp": ts,
            "topic": session_data.get("topic", ""),
            "folder": folder,
            "output_type": session_data.get("output_type", "summary"),
        })
        self._save_settings(self.settings)
        return folder, session_file


config = Config()
