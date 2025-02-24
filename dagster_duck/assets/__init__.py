from dagster import load_assets_from_package_module

from . import fill_data_swamp, fill_duck_pond, filter_duck_pond

data_swamp_asset = load_assets_from_package_module(
    package_module=fill_data_swamp, 
    group_name="ga_sessions_pipeline"
) 

duck_pond_asset = load_assets_from_package_module(
    package_module=fill_duck_pond,
    group_name="ga_sessions_pipeline"
)

duck_pond_dbt_asset = load_assets_from_package_module(
    package_module=filter_duck_pond,
    group_name="ga_sessions_pipeline"
)

__all__ = ["data_swamp_asset", "duck_pond_asset"]
