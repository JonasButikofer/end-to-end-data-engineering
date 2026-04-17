# Writing Agent-Friendly Data Documentation

When an AI agent connects to your dbt project through the MCP server, the only thing it has to understand your data is what you've written in the `description` fields of your YAML files. The agent can't look at sample data, can't read your mind, and can't infer business context from column names alone. Your descriptions ARE the agent's understanding of your data.

This guide will help you write descriptions that make your data genuinely useful to agents (and, as a bonus, to every human who reads your project).

---

## Why This Matters

Think about what happens when someone asks an agent: "What were our top-selling products last month?"

The agent needs to:
1. Figure out which model contains sales data
2. Understand what "product" means in your schema
3. Find the right columns for revenue and dates
4. Know how to join product information to sales data
5. Understand the grain (is each row an order? a line item? a daily aggregate?)

If your model description says "Staging model for orders," the agent is mostly guessing. If it says "Each row is one sales order line item from the e-commerce system, with one row per product per order. Join to stg_adventure_db__products via product_id to get product names and categories," the agent can confidently build the right query.

---

## Model Description Principles

Every model description should answer these questions:

1. **What business entity or event does each row represent?**
   - "Each row is one customer order"
   - "Each row is one product inventory snapshot"
   - "Each row is one customer support chat session"

2. **What is the grain?**
   - "Grain: one row per order" (NOT "one row per customer per order")
   - "Grain: one row per line item per order"
   - "Grain: one row per chat session"

3. **What are the key relationships to other models?**
   - "Join to stg_customers via customer_id"
   - "Downstream: used by int_orders_with_customers"

4. **Are there important caveats?**
   - "Excludes cancelled orders"
   - "Only includes orders from the past 90 days"
   - "Chat logs may contain multiple messages per session"

**Target length**: 2-4 sentences per model.

### Good Example

```yaml
- name: stg_ecom__sales_orders
  description: >
    Each row represents a single sales order from the e-commerce PostgreSQL source.
    Grain: one row per order. This staging model applies basic cleaning (trimming
    whitespace, casting dates) to raw order data. Join to stg_adventure_db__customers
    via customer_id for customer details, or to int_sales_order_line_items via
    order_id for individual product line items.
```

### Bad Example

```yaml
- name: stg_ecom__sales_orders
  description: "Staging model for sales orders"
```

The bad example tells the agent almost nothing. What's a "sales order"? What's the grain? How does it relate to other models?

---

## Column Description Principles

Every column description should explain:

1. **What the column represents in business terms**
   - Not just "Customer ID" for `customer_id`
   - Instead: "Unique identifier for the customer who placed this order"

2. **Whether it's a key column and what it joins to**
   - "Primary key for this table"
   - "Foreign key to stg_adventure_db__customers.customer_id"

3. **Any special meaning, encoding, or edge cases**
   - "1 = active, 0 = inactive"
   - "Can be null for guest checkout orders"
   - "Stored in UTC"

4. **The source of the data (for staging models)**
   - "Source: PostgreSQL ecom.sales_orders.order_date"

**Target length**: 1-2 sentences per column.

### Good Example

```yaml
columns:
  - name: order_id
    description: >
      Unique identifier for this sales order. Primary key.
      Source: PostgreSQL ecom.sales_orders.order_id.
      Join to int_sales_order_line_items.order_id for line item details.
  - name: customer_id
    description: >
      Identifier of the customer who placed this order.
      Foreign key to stg_adventure_db__customers.customer_id.
      Use this join to get customer name, email, and demographics.
  - name: order_date
    description: >
      Date and time the customer placed this order, in UTC.
      Used for time-based analysis like orders per month or daily revenue.
  - name: total_amount
    description: >
      Total dollar amount for this order before tax and shipping.
      Sum of all line item amounts. Can be zero for fully discounted orders.
  - name: status
    description: >
      Current status of the order. Values: 'pending', 'shipped', 'delivered',
      'cancelled'. Only non-cancelled orders are included in revenue calculations.
```

### Bad Example

```yaml
columns:
  - name: order_id
    description: "Order ID"
  - name: customer_id
    description: "Customer ID"
  - name: order_date
    description: "Date"
  - name: total_amount
    description: "Amount"
  - name: status
    description: "Status"
```

---

## Anti-Patterns: What NOT to Do

1. **Don't duplicate the column name in the description.**
   Bad: `order_id: "The order id"`
   Good: `order_id: "Unique identifier for this sales order. Primary key."`

2. **Don't assume the agent knows the business domain.**
   Bad: `campaign_id: "Campaign identifier"`
   Good: `campaign_id: "Identifier for the email marketing campaign that generated this order. Foreign key to stg_ecom__email_campaigns.campaign_id. Null if the order was not attributed to a campaign."`

3. **Don't skip descriptions for "obvious" columns.**
   Even `created_at` needs context: is it UTC? Is it the record creation time or the event time? Does it come from the source system or the warehouse?

