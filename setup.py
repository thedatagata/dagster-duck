from setuptools import find_packages, setup

setup(
    name="dagster_duck",
    packages=find_packages(exclude=["dagster_duck_tests"]),
    install_requires=[
        "dagster",
        "dagster-cloud",
        "dagster-dlt",
        "dagster-dbt",
        "dbt-core", 
        "dbt-duckdb",
        "polars",
        "pandas",
        "duckdb",
        "dlt[duckdb,filesystem,parquet,pyiceberg]",
        "pyarrow"
    ],
    extras_require={"dev": ["dagster-webserver", "pytest"]},
)
