async def run_workflow_stream(user_input: str) -> None:
    """
    Runs the LangGraph workflow with streaming output and prints each update to the terminal.

    Args:
        user_input (str): The user's question or request to be processed by the assistant.

    Returns:
        None
    """
    # Generate current time string
    current_time: str = datetime.now().strftime("%Y-%m-%d %H:%M:%S %Z")

    # Format the prompt with user input and current time
    formatted_messages: list[BaseMessage] = template.format_messages(
        user_input=user_input, current_time=current_time
    )

    # Prepare the initial state for the workflow
    inputs: dict = {"messages": formatted_messages, "llm_final_answer": ""}

    print("\n→ Streaming workflow updates:")
    # Stream the workflow execution and print each update
    try:
        async for update in workflow.astream(
            input=inputs, stream_mode="messages", config={"callbacks": [tracer]}
        ):
            print("\n=== Workflow Update ===")
            print(update, flush=True)  # save this for debugging if needed.

            # Check if the update dictionary has the 'assistant' key. Otherwise it will have 'tools' key.
            if "assistant" in update:
                # get the object associated with the key 'assistant'
                assistant_output = update.get("assistant", {})

                # Ensure the assistant_output is not empty and has the 'messages' key
                if not assistant_output or not assistant_output.get("messages"):
                    continue

                # Get the stuff inside 'messages' array. We get the first index because "updates" mode only adds one message at a time in the array.
                assistant_message = assistant_output["messages"][0]

                # CASE 1: Check for TOOL CALLS and make sure they are not empty
                if hasattr(assistant_message, "tool_calls") and assistant_message.tool_calls:
                    # Some models like GPT 4.1 can output content and tool calls in the same message. This if condition is for them.
                    if assistant_message.content:
                        print(f"LLM Answer: {assistant_message.content}", flush=True)
                        
                    # loop through tool calls because there may be multiple tool calls. tool_calls is a list of dicts.
                    for tool_call in assistant_message.tool_calls:
                        tool_name = tool_call.get("name", "unknown_tool")
                        tool_args = tool_call.get("args", {})

                        # Format the arguments nicely: key1="value1", key2="value2"
                        args_str = ", ".join(f'{k}="{v}"' for k, v in tool_args.items())
                        print(f"Tool Call to {tool_name}: Ran with arguments: {args_str}", flush=True)

                # CASE 2: Check for FINAL ANSWER (content without tool calls)
                # Check if content is present and non empty AND ensure tool_calls is empty or not present
                elif hasattr(assistant_message, "content") and assistant_message.content and not (
                        hasattr(assistant_message, "tool_calls") and assistant_message.tool_calls
                    ):
                    print(f"LLM Answer: {assistant_message.content}", flush=True)
                # ---------------------------------------------------
                
            # for tool processing, we will only show tool processing, tool results can be large and we will not yield them.
            elif "tools" in update:
                print("Processing tool call ...", flush=True)
            else:
                # this shouldn't happen but just in case some shit happens
                print(
                    "\n-------------- GOT UNKNOWN TYPE OF NODE -------- CHECK output!",
                    flush=True,
                )
                print(f"Unknown node type: {update}", flush=True)

        # try block finished so output workflow done. 
        print("\n====✓✓ Workflow completed successfully")

    except Exception as exc:
        print(f"\n✗ Workflow Error: {exc}")