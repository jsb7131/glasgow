import requests
import json

def run_code_in_docker(code: str, arr: list, timeout: int = 30) -> float:
    try:
        input_str = json.dumps(arr)

        # Append wrapper to call sort_array from stdin, measure time, and validate correctness
        wrapped_code = (
            code.strip()
            + "\n\n"
            + "import sys, json, time\n"
            + "arr = json.loads(sys.stdin.read())\n"
            + "start = time.time()\n"
            + "result = sort_array(arr)\n"
            + "end = time.time()\n"
            + "if result != sorted(arr):\n"
            + " print('NOT_SORTED')\n"
            + "else:\n"
            + " print(round(end - start, 6))"
        )

        payload = {
            "image": "glot/python:latest",
            "payload": {
                "language": "python",
                "files": [
                    {"name": "main.py", "content": wrapped_code}
                ],
                "stdin": input_str,
                "args": [],
                "compile_timeout": timeout,
                "run_timeout": timeout
            }
        }

        headers = {
            "Content-Type": "application/json",
            "X-Access-Token": "my-token"
        }

        response = requests.post("http://localhost:8088/run", json=payload, headers=headers, timeout=timeout+10)
        if response.status_code != 200:
            print("Non-200 response:", response.status_code, response.text)
            return float("inf")
        
        data = response.json()

        if data.get("error") or data.get("stderr"):
            print("Runtime error:", data.get("error"))
            print("Runtime stderr:", data.get("stderr"))
            return float("inf")
        
        stdout = data.get("stdout", "").strip()
        if stdout == "NOT_SORTED":
            print("Output array is not sorted correctly")
            return float("inf")
        
        try:
            return float(stdout)
        except ValueError:
            print("Unexpected output, not a float:", stdout)
            return float("inf")

    except Exception as e:
        print("Docker runner error:", str(e))
        return float("inf")
