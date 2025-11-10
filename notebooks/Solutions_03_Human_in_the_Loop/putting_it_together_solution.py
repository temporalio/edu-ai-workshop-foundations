async def query_research_result(client: Client, workflow_id: str) -> None:
    handle = client.get_workflow_handle(workflow_id)

    try:
        research_result = await handle.query(GenerateReportWorkflow.get_research_result)
        if research_result:
            print(f"Research Result: {research_result}")
        else:
            print("Research Result: Not yet available")

    except Exception as e:
        print(f"Query failed: {e}")


async def send_user_decision(client: Client, workflow_id: str) -> None:
    handle = client.get_workflow_handle(workflow_id)

    while True:
        print("\n" + "=" * 50)
        print("Research is complete!")
        print("1. Type 'query' to query for research result.")
        print("2. Type 'keep' to approve the research and create PDF")
        print(
            "3. Type 'edit' to modify the research."
        )
        print("=" * 50)

        decision = input("Your decision (query/keep/edit): ").strip().lower()

        if decision in {"query", "1"}:
            await query_research_result(client, workflow_id)
        elif decision in {"keep", "2"}:
            signal_data = UserDecisionSignal(decision=UserDecision.KEEP)
            await handle.signal("user_decision_signal", signal_data)
            print("Signal sent to keep research and create PDF")
            break
        elif decision in {"edit", "3"}:
            additional_prompt_input = input("Enter additional instructions for the research (optional): ").strip()
            additional_prompt = additional_prompt_input if additional_prompt_input else ""
            signal_data = UserDecisionSignal(decision=UserDecision.EDIT, additional_prompt=additional_prompt)
            await handle.signal("user_decision_signal", signal_data)
            print("Signal sent to regenerate research")
        else:
            print("Please enter either 'query', 'keep', or 'edit'")