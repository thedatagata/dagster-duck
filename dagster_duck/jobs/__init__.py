from dagster import define_asset_job
from ..assets import data_swamp_asset, duck_pond_asset

daily_processing_job = define_asset_job(
   name="daily_processing_job",
   selection=[*data_swamp_asset, *duck_pond_asset]
)