## Demo Instructions

### Setup Instructions

Before running the demos, ensure you have the correct Python version and dependencies installed:

#### Install Python 3.13 with uv
This project requires Python 3.13. If you don't have it installed, use uv to install it:

```bash
# Install Python 3.13 using uv
uv python install 3.13

# Verify the version
uv python list
```

The project is already configured to use Python 3.13 via the `.python-version` file, so uv will automatically use the correct version when you run commands in this directory.

#### Install Dependencies

1. Create a virtual environment: `python -m venv env`

2. Activate the environment:
- Mac: `source env/bin/activate`
- Windows: `env\Scripts\activate`

3. Install dependencies from `pyproject.toml` directory: `pip install -e ..`

4. Once activated, you should see (env) prepended to your bash prompt

### Instructor Instructions 

#### Normal Execution Demo

1. Demonstrate normal (non-durable) execution by routing to `mpdule_01_ai_agent` and running `python app.py`.
2. Enter a research topic or question in the CLI. 
3. When the countdown starts, kill the process with 'CTRL+C'.
4. Ask the auidience
    > What will happen if I run the execution again?
        The answer should be "It will start over."
        You can ask
    > Who thinks it will resume where it left off?"
        No one will probably think this, as this is not typical behavior for any programming language.
4. Run the Normal Execution script again with `python app.py`. Confirm that the code did, in fact, start over. The state is lost, meaning the LLM no longer remembers your original prompt. Imagine this happening during a more intensive workflow — if you’ve already made significant progress, you’ve likely consumed a considerable number of tokens. Restarting the process would require you to repeat steps and spend additional tokens unnecessarily.

#### Durable Execution Demo
1. We will now showcase how this is different with Temporal. Route to the `module_02_adding_durability` directory. 
2. Open three terminal windows.
3. In one terminal window, start the Temporal server with `temporal server start-dev --ui-port 8080 --db-filename clusterdata.db`.
4. In another terminal window, run the worker with `python worker.py`. You'll see some output indicating that the Worker has been started.
5. In the third terminal window, execute your Workflow with `python starter.py`.
6. You'll be prompted to enter a research topic or question in the CLI. 
7. Once you do, in the terminal window with the Worker running, you'll see: `Research complete! Time to generate PDF. Kill the Worker now to demonstrate durability.`. Kill the process with `CTRL+C`.
8. Go on the Web UI and showcase that even though there is no Worker running, the Workflow can still persist despite restarts and infrastructure failures.
9. Now point out that when we restart the process (by rerunning the Worker with `python worker.py`), you won't lose your state or progress, you'll continue from where you left off. Showcase two things:
    - You'll see the Workflow Execution complete successfully in the Web UI. 
    - You can also show the PDF that will appear in the `module_02_adding_durability` directory.  

### Human in the Loop Demo (Signals)
1. We will now showcase how we can leverage human-in-the-loop with Temporal Signals. Route to the `module_one_03_human_in_the_loop` directory. 
2. In one terminal window, run your Worker with `python worker.py`.
3. In another terminal window, execute your Workflow with `python starter.py`.
4. You'll be prompted to enter a research topic or question in the CLI. 
5. Once you do, you'll be prompted with the ability to Signal or Query the Workflow.
6. Type 'query' and you'll see the output in the terminal window where you started your Workflow Execution. 
7. Time to demonstrate Signals. Back in the terminal window when you started your Workflow Execution, you'll see that you are prompted to choose one of the two options:
    a. Approve of this research and if you would like it to create a PDF (type 'keep' to send a Signal to the Workflow to create the PDF).
    b. Modify the research by adding extra info to the prompt (type 'edit' to modify the prompt and send another Signal to the Workflow to prompt the LLM again).
8. Demonstrate the modification by typing `edit`.
9. Enter additional instructions (e.g.: "turn this into a poem") and see the new output in the terminal window by typing `query` again.
10. Finally, show that you can keep changing the execution path of your Workflow Execution by typing `keep`. Show that the PDF has appeared in your `module_one_03_human_in_the_loop` directory.

### Human in the Loop Demo (Signals)
1. We will now showcase how we can leverage human-in-the-loop with Temporal Signals. Route to the `module_one_03_human_in_the_loop` directory. 
2. In one terminal window, run your Worker with `python worker.py`.
3. In another terminal window, execute your Workflow with `python starter.py`.
4. You'll be prompted to enter a research topic or question in the CLI. 
5. Once you do, you'll be prompted with the ability to Signal or Query the Workflow.
6. Type 'query' and you'll see the output in the terminal window where you started your Workflow Execution. 
7. Time to demonstrate Signals. Back in the terminal window when you started your Workflow Execution, you'll see that you are prompted to choose one of the two options:
    a. Approve of this research and if you would like it to create a PDF (type 'keep' to send a Signal to the Workflow to create the PDF).
    b. Modify the research by adding extra info to the prompt (type 'edit' to modify the prompt and send another Signal to the Workflow to prompt the LLM again).
8. Demonstrate the modification by typing `edit`.
9. Enter additional instructions (e.g.: "turn this into a poem") and see the new output in the terminal window by typing `query` again.
10. Finally, show that you can keep changing the execution path of your Workflow Execution by typing `keep`. Show that the PDF has appeared in your `module_one_03_human_in_the_loop` directory.

### Agentic Loop Demo - Simple AI Booking Agent
1. We will now showcase how an AI agent can dynamically choose its own tools with Temporal. Route to the `module_one_04_agentic_loop` directory with `cd module_one_04_agentic_loop`.
2. Open three terminal windows.
3. In one terminal window, start the Temporal server with `temporal server start-dev --ui-port 8080` (if not already running).
4. In another terminal window, navigate to the `module_one_04_agentic_loop` directory and run the worker with `python worker.py`.
5. In the third terminal window, execute your Workflow with `python starter.py`.
6. Enter a booking goal when prompted (e.g., "Book a flight from RDU to London on November 18").
7. Watch as the AI agent:
    - Decides to search for flights first
    - Extracts the origin, destination, and date from your goal
    - Executes the search
    - Decides to book the flight
    - Completes the process
8. The output shows:
    - The final result
    - Steps the AI agent took
9. In the Web UI, point out the:
    - Input, output
    - The execution of each tool (search_flights, check_availability, book_flight)
    - The difference in the tools selected if you do something like "Book a flight from RDU to NYC on Oct 18, check seat availability first and show me the total cost" vs. "Book a flight from RDU to NYC on Oct 18".