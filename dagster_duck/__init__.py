from dagster import Definitions, AssetSpec
from dagster_dlt import DagsterDltResource
from dagster_dbt import DbtCliResource 
from .assets import data_swamp_asset, duck_pond_asset, dbt_asset, iceberg_asset

from .constants import DBT_PROJECT_DIR

# Define external asset
source_file = AssetSpec(
    "s3_source_data",
    description="Google Analytics data in S3 located at s3://duck-lake/data-swamp/train_v2.csv"
)

dbt_resource = DbtCliResource(
    project_dir=DBT_PROJECT_DIR,
)

defs = Definitions(
   assets=[source_file, *data_swamp_asset, *duck_pond_asset, *dbt_asset, *iceberg_asset],
   resources={
       "dlt": DagsterDltResource(),
       "dbt": dbt_resource,
   }
)