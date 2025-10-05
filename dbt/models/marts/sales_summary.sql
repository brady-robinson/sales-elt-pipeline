with base as (
    select
        customer_id,
        date_trunc('day', created_at) as day,
        amount
    from {{ ref('stg_sales') }}
)

select
    day,
    count(*) as orders,
    sum(amount) as total_amount,
    avg(amount) as avg_amount
from base
group by day
order by day