4. **Don't include SQL syntax or technical implementation details.**
   Bad: `"Computed as COALESCE(discount_pct, 0) * unit_price"`
   Good: `"The discount amount applied to this line item. Zero if no discount was applied."`

5. **Don't use abbreviations without explanation.**
   Bad: `"SCD Type 2 flag"`
   Good: `"Indicates whether this customer record is the current version (1) or a historical snapshot (0). Used for slowly changing dimension tracking."`

---

## Before/After Examples

### Example 1: Staging Model

```yaml
# BEFORE
- name: stg_real_time__chat_logs
  description: "Chat logs staging"
  columns:
    - name: chat_id
      description: "Chat ID"
    - name: customer_id
      description: "Customer"
    - name: message
      description: "Message text"
    - name: created_at
      description: "Timestamp"

# AFTER
- name: stg_real_time__chat_logs
  description: >
    Each row is one customer support chat session from the MongoDB source.
    Grain: one row per chat session. Contains the full conversation text
    and metadata. Join to stg_adventure_db__customers via customer_id
    to get customer details. Used downstream by int_chats_by_customer
    for customer service analytics.
  columns:
    - name: chat_id
      description: >
        Unique identifier for this chat session. Primary key.
        Source: MongoDB support_logs.chats._id (converted from ObjectId to string).
    - name: customer_id
      description: >
        Identifier of the customer who initiated this chat session.
        Foreign key to stg_adventure_db__customers.customer_id.
        Can be null for anonymous/unauthenticated chat sessions.
    - name: message
      description: >
        Full text of the customer support conversation. Contains the
        complete chat transcript. May include multiple messages from
        both the customer and support agent in a single text field.
    - name: created_at
      description: >
        Timestamp when the chat session was initiated, in UTC.
        Source: MongoDB document creation timestamp.
```

### Example 2: Intermediate Model

```yaml
# BEFORE
- name: int_sales_order_line_items
  description: "Order line items"
  columns:
    - name: line_item_id
      description: "Line item ID"
    - name: order_id
      description: "Order ID"
    - name: product_id
      description: "Product"
    - name: quantity
      description: "Qty"
    - name: unit_price
      description: "Price"

# AFTER
- name: int_sales_order_line_items
  description: >
    Each row is one product line item within a sales order. Grain: one row
    per product per order. This intermediate model joins raw order details
    with product information to create a complete line-item view. Upstream:
    stg_ecom__sales_orders (via order_id) and stg_adventure_db__products
    (via product_id). Used for revenue analysis, product performance, and
    order composition reporting.
  columns:
    - name: line_item_id
      description: >
        Unique identifier for this line item. Primary key. Composite of
        order_id and product_id in the source system.
    - name: order_id
      description: >
        Sales order this line item belongs to. Foreign key to
        stg_ecom__sales_orders.order_id. Multiple line items can share
        the same order_id (one per product in the order).
    - name: product_id
      description: >
        Product purchased in this line item. Foreign key to
        stg_adventure_db__products.product_id. Join to get product
        name, category, and vendor information.
    - name: quantity
      description: >
        Number of units of this product purchased in this line item.
        Always a positive integer. Used to calculate line item revenue
        (quantity * unit_price).
    - name: unit_price
      description: >
        Price per unit of this product at the time of purchase, in USD.
        May differ from the product's current list price due to promotions
        or price changes.
```

### Example 3: Source Definition

```yaml
# BEFORE
- name: raw_sales_orders
  description: "Raw orders"

# AFTER
- name: raw_sales_orders
  description: >
    Raw sales order data loaded from PostgreSQL via the Python ETL processor.
    Each row is one order. Data arrives via Snowflake internal stage with
    COPY INTO. Updated incrementally using watermark timestamps. This is
    the source for stg_ecom__sales_orders.
```

---

## Checklist

Before you consider your documentation complete, verify:

- [ ] Every model has a description (no empty descriptions)
- [ ] Every model description states the grain (what each row represents)
- [ ] Every model description mentions key relationships to other models
- [ ] Every column has a description (no empty descriptions)
- [ ] Column descriptions explain business meaning, not just echo the column name
- [ ] Primary key columns are identified as such
- [ ] Foreign key columns name the target model and column
- [ ] Date/time columns specify the timezone
- [ ] Status/flag columns explain possible values
- [ ] Descriptions use plain English, not SQL syntax or technical jargon
- [ ] No abbreviations are used without explanation

---

## Where to Add Descriptions

All model and column descriptions go in your YAML files, typically:

- `dbt/models-m1/models.yml` (if you use a single file)
- `dbt/models-m1/staging/sources.yml` (for source definitions)
- Or individual `_schema.yml` files alongside your models

The `description:` field goes at the model level and at the column level within each model. Use YAML multi-line strings (`>` or `|`) for longer descriptions to keep the file readable.

```yaml
models:
  - name: my_model
    description: >
      Multi-line description goes here.
      This is a continuation of the same paragraph.
    columns:
      - name: my_column
        description: >
          Column description goes here.
```
