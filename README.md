# [Self-Serve Version] Foundations of Durable AI with Temporal

This repository contains the self-serve version of this workshop, demonstrating how to build AI agents with Temporal Workflows. 
The workshop teaches the progression from simple AI agents to production-ready, durable systems that handle failures gracefully and support human-in-the-loop interactions.

## How to Use this Repository

1. To present this workshop, present in Codespace so that students don't need to download any software on their machines. To do so, refer to [this document](./codespaces.md).
2. This repository contains the Jupyter notebooks under [the notebooks directory](./notebooks). The notebooks are used as an educational tool for students to get practice with being hands-on with Temporal. 
3. The slides that accompany the Jupyter notebooks are [here](https://docs.google.com/presentation/d/1N4YSml7yA3Gfq3svDFJpC6afQVn_m2txl4jwQ-lJqBQ/edit?usp=drive_link) and are given in the non-self-serve version (live version).
4. The instructor goes through the slides. When there is a a little icon of a person at a keyboard on the bottom right of the slides, this lets students know that it's time to get hands-on and move to the notebooks.
5. There will also be time for students to practice working independently with the material in the [exercises directory](./exercises/). The Jupyter notebooks will reference when it's time to do work on an exercise directory.
6. For the live version of this workshop (using slides), refer to the `main` branch on this repository.

## Workshop Overview

This workshop demonstrates three key concepts:

1. **Traditional AI Agent** - A simple research agent that calls an LLM and generates a PDF report
2. **Durable Execution** - The same agent built with Temporal workflows for fault tolerance and automatic retries
3. **Human-in-the-Loop** - Adding Temporal Signals to enable human decision-making within AI workflows
4. **AI Agents** - An introduction into the Agentic Loop

## Repository Structure

```
├── notebooks/          # Interactive Jupyter notebooks for the workshop
│   ├── Solution        # Solutions for the code-alongs during the workshop
│   ├── Content         # Jupyter notebooks to run during workshop
├── exercises/          # Hands-on exercises for the workshop
│   ├── Practice        # Every chapter will have a Practice dir where students do their work in
│   ├── Solution        # Every chapter will have a Solution dir where students can refer
├── demos/              # Directory for demos for the instructor
│   ├── module_one_01_foundations_ai/     # Simple chain workflow
│   ├── module_one_02_adding_durability/  # Temporal-based durable workflow
│   └── module_one_03_human_in_the_loop/  # Adding human in the loop into our application
|   └── module_one_04_agentic_loop/       # Agent that can make its own decisions
|   └── README.md      # Instructions on how to run demos
```

## Prerequisites

- Python 3.13+
- [OpenAI API key](https://platform.openai.com/api-keys)

## Running the Workshop: Codespaces

You can run this workshop on Codespaces as an Exercise Environment.

You can launch an exercise environment for this course using GitHub Codespaces by following [this](codespaces.md) walkthrough.

Before presenting, make sure you have cleared all outputs if you've experiemented with this workshop prior to presenting.
![Clear all outputs](https://i.postimg.cc/RZvQmxLP/clear-all-outputs.png)

## Key Learning Outcomes

By completing this workshop, you'll learn:

1. **Why AI Agents are Distributed Systems** - Understanding the complexity that emerges when AI agents call external APIs and other services

2. **Durability and Fault Tolerance** - How Temporal workflows provide automatic recovery from failures without losing progress

3. **Human-in-the-Loop Patterns** - Using Temporal Signals to incorporate human decision-making into AI workflows

## Workshop Structure

### Part 1: Building Your First AI Chain Workflow
- Creating basic LLM interactions
- Calling Actions from your LLM interactions
- Identifying distributed systems challenges

### Part 2: Adding Durability
- Introduction to Temporal
- Converting agents to durable Workflows
- Implementing automatic retries
- Monitoring Workflow Execution

### Part 3: Human Integration
- Temporal Signals for real-time communication
- Workflow pause/resume patterns
- Sending Queries to your Workflows

### Part 4: AI Agents
- Introduction to Agentic loop
- Determining when the goal is complete

## Contributing

This workshop is designed for educational purposes. Feel free to:
- Submit issues for bugs or unclear instructions
- Propose improvements to the examples
- Share your own AI agent implementations