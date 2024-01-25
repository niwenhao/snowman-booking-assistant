from openai import OpenAI
from functions import resorts

import time

client = OpenAI()

assistant = client.beta.assistants.retrieve(
    assistant_id="asst_kmRH7iY8sxNOHbk0aGBipCHf"
)


thread = client.beta.threads.create()

while 1:
    msg = ""
    while msg[-2:] != "\n\n":
        try:
            s = input(">>> ")
            msg = msg + s + "\n"
        except EOFError:
            client.beta.threads.delete(thread.id)
            exit()
        
    message = client.beta.threads.messages.create(thread_id=thread.id, role="user", content=msg)
    create_ts = message.created_at
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )

    while run.status != "completed":
        print("run.status = {}".format(run.status))
        match run.status:
            case "queued":
                time.sleep(3)
            case "in_progress":
                time.sleep(3)
            case "failed":
                exit()
            case "requires_action":
                outputs = []
                for call in run.required_action.submit_tool_outputs.tool_calls:
                    call_id = call.id
                    call_name = call.function.name
                    call_args = call.function.arguments

                    print("function call -> {}:{}({})".format(call_id, call_name, call_args))
                    match call_name:
                        case "get_resorts":
                            outputs.append({
                                "tool_call_id": call_id,
                                "output": resorts.get_resorts()
                            })
                client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=outputs
                )
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

    for msg in client.beta.threads.messages.list(thread_id=thread.id):
        if msg.created_at > create_ts:
            for c in msg.content:
                print(">>> {}".format(c.text.value))



