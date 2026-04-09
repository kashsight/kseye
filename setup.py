from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="kseye",
    version="3.0.0",
    author="KashSight Platform",
    author_email="kashsightplatform@gmail.com",
    description="AI-Human Collaborative Research Assistant — Step-by-step guided research with human oversight",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/kashsightplatform/kseye",
    license="Proprietary — KashSight Platform",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: Science/Research",
        "License :: Other/Proprietary License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Education :: Computer Aided Instruction (CAI)",
    ],
    keywords="research ai academic scholar parallel agents terminal",
    packages=find_packages(),
    python_requires=">=3.7",
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
    project_urls={
        "Bug Reports": "https://github.com/kashsightplatform/kseye/issues",
        "Source": "https://github.com/kashsightplatform/kseye",
        "Documentation": "https://github.com/kashsightplatform/kseye/blob/main/README.md",
    },
)
