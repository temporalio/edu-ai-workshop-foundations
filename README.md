# AI Agent Workshop with Temporal

This repository contains a hands-on workshop demonstrating how to build AI agents with Temporal Workflows. 
The workshop teaches the progression from simple AI agents to production-ready, durable systems that handle failures gracefully and support human-in-the-loop interactions.

## Workshop Overview

This workshop demonstrates three key concepts:

1. **Traditional AI Agent** - A simple research agent that calls an LLM and generates a PDF report
2. **Durable Execution** - The same agent built with Temporal workflows for fault tolerance and automatic retries
3. **Human-in-the-Loop** - Adding Temporal Signals to enable human decision-making within AI workflows

## Repository Structure

```
├── notebooks/          # Interactive Jupyter notebooks for the workshop
│   ├── content/        # Main workshop content
│   └── exercises/      # Hands-on exercises
├── src/                # Standalone Python implementations
│   ├── module_one_01_ai_agent/           # Simple AI agent
│   ├── module_one_02_adding_durability/  # Temporal-based durable agent
│   └── module_one_03_human_in_the_loop/  # Agent with human interaction
└── justfile           # Development automation commands
```

## Prerequisites

- Python 3.13+
- OpenAI API key (or other LLM provider API key)
- Basic familiarity with Python and async programming

## Installation

### 1. Install Python 3.13 with uv

This project uses `uv` for Python version and package management:

```bash
# Install uv if you haven't already
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install Python 3.13
uv python install 3.13

# Verify installation
uv python list
```

### 2. Install Dependencies

```bash
# Clone the repository
git clone https://github.com/temporalio/edu-ai-workshop.git
cd edu-ai-workshop

# Install all dependencies
uv sync
```

### 3. Configure API Keys

Copy the example environment file and add your API key:

```bash
cp .env.example .env
```

Then edit `.env` and replace `YOUR_API_KEY` with your actual OpenAI API key:

```bash
LLM_API_KEY = "your-actual-openai-api-key"
LLM_MODEL = "openai/gpt-4o"
```

## Running the Workshop

### Option 1: Google Colab

You can use [Google Colab](https://colab.research.google.com/) and run the workshop from the files in this [Google Drive]().

1. Ensure you are signed in to a Google account.
2. Open the notebook, go to **File** and click **Save a copy in Drive** to save the notebook to your Google Drive.
3. Follow the notebook instructions step by step. Do this for every content and exercise.

### Option 2: Interactive Notebooks

For the complete workshop experience with explanations:

1. Start Jupyter Lab:
   ```bash
   uv run --with jupyter jupyter lab
   ```

2. Navigate to `notebooks/content/` and open `01_An_AI_Agent.ipynb`

3. Follow the notebook instructions step by step

### Option 3: Standalone Code Examples

For running the code examples directly, follow the README in the `src` directory.

#### Module 1: Basic AI Agent

This demonstrates a simple agent that:
- Prompts for a research topic
- Calls an LLM for research
- Generates a PDF report
- Shows the limitations of non-durable execution

#### Module 2: Durable Execution with Temporal

- Fault-tolerant execution that survives process crashes
- Automatic retries with exponential backoff
- State persistence across worker restarts
- Monitoring via Temporal Web UI at http://localhost:8080

#### Module 3: Human-in-the-Loop

- Pausing workflows for human decision-making
- Using Temporal Signals for real-time communication
- Allowing humans to approve or modify AI-generated content

## Development Commands

The project uses `just` for development automation:

```bash
just check          # Run all checks (lint, format-check, typecheck)
just fix            # Auto-fix linting and formatting issues  
just lint           # Run ruff linter with fixes
just format         # Format code with ruff
just typecheck      # Run mypy type checking
just clean          # Remove Python cache files
```

## Key Learning Outcomes

By completing this workshop, you'll learn:

1. **Why AI Agents are Distributed Systems** - Understanding the complexity that emerges when AI agents call external APIs and other services

2. **Durability and Fault Tolerance** - How Temporal workflows provide automatic recovery from failures without losing progress

3. **Human-in-the-Loop Patterns** - Using Temporal Signals to incorporate human decision-making into AI workflows


## Workshop Structure

### Part 1: Building Your First AI Agent
- Understanding agentic AI concepts
- Creating basic LLM interactions
- Generating PDF reports
- Identifying distributed systems challenges

### Part 2: Adding Durability
- Introduction to Temporal Workflows
- Converting agents to durable Workflows
- Implementing automatic retries
- Monitoring Workflow Execution

### Part 3: Human Integration
- Temporal Signals for real-time communication
- Workflow pause/resume patterns
- Building approval workflows
- Production deployment considerations

## Technical Architecture

### Normal Execution (`module_one_01_ai_agent/`)
- Single-threaded execution
- No state persistence
- Manual error handling
- Process failure loses all progress

### Durable Execution (`module_one_02_adding_durability/`)
- **Workflows**: Orchestrate the overall process
- **Activities**: Contain business logic (LLM calls, PDF generation)
- **Workers**: Execute workflows and activities
- **Automatic retries**: Configurable retry policies
- **State persistence**: Survives worker restarts

### Human-in-the-Loop (`module_one_03_human_in_the_loop/`)
- **Signals**: Enable real-time workflow communication
- **Workflow pause/resume**: Wait for human decisions
- **Dynamic routing**: Based on human input
- **Audit trail**: Complete history of decisions and actions

## Troubleshooting

### Common Issues

1. **Python Version**: Ensure you're using Python 3.13+
2. **API Keys**: Verify your OpenAI API key is correctly configured
3. **Temporal Server**: Make sure the Temporal server is running before starting workers
4. **Port Conflicts**: The Temporal Web UI runs on port 8080 by default

### Getting Help

- Check the Temporal documentation: https://docs.temporal.io/
- Review the workshop notebooks for detailed explanations
- Examine the source code in `src/` for implementation details

## Contributing

This workshop is designed for educational purposes. Feel free to:
- Submit issues for bugs or unclear instructions
- Propose improvements to the examples
- Share your own AI agent implementations

## License

[Include appropriate license information]