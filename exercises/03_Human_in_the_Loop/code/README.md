# Exercise 3: Human in the Loop

Add interactive control to your workflow with Temporal Signals and Queries.

## Prerequisites

- Temporal server running (`temporal server start-dev`)
- `.env` file configured with `LLM_API_KEY` and `LLM_MODEL`
- An OpenAI API key is required for image generation with DALL-E

## Overview

In this exercise, you'll:

- Review a workflow with an existing keep/edit Signal loop
- Add a `filename_signal` with a `wait_condition` timeout
- Register the `generate_ai_image` Activity with the Worker
- Send a filename Signal from the client
- Add a `_character_count` Query handler
- Send a Query from the client

## Instructions

### Part 1: Review the Existing Code

Open `practice/workflow.py` and review the existing patterns:
- `user_decision_signal` — already decorated with `@workflow.signal`
- `get_research_result` — already decorated with `@workflow.query`
- The keep/edit loop in `run()` — already working

### Part 2: Add the Filename Signal

In `practice/workflow.py`:

1. Set `self._filename` to the default value `"research_report"`
2. Add the `@workflow.signal` decorator to the `filename_signal` method
3. In the `wait_condition` for the filename signal:
   - Set the lambda condition so `self._filename != "research_report"`
   - Set the timeout to `timedelta(seconds=20)`

### Part 3: Register the Activity

In `practice/worker.py`, add `generate_ai_image` to the activities list.

### Part 4: Send the Filename Signal

In `practice/starter.py`, find the `send_user_decision_signal` function. After getting the filename input, send the `filename_signal`:
```python
await handle.signal("filename_signal", FilenameSave(filename=filename))
```

### Part 5: Add the Character Count Query

In `practice/workflow.py`:

1. Add a `_character_count: int = 0` attribute in `__init__`
2. Add a `@workflow.query` handler called `get_research_stats` that returns `self._character_count`
3. After storing the research result, set `self._character_count = len(research_facts["choices"][0]["message"]["content"])`

### Part 6: Send the Query

In `practice/starter.py`, in the `query_research_stats` function:

1. Pass `GenerateReportWorkflow.get_research_stats` to the `handle.query()` call
2. Print the `stats` variable in the f-string

## Running the Exercise

```bash
# Terminal 1: Start the Worker
cd code/03_human_in_the_loop/practice
uv run worker.py

# Terminal 2: Start the Workflow
cd code/03_human_in_the_loop/practice
uv run starter.py
```

### Testing Signals
1. Run the starter and enter a research topic
2. When prompted, type `keep` to approve, or `edit` to modify
3. Enter a filename within 20 seconds to test the filename signal
4. Check the file explorer for your new PDF

### Testing the Timeout
1. Run the starter again
2. Type `keep` when prompted
3. Do NOT enter a filename — wait 20 seconds
4. The file will be saved as `research_report.pdf`

### Testing Queries

To test the query independently, you can use the Temporal CLI:
```bash
temporal workflow query --workflow-id <your-workflow-id> --name get_research_stats
```

## Hints

If you get stuck, check the `solution/` directory for the completed code.
