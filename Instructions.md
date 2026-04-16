# Final Project // Milestone 1: Full-Stack Data Pipeline Integration

Well, my friends. We're here. The journey has been long and arduous, but we've learned a lot along the way. And to help you demonstrate (to me, a future interviewer, and most importantly, to _yourself_) that you have indeed learned _a ton_ here in this class, this final project will bring it all together in a single flow. This project (across the three milestones) will be your finest work yet, and something you will be proud and excited to talk about with your future employers.

As you might expect, this project will flow a bit differently compared to the labs we've worked on. Each of those labs was an extremely detailed, close-up view of how to use a particular technology to accomplish something that relates to data engineering. There was plenty of "learn by doing" in which I asked you to explore some things, teach yourself about how to accomplish something, and gave you fairly particular requirements about what the end product should look like.

By contrast, this project will be much more "zoomed out", and you'll be asked to build various components of a full data pipeline with much less guidance from me. Nearly everything I'm asking you to do will be something that we have already done in a prior lab assignment. (The few new things I'm adding in will be accompanied by some detailed examples and a video walkthrough explaining anything you need to know.)

## Project Scenario

My plan is to treat this project like a real-world data team project. I will be acting as your manager, and you'll be given tasks that I would ask a junior member of my team to accomplish. In a real-world project, managers don't usually do a lot of hand-holding (nor do you want them to!). Instead, a good manager will ask you to work on something, give clear guidelines and context about what you're supposed to accomplish and why, but not get lost in the details. Very soon, you'll join a team in the workforce, and this is 100% the type of situation you'll find yourself in. So we're going to give you some exposure to that.

As usual, I've broken down the milestone into five key tasks. For each, I'll describe the goal in managerial terms and list specific objectives you should meet. Remember, these are high-level requirements, and you'll need to determine how to achieve them using the skills and tools you've acquired over the course of the semester.

And here's a rough idea of what the ending file system looks like. As you'll find out below, I'm not being prescriptive about how you name things, so this is just here in case it's helpful.

```bash
is-566-11-final-project-1
├─ README.md
├─ compose.yml
├─ .env.sample
├─ dbt
│ ├─ analyses
│ │ ├─ campaign_sales_analysis.sql
│ │ └─ email_campaign_performance.sql
│ ├─ dbt_project.yml
│ ├─ models-m1
│ │ ├─ intermediate
│ │ │  ├─ int_sales_order_line_items.sql
│ │ │  └─ int_sales_orders_with_campaign.sql    # <-- Task 4
│ │ ├─ models.yml
│ │ └─ staging
│ │    ├─ adventure_db
│ │    │  ├─ stg_adventure_db__customers.sql
│ │    │  ├─ stg_adventure_db__inventory.sql
│ │    │  ├─ stg_adventure_db__product_vendors.sql
│ │    │  ├─ stg_adventure_db__products.sql
│ │    │  └─ stg_adventure_db__vendors.sql
│ │    ├─ ecom
│ │    │  ├─ base
│ │    │  │  ├─ base_ecom__email_campaigns.sql
│ │    │  │  ├─ base_ecom__email_mktg_new.sql
│ │    │  │  └─ base_ecom__sales_orders.sql
│ │    │  ├─ stg_ecom__email_campaigns.sql
│ │    │  ├─ stg_ecom__purchase_orders.sql
│ │    │  └─ stg_ecom__sales_orders.sql          # <-- Task 3
│ │    ├─ real_time                              # <-- Task 3
│ │    │  ├─ base                                # <-- Task 3
│ │    │  │  └─ base_real_time__sales_orders.sql # <-- Task 3
│ │    │  └─ stg_real_time__chat_logs.sql        # <-- Task 3
│ │    └─ sources.yml                            # <-- Task 3
│ ├─ seeds
│ │ ├─ _seeds.yml
│ │ ├─ measures.csv
│ │ └─ ship_method.csv
│ └─ tests
│   ├─ no_negative_inventory_amounts.sql
│   ├─ preferred_vendors_have_credit.sql
│   ├─ products_sell_end_date_is_null.sql
│   └─ single_conversion_per_order.sql
├─ sql
│ ├─ check_data_flow_queries.sql
│ └─ create_raw_tables.sql                             # <-- Task 2
├─ processor
│ ├─ Dockerfile                # <-- Task 1
│ ├─ etl
│ │ ├─ extract.py
│ │ └─ load.py                 # <-- Tasks 1 & 2
│ ├─ init.sql
│ ├─ main.py                   # <-- Tasks 1 & 2
│ ├─ pyproject.toml
│ └─ utils
│   ├─ connections.py
│   ├─ env_loader.py
│   └─ watermark.py
├─ scratch.sql
└─ screenshots
```

> [!TIP]
> Despite my desire for this to feel like a real-world project and encouraging you to use some autonomy, that doesn't mean I'm not here to help. As usual, we'll try to balance this appropriately. But you'll be free to choose how you go about your solution without strict guidelines, and I'll plan to just be around to answer questions, help troubleshoot, etc.
>
> Note also: Unlike the last dbt lab, there are no tricks or "gotcha's" built into this assignment (at least not intentionally...). I'm much more interested in you _making it through_ the full data pipeline experience rather than experiencing some real-world pain along the way.

I couldn't be more excited for you. Let's do it.

---

## Task 1: Containerized Python ETL Microservice

Our team needs a lightweight ETL microservice to regularly collect data from two production systems and prepare it for our data warehouse. I'm tasking you with building a Python-based ETL process that connects to our two transactional databases (one PostgreSQL, one MongoDB), extracts the latest data, and lands it into an internal Snowflake stage for further processing. This service must be packaged as a Docker container to align with our deployment standards. We have some existing utility code to get you started, but you'll need to understand that codebase and integrate your work into it. Treat this as if you're joining an ongoing project, the framework is there, and you're adding a new component to meet our goals.

The processor will also handle loading and cleanup in Task 2, so this task focuses on getting extraction and staging working correctly first.

- **Build a Python ETL process**: Develop a script or module that connects to the PostgreSQL and MongoDB sources and retrieves the required data (e.g. recent transactions related to our multi-week Adventure data scenario). Ensure the ETL logic can handle data from both sources and format it as needed for loading. There are two sales tables to extract from the PostgreSQL database, and one chat logs collection to extract from MongoDB. Each of these three extractions can be placed in their own stage on Snowflake. (In other words, this python script doesn't need to do any combining; we'll take care of that with dbt downstream.)

> [!TIP]
> Part of the trick to properly pulling data from the two databases will entail using some timestamps and a "watermark" strategy to ensure that you only pull the data that has been added since the last time you queried that particular table. This will likely be a new concept for many, and you can read about the approach [here](https://chatgpt.com/share/67ee02e0-8d58-8010-a090-fb2cae0af5d6). I have provided the functions to implement this strategy, but here is one very helpful tip that will save you a lot of troubleshooting: notice that the two `extract_` functions will filter the data based on a column _in the table/collection that is being queried_. Given this, it would be a good idea to derive your new "watermark" timestamp from the data that you pull down each time (rather than, say, getting the current system time using a `datetime` function). This way, you're always trusting in the same source of timestamps (i.e., the generator service) to compare along a single linear timeline. (Cue the Loki reference!)

- **Use provided code framework**: You'll want to carefully review and understand the provided utility code (e.g. database connection helpers, config loaders, etc.). You'll be integrating your ETL logic into this existing codebase rather than starting from scratch, _just like you would do if you joined a real data team_. This will require you to read and understand the existing code structure and follow the project's coding conventions.

> [!IMPORTANT]
> **Snowflake PAT Authentication**: Since we use Programmatic Access Tokens (PATs) for Snowflake authentication, the `SNOWFLAKE_ROLE` variable in your `.env` is **required**, not optional. Without it, your Snowflake session will default to a role that cannot access the database. Make sure this is set to your assigned role (e.g. `BADGER_ROLE` or whatever role your account uses).

> [!TIP]
> During development, set `PROCESSOR_INTERVAL_SEC=0` in your `.env` to make the processor run one cycle and exit. This is much faster for testing than waiting for the default 5-minute interval. Set it back to `300` (or another value) when you want continuous operation.

- **Export to Snowflake stage**: After extraction (and without really doing any transformations unless you find you need them), the processor should load the data into an internal Snowflake stage. You'll see that there are already utility functions that will handle this for you, including some suggested names for the stages and the schema where you will be landing this data. Ensure that the data from both Postgres and MongoDB sources end up as staged files ready for Snowflake to ingest.
- **Containerize with Docker**: Write a Dockerfile and containerize the entire ETL service. Include all necessary dependencies (Python libraries for PostgreSQL, MongoDB, Snowflake, etc.) in the image. The container should then be configured to run inside the provided Docker Compose environment to ensure that it could run in our company's cloud-based container environment (which is outside the scope of this class...but I'm just making up some context).
- **Test the microservice independently**: Run your containerized ETL service to verify it pulls data correctly from both databases and uploads files to the Snowflake stage. Debug any issues with connectivity (e.g. verifying that the credentials for Postgres and Mongo work as intended both locally and in the Docker Compose environment) and ensure the container logs or outputs indicate that the environment can remain running (if so configured) to constantly generate, process, and load data. The goal is a repeatable ETL process that the rest of our pipeline can depend on.

> [!IMPORTANT]
> The deliverable(s) for this milestone will (I think) just be a few short screen recordings of you showing your full system in action. But this won't happen until Milestone 3 in a couple of weeks. You'll obviously need to submit your code via GitHub by the due date, but you can wait to create this screen recording until I give you some clear direction on how to do so as a part of Milestone 3. For now, you should just carefully doublecheck that this task is doing exactly what has been requested in the high-level instructions.
>
> You'll know that your Task 1 is done when you:
> 1. Have both the generator and processor running, seeing records consistently processed (but not consistently increasing, meaning that you're only pulling and processing new records). If you look at the logs for the processor container in Docker Desktop, you will likely see something similar to the first screenshot below.)
> 2. You can run a `list @orders_stage`, `list @order_details_stage`, and `list @chat_stage` and see files staged there (and being constantly added, given the activity in #1 above). To be extra sure, you may want to first run `remove @orders_stage`, etc., and then make sure that the files being _currently_ generated are landing there in each stage. (See the second screenshot below for a glimpse of what it should look like when you've run a `list` command after clearing out the stage with `remove`.)

<img src="screenshots/readme_img/docker_flowing.png"  width="80%">

<img src="screenshots/readme_img/files_staged.png"  width="80%">



---

## Task 2: Processor-Driven Loading and Stage Cleanup

With data now landing in the Snowflake stages, we need to get those staged files into raw tables so they can feed our dbt models downstream. In many production environments, orchestration tools like Airflow or Prefect handle this loading step. For our project, the Python processor itself will handle loading (COPY INTO) and cleanup (REMOVE) directly, which is simpler and gives us full control of the data lifecycle in one place.

> [!IMPORTANT]
> This milestone does NOT use Snowflake Tasks. Instead, your processor executes COPY INTO and REMOVE commands directly after staging files. This approach is simpler, avoids the risk of runaway credit consumption from tasks left running, and reflects a common real-world pattern where the ETL code owns the full lifecycle.

### 2.1: Create Raw Tables

Before the processor can load data, you need raw tables ready to receive it. Use the provided `sql/create_raw_tables.sql` as a reference for the table schemas, and create these three tables manually in Snowflake:

```sql
USE SCHEMA raw_ext;

CREATE TABLE IF NOT EXISTS orders_raw (
    sales_order_id VARCHAR,
    revision_number INT,
    status VARCHAR,
    online_order_flag BOOLEAN,
    sales_order_number VARCHAR,
    purchase_order_number VARCHAR,
    account_number VARCHAR,
    customer_id VARCHAR,
    sales_person_id VARCHAR,
    territory_id VARCHAR,
    bill_to_address_id VARCHAR,
    ship_to_address_id VARCHAR,
    ship_method_id VARCHAR,
    credit_card_id VARCHAR,
    credit_card_approval_code VARCHAR,
    currency_rate_id VARCHAR,
    sub_total DECIMAL(18, 2),
    tax_amt DECIMAL(18, 2),
    freight DECIMAL(18, 2),
    total_due DECIMAL(18, 2),
    comment VARCHAR,
    due_date TIMESTAMP,
    order_date TIMESTAMP,
    ship_date TIMESTAMP,
    last_modified TIMESTAMP
);

CREATE TABLE IF NOT EXISTS order_details_raw (
    sales_order_detail_id VARCHAR,
    sales_order_id VARCHAR,
    carrier_tracking_number VARCHAR,
    order_qty INT,
    product_id VARCHAR,
    special_offer_id VARCHAR,
    unit_price DECIMAL(18, 2),
    unit_price_discount DECIMAL(18, 2),
    line_total DECIMAL(18, 2),
    last_modified TIMESTAMP
);

CREATE TABLE IF NOT EXISTS chat_logs_raw (
    raw VARIANT
);
```

> [!TIP]
> Use `sql/create_raw_tables.sql` as a reference for the table schemas. The columns match the data your processor extracts.

### 2.2: Implement the Load and Cleanup Functions

The processor's `load.py` module contains three functions. The first one — `upload_dataframe_to_stage()` — is already fully implemented and handles writing DataFrames to CSV/JSON and PUTting them into a Snowflake stage.

The other two are stubs that you need to implement:

- **`copy_stage_to_table()`** — Execute a Snowflake COPY INTO command to load staged files into a raw table. Must handle both CSV and JSON formats and return a metrics dict with `rows_copied`, `rows_skipped`, `execution_time_sec`, `status`, and `error_message`.
- **`clean_stage()`** — Execute a Snowflake REMOVE command to delete staged files after successful loading. Return a metrics dict with `files_removed`, `execution_time_sec`, `status`, and `error_message`.

The function signatures, docstrings, and return contracts are already defined — read them carefully. After implementing these two functions, you'll also need to complete the TODO in `main.py` that loops through the three stages and calls your functions. The extract section and stage list are already provided — you just need to wire up the copy and cleanup calls.

> [!TIP]
> Snowflake's [COPY INTO](https://docs.snowflake.com/en/sql-reference/sql/copy-into-table) and [REMOVE](https://docs.snowflake.com/en/sql-reference/sql/remove) documentation will be your best friends here. You can also use AI assistance — share the function signatures and docstrings with your agent and ask it to implement the logic.

Make sure your `.env` has these set to `true`:
- `PROCESSOR_ENABLE_COPY_INTO=true`
- `PROCESSOR_ENABLE_CLEANUP=true`

The full processor cycle runs in this order:

1. Extract and stage orders
2. Extract and stage order_details
3. Extract and stage chats
4. Copy orders_stage -> orders_raw
5. Copy order_details_stage -> order_details_raw
6. Copy chat_stage -> chat_logs_raw
7. Clean all three stages
8. Log metrics

> [!TIP]
> Your orchestration code should implement a smart pattern: if COPY INTO fails for a stage, skip cleanup for that stage so the files stay available for retry on the next cycle. Store each copy result and check `result["status"]` before cleaning.

### 2.3: Test the Full Cycle

Once you've implemented the functions, rebuild the Docker image and start all services:

```bash
docker compose up --build
```

> [!WARNING]
> **Snowflake credit usage:** Every time the processor runs a cycle, it uses your Snowflake warehouse (which costs credits). The default `PROCESSOR_INTERVAL_SEC=0` runs one cycle and exits — this is the safest option during development. If you change it to `300` for continuous operation, the processor and generator will automatically shut down after 1 hour (`PROCESSOR_MAX_RUNTIME_SEC=3600` in `.env`). You can change this timeout or set it to `0` to run indefinitely — but **remember to stop it when you're done** (`docker compose down`).

Monitor the processor logs. You should see output similar to this for each cycle:

```
============================================================
[2026-03-21T14:30:00+00:00] CYCLE START
============================================================
Found 1234 new records in orders.
Uploading orders_20260321_143000.csv to Snowflake stage orders_stage
Found 5678 new records in order_details.
Uploading order_details_20260321_143000.csv to Snowflake stage order_details_stage
Found 89 new chat logs.
Uploading chat_logs_20260321_143000.json to Snowflake stage chat_stage
COPY orders_stage -> orders_raw: 1234 rows copied, 0 skipped (1.2s)
COPY order_details_stage -> order_details_raw: 5678 rows copied, 0 skipped (1.8s)
COPY chat_stage -> chat_logs_raw: 89 rows copied, 0 skipped (0.6s)
Cleaning orders_stage: 1 files removed (0.3s)
Cleaning order_details_stage: 1 files removed (0.3s)
Cleaning chat_stage: 1 files removed (0.2s)

[2026-03-21T14:30:07+00:00] CYCLE COMPLETE (7.2 sec)
============================================================
```

Verify data is flowing by querying the raw tables:

```sql
SELECT COUNT(*) FROM raw_ext.orders_raw;
SELECT COUNT(*) FROM raw_ext.order_details_raw;
SELECT COUNT(*) FROM raw_ext.chat_logs_raw;
```

And confirm stages are empty after cleanup:

```sql
LIST @orders_stage;
LIST @order_details_stage;
LIST @chat_stage;
```

> [!IMPORTANT]
> 📷 Grab a screenshot of the processor logs showing a complete cycle (extract, stage, copy, cleanup). Save this screenshot as `m1_task2.3.png` (or jpg) to the `screenshots` folder in the assignment repository.

**Success Criteria:**
- Raw tables exist in Snowflake and are being populated.
- Processor logs show successful COPY INTO and REMOVE operations.
- Stages are empty after each cycle (files are cleaned up after loading).
- No Snowflake Tasks have been created.

> [!TIP]
> Depending on how much data accumulated in your stages during Task 1 development, it would be a great idea to manually clear them out before testing Task 2. Use `REMOVE @orders_stage;` etc. to empty them, then let the processor run a fresh cycle.

---

## Task 3: dbt Integration

Now that the raw data from our two sources is flowing into Snowflake automatically, we need to integrate it into our warehouse model. Use dbt to create models that incorporate this raw data into the existing warehouse flow, following the same general workflow (base, stage, intermediate). This step is where you apply your data modeling skills to join, clean, and prepare the data to be incorporated into an intermediate, analysis-focused view. (The specific use case driving this modeling is a sales-monitoring dashboard for the last 30 days of sales, which you'll be building in the next task.) Your job is to use what you have learned about using dbt to incorporate these new sources of data into the broader warehouse environment.

> [!TIP]
> Unlike the last lab assignment, you don't need to worry about whether these builds happen in `dev` or `prod`. We won't use dbt Cloud until Milestone 2, so there's no need to keep track of which one you're building in. I've intentionally pulled the dbt setup from the _solution_ to last week's assignment so that you shouldn't need to change anything in the project or connection profiles. This means that you're almost certainly going to be applying any model changes to the `dbt_dev` schema in your database when you use `dbt build`. (Just sharing this in case it helps you know where to go look for the tables you'll be building out in this task.)

- **Configure sources for new data**: Update your dbt project to declare the new raw data as sources.
- **Develop staging models**: Create (or adapt existing) staging models that select from the raw source data and apply initial transformations/cleaning. Use the same conventions that we have been using in the last two projects, and make smart decisions that you could easily justify. The chat logs can go wherever you'd like them to go, but the two sales tables coming out of the PostgreSQL need to be formatted carefully so that they can be added to the existing sales table and downstream flow.

>[!TIP]
> To be clear, both tables of sales data that are coming out of your docker environment should be carefully added to the existing `stg_ecom__sales_orders` model from the last few weeks. This will require you to (a) be very particular about the format and order of the columns, and (b) figure out how to nest the order detail data into the `order_detail` column that is found in the `stg_ecom__sales_orders` table. (You're essentially going to have to do a lateral flatten in reverse, if that makes sense.) To help narrow your search for how to get this done, I would look into the `ARRAY_AGG()` function.

- **Adhere to dbt best practices**: Organize your models properly in the project structure, probably using the same hierarchy that we've already been using. Again, your goal is to integrate your new functionality into the existing flow of data. (And you can use my directory tree up above if that helps, but you don't have to follow it exactly.)
- **Test and iterate**: Run your dbt models to materialize the new tables, and verify the results. Check that the data looks correct (especially that your newly added data is showing up). The data being generated in the docker environment has _current_ dates, so this will be easy to verify. (Actually, I decided to provide a couple of sample queries to help you make sure you got this right. They are in a separate SQL file here in the repository, and here's a [direct link](https://github.com/byu-is-566/is-566-11-final-project-1-instructions/blob/main/check_data_flow_queries.sql) if that's helpful.) You are also welcome to add a few basic tests that make sense on important fields to validate data integrity, but I'm not going to be overly prescriptive about this. While testing isn't the main focus of this milestone, just find some way to ensure the pipeline's transformations are reliable so the final analytics will be accurate.

> [!IMPORTANT]
> Before moving on, make sure that your system is doing exactly what is being asked in the instructions. We'll take some video evidence in Milestone 3.
>
> When you run the validation queries, you should see results that are similar to the two screenshots I've provided below. The only major difference you should expect between your query results and mine would be the first row where the rows (or items) are being counted; those values will depend on how many records you have accumulated in your warehouse from the docker generator. Otherwise, the proportions should be very similar to mine.

<img src="screenshots/readme_img/query_1.png"  width="80%">

<img src="screenshots/readme_img/query_2.png"  width="80%">

---

## Task 4: Analytical View and Dashboard in Snowsight

With clean, transformed data flowing through dbt, we'll create a dashboard for stakeholders. This is where you prove the entire pipeline works, from source databases all the way through to a visual output that a business user could actually use.

The last step is to present our insights in a user-friendly way. We need an analytical output (i.e., intermediate view like the others we've made) in the warehouse, which will feed a dashboard for visualization. You will create a final dbt model that specifically prepares the data for the sales dashboard, an example of which is provided as a screenshot below. You'll be using Snowflake's "Snowsight" visualization tools to build an interactive dashboard for end users. Again, because this is new territory, I'll provide a [short video overview](https://www.dropbox.com/scl/fi/psq15tg8sl94zbt90f4ma/snowsight-dashboards.mov?rlkey=5fpkvtpb8e0xp7eqlheaytklk&dl=0) to orient you to this tool. The dashboard should highlight sales volume over the past 30 days, over time (e.g. daily) and by the customer's country, as you see in the example below. The expectation is that by the end of this milestone, a stakeholder could open the Snowsight dashboard and immediately see how our sales are trending and which countries are driving those sales.

<img src="screenshots/readme_img/dashboard.png"  width="80%">

- **Create an analytical dbt model**: Develop a top-level dbt model that aggregates or summarizes the sales data for the dashboard. This model likely builds on your silver-layer models from step 3. (For reference, I called mine `int_sales_orders_with_campaign`.) This view will serve as the direct source for your dashboard.
- **Build the Snowsight dashboard**: Using the Snowsight interface in Snowflake, create a new dashboard. Add a chart for sales over time, similar to the one I've provided.
- **Demonstrate end-to-end functionality**: Finally, verify that the _entire_ pipeline works together. Turn on your docker environment to generate data (perhaps with a large batch size?), let your processor run a few cycles to extract, stage, load, and clean, then (manually, for this milestone) execute dbt from your terminal to refresh models. Use the [validation queries I provided](https://github.com/byu-is-566/is-566-11-final-project-1-instructions/blob/main/check_data_flow_queries.sql) in this repository to verify that you are populating the sales data correctly. Finally, confirm that the Snowsight dashboard reflects the new data. This will prove that your containerized ETL, Snowflake loading, dbt transformations, and dashboard are all integrated. By completing this, you've essentially delivered a full-stack data pipeline: from source systems to an analytics dashboard.

> [!IMPORTANT]
> You will know that you're done with this task when:
> 1. The validation queries linked above are showing comparable proportions (with a few exceptions, most rows should show 1s in both columns).
> 2. You have a dashboard that looks similar to mine above. (Getting a nice spread like you see in mine may require adding several thousand new records from the docker generator.)
> 3. You can confirm that everything is flowing properly from one end to the other, which is easily demonstrated by (a) turning on the generator and letting it run for a few minutes, (b) allowing the processor to automatically load the data into raw tables, and then (c) re-running dbt from your terminal to pull the new records through the rest of the warehouse. If you look at the dashboard before and after doing a, b, and c, and you see the changes represented in your chart, then CONGRATULATIONS! You have officially implemented your first end-to-end data pipeline. Pretty awesome.

---

## Task 5: Clean Up and Document

Before submitting Milestone 1, make sure your project is clean and tells a coherent story. You'll do the heavier portfolio documentation work in Milestone 3, but now is the time to build good habits. Commented code, explanations, etc., should all be completed now while it's fresh.

### 5.1: Polish Your Code and README

- Remove any debug print statements or commented-out experiments.
- Make sure comments explain WHY, not WHAT (e.g., "Watermark prevents duplicate processing" not "Get the watermark").
- You may want to take a few notes that explain the business problem and how to run this portion of the project.
- Include 2-3 screenshots at key verification steps (processor logs, raw table counts, dashboard).

> [!TIP]
> Write clear commit messages. Instead of "fix bug", write "Fix watermark calculation to use data timestamp, not system time." Your commit history should tell a story.

**Success Criteria:**
- README has a clear explanation of what the project does.
- Code is clean and well-commented.
- Screenshots show the pipeline working end-to-end.

---

## Wrapping Up

When you've completed all five tasks, take a step back and look at what you've built: a containerized ETL service that extracts from two different database systems, stages and loads data into a cloud warehouse, transforms it through a modern analytics engineering framework, and visualizes the results in a dashboard. That is a real, end-to-end data pipeline, and it's the kind of thing that data engineering teams build every day.

Make sure everything is committed and pushed to your GitHub repository **before the Milestone 1 deadline**. Whatever code is pushed by that deadline will be considered in the grading for Milestone 1. We'll build on this foundation in Milestones 2 and 3, where we'll add orchestration, data quality checks, and an AI agent access layer.

You deserve my CONGRATULATIONS for making it through Milestone 1. This is complex stuff, and the fact that you've built a working pipeline from scratch is genuinely impressive. Well done.

# Final Project // Milestone 2: Data Quality, Orchestration, and Agent-Assisted Development

Welcome back. In Milestone 1, you built a working data pipeline that pulls sales data from PostgreSQL, chat logs from MongoDB, loads everything into Snowflake, and transforms it with dbt. That was a real accomplishment, and it gave you a solid foundation.

Now we're going to build on top of it. Milestone 2 adds three things to your data platform:

1. **A new data source.** Adventure Works wants to understand customer browsing behavior on its website. We'll pull web analytics (clickstream) data from a REST API and land it in Snowflake.
2. **Orchestration with Prefect.** Instead of running a Python script manually, we'll use Prefect (remember Assignment 8?) to orchestrate the new pipeline with scheduling, retries, and observability.
3. **Data quality infrastructure.** We'll add dbt tests and source freshness checks so that bad data gets caught instead of silently corrupting your warehouse.

There's one more twist: you'll build the Prefect flow using an AI agent. Not because the agent will do better work than you can, but because learning to work effectively with AI tools is a skill that every data engineer needs right now. You'll write a requirements document first, hand it to an agent, review what it generates, fix what's broken, and document the entire process.

By the end of this milestone, you'll have three data sources flowing through your pipeline, comprehensive testing, and a production-grade deployment via dbt Cloud. That's a real data platform, and it's something worth talking about in interviews.

Okay. Let's get to it.

---

## Before You Begin

Make sure you have the following from Milestone 1:

- [ ] Your Docker Compose environment was successfully tested (but you don't have to leave it running!)
- [ ] Your processor has successfully loaded data into Snowflake
- [ ] Your dbt models are building and your dashboard is working
- [ ] Your repository is committed and pushed to GitHub

> [!IMPORTANT]
> If your Milestone 1 pipeline is not working, fix it first. Milestone 2 builds directly on top of it. Everything we do here assumes your Snowflake raw tables are populated and your dbt models are running.

Here is an updated system overview showing where the new Milestone 2 components fit:

```
                                ┌───────────────────┐
                                │   REST API        │
                                │  (Web Analytics)  │  <-- NEW (Milestone 2)
                                └────────┬──────────┘
                                         │
┌──────────────┐                         │                     ┌──────────────┐
│  PostgreSQL  │──┐                      │                     │  dbt Cloud   │
│  (Sales)     │  │    ┌─────────────────┼────────────┐        │  (CI/CD)     │
└──────────────┘  ├──> │   Snowflake Warehouse        │ <──────│              │
┌──────────────┐  │    │                              │        └──────────────┘
│  MongoDB     │──┘    │  RAW_EXT (raw tables)        │
│  (Chat Logs) │       │    ├── orders_raw            │
└──────────────┘       │    ├── chat_logs_raw         │
                       │    ├── web_analytics_raw  ◄──── NEW
       Prefect ──────> │                              │
       (orchestrates   │                              │
        API ingestion) │  dbt (staging + intermediate)│
                       │    ├── stg_web_analytics  ◄──── NEW
                       │    └── int_web_analytics  ◄──── NEW
                       └──────────────────────────────┘
```

---

## Task 1: Write a Product Requirements Document (PRD)

Before you write a single line of code (or ask an agent to write one for you), you need to think through what you're building. In the professional world, this is called a Product Requirements Document, and it's how engineers communicate what they need to build, why, and how they'll know it's done.

This matters because AI agents are only as good as the instructions you give them. A vague prompt produces vague code. A detailed PRD produces something much closer to what you actually need.

### 1.1 Understand the Business Context

Adventure Works currently has sales and customer data in the warehouse, but no visibility into what customers are doing on the website before they buy. Web analytics data (page views, clicks, add-to-cart events) would let analysts connect browsing behavior to purchasing patterns.

### 1.2 Explore the API

The web analytics data comes from a REST API. Before writing your PRD, you need to understand the data contract. Start by browsing to the base URL — it has a landing page that explains the scenario and links to everything you need:

**API Base URL:** `https://is566-web-analytics-api.fly.dev`

From the landing page you can reach:

| Page | What it gives you |
|------|-------------------|
| **Landing page** (`/`) | The scenario, quick-start examples, endpoint table, and event schema |
| **Interactive docs** (`/docs`) | Swagger UI — explore endpoints, see schemas, and try requests live in your browser |
| **Agent reference** (`/agent-docs`) | Plain-text markdown designed to paste into an AI coding agent's context |
| **Example event** (`/example`) | A single event — quick way to inspect the data shape |
| **Clickstream data** (`/analytics/clickstream`) | The actual data endpoint your flow will call |

Set `API_BASE_URL=https://is566-web-analytics-api.fly.dev` in your `.env` file (uncomment the Milestone 2 section).

> [!TIP]
> Start at the landing page to understand the scenario and data shape. Then open `/docs` to try the clickstream endpoint interactively — experiment with the `since` parameter to see how incremental pulls work. When you're ready to write your PRD, you can have your agent explore the `/agent-docs` page so it can understand field types, value ranges, and loading strategy. Your PRD should be based on what you (and/or your agent) discover here.

### 1.3 Complete the PRD Template

Open `templates/m2/prd_template.md`. This is a structured template with eight sections. Fill in each section based on what you learned from exploring the API. Save your completed document as `prefect/prd.md` (rename from the template). You'll use this to drive your implementation in Task 2. 

Your Prefect flow must:

1. **Pull clickstream events** from the web analytics API. Handle HTTP errors, rate limits (429), and timeouts with retries and backoff.
2. **Clean and validate** the data. Cast types, handle nulls, and deduplicate records.
3. **Stage cleaned data** in a Snowflake internal stage (the stage DDL is in `prefect/snowflake_objects.sql`).
4. **Load into a raw table** using Snowflake's COPY INTO command.
5. **Clean up staged files** after a successful load.
6. **Log summary statistics**: records fetched, cleaned, and loaded.

The flow should use Prefect 2.0 tasks and flows, connect to Snowflake using environment variables from `.env`, and be deployable via the Docker Compose services already defined in `compose.yml`. Note also that the API has an `/agent-docs` endpoint that returns a markdown document designed to be pasted directly into an AI agent's context. 

> [!TIP]
> Don't rush this. A well-written PRD saves you time later. Spend 20-30 minutes thinking through the acceptance criteria and edge cases. You can use an agent to help you brainstorm about things you aren't thinking of, ask it to interview you to exlore the use case, and otherwise build out a full, comprehensive plan for this component of the system. Make sure that the PRD accounts for the API structure and interaction pattern, that it specifies where it should be adding code, that it is going to be running inside of the docker compose environment using variables from the `.env` file, and everything else relevant to this development task.

---

## Task 2: Build Your Prefect Flow

This is **spec-driven development**: you wrote the spec (your PRD), and now you build to that spec. The flow file at `prefect/flows/web_analytics_flow.py` is intentionally nearly empty — you're creating the architecture and implementation from scratch.

> [!IMPORTANT]
> It's a good idea to **save and commit your changes locally** before you ask your agent to build anything out. If your agent does something unexpected that you didn't intend, you can always revert those changes and try again.

### 2.1 Build It

Open up the `agent_log_template.md` document and save a renamed copy to `prefect/agent_log.md`. You'll be filling this out as you build so that later (in Milestone 3) you can produce a recruiter-facing demonstration of your ability to interact with AI agents to do meaningful work. Don't worry too much about having your log be perfect or fully coherent; we'll refine it later. The goal is to capture your process so that you can remember what you did and how you interacted with the agent.

Now you cans hare your PRD and the API docs with your agent, ask it to build the flow, then review and iterate. Document the process in the agent log.

> [!IMPORTANT]
> Even though your agent is doing the building, **you are responsible for the final result**. Understand every line of code in your flow. Do not blindly accept AI-generated code. AI agents frequently get Snowflake-specific syntax wrong (they default to PostgreSQL patterns) and miss edge cases in error handling. Review everything.

### 2.2 Test Your Flow

Verify your flow works end-to-end:

1. **Syntax check**: Make sure the flow imports cleanly:
   ```bash
   cd prefect
   uv run python -c "from flows.web_analytics_flow import web_analytics_flow; print('Import OK')"
   ```

2. **Local run**: Run the flow directly to test against the live API:
   ```bash
   uv run python -m flows.web_analytics_flow
   ```

3. **Docker run**: Uncomment the Prefect services in `compose.yml` (prefect-server, prefect-worker, web-analytics-flow) and start them:
   ```bash
   docker compose up --build -d prefect-server prefect-worker web-analytics-flow
   docker compose logs -f web-analytics-flow
   ```

4. **Verify in Snowflake**: Check that data landed in `RAW_EXT.web_analytics_raw`:
   ```sql
   SELECT COUNT(*), MIN(event_timestamp), MAX(event_timestamp) FROM RAW_EXT.web_analytics_raw;
   ```

Assuming your agent did its job, you should be able to access the prefect environment from `http://localhost:4200` and see that flows have run. I'll show a screenshot of what mine looked like, but of course yours might be very different because our agents will build things in their own way.

<img src="screenshots/readme_img/flow_run.png"  width="80%">

What the flow is producing in Snowflake, however, will be more deterministic. You should be able to run some test queries (including the count query in #4 above) to see data flowing into the `WEB_ANALYTICS_RAW` table. Here's what my data from that table looks like (with a SELECT *, limit 10 query):

<img src="screenshots/readme_img/web_analytics_table.png"  width="80%">

Poke around a bit to make sure you're comfortable with what your agent built, and to be sure that data is flowing all the way from API to Snowflake.

> [!IMPORTANT]
> 📷 Grab two screenshots: one of your own prefect flow having run successfully, and another of your `WEB_ANALYTICS_RAW` table populated from your prefect flow. Save these screenshots as `m2_task2.3a.png` and `m2_task2.3b.png`, respectively, to the `screenshots` folder in the assignment repository.

### 2.3 Document Your Process

Use `prefect/agent_log.md` to document your development process: what worked, what didn't, what you'd do differently.

---

## Task 3: Integrate Web Analytics Data into dbt

Now that your Prefect flow is loading data into `RAW_EXT.web_analytics_raw`, we need to bring it into the dbt layer. In Assignment 9, we learned dbt fundamentals. Now we're adding a new data source to our dbt project and following the same staging-to-intermediate patterns you've already built.

### 3.1 Create the Snowflake Objects

Before dbt can reference your web analytics data, the raw table and stage need to exist in Snowflake. Open `prefect/snowflake_objects.sql` and run all three statements in a Snowflake worksheet:

```sql
-- Creates the internal stage and raw table
-- See prefect/snowflake_objects.sql for the full DDL
```

Verify the objects were created:

```sql
SHOW TABLES IN SCHEMA RAW_EXT;
SHOW STAGES IN SCHEMA RAW_EXT;
```

### 3.2 Create the dbt Source Definition

Create `dbt/models-m2/staging/web_analytics/sources.yml`. This file defines `web_analytics_raw` as a dbt source. You can look at `dbt/models-m1/staging/sources.yml` as a reference for the basic structure. (And while it might feel unnatural to add another sources file rather than just editing the previous one, don't worry — I'll show you how to integrate both down in Task 3.5.)

Your `sources.yml` should go beyond a bare table definition. Include:

- **Column descriptions** for each field in `web_analytics_raw`
- **Generic tests** on the source columns. Think about which columns should never be null, which have a known set of valid values, and which should link to an existing model in your warehouse. Look at how `models-m1/models.yml` defines `data_tests` for reference on the syntax.
- **Source freshness configuration** so dbt can alert you when the raw table hasn't been updated recently. You'll need a `loaded_at_field` (which column tracks when events occurred?) and `warn_after` / `error_after` thresholds. Set them wide enough to handle periods when your Prefect flow isn't running — something like 12 hours for warn and 24 hours for error.

### 3.3 Create the Staging Model

Create `dbt/models-m2/staging/web_analytics/stg_web_analytics.sql`. Your staging model should:

- Pull from the `raw_ext.web_analytics_raw` source
- Cast columns to consistent types
- Normalize timestamps to UTC
- Add `dbt_loaded_at` metadata

Use your existing staging models (like `stg_adventure_db__customers.sql`) as a reference. Follow the same pattern: source CTE, cleaning CTE, final select.

Also create a companion schema file `dbt/models-m2/staging/web_analytics/stg_web_analytics.yml` that describes the model and adds `not_null` tests on the key columns (customer_id, product_id, session_id, event_timestamp). This is the same pattern you used in `models-m1/models.yml`.

Before moving on, you may want to run `dbt build` to ensure that you have your `sources.yml` and `stg_web_analytics.sql` set up correctly. If you want to do so, you'll have to skip ahead to Task 3.5 and make sure to register the M2 model path in your dbt config.

### 3.4 Create the Intermediate Model

Create `dbt/models-m2/intermediate/int_web_analytics_with_customers.sql`. The purpose of this model is to enrich web analytics events with customer context from Milestone 1, so that downstream analysts can slice browsing behavior by customer attributes without writing joins themselves.

Your intermediate model should:

- **Start from your staging model** (`stg_web_analytics`) as the base — every clickstream event should appear in the output
- **Join to your existing customer staging model** (`stg_adventure_db__customers`) on customer ID. Use a left join so that events are preserved even if a customer ID doesn't match (the API can generate IDs outside the customer dimension)
- **Bring in useful customer attributes** alongside the event data — think about what an analyst would need to answer questions like "Which customers from the US viewed the most product pages?" or "What's the browsing pattern for customers in different regions?" You don't need every column from the customer model, just the ones that add analytical value (name, geography, contact info)
- **Keep the event grain** — one row per clickstream event. Don't aggregate anything; this is an enrichment model, not a summary

> [!TIP]
> Look at the columns available in `stg_adventure_db__customers` to decide which customer attributes to pull in. Think about which fields would be most useful for filtering and grouping in a dashboard. Also pay attention to the data types on your join keys — they may not match between models, and Snowflake is strict about implicit casting.

Also create `dbt/models-m2/intermediate/int_web_analytics_with_customers.yml` with a model description and `not_null` tests on the key columns (customer_id, session_id).

### 3.5 Register the New Model Path

Your M2 models live in `dbt/models-m2/`, but dbt only knows about directories listed in `dbt_project.yml`. Open `dbt/dbt_project.yml` and add `"models-m2"` to the `model-paths` list:

```yaml
model-paths: ["models-m1", "models-m2"]
```

Without this change, `dbt build` won't discover your new models.

### 3.6 Build and Verify

Run dbt to build the new models. My output from the command is shown, but note that yours may not match exactly because I think I have a few tests enabled that you won't have done just yet.

```bash
dbt build --select stg_web_analytics int_web_analytics_with_customers
```

<img src="screenshots/readme_img/int_web_analytics_with_customers.png"  width="80%">

You should also verify your models in Snowflake:

```sql
SELECT COUNT(*) FROM dbt_dev.stg_web_analytics;
SELECT * FROM dbt_dev.int_web_analytics_with_customers LIMIT 10;
```

> [!IMPORTANT]
> 📷 Grab a screenshot of `dbt build` output showing the new models created successfully. Save this screenshot as `m2_task3.6a.png` (or jpg) to the `screenshots` folder in the assignment repository.

> [!IMPORTANT]
> 📷 Grab a screenshot of the `int_web_analytics_with_customers` model in Snowflake showing sample rows with customer attributes joined to clickstream events. Save this screenshot as `m2_task3.6b.png` (or jpg) to the `screenshots` folder in the assignment repository.

**Deliverables:** New dbt models, updated sources.yml

---

## Task 4: Add Data Quality Checks

We've been testing our models since Assignment 10. In this milestone, we're expanding those tests to cover our new web analytics data and adding source freshness checks. Data quality is not optional on a real data team. Bad data that slips through undetected will show up in dashboards, confuse analysts, and erode trust in the data platform.

### 4.1 Review Your Generic Tests

In Task 3, you added generic tests to your YAML files (`sources.yml`, `stg_web_analytics.yml`, and `int_web_analytics_with_customers.yml`). Before moving on, review them and make sure you have coverage on the critical columns:

- `not_null` on customer_id, product_id, session_id, and event_timestamp
- `accepted_values` on event_type (the API guarantees four valid values — your test should enforce that)
- `relationships` on customer_id linking back to `stg_adventure_db__customers` (this validates referential integrity across your data sources)

If any of these are missing from your YAML files, add them now. These tests will run as part of `dbt build` and catch data quality issues before they reach your intermediate models.

### 4.2 Verify Source Freshness

In Task 3.2, you added freshness configuration to your `sources.yml`. It should look something like this:

```yaml
freshness:
  warn_after: {count: 12, period: hour}
  error_after: {count: 24, period: hour}
loaded_at_field: event_timestamp
```

This tells dbt to check the most recent `event_timestamp` in the raw table. If no events are newer than 12 hours, dbt warns; if the gap exceeds 24 hours, it errors. We use `event_timestamp` (not `_loaded_at`) because `COPY INTO` with column count mismatch doesn't populate DEFAULT values for missing columns. The thresholds are set wide enough to handle timezone differences and periods when your Prefect flow isn't running. Run the freshness check:

```bash
dbt source freshness
```

You should see output showing the freshness status of your web analytics source (and any other sources that have `loaded_at_field` configured).

### 4.3 Implement Custom Tests

Two custom test files are provided in `templates/m2/` (copy them to `dbt/tests/` when you begin M2):

1. **`web_analytics_row_count_minimum.sql`** - Already implemented. Verifies that `stg_web_analytics` has at least 50 rows. A simple smoke test to catch empty tables.

2. **`web_analytics_freshness_check.sql`** - This one has a `TODO` for you. Implement the SQL that checks whether the most recent `event_timestamp` in `stg_web_analytics` is within 4 hours. The comments in the file explain what to do.

> [!TIP]
> Use Snowflake's `DATEDIFF` function and `MAX` aggregate. The test should return rows only when data is stale (that's how dbt custom tests work: returning rows means failure).

### 4.4 Add Error Handling to Your Prefect Flow

If you haven't already (from Task 2), make sure your Prefect flow includes:

- **Try/except blocks** around API calls and Snowflake operations
- **Logging** at each major step (with record counts, not just "step completed")

### 4.5 Run All Tests

```bash
dbt test
```

Review the output. All tests should pass. If any fail, read the error message carefully. It tells you exactly what went wrong.

> [!IMPORTANT]
> 📷 Grab a screenshot of `dbt test` output with all tests passing. Save this screenshot as `m2_task4.5a.png` (or jpg) to the `screenshots` folder in the assignment repository.

> [!IMPORTANT]
> 📷 Grab a screenshot of `dbt source freshness` output. Save this screenshot as `m2_task4.5b.png` (or jpg) to the `screenshots` folder in the assignment repository.

**Deliverables:** Custom test implementation, source freshness configuration

---

## Task 5: Set Up dbt Cloud

Until now, you've been running dbt from the command line. That works for development, but in production, you need automated scheduling, CI/CD on pull requests, and a UI for monitoring job runs. That's what dbt Cloud provides.

Follow the step-by-step instructions in `templates/m2/dbt_cloud_setup.md` to:

### 5.1 Replace Your Lab Project

You already have a dbt Cloud account from the earlier lab assignment. Delete your old lab project (free tier only allows one), then create a new project connected to your `is-566-11-final-project` repo with the subdirectory set to `dbt/`.

### 5.2 Verify Snowflake Connection

Your Snowflake credentials should carry over. Test the connection and set the production schema to `dbt_prod`.

### 5.4 Create a Scheduled Job

Set up a job called "Scheduled dbt Build" that runs `dbt build` on a schedule (daily or hourly).

### 5.5 Create a CI/CD Job

Set up a second job called "CI - Pull Request Tests" that runs `dbt build` on every pull request.

### 5.6 Verify Everything Works

Manually trigger your scheduled job and confirm it completes successfully. Then create a test branch, push a small change, and open a pull request to verify the CI job runs.

> [!IMPORTANT]
> The `templates/m2/dbt_cloud_setup.md` file has detailed instructions for each step, including troubleshooting tips for common issues. Follow it carefully and take screenshots at each checkpoint.

> [!IMPORTANT]
> 📷 Grab a screenshot of your dbt Cloud project dashboard. Save this screenshot as `m2_task5.6a.png` (or jpg) to the `screenshots` folder in the assignment repository.

> [!IMPORTANT]
> 📷 Grab a screenshot of a successful scheduled job run. Save this screenshot as `m2_task5.6b.png` (or jpg) to the `screenshots` folder in the assignment repository.

> [!IMPORTANT]
> 📷 Grab a screenshot of a pull request with the CI job running. Save this screenshot as `m2_task5.6c.png` (or jpg) to the `screenshots` folder in the assignment repository.

**Deliverables:** Completed `templates/m2/dbt_cloud_setup.md` with evidence, working scheduled and CI jobs

---

## Task 6: Documentation, Reflection, and Portfolio Updates

This is the part where you step back and look at what you've built. By the end of this task, your repository should tell a clear story to anyone who opens it.

### 6.1 Finalize Your Agent Log

Review `prefect/agent_log.md`. Make sure every section is filled in with honest, specific reflections. This is a learning artifact. I'm not grading you on whether the agent worked perfectly. I'm looking at whether you can articulate what happened, what you learned, and how you'd approach it differently next time.

### 6.2 Update Your Architecture Diagram

Update your README to reflect the new components from Milestone 2 (you'll create a proper architecture diagram in Milestone 3):

- REST API as a new data source
- Prefect as the orchestration layer for web analytics
- Web analytics raw, staging, and intermediate tables
- dbt Cloud as the scheduled build and CI/CD system

You can use any diagramming tool (draw.io, Excalidraw, Mermaid, or even ASCII art like the one at the top of this README).

### 6.3 Update Your README

Add a "Milestone 2" section to your README that covers:

- What you built and why
- The three data sources now flowing through your pipeline
- Your data quality strategy (tests, freshness checks)
- A link to your agent log with a brief summary of the experience
- Updated setup instructions (new environment variables, Prefect services)

### 6.4 Review Your .env.sample

Open `.env.sample` and verify that all new environment variables are documented:

- `API_BASE_URL`
- `PREFECT_API_URL`
- `FLOW_SCHEDULE_MINUTES`

### 6.5 Clean Up and Commit

Review your full repository. Make sure:

- No credentials are committed (check `.gitignore`)
- No unnecessary files are hanging around
- Your commit messages describe what and why, not just "updated files"

```bash
git add -A
git commit -m "Milestone 2: Add web analytics pipeline, dbt quality checks, and dbt Cloud integration"
git push
```

> [!IMPORTANT]
> 📷 Grab a screenshot of your completed agent log. Save this screenshot as `m2_task6.5.png` (or jpg) to the `screenshots` folder in the assignment repository.


**Deliverables:** Completed `prefect/agent_log.md`, updated README with Milestone 2 section and architecture diagram, clean Git history

---

## What You've Accomplished

Take a moment to appreciate what you have now. Your data platform ingests from three sources (PostgreSQL, MongoDB, REST API), orchestrates ingestion with Prefect, lands raw data in Snowflake, transforms it through staging and intermediate layers with dbt, validates quality with automated tests and freshness checks, and deploys to production with dbt Cloud scheduling and CI/CD.

That's not a homework assignment. That's a data platform. And you built it.

Milestone 3 will add the final layer: exposing your data models to AI agents through a dbt MCP server, finalizing your portfolio documentation, and polishing everything so it's ready to show in interviews.

See you there.

---

## Quick Reference: New Files in Milestone 2

| File | Purpose |
|------|---------|
| `prefect/flows/web_analytics_flow.py` | Prefect flow for API ingestion |
| `prefect/prd.md` | Your completed PRD (from template) |
| `prefect/agent_log.md` | Your agent interaction log (from template) |
| `prefect/Dockerfile` | Docker image for Prefect flow |
| `prefect/pyproject.toml` | Python dependencies for Prefect |
| `prefect/snowflake_objects.sql` | DDL for raw table and stage |
| `dbt/models-m2/staging/web_analytics/sources.yml` | dbt source definition with freshness and tests |
| `dbt/models-m2/staging/web_analytics/stg_web_analytics.sql` | Staging model for web analytics |
| `dbt/models-m2/intermediate/int_web_analytics_with_customers.sql` | Intermediate model joining with customers |
| `templates/m2/web_analytics_row_count_minimum.sql` | Custom test: minimum row count (copy to `dbt/tests/`) |
| `templates/m2/web_analytics_freshness_check.sql` | Custom test: data freshness — you implement (copy to `dbt/tests/`) |
| `templates/m2/dbt_cloud_setup.md` | Step-by-step dbt Cloud configuration guide |
| `compose.yml` | Updated with Prefect services |
| `.env.sample` | Updated with new environment variables |

---

## Troubleshooting

**Prefect server not starting:**
- Check that port 4200 is not already in use: `lsof -i :4200`
- Review Prefect server logs: `docker compose logs prefect-server`

**Prefect flow hangs or can't connect:**
- Verify `PREFECT_API_URL` is set to `http://prefect-server:4200/api` in the container environment
- Make sure the Prefect server is healthy before starting the flow: `docker compose ps`

**dbt source freshness fails:**
- This is expected if you haven't loaded any data recently. Run your Prefect flow first, then check freshness again.
- If freshness is stale even after loading data, check that `event_timestamp` values are recent in your raw table. Note that `event_timestamp` is stored as `TIMESTAMP_NTZ` in UTC — if your Snowflake session uses a different timezone, the comparison may be off by your UTC offset.

**dbt test failures:**
- Read the error message. It tells you the model, column, and test that failed.
- `relationships` test failures often mean your web analytics data has customer_id values that don't exist in the customer table. This can happen if your data generator and API produce different ID ranges.

**Docker Compose networking issues:**
- All services are on the default Docker Compose network. Service names (e.g., `prefect-server`, `postgres`) resolve as hostnames automatically.
- If you're running dbt locally (not in Docker), us
# Setting Up the dbt MCP Server in Docker Compose

> **Why this document exists:** The original Milestone 3 instructions described running the dbt MCP server locally. We've updated the approach to run it in Docker Compose instead, which is cleaner and consistent with how the rest of your services run. This guide walks you through the files you need to create. Credit to Logan McNatt for pioneering this approach.

---

## Overview

You'll create five new files in your `dbt/` directory and update your `compose.yml`. When you're done, running `docker compose up --build dbt-mcp` will:

1. Build a container with your dbt project and the MCP server
2. Run `dbt seed` and `dbt compile` to generate the `target/manifest.json` the MCP server needs
3. Start the MCP server on port 8000, accessible from your host machine

---

## Prerequisites

Before you begin:

- [x] Milestones 1 and 2 are complete (dbt models build, data flowing, tests passing)
- [x] Docker Desktop is running
- [x] Your `.env` file has valid Snowflake credentials (`SNOWFLAKE_USER`, `SNOWFLAKE_PASSWORD`, `SNOWFLAKE_ACCOUNT`, `SNOWFLAKE_WAREHOUSE`, `SNOWFLAKE_DATABASE`, `SNOWFLAKE_ROLE`)

---

## Step 1: Create `dbt/profiles.yml`

Create a new file at `dbt/profiles.yml` with the following content:

```yaml
adventure-ops:
  target: dev
  outputs:
    dev:
      type: snowflake
      account: "{{ env_var('SNOWFLAKE_ACCOUNT') }}"
      user: "{{ env_var('SNOWFLAKE_USER') }}"
      password: "{{ env_var('SNOWFLAKE_PASSWORD') }}"
      role: "{{ env_var('SNOWFLAKE_ROLE') }}"
      database: "{{ env_var('SNOWFLAKE_DATABASE') }}"
      warehouse: "{{ env_var('SNOWFLAKE_WAREHOUSE') }}"
      schema: dbt_dev
      threads: 4
```

**What's happening here:** This file tells dbt how to connect to Snowflake, but instead of hardcoding your credentials, it uses dbt's `env_var()` Jinja function to read them from environment variables at runtime. This is the same pattern your processor and Prefect services use — credentials live in your `.env` file, not in code. This file is safe to commit because it contains no secrets.

> [!NOTE]
> **Impact on local `dbt build`:** If you run `dbt build` from the `dbt/` directory, dbt will find this `profiles.yml` and try to use it. For that to work, your `SNOWFLAKE_*` environment variables must be set. You can either:
> - Continue using your `~/.dbt/profiles.yml` by running `dbt build --profiles-dir ~/.dbt`
> - Or export your env vars first: `set -a; source ../.env; set +a; dbt build`
> - **Windows (PowerShell):** `Get-Content ../.env | ForEach-Object { if ($_ -match '^\s*([^#=\s]+)\s*=\s*(.*)$') { Set-Item "env:$($matches[1])" $matches[2] } }; dbt build`

---

## Step 2: Create `dbt/pyproject.toml`

Create a new file at `dbt/pyproject.toml`:

```toml
[project]
name = "dbt-mcp-server"
version = "0.1.0"
requires-python = ">=3.12,<3.14"
dependencies = [
    "dbt-snowflake>=1.9.0",
    "dbt-mcp>=0.1.0",
]
```

Then generate the lock file:

```bash
cd dbt
uv sync
```

This creates a `uv.lock` file that the Docker build needs. You should see it install `dbt-snowflake` and `dbt-mcp` along with their dependencies.

> [!TIP]
> If you don't have `uv` installed, follow the [install guide](https://docs.astral.sh/uv/getting-started/installation/). You already used it in earlier milestones, so it should be available.

---

## Step 3: Create `dbt/start_mcp.py`

Create a new file at `dbt/start_mcp.py`:

```python
"""Wrapper to start dbt-mcp with configurable host binding.

The upstream dbt-mcp hardcodes host=127.0.0.1 in the FastMCP constructor,
which prevents Docker port mapping from working. This wrapper overrides
server.settings.host after creation so FASTMCP_HOST is respected.
"""

import asyncio
import os

from dbt_mcp.config.config import load_config
from dbt_mcp.config.transport import validate_transport
from dbt_mcp.mcp.server import create_dbt_mcp


def main() -> None:
    config = load_config()
    server = asyncio.run(create_dbt_mcp(config))

    host = os.environ.get("FASTMCP_HOST")
    if host:
        server.settings.host = host

    transport = validate_transport(os.environ.get("MCP_TRANSPORT", "stdio"))
    server.run(transport=transport)


if __name__ == "__main__":
    main()
```

**Why this file is necessary:** The `dbt-mcp` package hardcodes `host=127.0.0.1` when it starts its web server. Inside a Docker container, `127.0.0.1` means "only listen on the container's own loopback interface," which makes the server invisible to the outside world — even with Docker's `-p 8000:8000` port mapping. This wrapper patches the host to `0.0.0.0` (listen on all interfaces) so the port mapping works and you can reach the server from your host machine.

---

## Step 4: Create `dbt/entrypoint.sh`

Create a new file at `dbt/entrypoint.sh`:

```bash
#!/usr/bin/env bash
set -e

echo "==> Seeding dbt project..."
uv run dbt seed --profiles-dir . --project-dir .

echo "==> Compiling dbt project to generate target/manifest.json..."
uv run dbt compile --profiles-dir . --project-dir .

echo "==> Starting dbt MCP server on port 8000..."
exec uv run python start_mcp.py
```

Then make it executable:

```bash
chmod +x dbt/entrypoint.sh
```

> [!NOTE]
> **Windows users:** skip this step. `chmod` doesn't exist in PowerShell, and the `Dockerfile` already runs `RUN chmod +x entrypoint.sh` inside the Linux container — which is the only place the executable bit actually needs to be set.

**What each step does:**
- **`dbt seed`** loads any seed CSV files into Snowflake (these are reference data files in your `seeds/` directory)
- **`dbt compile`** parses your dbt project and generates `target/manifest.json`, which is the file the MCP server's lineage and model discovery tools depend on
- **`exec ... start_mcp.py`** starts the MCP server. The `exec` replaces the shell process with the Python process, which ensures Docker can properly send shutdown signals to it.

---

## Step 5: Create `dbt/Dockerfile`

Create a new file at `dbt/Dockerfile`:

```dockerfile
FROM python:3.12-slim
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Install dependencies first for better layer caching
COPY pyproject.toml uv.lock ./
RUN uv sync --no-dev --frozen

# Copy dbt project files
COPY dbt_project.yml profiles.yml ./
COPY models-m1/ ./models-m1/
COPY models-m2/ ./models-m2/
COPY analyses/ ./analyses/
COPY tests/ ./tests/
COPY seeds/ ./seeds/
COPY entrypoint.sh start_mcp.py ./
RUN chmod +x entrypoint.sh

CMD ["./entrypoint.sh"]
```

> [!IMPORTANT]
> The `COPY models-m2/` line requires your Milestone 2 models directory to exist. If you haven't completed Milestone 2 yet, this build will fail. Complete M2 first, then come back here.

---

## Step 6: Update `compose.yml`

Open your `compose.yml`. Find the Milestone 3 comment block at the bottom (it looks like this):

```yaml
  # =========================================================================
  # Milestone 3: dbt MCP Server
  # =========================================================================
  # The dbt MCP server runs LOCALLY (not in Docker). Start it from the dbt/
  # directory so that lineage tools can find target/manifest.json:
  #
  #   cd dbt
  #   MCP_TRANSPORT=sse \
  #   ...
```

**Replace that entire block** with:

```yaml
  # =========================================================================
  # Milestone 3: dbt MCP Server
  # =========================================================================

  dbt-mcp:
    build: ./dbt
    container_name: dbt-mcp
    env_file:
      - .env
    ports:
      - "8000:8000"
    environment:
      - MCP_TRANSPORT=sse
      - DBT_PROJECT_DIR=.
      - DBT_PROFILES_DIR=.
      - FASTMCP_HOST=0.0.0.0
      - PYTHONUNBUFFERED=1
    restart: on-failure
```

**What each setting does:**
- **`env_file: .env`** passes your Snowflake credentials (and other env vars) into the container — this is how `profiles.yml`'s `env_var()` calls get their values
- **`FASTMCP_HOST=0.0.0.0`** tells our `start_mcp.py` wrapper to bind the server to all interfaces (see Step 3 for why)
- **`MCP_TRANSPORT=sse`** uses Server-Sent Events over HTTP, so the demo client can connect via `http://localhost:8000/sse`
- **`DBT_PROJECT_DIR` and `DBT_PROFILES_DIR`** tell dbt where to find project files inside the container

---

## Step 7: Build and Verify

Build and start the MCP server:

```bash
docker compose up --build dbt-mcp
```

You should see three phases in the output:

1. **Seeding:** `==> Seeding dbt project...` followed by seed completion messages
2. **Compiling:** `==> Compiling dbt project to generate target/manifest.json...` followed by model parsing
3. **Server start:** `==> Starting dbt MCP server on port 8000...` followed by:
   ```
   INFO [dbt_mcp.mcp.server] Registering dbt cli tools
   INFO [dbt_mcp.mcp.server] Registering dbt codegen tools
   INFO:     Uvicorn running on http://0.0.0.0:8000
   ```

From a **separate terminal**, verify the SSE endpoint:

```bash
curl -s http://localhost:8000/sse | head -3
```

> **Windows (PowerShell):** `curl.exe -s http://localhost:8000/sse | Select-Object -First 3`

You should see:

```
event: endpoint
data: /messages/?session_id=...
```

If you see that, your MCP server is running and ready for the demo client. Return to the Milestone 3 instructions and continue with Task 1.3.

---

## Troubleshooting

### "Connection refused" when curling the SSE endpoint

The container may still be building, seeding, or compiling. Check the logs:

```bash
docker compose logs dbt-mcp
```

Wait for the "Uvicorn running" message before testing.

### Build fails with "COPY failed: file not found ... models-m2"

Your Milestone 2 models directory doesn't exist yet. Complete Milestone 2 first — you need the `dbt/models-m2/` directory with your web analytics models.

### Snowflake authentication errors during seed/compile

Your `.env` file may have incorrect Snowflake credentials. Verify them by checking that your other services (processor, Prefect) can still connect to Snowflake. The dbt-mcp container reads from the same `.env` file.

### Port 8000 already in use

If you previously ran the MCP server locally, make sure it's stopped (Ctrl+C in its terminal). Only one process can use port 8000.

### Container exits immediately / restart loop

Check the logs with `docker compose logs dbt-mcp`. Common causes:
- Missing or invalid `profiles.yml` in the `dbt/` directory
- Snowflake warehouse is suspended with auto-resume disabled
- A dbt seed or compile error (check the log output for the specific error)

---

## Appendix: Running Locally (Fallback)

If Docker gives you trouble, you can run the MCP server locally as a fallback. This requires `uv` and `dbt-snowflake` on your PATH.

```bash
# Install dbt if not already available
uv tool install dbt-snowflake

# From the dbt directory
cd dbt

# Start the MCP server
MCP_TRANSPORT=sse \
DBT_PROJECT_DIR=. \
DBT_PROFILES_DIR=. \
uvx dbt-mcp
```

**Windows (PowerShell):**

```powershell
# Install dbt if not already available
uv tool install dbt-snowflake

# From the dbt directory
cd dbt

# Start the MCP server
$env:MCP_TRANSPORT = "sse"
$env:DBT_PROJECT_DIR = "."
$env:DBT_PROFILES_DIR = "."
uvx dbt-mcp
```

The server will listen on `http://localhost:8000/sse`, same as the Docker approach. Note that for the local approach, you'll need a `profiles.yml` in your `dbt/` directory (or at `~/.dbt/profiles.yml`) with working Snowflake credentials, and you should run `dbt compile` first to generate the manifest.
# Final Project // Milestone 3: Agent Data Access Layer and Portfolio Finalization

Over the past two weeks, you've built something substantial. You have a working data pipeline that extracts from multiple sources, loads into Snowflake, transforms with dbt, passes data quality tests, and serves analytics through dashboards. That's real data engineering.

This week, we're going to do two things. First, we'll make your data accessible to AI agents through a dbt MCP (Model Context Protocol) server. Second, we'll polish your entire project into something you'd be proud to show a hiring manager.

By the end of Milestone 3, you'll have:

- A dbt MCP server running in Docker Compose, exposing your data models to AI agents
- Agent-friendly documentation across all your dbt models
- A Python demo script that connects to the MCP server and demonstrates agent interaction
- A thoughtful reflection on what it means to design data for agent consumers
- A portfolio-ready README with architecture diagrams, technical decisions, and quantified metrics

This is the capstone. Let's make it count.

---

## Before You Start

A few orienting notes:

1. **Milestones 1 and 2 must be working.** Your dbt models should build successfully, your data should be flowing, and your tests should be passing. If anything is broken, fix it first.

2. **Docker Desktop must be running.** We're adding a new service to your Docker Compose configuration.

3. **Python 3.9+ with a virtual environment.** You'll need this for the MCP demo client script.

4. **Your `.env` file must have valid Snowflake credentials.** The MCP server will use these to connect to your warehouse.

> [!IMPORTANT]
> This milestone has two major components. **Component A** (Tasks 1-4) is about setting up the MCP server and demonstrating agent interaction. **Component B** (Task 5) is about finalizing your portfolio documentation. Both are required, and both matter for your grade.

> [!NOTE]
> **Windows users:** Several shell commands in this milestone are written for macOS/Linux (bash). Each one has a PowerShell equivalent called out in a blockquote directly below the command. Use the PowerShell version from your Windows terminal.

---

## Task 1: Set Up the dbt MCP Server

The Model Context Protocol (MCP) is an open standard that lets AI agents discover and interact with external tools and data sources. The dbt MCP server exposes your dbt project (models, descriptions, compiled SQL) to any MCP-compatible agent. Think of it as giving an AI agent a structured way to ask questions about your data.

Why does this matter? Because data engineers are increasingly responsible for making data accessible not just to dashboards and reports, but to AI agents. An agent that can browse your dbt models, read your column descriptions, and compile SQL is a fundamentally different consumer than a human looking at a chart. Understanding this shift is valuable, both for your career and for this project's portfolio value.

> [!IMPORTANT]
> **Updated instructions:** The MCP server now runs in Docker Compose instead of locally. Follow the step-by-step setup guide in [**`m3_dbt_docker_setup.md`**](m3_dbt_docker_setup.md) (here in the instructions repo) to create the required files, then return here to continue with section 1.3 (verification).

### 1.1 - Prerequisites

Before setting up the MCP server, make sure you have:

1. **Docker Desktop running** — you've been using it since Milestone 1
2. **Milestones 1 and 2 complete** — your dbt models must build, and `dbt/models-m2/` must exist
3. **Valid Snowflake credentials in your `.env` file** — the MCP container reads from the same `.env` as your other services
4. **`uv` installed** — needed to generate a lock file and later for the demo client ([install guide](https://docs.astral.sh/uv/getting-started/installation/))

### 1.2 - Create Files and Start the MCP Server

Follow the **`m3_dbt_docker_setup.md`** guide to create five new files in your `dbt/` directory and update your `compose.yml`. The guide walks you through each file and explains what it does and why.

Once you've completed the setup guide, start the MCP server:

```bash
docker compose up --build dbt-mcp
```

You should see three phases: seeding, compiling, then the server starting:

```
==> Seeding dbt project...
==> Compiling dbt project to generate target/manifest.json...
==> Starting dbt MCP server on port 8000...
INFO [dbt_mcp.mcp.server] Registering dbt cli tools
INFO [dbt_mcp.mcp.server] Registering dbt codegen tools
INFO:     Uvicorn running on http://0.0.0.0:8000
```

**Leave this terminal running** (or add `-d` to run in the background). Open a new terminal for the next steps.

### 1.3 - Verify Server is Running

From a **separate terminal**, test the SSE endpoint:

```bash
curl -s http://localhost:8000/sse | head -3
```

> **Windows (PowerShell):** `curl.exe -s http://localhost:8000/sse | Select-Object -First 3`

You should see an SSE event stream like:

```
event: endpoint
data: /messages/?session_id=abc123...
```

If you get "Connection refused," the server hasn't finished starting. Wait a few seconds and try again.

### 1.4 - Troubleshooting

If things aren't working, check the container logs first:

```bash
docker compose logs dbt-mcp
```

Common issues:

- **"Connection refused"**: The container may still be building, seeding, or compiling. Wait for the "Uvicorn running" message in the logs before testing.
- **Build fails on `COPY models-m2/`**: Your Milestone 2 models directory doesn't exist yet. Complete M2 first.
- **Snowflake authentication errors during seed/compile**: Your `.env` file may have incorrect Snowflake credentials. Verify that your other services (processor, Prefect) can still connect.
- **Port 8000 already in use**: If you previously ran the MCP server locally, make sure it's stopped (Ctrl+C). Only one process can use port 8000.
- **Container exits immediately / restart loop**: Check the logs. Common causes include missing `profiles.yml`, suspended Snowflake warehouse, or dbt compile errors.

> [!TIP]
> If Docker gives you trouble, a local fallback approach is documented in the appendix of `m3_dbt_docker_setup.md`.

### Verification

- [ ] `curl -s http://localhost:8000/sse | head -3` returns an SSE event stream (Windows: `curl.exe -s http://localhost:8000/sse | Select-Object -First 3`)
- [ ] The server terminal shows no Snowflake authentication errors
- [ ] Server logs show "Registering dbt cli tools"

> [!IMPORTANT]
> 📷 Grab a screenshot showing the MCP server running in your terminal with the "Uvicorn running" message. Save this screenshot as `m3_task1.png` (or jpg) to the `screenshots` folder in the assignment repository.

---

## Task 2: Upgrade Your dbt Model Documentation

Here's an important insight: when an AI agent looks at your dbt models through the MCP server, the only way it understands what a model or column represents is through the `description` field in your YAML files. If your descriptions say "Order ID" for every ID column and "Staging model" for every staging model, the agent has almost nothing to work with.

Agent-friendly documentation is different from the minimal descriptions you might have written in earlier milestones. It explains business context, grain, relationships, and how columns connect across models. Improving these descriptions makes your data more accessible to agents AND to the humans who will read your project.

### 2.1 - Read the Agent-Friendly Documentation Guide

I've provided a guide at `templates/m3/AGENT_FRIENDLY_DOCS_GUIDE.md` that explains the principles of writing documentation that agents can actually use. Copy it into your `dbt/` directory so it lives alongside your models, then read through it before making changes to your YAML files:

```bash
cp templates/m3/AGENT_FRIENDLY_DOCS_GUIDE.md dbt/AGENT_FRIENDLY_DOCS_GUIDE.md
```

The key ideas:

1. **Every model description should explain what business entity it represents, what grain it has, and how it relates to other models.** Not just "staging model for orders."
2. **Every column description should explain the business meaning, not just echo the column name.** Not just "customer_id" for `customer_id`.
3. **Key columns (primary keys, foreign keys) should explicitly say they're used for joins** and name the target model.

### 2.2 - Upgrade Your Model Descriptions

Open your `dbt/models-m1/models.yml` (or whichever YAML file contains your model definitions). For every model in `staging/`, `intermediate/`, and `marts/` (if you have marts), update the description to follow the guide.

Here's a before/after example to calibrate your expectations:

```yaml
# BEFORE (minimal)
- name: stg_ecom__sales_orders
  description: "Staging model for sales orders"

# AFTER (agent-friendly)
- name: stg_ecom__sales_orders
  description: >
    Each row represents a single sales order from the e-commerce system.
    This staging model cleans and standardizes raw order data from the
    PostgreSQL source. Grain: one row per order. Join to
    stg_adventure_db__customers via customer_id to get customer details.
```

### 2.3 - Upgrade Your Column Descriptions

For every column in every model, add or improve the description. Focus especially on:

- **Primary keys**: Say it's a primary key and what table it uniquely identifies
- **Foreign keys**: Say what model this column joins to and on what field
- **Date/time columns**: Specify the timezone and what event the timestamp represents
- **Status or flag columns**: Explain the possible values and what they mean
- **Calculated columns**: Briefly explain the calculation logic

Example:

```yaml
columns:
  - name: order_id
    description: >
      Unique identifier for this sales order. Primary key.
      Source: PostgreSQL ecom.sales_orders.order_id.
      Join to int_sales_order_line_items on order_id to get line item details.
  - name: customer_id
    description: >
      Identifier of the customer who placed this order. Foreign key to
      stg_adventure_db__customers.customer_id. Use this join to access
      customer name, email, and demographic information.
  - name: order_date
    description: >
      Date and time the customer placed this order, in UTC.
      Used for time-based analysis like orders per month or daily revenue trends.
```

### 2.4 - Verify Completeness

Run a quick check to make sure you haven't missed any models or columns:

```bash
# Check for models without descriptions
grep -A1 "name:" dbt/models-m1/models.yml | grep -B1 'description: ""'

# Or, more simply, open the file and scan for any empty description fields
```

> **Windows (PowerShell):** `Select-String -Path dbt/models-m1/models.yml -Pattern 'description: ""'`

Every `description:` field should have meaningful content. No empty strings, no single-word descriptions, no descriptions that just repeat the column name.

> [!TIP]
> This is a place where an AI coding assistant can genuinely help. You can share your YAML file and the documentation guide with ChatGPT, Cursor, or Claude and ask it to suggest improved descriptions. Just make sure you review and customize the suggestions. The descriptions should be accurate to YOUR project, not generic.

### Verification

- [ ] Every model has a multi-sentence description (grain, business entity, key relationships)
- [ ] Every column has a description explaining business meaning
- [ ] No empty `description: ""` fields remain
- [ ] Key columns (PKs, FKs) explicitly mention join targets
- [ ] Descriptions use plain English, not SQL syntax

> [!IMPORTANT]
> 📷 Grab a screenshot showing one of your updated model YAML entries with full descriptions. Save this screenshot as `m3_task2.png` (or jpg) to the `screenshots` folder in the assignment repository.

---

## Task 3: Run the dbt MCP Demo Script

Now for the fun part. You're going to run a Python script that connects to your MCP server and demonstrates how an AI agent would interact with your data models. This is the kind of demo that makes a portfolio project come alive.

### 3.1 - Review the Demo Script

I've provided a starter script at `templates/m3/demo_client_starter.py`. Copy it to your working location and then open it to read through the code:

```bash
mkdir -p mcp
cp templates/m3/demo_client_starter.py mcp/demo_client.py
```

Open `mcp/demo_client.py` and read through the code. The script has six steps, each demonstrating a different MCP capability:

1. **Connect** to the MCP server via SSE
2. **List available tools** the server exposes
3. **Discover all dbt models** with their descriptions
4. **Get details** on a specific model (columns, tests, dependencies)
5. **Compile SQL** for a model (the fully resolved query dbt would execute)
6. **Explore model lineage** (upstream sources and downstream dependents)

The script is structured as a series of TODO blocks. You'll need to implement each one using the MCP Python SDK.

### 3.2 - Install Dependencies

Set up a virtual environment (if you don't already have one) and install the MCP client library:

```bash
cd mcp
cp ../templates/m3/mcp_pyproject.toml pyproject.toml
uv sync
```

> [!TIP]
> A `pyproject.toml` for the MCP client dependencies is provided as a template. Copy it into your `mcp/` directory and install:
> ```bash
> cp templates/m3/mcp_pyproject.toml mcp/pyproject.toml
> cd mcp && uv sync
> ```

The dependencies include `mcp` (the MCP Python client library), `httpx` (HTTP client for SSE transport), and `python-dotenv` (environment variable loading).

### 3.3 - Implement the Demo Steps

Open `demo_client.py` and fill in the TODO sections. The comments in each section explain what to do, and here are some additional hints:

**Connecting to the server (Step 1):**

```python
from mcp.client.sse import sse_client
from mcp.client.session import ClientSession

async with sse_client(MCP_SERVER_URL) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        # ... rest of your demo code goes here ...
```

**Listing tools (Step 2):**

```python
tools = await session.list_tools()
for tool in tools.tools:
    log(f"  - {tool.name}: {tool.description}")
```

**Calling a tool (Steps 3-6):**

```python
result = await session.call_tool("tool_name", {"param": "value"})
# Parse result.content to get the data
```

The exact tool names and parameters depend on what the dbt MCP server exposes. Use the tool list from Step 2 to discover what's available. Common tools include operations for listing models, getting model details, and compiling SQL.

> [!TIP]
> The MCP SDK uses async/await throughout. Make sure all your MCP calls are inside the `async with` blocks. If you're not familiar with async Python, that's okay. The pattern shown above is all you need. The key thing is that every `await` call must be inside an `async` function.

> [!IMPORTANT]
> The exact tool names may differ from what's shown in the comments. Use the output from Step 2 (listing tools) to discover the actual names, then update your Step 3-6 calls accordingly.

### 3.4 - Run the Demo

With the MCP server running and your script implemented:

```bash
cd mcp
uv run python demo_client.py
```

The script will print output to the console and save everything to `demo_output.log`.

### 3.5 - Review the Output

Open `mcp/demo_output.log` and verify you see:

1. A successful connection message
2. A list of available MCP tools
3. All your dbt models with their (improved) descriptions
4. Detailed information about at least one model (columns, tests, dependencies)
5. Compiled SQL for at least one model
6. Lineage information showing model relationships

If any step failed, the script should log the error and continue to the next step. Check the error messages for hints about what went wrong.

### 3.6 - Understand What Happened

Take a moment to think about what just happened. A Python script connected to a server that understands your dbt project. It discovered your models, read your documentation, compiled SQL, and traced lineage, all programmatically. This is exactly what an AI agent does when it needs to answer a question about your data.

The quality of the agent's answers depends directly on the quality of your model documentation (Task 2). If your descriptions are clear and complete, the agent can make informed decisions about which models to query and how to join them.

### Verification

- [ ] `python mcp/demo_client.py` runs without crashing
- [ ] `mcp/demo_output.log` contains output from all six steps
- [ ] Tool list, model list, model details, compiled SQL, and lineage are all present
- [ ] Error handling works (script continues past individual failures)

> [!IMPORTANT]
> 📷 Grab a screenshot showing the tail of your `demo_output.log` file. Save this screenshot as `m3_task3.png` (or jpg) to the `screenshots` folder in the assignment repository.

---

## Task 4: Write the Reflection on Agent Data Access

This reflection is not busywork. The questions it asks are exactly the kind of thing you'll discuss in data engineering interviews, especially as companies start thinking about how agents interact with their data platforms.

### 4.1 - Open the Reflection Template

Copy the reflection template to your `dbt/` directory and open it:

```bash
cp templates/m3/agent_access_reflection_template.md dbt/agent_access_reflection.md
```

Open `dbt/agent_access_reflection.md`. You'll find six guided prompts, each with context and hints to help you think deeply.

### 4.2 - Address Each Prompt

Write substantive responses (the entire reflection should be 500-800 words). Here's what makes a good response vs. a weak one:

**Weak**: "The MCP server worked well and the agent could see my models."

**Strong**: "The agent immediately understood my `stg_ecom__sales_orders` model because the description explicitly stated the grain (one row per order) and the join key to customers. However, it struggled with `int_sales_order_line_items` because I hadn't documented that the `discount_amount` column could be null for orders without promotions, which led the agent to write a query that produced unexpected results."

The six sections are:

1. **What Worked Well** - What aspects of your data models made agent interaction smooth?
2. **What Was Difficult** - Where did the agent struggle or need help?
3. **Documentation Quality** - How did improving descriptions change agent behavior?
4. **Production Considerations** - Security, cost, access control for real deployments
5. **Business Use Cases** - Specific problems agents could solve with your data
6. **The Bigger Picture** - How agent access changes the data engineering role

### 4.3 - Review and Polish

Read your reflection once more. Does it reference specific models and columns from YOUR project? Does it show genuine critical thinking? Could you discuss these ideas in a job interview?

### Verification

- [ ] All six sections have substantive responses
- [ ] Responses reference specific models, columns, or decisions from your project
- [ ] Total length is 500-800 words
- [ ] Responses show critical thinking, not placeholder text

---

## Task 5: Finalize Your Portfolio Documentation

This is the multi-part capstone. You're transforming your project from a class assignment into something you'd share with a hiring manager. This matters because most candidates show up to interviews talking vaguely about projects they've done. You'll show up with a polished, quantified, well-documented data platform.

### 5.1 - Restructure Your README into Portfolio Format

Replace your current assignment-focused `README.md` with a portfolio-ready version. Start by copying the provided template:

```bash
cp templates/m3/portfolio_readme_template.md README.md
```

Open `README.md` and fill in every `[TODO: ...]` placeholder with real content from your project. This is what a hiring manager will see first when they look at your repo, so make it count. Your README should include:

1. **Project title and one-line description** — what this is, in plain English
2. **Architecture diagram** — embed your diagram or link to the image from Task 5.2
3. **Problem statement** — the business context (Adventure Works needs visibility into web behavior)
4. **Tech stack with rationale** — not just a list of tools, but WHY each one
5. **Data flow** — end-to-end journey from source systems to analytics
6. **Setup and run instructions** — someone could clone your repo and get it running
7. **Key metrics** — quantified from actual queries (from Task 5.3)
8. **What I learned** — genuine reflection, not platitudes

> [!IMPORTANT]
> The tech stack section is where most students fall flat. Don't just list "Snowflake" and "dbt." Explain WHY. For example: "Snowflake was chosen for its separation of compute and storage, which prevents idle resource costs, and its native support for semi-structured data (JSON), which we use for MongoDB chat logs." That's the kind of rationale that shows understanding.

### 5.2 - Create an Architecture Diagram

Create a visual architecture diagram showing your complete data platform. Use any diagramming tool you like — Lucidchart, draw.io, Excalidraw, or even a whiteboard photo that's clean enough to read.

Your diagram should show:
- All data sources (PostgreSQL, MongoDB, REST API)
- The ETL processor and Snowflake stages
- dbt transformations (staging, intermediate)
- Prefect orchestration
- The MCP server and agent access layer

Export it as a PNG or SVG and include it in your repo (e.g., `screenshots/architecture.png`). Reference it in your README.

> [!TIP]
> Alternatively, you can embed a Mermaid diagram directly in your README — GitHub renders it natively. But a polished visual diagram often makes a stronger impression in a portfolio.

### 5.3 - (Optional) Document Technical Decisions

If you want to strengthen your portfolio further, create a `technical_decisions.md` documenting 3-5 key decisions you made. A template is available at `templates/m3/technical_decisions_template.md` with a worked example. Good decisions to document:

- Data warehouse choice (Snowflake vs. alternatives)
- Transformation framework (dbt vs. alternatives)
- Orchestration approach (Prefect vs. alternatives)
- Data loading strategy (internal stages, watermarks)

> [!TIP]
> In interviews, being able to say "I chose X because of Y, but I'd consider Z at larger scale" demonstrates mature engineering judgment. This is optional but powerful.

### 5.3 - Quantify Your Metrics

Go to Snowflake and run queries to get actual numbers. Don't estimate. Don't guess. Query your data and report what you find.

```sql
-- Example queries to calculate metrics
SELECT COUNT(*) as total_orders FROM your_schema.stg_ecom__sales_orders;
SELECT COUNT(*) as total_customers FROM your_schema.stg_adventure_db__customers;
SELECT COUNT(*) as total_chat_logs FROM your_schema.stg_real_time__chat_logs;

-- Pipeline latency (difference between source timestamp and warehouse load time)
-- Test coverage (count of dbt tests)
-- Availability (check dbt Cloud run history)
```

Put these numbers in your README's Key Metrics section and reference them in your technical decisions where relevant.

Metrics to quantify:

| Metric | How to Calculate |
|--------|-----------------|
| Records per cycle | Query raw table counts |
| Pipeline execution time | Time your Docker Compose processor run |
| dbt model count | macOS/Linux: `dbt ls --resource-type model \| wc -l` &nbsp; • &nbsp; Windows: `(dbt ls --resource-type model).Count` |
| dbt test count | macOS/Linux: `dbt ls --resource-type test \| wc -l` &nbsp; • &nbsp; Windows: `(dbt ls --resource-type test).Count` |
| Test pass rate | `dbt test` and count pass/fail |
| Data sources integrated | Count your sources in sources.yml |
| Models exposed via MCP | Count from demo script output |

### 5.4 - Final Polish

Before you call it done, review everything one more time:

- [ ] README reads smoothly from top to bottom — no placeholder text (`[FILL THIS IN]`, `[TODO]`)
- [ ] Architecture diagram renders correctly on GitHub
- [ ] Key metrics use specific numbers from actual queries, not estimates
- [ ] Setup instructions are complete enough that someone could clone and run your project
- [ ] `.env.sample` is up to date with all required variables
- [ ] `.gitignore` includes `.env`, `venv/`, `.venv/`, and any other sensitive/generated files
- [ ] No secrets in the repository — run `grep -r "eyJ\|password\|secret" . --include="*.py" --include="*.md" --include="*.yml"` to check
- [ ] All code blocks have syntax highlighting (` ```sql `, ` ```python `, ` ```bash `)

> [!TIP]
> **The hiring manager test:** Read your README as if you're a hiring manager with 5 minutes. Does the first screen tell them what this project does, what technologies you used, and why? Can they see the architecture at a glance? That's the bar. Most candidates show up to interviews talking vaguely about projects. You'll show up with a polished, quantified, well-documented data platform.

### Verification

- [ ] README has all sections filled in with real content
- [ ] Architecture diagram is present and covers all 3 milestones
- [ ] Key metrics are backed by actual Snowflake queries
- [ ] Setup instructions are complete (someone could clone and run)
- [ ] No placeholder text or TODO comments anywhere in documentation

> [!IMPORTANT]
> 📷 Grab a screenshot of your final README rendered on GitHub (push first, then view on GitHub). Save this screenshot as `m3_task5.png` (or jpg) to the `screenshots` folder in the assignment repository.

---

## Wrapping Up

Take a step back and look at what you've built across three weeks:

- **A multi-source ETL pipeline** that extracts from PostgreSQL, MongoDB, and a REST API
- **A cloud data warehouse** with staging, intermediate, and analytics layers
- **Data quality infrastructure** with automated tests, source freshness checks, and error handling
- **Orchestration and CI/CD** with Prefect and dbt Cloud
- **An agent data access layer** that exposes your models to AI through MCP
- **Portfolio documentation** that quantifies your work and demonstrates engineering judgment

That's a complete, production-style data platform. It demonstrates every major concept in modern data engineering, and it's yours.

### Commit and Push

```bash
git add .
git commit -m "Milestone 3: Agent data access layer and portfolio finalization"
git push origin main
```

### What to Submit

1. Your GitHub repository URL
2. Screenshots for Tasks 1, 2, 3, and 5 (saved in `screenshots/`)
3. The completed `agent_access_reflection.md`
4. The `mcp/demo_output.log` file (committed to your repo)

### Looking Ahead

Consider doing these (optional but valuable) things:

- **Record a 3-5 minute video walkthrough** of your project. Walk through the architecture, show the pipeline running, demonstrate the MCP demo. This is powerful in interviews.
- **Prepare to discuss your technical decisions.** If someone asks "Why Snowflake?", you should have a confident, nuanced answer.
- **Think about extensions.** What would you build next? Streaming ingestion? Real-time dashboards? A Slack bot that queries your data through MCP?

You deserve my CONGRATULATIONS. This has been a demanding three weeks, and you've built something that genuinely demonstrates data engineering competence. I hope you feel proud of what you've accomplished, because you should.