import requests

url = "http://localhost:8000/mcp/"

headers = {
    "Accept": "application/json",
}

# 1) List tools
list_body = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/list",
    "params": {},
}
list_resp = requests.post(url, headers=headers, json=list_body)
print("TOOLS:", list_resp.json())

# 2) Call weather tool
call_body = {
    "jsonrpc": "2.0",
    "id": 2,
    "method": "tools/call",
    "params": {
        "name": "weather",
        "arguments": {"query": "Karachi", "units": "metric"},
    },
}
call_resp = requests.post(url, headers=headers, json=call_body)
print("WEATHER:", call_resp.json())