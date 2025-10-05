# Make the API call
print("Welcome to the Research Report Generator!")
prompt = input("Enter your research topic or question: ")
result = llm_call(prompt, LLM_API_KEY, LLM_MODEL)

# Extract the response content
response_content: str = result["choices"][0]["message"]["content"]

pdf_filename = create_pdf(response_content, "research_report.pdf")
print(f"SUCCESS! PDF created: {pdf_filename}")