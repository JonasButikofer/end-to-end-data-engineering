# Working with AI Coding Agents

In Milestone 2, you'll use an AI agent to help you build a Prefect flow. This isn't a gimmick — it's how a growing number of engineering teams work today. The agent handles the boilerplate. You handle the thinking, the review, and the business logic that the agent gets wrong.

This guide covers what tools are available to you, how to use them effectively, and some honest advice about what works and what doesn't.

---

## What "Agentic Coding" Means

Most of you have already used AI for coding — asking ChatGPT to explain an error, having Copilot autocomplete a function. Agentic coding takes this further: instead of asking for one snippet at a time, you give the agent a specification (your PRD) and a codebase (your flow skeleton), and it generates a working implementation that you review, test, and refine.

The key difference: you're directing, not typing. You still need to understand what the code should do. The agent just writes it faster than you would.

---

## Tools Available to You

You don't need to spend money on this. Several good options are free for students.

### Free Tools

**GitHub Copilot** (via GitHub Student Developer Pack)
- If you haven't already, sign up at [education.github.com](https://education.github.com/pack)
- Works inside VS Code as an extension — inline completions plus a chat panel
- Best for: writing code incrementally, getting autocomplete suggestions as you type, asking questions about your codebase in the chat panel
- Limitation: works best with context already open in your editor; less useful for "build this whole thing from scratch"

**ChatGPT** (via BYU campus access)
- BYU provides access to ChatGPT through the campus agreement
- Best for: the PRD-to-code workflow in M2. Paste your PRD, the flow skeleton, and the API docs into a conversation. Ask it to implement one task at a time.
- Limitation: doesn't have direct access to your files, so you'll need to copy-paste code back and forth

**Google Gemini** (1 year free for students)
- If you haven't activated it yet, you likely have a year of Gemini access through Google's student program
- Gemini Code Assist works as a VS Code extension
- Best for: similar to Copilot — inline completions and chat-based code generation
- Limitation: context window is large but the quality can be uneven for complex multi-file tasks

### Paid Tools (Optional)

**Claude Code** (Anthropic)
- Full agentic coding tool — reads your files, runs commands, edits code autonomously
- This is what I used to build much of the course materials
- Costs money (API credits). I'm mentioning it because it's genuinely powerful, not because I expect you to buy it
- If you're curious and want to try it: [claude.ai/claude-code](https://claude.ai/claude-code)

**Cursor**
- AI-native code editor (fork of VS Code) with built-in chat, edit, and multi-file context
- Has a free tier that's quite capable
- Best for: if you want a more integrated experience than VS Code + Copilot
- [cursor.com](https://cursor.com)

> [!TIP]
> You don't need to use the most powerful tool. GitHub Copilot + ChatGPT (both free) is a solid combination for M2. Use Copilot for moment-to-moment coding and ChatGPT for the bigger "implement this task" conversations.

---

## Recommended Workflow for Milestone 2

Here's how I'd approach Task 2 (building the Prefect flow with an agent):

### Step 1: Write your PRD first

Don't skip this. The PRD is your spec. A vague prompt produces vague code. A detailed PRD with acceptance criteria, edge cases, and the data schema produces code you can actually use.

### Step 2: Gather context for the agent

Give your agent as much relevant context as possible. At minimum:

- Your completed PRD
- The flow skeleton (`prefect/flows/web_analytics_flow.py`)
- The API documentation — fetch it from the API itself:
  ```bash
  curl https://YOUR_API_URL/agent-docs
  ```
  This returns a markdown document specifically designed to be pasted into an agent prompt. It includes the response schema, example code, Snowflake table DDL, and column mappings.
- The Snowflake DDL (`prefect/snowflake_objects.sql`)

### Step 3: Ask for one task at a time

Don't say "implement the entire flow." Instead:

1. "Implement the `pull_api_data()` task. Here's the API docs and the function signature."
2. Review what it generates. Test it against the mock API (`prefect/mock_api.py`).
3. "Now implement `clean_data()`. Here's what pull_api_data returns."
4. Continue through each task.

This gives you checkpoints and makes debugging much easier.

### Step 4: Test incrementally

After each task implementation:
- Does it run without errors?
- Does it handle the edge cases from your PRD?
- Does the output look right?

Use the mock API (`python prefect/mock_api.py`) for local testing before pointing at the real API.

### Step 5: Document what happened

Fill in `templates/m2/agent_log_template.md` as you go. Note:
- What prompts worked well
- What the agent got wrong and how you fixed it
- What you wrote yourself vs. what the agent generated
- How long it took (with agent vs. your estimate without)

---

## Tips for Effective Agent Prompting

**Be specific about error handling.** Don't say "add error handling." Say "wrap the API call in a try/except. On HTTP 429, read the Retry-After header and wait. On timeout, retry with exponential backoff (2, 4, 8 seconds). After 3 failures, raise a RuntimeError."

**Provide example input and output.** "The API returns this JSON: [paste example]. I need to produce a pandas DataFrame with these columns: [list]. Rows with null customer_id should go into a separate failed_records list."

**Ask the agent to explain its choices.** "Why did you use `pd.to_numeric(errors='coerce')` here instead of `int()`?" This helps you learn and catches cases where the agent made a bad assumption.

**Don't accept code you don't understand.** If the agent generates something you can't explain, ask it to walk you through it. If you still don't understand, simplify the approach.

---

## What Agents Are Bad At

Be honest with yourself about what the agent can and can't do well:

- **Business logic judgment**: The agent doesn't know that `customer_id` must join with your customer table. You do.
- **Your specific infrastructure**: The agent doesn't know your Snowflake account name, your stage naming conventions, or your .env variable names unless you tell it.
- **Testing end-to-end**: The agent can write code that looks right but doesn't actually work with your specific data and infrastructure. You still need to run it.
- **Knowing when to stop**: Agents will happily over-engineer a solution. If you asked for error handling, you might get retry logic, circuit breakers, and a custom exception hierarchy. Keep it simple.

---

## The Honest Version

Using an agent well is a skill. It's not "type a prompt and get perfect code." It's more like working with a very fast but somewhat literal junior developer. You need to:

1. Know what you want (PRD)
2. Give clear instructions (context + specific asks)
3. Review everything (don't trust blindly)
4. Fix what's wrong (iterate)
5. Understand what was built (you own it)

The students who do best with M2 are the ones who write a thorough PRD and review the generated code critically. The ones who struggle are the ones who paste "build me a Prefect flow" and accept whatever comes back.
