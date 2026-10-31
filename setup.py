from setuptools import setup, find_packages

setup(
    name="sitepulse",
    version="0.1.0",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=5.0.0",
        "click>=8.1.0",
        "rich>=13.7.0",
    ],
    extras_require={
        "dev": ["pytest>=8.0.0", "pytest-cov>=4.1.0"],
    },
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "sitepulse=sitepulse.cli:main",
        ],
    },
)
