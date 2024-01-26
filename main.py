from openai import OpenAI
from functions import resorts, hotels

import time
import json

### OpenAIの呼び出しクライアントを作成する。
client = OpenAI()

### アシスタントIDを指定して、情報を取得する。
### ※アシスタントはOpenAI社のページで定義され、詳細はREADMEに参照
assistant = client.beta.assistants.retrieve(
    assistant_id="asst_kmRH7iY8sxNOHbk0aGBipCHf"
)

### 対話スレッド（セッション）を作成する。
thread = client.beta.threads.create()

### 対応を繰り返し。
while 1:
    ### 送信メッセージを組み立て、連続２回改行でメッセージ完了と認識します。
    msg = ""
    while msg[-2:] != "\n\n":
        try:
            s = input(">>> ")
            msg = msg + s + "\n"
        except EOFError:
            client.beta.threads.delete(thread.id)
            exit()

    ### メッセージをアシスタントに送信する。
    message = client.beta.threads.messages.create(thread_id=thread.id, role="user", content=msg)
    ### 送信メッセージのタイムスタンプを記録、スレッドのメッセージを出力するとき、この時間以降のメッセージのみ表示する。
    create_ts = message.created_at
    ### メッセージ会話処理を実行する。
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant.id
    )

    ### 実行状態を取得する。
    run = client.beta.threads.runs.retrieve(
        thread_id=thread.id,
        run_id=run.id
    )

    ### 処理完了まで処理を監視する
    while run.status != "completed":
        print("run.status = {}".format(run.status))
        match run.status:
            ### 実行待ちの場合、１０秒間待機
            case "queued":
                time.sleep(10)
            ### 実行中の場合、１０秒間待機
            case "in_progress":
                time.sleep(10)
            ### 何らかの原因でエラーになる場合、プログラムを終了する。
            case "failed":
                exit()
            ### ファンクションの呼び出しが必要な場合、ファンクション処理に入る。
            case "requires_action":
                ### 処理結果リストを用意
                outputs = []
                ### 各呼び出し要求に対して順番に処理する。
                for call in run.required_action.submit_tool_outputs.tool_calls:
                    ### 呼び出し情報を取得する。
                    call_id = call.id
                    call_name = call.function.name
                    call_args = call.function.arguments

                    print("function call -> {}:{}({})".format(call_id, call_name, call_args))
                    ### 呼び出し名で振り分ける。
                    match call_name:
                        ### スキー場一覧取得処理ファンクションの呼び出し
                        case "get_resorts":
                            outputs.append({
                                "tool_call_id": call_id,
                                "output": resorts.get_resorts()
                            })
                        ### スキー場に属するホテル一覧取得処理ファンクションの呼び出し
                        case "get_resort_hotels":
                            args = json.loads(call_args)
                            output = hotels.get_resort_hotels(args['resortId'])
                            outputs.append({
                                "tool_call_id": call_id,
                                "output": output
                            })
                        ### ホテル予約処理ファンクションの呼び出し
                        case "booking_hotel":
                            args = json.loads(call_args)
                            output = hotels.booking_resort_hotels(args)
                            outputs.append({
                                "tool_call_id": call_id,
                                "output": output
                            })

                ### 呼び出した結果をアシスタントに送信する。
                client.beta.threads.runs.submit_tool_outputs(
                    thread_id=thread.id,
                    run_id=run.id,
                    tool_outputs=outputs
                )
        ### 再度実行状態を取得する。
        run = client.beta.threads.runs.retrieve(
            thread_id=thread.id,
            run_id=run.id
        )

    ### 対話メッセージの出力。
    for msg in client.beta.threads.messages.list(thread_id=thread.id):
        if msg.created_at > create_ts:
            for c in msg.content:
                print("<<< {}".format(c.text.value))



