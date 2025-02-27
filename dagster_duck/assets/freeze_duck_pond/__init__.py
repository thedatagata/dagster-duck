from dagster import AssetExecutionContext, AssetKey
from dagster_dlt import DagsterDltResource, DagsterDltTranslator, dlt_assets
from dagster_dlt.translator import DltResourceTranslatorData
import dlt
from dlt.destinations import filesystem as dest_fs
import polars as pl 
import duckdb

from ...constants import DUCKDB_PATH

dlt_resource = DagsterDltResource()

# Define custom translator to handle dependencies
class FreezeDuckPondTranslator(DagsterDltTranslator):
    def get_asset_spec(self, data: DltResourceTranslatorData):
        default_spec = super().get_asset_spec(data)
        return default_spec.replace_attributes(
            deps=[AssetKey("stg_users_dim")]
        )

@dlt.source
def source():
    def process(df: pl.DataFrame, chunk_size: int = 25000):
        for chunk in df.iter_slices(n_rows=chunk_size):            
            yield chunk.to_dicts()

    @dlt.resource(
        name="stg_users_dim",
        table_format="iceberg",
        primary_key="user_id", 
        write_disposition={"disposition":"merge", "strategy":"delete-insert"}
    )
    def extract_data():
        conn = duckdb.connect(str(DUCKDB_PATH))  # Convert Path to string here
        df = conn.execute("SELECT * FROM source_data.stg_users_dim").pl()
        conn.close()
        yield from process(df)

    return extract_data


@dlt_assets(
    dlt_source=source(),
    dlt_pipeline=dlt.pipeline(
        pipeline_name="freeze_duck_pond",
        destination=dest_fs(bucket_url="s3://duck-lake/data-pond/"),
        dataset_name="staging",
        progress="log"
    ),
    name="freeze_duck_pond",
    dagster_dlt_translator=FreezeDuckPondTranslator()
)
def freeze_duck_pond(context: AssetExecutionContext, dlt: DagsterDltResource):
    yield from dlt.run(
        context=context
    )