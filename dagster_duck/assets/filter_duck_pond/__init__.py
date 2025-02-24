
from dagster import AssetExecutionContext
from dagster_dbt import DbtCliResource, DbtProject, dbt_assets

from ...constants import DBT_PROJECT_DIR, DBT_MANIFEST_PATH

# Initialize the dbt project
dbt_project = DbtProject(
    project_dir=DBT_PROJECT_DIR,
)

# This will generate the manifest.json in development mode when using dagster dev
dbt_project.prepare_if_dev()

@dbt_assets(manifest=DBT_MANIFEST_PATH)
def filter_duck_pond(context: AssetExecutionContext, dbt: DbtCliResource):
    """Assets representing the dbt models in the dagster_duck_models project."""
    # Run dbt build command to execute the dbt models
    yield from dbt.cli(["build"], context=context).stream()

