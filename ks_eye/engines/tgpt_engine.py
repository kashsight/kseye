"""
tgpt Engine Integration for ks-eye
Copied from kslearn's ai_chat.py pattern - provides tgpt CLI wrapper
"""

import subprocess
import shutil
import os
import json
from pathlib import Path

# tgpt binary paths to check
TGPT_PATHS = [
    "/data/data/com.termux/files/usr/bin/tgpt",
    "/usr/local/bin/tgpt",
    "/usr/bin/tgpt",
]

# API keys directory
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
API_KEYS_DIR = os.path.join(DATA_DIR, "config", "tgpt", "api_keys")


def find_tgpt():
    """Find tgpt binary"""
    for path in TGPT_PATHS:
        if os.path.exists(path) and os.access(path, os.X_OK):
            return path
    return shutil.which("tgpt")


def load_api_key(provider):
    """Load API key for a provider from file"""
    keys_file = os.path.join(API_KEYS_DIR, f"{provider}.key")
    if os.path.exists(keys_file):
        with open(keys_file, "r") as f:
            return f.read().strip()
    return None


def save_api_key(provider, key):
    """Save API key for a provider"""
    os.makedirs(API_KEYS_DIR, exist_ok=True)
    keys_file = os.path.join(API_KEYS_DIR, f"{provider}.key")
    with open(keys_file, "w") as f:
        f.write(key)


def run_tgpt(message, provider="sky", system_prompt=None, api_key=None, timeout=60):
    """
    Run tgpt with specified provider and get response
    
    Args:
        message: The query/message
        provider: AI provider (sky, phind, gemini, etc.)
        system_prompt: Optional system prompt
        api_key: Optional API key
        timeout: Timeout in seconds
    
    Returns:
        Response text or None on error
    """
    tgpt = find_tgpt()
    if not tgpt:
        return None

    cmd = [tgpt, "--provider", provider, "-q"]

    # Add system prompt if provided
    if system_prompt:
        cmd.extend(["-preprompt", system_prompt])

    # Add API key if provided
    if api_key:
        cmd.extend(["--key", api_key])
    else:
        # Try to load from file
        key = load_api_key(provider)
        if key:
            cmd.extend(["--key", key])

    cmd.append(message)

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        if result.returncode == 0:
            return result.stdout.strip()
        else:
            return None
    except subprocess.TimeoutExpired:
        return None
    except (subprocess.SubprocessError, OSError):
        return None


def run_tgpt_async(message, provider="sky", system_prompt=None, api_key=None, timeout=60):
    """
    Run tgpt asynchronously (non-blocking)
    Returns a subprocess.Popen object
    
    Args:
        message: The query/message
        provider: AI provider
        system_prompt: Optional system prompt
        api_key: Optional API key
        timeout: Timeout in seconds
    
    Returns:
        subprocess.Popen object
    """
    tgpt = find_tgpt()
    if not tgpt:
        return None

    cmd = [tgpt, "--provider", provider, "-q"]

    if system_prompt:
        cmd.extend(["-preprompt", system_prompt])

    if api_key:
        cmd.extend(["--key", api_key])
    else:
        key = load_api_key(provider)
        if key:
            cmd.extend(["--key", key])

    cmd.append(message)

    try:
        proc = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        return proc
    except (subprocess.SubprocessError, OSError):
        return None


def check_tgpt_installed():
    """Check if tgpt is installed and available"""
    return find_tgpt() is not None


def get_tgpt_version():
    """Get tgpt version if available"""
    tgpt = find_tgpt()
    if not tgpt:
        return None
    try:
        result = subprocess.run([tgpt, "--version"], capture_output=True, text=True, timeout=5)
        return result.stdout.strip()
    except Exception:
        return None


def list_providers():
    """List available providers"""
    from ks_eye import AVAILABLE_PROVIDERS
    return AVAILABLE_PROVIDERS


def get_provider_info(provider):
    """Get info about a provider"""
    provider_info = {
        "sky": {"name": "Sky", "free": True, "description": "Free, fast, default provider"},
        "phind": {"name": "Phind", "free": True, "description": "Free, code-focused AI"},
        "deepseek": {"name": "DeepSeek", "free": False, "description": "Advanced AI model"},
        "gemini": {"name": "Google Gemini", "free": False, "description": "Google's AI model, good for research"},
        "groq": {"name": "Groq", "free": False, "description": "Fast inference engine"},
        "openai": {"name": "OpenAI GPT", "free": False, "description": "OpenAI's GPT model"},
        "ollama": {"name": "Ollama", "free": True, "description": "Local AI (requires Ollama installed)"},
        "kimi": {"name": "Kimi", "free": True, "description": "Free AI provider"},
        "isou": {"name": "iSou", "free": True, "description": "Free search-based AI"},
        "pollinations": {"name": "Pollinations", "free": True, "description": "Free generative AI"},
    }
    return provider_info.get(provider, {"name": provider, "free": False, "description": "Unknown provider"})
