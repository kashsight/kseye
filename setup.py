"""ks-eye — Online AI Research Platform"""

from setuptools import setup, find_packages

setup(
    name="kseye",
    version="2.0.0",
    description="Online AI Research Platform — Scrape real websites, AI reads & analyzes, produces structured reports",
    author="KashSight Platform",
    packages=find_packages(),
    install_requires=[
        "click>=8.0",
        "rich>=13.0",
    ],
    extras_require={
        "docx": ["python-docx>=0.8.11"],
    },
    entry_points={
        "console_scripts": [
            "kseye=ks_eye.cli:main",
            "ks-eye=ks_eye.cli:main",
        ],
    },
    python_requires=">=3.8",
)
