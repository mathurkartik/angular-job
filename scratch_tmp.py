import json

log_path = r"C:\Users\KartikMathur\.gemini\antigravity-ide\brain\0e5cd0e5-048a-425d-bb9d-8eb869a5ab9d\.system_generated\logs\transcript.jsonl"
out_path = r"C:\Users\KartikMathur\.gemini\antigravity-ide\brain\0e5cd0e5-048a-425d-bb9d-8eb869a5ab9d\scratch\user_request_3129.txt"

with open(log_path, "r", encoding="utf-8") as f:
    for line in f:
        data = json.loads(line)
        if data.get("step_index") == 3129:
            with open(out_path, "w", encoding="utf-8") as out:
                out.write(data.get("content"))
            print("Successfully wrote step 3129 to user_request_3129.txt")
            break
