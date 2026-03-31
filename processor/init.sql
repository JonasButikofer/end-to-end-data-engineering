-- Orders table
CREATE TABLE orders (
    sales_order_id UUID PRIMARY KEY,
    revision_number INTEGER,
    status INTEGER,
    online_order_flag INTEGER,
    sales_order_number TEXT,
    purchase_order_number TEXT,
    account_number TEXT,
    customer_id INTEGER,
    sales_person_id TEXT,
    territory_id INTEGER,
    bill_to_address_id INTEGER,
    ship_to_address_id INTEGER,
    ship_method_id INTEGER,
    credit_card_id TEXT,
    credit_card_approval_code TEXT,
    currency_rate_id TEXT,
    sub_total NUMERIC,
    tax_amt NUMERIC,
    freight NUMERIC,
    total_due NUMERIC,
    comment TEXT,
    due_date TIMESTAMP,
    order_date TIMESTAMP,
    ship_date TIMESTAMP,
    last_modified TIMESTAMP
);

-- Order Details table
CREATE TABLE order_details (
    sales_order_detail_id UUID PRIMARY KEY,
    sales_order_id UUID REFERENCES orders(sales_order_id),
    carrier_tracking_number TEXT,
    order_qty INTEGER,
    product_id INTEGER,
    special_offer_id INTEGER,
    unit_price NUMERIC,
    unit_price_discount NUMERIC,
    line_total NUMERIC,
    last_modified TIMESTAMP
);

-- Export Tracking table
CREATE TABLE processor_metadata (
    id TEXT PRIMARY KEY,
    last_export TIMESTAMP
);