from dagster import AssetExecutionContext, AssetKey
from dagster_dlt import DagsterDltResource, DagsterDltTranslator, dlt_assets
from dagster_dlt.translator import DltResourceTranslatorData
import dlt
from dlt.sources.filesystem import filesystem as src_fs
import polars as pl 
import ast 

from ...constants import DUCKDB_PATH

dlt_resource = DagsterDltResource()

# Define custom translator to add dependencies
class DuckPondTranslator(DagsterDltTranslator):
    def get_asset_spec(self, data: DltResourceTranslatorData):
        default_spec = super().get_asset_spec(data)
        return default_spec.replace_attributes(
            deps=[AssetKey("dlt_source_swamp_data")]
        )


@dlt.source
def source():
    def process_data(date_df):
        def process_hits(hits):
            try:
                return ast.literal_eval(hits)
            except Exception as e:
                return None
            
        hits_df = date_df.select(['visit_id', 'full_visitor_id', 'hits']).to_pandas()
        hits_df['hits'] = hits_df['hits'].apply(process_hits)
        hits_df = hits_df.dropna(subset=['hits'])

        sessions_df = date_df.select([
            'visit_id', 'full_visitor_id', 'visit_number', 'visit_start_time', 'date',
            'device', 'geo_network', 'totals', 'traffic_source'
        ])
        processed_df = sessions_df.join(pl.DataFrame(hits_df), on=['visit_id','full_visitor_id'], how='inner')
        return processed_df.to_dicts()

    @dlt.resource(name="pond_data",max_table_nesting=3)
    def extract_data():
        for file_object in src_fs(bucket_url="s3://duck-lake/data-swamp/daily/swamp_data/", file_glob="*.parquet"):
            scan = pl.scan_parquet(file_object['file_url'])
            
            # Get unique months
            months = (scan.select(pl.col("date").str.slice(0, 6).unique().alias("month"))
                     .collect()
                     .get_column("month")
                     .sort()
                     .to_list())
            
            for month in months:
                # Filter to month and get unique dates
                month_scan = scan.filter(pl.col("date").str.slice(0, 6) == month)
                dates = (month_scan.select("date")
                        .unique()
                        .collect()
                        .get_column("date")
                        .sort()
                        .to_list())
                
                for date in dates:
                    # Process one date at a time with streaming
                    date_df = (month_scan.filter(pl.col("date") == date)
                             .collect(streaming=True))
                    yield from process_data(date_df)

    return extract_data

@dlt_assets(
    dlt_source=source(),
    dlt_pipeline=dlt.pipeline(
        pipeline_name="fill_duck_pond",
        destination=dlt.destinations.duckdb(str(DUCKDB_PATH)),  # Convert Path to string here
        dataset_name="source_data",
        progress="log"
    ),
    name="fill_duck_pond",
    dagster_dlt_translator=DuckPondTranslator()
)
def fill_duck_pond(context: AssetExecutionContext, dlt: DagsterDltResource):
    yield from dlt.run(
        context=context
    )