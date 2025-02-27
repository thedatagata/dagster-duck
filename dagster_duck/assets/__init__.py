from dagster import load_assets_from_package_module, AssetSpec

# Define external asset
source_file = AssetSpec(
    "s3_source_data",
    description="Google Analytics data in S3 located at s3://duck-lake/data-swamp/train_v2.csv"
)

from . import fill_data_swamp, fill_duck_pond, filter_duck_pond, freeze_duck_pond

data_swamp_asset = load_assets_from_package_module(
    package_module=fill_data_swamp
) 

duck_pond_asset = load_assets_from_package_module(
    package_module=fill_duck_pond
)

dbt_asset = load_assets_from_package_module(
    package_module=filter_duck_pond
)

iceberg_asset = load_assets_from_package_module(
    package_module=freeze_duck_pond
)

__all__ = ["source_file", "data_swamp_asset", "duck_pond_asset", "dbt_asset", "iceberg_asset"]
