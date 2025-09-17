import requests

url = "http://localhost:8000/mcp/"

headers = {
    "Accept": "application/json, text/event-stream",
}

# 1) List tools (SSE stream)
list_body = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {},
}
with requests.post(url, headers=headers, json=list_body, stream=True) as list_resp:
    print("TOOLS (SSE):")
    for line in list_resp.iter_lines():
        if line:
            print(line.decode("utf-8", errors="replace"))

# 2) Call weather tool (SSE stream)
call_body = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "weather",
        "arguments": {"query": "Karachi", "units": "metric"},
    },
}
with requests.post(url, headers=headers, json=call_body, stream=True) as call_resp:
    print("WEATHER (SSE):")
    for line in call_resp.iter_lines():
        if line:
            print(line.decode("utf-8", errors="replace"))