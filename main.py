from openai import OpenAI

import time

client = OpenAI()

assistant = client.beta.assistants.retrieve(
    assistant_id="asst_kmRH7iY8sxNOHbk0aGBipCHf"
)


message_index = 1
thread = client.beta.threads.create()

while 1:
    msg = ""
    while msg[-2:] != "\n\n":
        s = input(">>> ")
        msg = msg + s + "\n"
        
    message = client.beta.threads.messages.create(thread_id=thread.id, role="user", content=msg)
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )

    while run.status != "completed":
        match run.status:
            case "queued":
                time.sleep(10)
            case "in_progress":
                time.sleep(10)
            case "requires_action":
                call_id = run.required_action.submit_tool_outputs.tool_calls[0].id
                call_name = run.required_action.submit_tool_outputs.tool_calls[0].function.name
                call_args = run.required_action.submit_tool_outputs.tool_calls[0].function.arguments

                match call_name:
                    case "get_resorts":
                        client.beta.threads.runs.submit_tool_outputs(
                            thread_id=thread.id,
                            run_id=run.id,
                            tool_outputs=[
                                {
                                    "tool_call_id": call_id,
                                    "output": "・岩原スキー場, 住所：〒949-6103新潟県南魚沼郡湯沢町土樽731-79\n・蔵王温泉スキー場, 住所：〒990-2301山形県山形市蔵王温泉"
                                }
                            ]
                        )
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

    for msg in client.beta.threads.messages.list(
        thread_id=thread.id
    ):
        print(msg.content)



