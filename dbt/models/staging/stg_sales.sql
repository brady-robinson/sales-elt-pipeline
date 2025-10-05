with raw as (
    select
        id::int as id,
        order_id::varchar as order_id,
        customer_id::varchar as customer_id,
        cast(amount as float) as amount,
        created_at
    from {{ source('raw','sales') }}
)

select * from raw
