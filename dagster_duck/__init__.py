from dagster import Definitions
from dagster_dlt import DagsterDltResource
from dagster_dbt import DbtCliResource 
from .assets import data_swamp_asset, duck_pond_asset, duck_pond_dbt_asset

from .constants import DBT_PROJECT_DIR

dbt_resource = DbtCliResource(
    project_dir=DBT_PROJECT_DIR,
)

defs = Definitions(
   assets=[*data_swamp_asset, *duck_pond_asset, *duck_pond_dbt_asset],
   resources={
       "dlt": DagsterDltResource(),
       "dbt": dbt_resource,
   }
)