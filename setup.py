from setuptools import setup, find_packages

setup(
    name="fda-finance-ai",
    version="1.0.0",
    description="Finance Data Analysis & AI Automation Dashboard",
    author="Antigravity Team",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "streamlit>=1.30.0",
        "pandas>=2.0.0",
        "numpy>=1.24.0",
        "altair>=5.0.0",
        "pillow>=10.0.0",
        "requests>=2.30.0",
    ],
    entry_points={
        "console_scripts": [
            "fda-dashboard=app:main",
        ],
    },
    python_requires=">=3.10",
)
