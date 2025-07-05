import json

def safe_json_loads(val):
    try:
        return json.loads(val)
    except json.JSONDecodeError:
        print(f"Invalid JSON: {val}")
        return {}  # Return an empty dictionary or None if JSON is invalid