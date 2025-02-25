from dagster import AssetExecutionContext
from dagster_dlt import DagsterDltResource, dlt_assets
import dlt
from dlt.destinations import filesystem as dest_fs
import polars as pl 
import duckdb

from pathlib import Path
PROJECT_ROOT = Path(__file__).parent.parent.parent.parent.resolve()
DATA_DIR = PROJECT_ROOT / "data"
DATA_DIR.mkdir(exist_ok=True)
DUCKDB_PATH = DATA_DIR / "duck_pond.duckdb"

dlt_resource = DagsterDltResource()

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
        conn = duckdb.connect(DUCKDB_PATH)
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
    group_name="ga_sessions_pipeline"
)
def freeze_duck_pond(context: AssetExecutionContext, dlt: DagsterDltResource):
    yield from dlt.run(
        context=context
    )