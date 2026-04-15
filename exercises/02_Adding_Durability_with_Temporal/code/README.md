# Exercise 2: Adding Durability with Temporal

Transform the fragile research report generator into a durable Temporal application.

## Prerequisites

- Temporal server running (`temporal server start-dev`)
- `.env` file configured with `LLM_API_KEY` and `LLM_MODEL`
- An OpenAI API key is required for image generation with DALL-E

## Overview

In this exercise, you'll:

- Transform LLM calls and tool executions into Temporal Activities
- Use a Temporal Workflow to orchestrate Activities
- Register Activities with a Worker
- Observe how Temporal handles retry failures (intentionally bad timeout)
- Fix the error and watch the Workflow complete successfully

## Instructions

### Part 1: Add the Activity Decorator

Open `practice/activities.py`. The `generate_ai_image` function is missing its `@activity.defn` decorator. Add it.

### Part 2: Fix the Workflow

Open `practice/workflow.py`:

1. Add the `@workflow.run` decorator to the `run` method
2. The `generate_ai_image` Activity call has a `start_to_close_timeout` of **1 second** — this is intentionally too short. Leave it for now to observe the retry behavior.

### Part 3: Register Activities with the Worker

Open `practice/worker.py`. The `activities` list is empty. Register `llm_call`, `create_pdf`, and `generate_ai_image`.

### Part 4: Set the Task Queue in the Starter

Open `practice/starter.py`. Set the `task_queue` to `"exercise-02-durability"` to match the Worker.

### Part 5: Run and Observe Retries

1. Start the Worker: `uv run worker.py`
2. In a separate terminal, run the Starter: `uv run starter.py`
3. Open the Temporal Web UI (http://localhost:8233)
4. Watch the `generate_ai_image` Activity retry repeatedly — the 1-second timeout is too short for image generation

In the Web UI, expand the Pending Activity to find:
- What is the error message?
- What retry attempt is it on?
- How many seconds until the next retry?

### Part 6: Fix the Timeout

1. Terminate the stuck workflow in the Web UI (dropdown → Terminate → reason: "Bad timeout")
2. Go back to `practice/workflow.py` and increase the `generate_ai_image` timeout to **30 seconds**
3. Restart the Worker and run the Starter again
4. Watch the Workflow complete successfully in the Web UI

## Running the Exercise

```bash
# Terminal 1: Start the Worker
cd code/02_adding_durability/practice
uv run worker.py

# Terminal 2: Start the Workflow
cd code/02_adding_durability/practice
uv run starter.py
```

## Hints

If you get stuck, check the `solution/` directory for the completed code.
