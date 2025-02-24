from dagster import AssetExecutionContext
from dagster_dlt import DagsterDltResource, dlt_assets
import dlt
from dlt.sources.filesystem import filesystem as src_fs
import polars as pl
import pendulum

dlt_resource = DagsterDltResource()

@dlt.source
def source():
    def process_data(df):
        days = df.select("date").unique().collect().get_column("date").sort()
        for day in days:
            yield df.filter(pl.col("date") == day).collect(streaming=True).to_dicts()
            

    @dlt.resource(
        name="swamp_data",
        primary_key=["fullVisitorId", "visitId"],
        write_disposition="replace",
        file_format="parquet"
    )
    def extract_data():
        for file_object in src_fs(
            bucket_url="s3://duck-lake/data-swamp/",
            file_glob="*.csv",
        ):
            ga_scan = pl.scan_csv(
                file_object['file_url'],
                infer_schema=False,
                ignore_errors=True,
                low_memory=True,
                encoding='utf8-lossy'
            )

        months = (ga_scan.select(pl.col("date").str.slice(0, 6).unique().alias("month"))
                        .collect()
                        .get_column("month")
                        .sort()
                        .to_list())
        
        for month in months:
            df = ga_scan.filter(pl.col("date").str.slice(0, 6) == month)
            yield from process_data(df)
            
    return extract_data

@dlt_assets(
    dlt_source=source(),
    dlt_pipeline=dlt.pipeline(
        pipeline_name="fill_data_swamp",
        destination=dlt.destinations.filesystem(
            bucket_url="s3://duck-lake/data-swamp/",  
            layout="{table_name}/{load_id}.{file_id}__{timestamp_ms}.{ext}",
            current_datetime=pendulum.now()
        ),
        dataset_name="daily",
        progress="log"
    ),
    name="fill_data_swamp",
    group_name="ga_sessions_pipeline"
)
def fill_data_swamp(context: AssetExecutionContext, dlt: DagsterDltResource):
    yield from dlt.run(
        context=context
    )