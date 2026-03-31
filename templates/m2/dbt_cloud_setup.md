# Setting Up dbt Cloud for Your Final Project

You already have a dbt Cloud account from the earlier lab assignment. In this guide, you'll replace your old lab project with a new one connected to your final project repository, then set up scheduled builds and CI/CD on pull requests.

---

## Step 1: Remove Your Old Lab Project

The free Developer tier only allows one project. You need to delete your lab project to make room.

1. Log in to [cloud.getdbt.com](https://cloud.getdbt.com).
2. Go to **Account Settings > Projects**.
3. Click into your existing lab project.
4. Scroll to the bottom and click **Delete Project**. Confirm the deletion.

> [!TIP]
> If you don't see a delete option, you may need to delete any jobs in the project first. Go to **Deploy > Jobs**, delete all jobs, then try again.

---

## Step 2: Create a New Project

1. From the dbt Cloud dashboard, click **New Project**.
2. Name it `IS566-Final-Project`.
3. Click **Continue**.

---

## Step 3: Connect Your GitHub Repository

1. When prompted, select **GitHub** as your Git provider. Your GitHub integration should still be authorized from the lab — if not, re-authorize it.
2. Select your `is-566-11-final-project` repository.
3. Set the **Project subdirectory** to `dbt/` (this tells dbt Cloud where your `dbt_project.yml` lives relative to the repo root).
4. Click **Save**.

> [!IMPORTANT]
> The subdirectory must be `dbt/`, not `dbt` or `/dbt/`. This is the relative path from your repository root to the folder containing `dbt_project.yml`.

📷 **Screenshot checkpoint:** Take a screenshot showing the GitHub integration connected to your final project repo.

---

## Step 4: Verify Snowflake Connection

Your Snowflake credentials should carry over from your previous project setup.

1. In your project settings, go to **Connection** (or **Credentials**).
2. Verify the Snowflake connection details are correct:
   - **Account:** Your Snowflake account identifier
   - **Database:** Your database name (same as `SNOWFLAKE_DATABASE` in your `.env`)
   - **Warehouse:** Your warehouse name
   - **Schema:** `dbt_prod` (use a different schema than your local `dbt_dev` so you can distinguish production builds from development builds)
3. Click **Test Connection** to verify everything works.

> [!TIP]
> If the connection test fails, re-enter your Snowflake username and password. Your credentials may not have transferred when the old project was deleted.

📷 **Screenshot checkpoint:** Take a screenshot of the successful connection test.

---

## Step 5: Create a Production Environment

1. Go to **Deploy > Environments**.
2. Click **Create Environment**.
3. Name it `Production`.
4. Set the **dbt version** to the latest available.
5. Under **Deployment credentials**, confirm your Snowflake connection details. Set the schema to `dbt_prod`.
6. Click **Save**.

---

## Step 6: Create a Scheduled Production Job

This is where dbt Cloud will automatically run your models and tests on a schedule, just like a production data platform.

1. Go to **Deploy > Jobs**.
2. Click **Create Job**.
3. Configure the job:
   - **Job name:** `Scheduled dbt Build`
   - **Environment:** Select the Production environment you just created
   - **Commands:**
     ```
     dbt build
     ```
     (The `dbt build` command runs models, tests, snapshots, and seeds in dependency order.)
   - **Triggers:** Check **Run on schedule**
   - **Schedule:** Pick a frequency that makes sense. For this project, "Every 1 hour" or "Every day at 8:00 AM" are both fine.
4. Click **Save**.
5. **Manually trigger the job** by clicking **Run Now** to verify it completes successfully.

> [!TIP]
> If the first run fails, click into the run and read the logs. The most common issues are: (1) wrong schema permissions, (2) source tables don't exist yet (you may need to run your Prefect flow first), or (3) a dbt test is failing.

📷 **Screenshot checkpoint:** Take a screenshot of your scheduled job configuration page.

📷 **Screenshot checkpoint:** Take a screenshot of a successful job run (green checkmark, logs showing models and tests completed).

---

## Step 7: Create a CI/CD Job for Pull Requests

This job runs automatically whenever you open a pull request against your main branch. It catches issues before they merge.

1. Go to **Deploy > Jobs** again.
2. Click **Create Job**.
3. Configure the job:
   - **Job name:** `CI - Pull Request Tests`
   - **Environment:** Same Production environment
   - **Commands:**
     ```
     dbt build
     ```
   - **Triggers:** Check **Run on pull requests** (uncheck the schedule trigger)
   - **Compare changes against:** Select your main branch (`main` or `master`)
4. Click **Save**.

> [!TIP]
> To test this, create a small branch, make a minor change to one of your dbt models (e.g., add a comment), push the branch, and open a pull request. You should see the CI job kick off automatically on GitHub.

📷 **Screenshot checkpoint:** Take a screenshot of a pull request on GitHub showing the dbt Cloud CI check running or completed.

---

## Step 8: Verify Everything is Working

1. Go to **Deploy > Run History** in dbt Cloud.
2. You should see at least one completed run (the manual run from Step 6).
3. Click into the run and review the output:
   - All models should show as "OK" or "SUCCESS".
   - All tests should show as "Pass".
   - Check for any warnings (yellow) that you might want to address.

If everything looks good, you're done with dbt Cloud setup.

---

## Troubleshooting

**"Connection failed" when testing Snowflake:**
- Verify your account identifier format. It should be `org-account` or `account.region`, not a URL.
- Re-enter your username and password — credentials may not transfer between projects.
- Make sure the warehouse is not suspended with auto-resume disabled.

**"Project subdirectory not found":**
- Ensure `dbt/dbt_project.yml` exists in your repository at the path you specified.
- The subdirectory is relative to the repo root. If your structure is `repo/dbt/dbt_project.yml`, the subdirectory is `dbt/`.

**Can't delete old project:**
- Delete all jobs in the project first (**Deploy > Jobs**), then try deleting the project again.

**Job fails with "source not found":**
- Your Snowflake raw tables may not exist yet. Run the DDL in `prefect/snowflake_objects.sql` first, then run your Prefect flow to load some data.

**Job fails with test errors:**
- Read the test failure output carefully. It tells you exactly which test failed and why.
- A `not_null` failure means you have null values in a column that should not have them. Check your data cleaning logic.
- A `relationships` failure means you have foreign key values that don't exist in the parent table. This could be expected if your data sources are out of sync.
