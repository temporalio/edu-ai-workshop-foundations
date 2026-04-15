# Exercise 1: Foundations of Durable AI

Build a non-durable AI research report generator to understand why durability matters.

## Prerequisites

- `.env` file configured with `LLM_API_KEY` and `LLM_MODEL` (see `.env.example` in the repo root)
- An OpenAI API key is required for image generation with DALL-E

## Overview

In this exercise, you'll:

- Call an LLM to generate research on a topic
- Use the LLM to extract the subject from the research prompt
- Generate an AI image of the research subject
- Create a PDF with the research and image
- Observe how killing the process loses all progress (no durability)

## Instructions

### Part 1: Implement the Image Generation Function

Open `practice/app.py` and find the `generate_ai_image` function. Fill in the TODO items:

1. Create an image prompt that includes the subject
2. Call the `image_generation` function with the prompt, model, and API key

### Part 2: Extract the Subject from the Prompt

In the main flow section, fill in the TODO items to:

1. Create a prompt that asks the LLM to extract the main topic as a single word or short phrase
2. Call `llm_call()` with that prompt
3. Extract the topic from the response

### Part 3: Wire Up Image Generation

In the main flow section, fill in the TODO to:

1. Call `generate_ai_image` with the research topic
2. Extract the image URL from the response

### Part 4: Test the Fragility

1. Run the app: `uv run app.py`
2. Enter a research topic
3. While the countdown is running, press `Ctrl+C` to kill the process
4. Restart the app — notice that all progress (LLM call, image generation) is lost

Think about what could go wrong in this application:
- What if the image generation API goes down?
- What if the PDF creation fails after you've already paid for the LLM call?
- How can we make this code more durable?

We'll solve these problems in the next exercise with Temporal.

## Running the Exercise

```bash
cd code/01_foundations/practice
uv run app.py
```

## Hints

If you get stuck, check the `solution/` directory for the completed code.
