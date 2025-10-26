with raw_data as (
    select *
    from {{ source('raw', 'sales') }}
)

select
    id,
    order_id,
    customer_id,
    amount,
    created_at
from raw_data
