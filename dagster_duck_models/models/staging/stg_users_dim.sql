{{
  config(
      materialized='incremental',
      unique_key='user_id',
      incremental_strategy='delete+insert'
  )
}}

SELECT
 user_id,
 MIN(session_date) as first_session_date,
 MAX(session_date) as last_session_date,
 MAX(session_start_time) as last_session_time,
 COUNT(DISTINCT session_id) as total_sessions,
 SUM(session_totals__pageviews) as total_pageviews,
 AVG(session_totals__time_on_site) as avg_time_on_site,
 MAX(session_device__browser) as primary_browser,
 MAX(session_device__device_category) as primary_device,
 MAX(session_geo__country) as primary_country,
 MAX(session_geo__continent) as primary_continent,
 COUNT(DISTINCT session_traffic_source__source) as distinct_traffic_sources,
 MAX(session_traffic_source__source) as last_traffic_source,
 MAX(session_traffic_source__medium) as last_traffic_medium,
 MAX(session_traffic_source__campaign) as last_campaign
FROM {{ ref('src_sessions_fct') }} base
{% if is_incremental() %}
WHERE user_id IN (
  SELECT DISTINCT user_id 
  FROM {{ ref('src_sessions_fct') }} inc
  WHERE inc.session_start_time > (SELECT MAX(this.last_session_time) FROM {{ this }} as this)
)
{% endif %}
GROUP BY user_id