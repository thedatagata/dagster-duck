from dagster import AssetExecutionContext, AssetKey
from dagster_dbt import DbtCliResource, DbtProject, dbt_assets, DagsterDbtTranslator

from ...constants import DBT_PROJECT_DIR, DBT_MANIFEST_PATH

# Initialize the dbt project
dbt_project = DbtProject(
    project_dir=DBT_PROJECT_DIR,
)

# This will generate the manifest.json in development mode when using dagster dev
dbt_project.prepare_if_dev()

# Create custom translator to handle dependencies
class FilterDuckPondTranslator(DagsterDbtTranslator):
    def get_asset_deps(self, dbt_resource_props):
        # Start with standard dependencies
        deps = super().get_asset_deps(dbt_resource_props)
        # Add dependency on fill_duck_pond
        deps.append(AssetKey("dlt_source_pond_data"))
        return deps

@dbt_assets(
    manifest=DBT_MANIFEST_PATH,
    dagster_dbt_translator=FilterDuckPondTranslator()
)
def filter_duck_pond(context: AssetExecutionContext, dbt: DbtCliResource):
    """Assets representing the dbt models in the dagster_duck_models project."""
    # Run dbt build command to execute the dbt models
    yield from dbt.cli(["build"], context=context).stream()

