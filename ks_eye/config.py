"""
ks-eye Configuration — v3: Human-in-the-Loop Research Assistant
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

from ks_eye import DEFAULT_AGENT_PROVIDERS

DEFAULT_SETTINGS = {
    "username": "researcher",
    "default_provider": "sky",
    "agent_timeout": 60,
    "citation_style": "apa",
    "auto_save_sessions": True,
    "research_sessions": [],
    "created_at": datetime.now().isoformat(),
    "updated_at": datetime.now().isoformat(),
}


class Config:
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
                    return json.load(f)
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

    def get_all(self):
        return self.settings.copy()

    def get_agent_provider(self, agent_type):
        if agent_type in self.agent_providers:
            return self.agent_providers[agent_type].get("provider", self.settings.get("default_provider", "sky"))
        return self.settings.get("default_provider", "sky")

    def set_agent_provider(self, agent_type, provider):
        if agent_type in self.agent_providers:
            self.agent_providers[agent_type]["provider"] = provider
            self._save_agent_providers(self.agent_providers)

    def get_all_agent_providers(self):
        return self.agent_providers.copy()

    def save_session(self, session_data):
        """Save a research session"""
        os.makedirs(RESEARCH_DIR, exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"session_{ts}.json"
        filepath = os.path.join(RESEARCH_DIR, filename)
        with open(filepath, "w") as f:
            json.dump(session_data, f, indent=2)

        if "research_sessions" not in self.settings:
            self.settings["research_sessions"] = []
        self.settings["research_sessions"].append({
            "timestamp": ts,
            "topic": session_data.get("topic", ""),
            "file": filename,
            "step": session_data.get("step", ""),
        })
        self._save_settings(self.settings)
        return filepath


config = Config()
