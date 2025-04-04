import requests
import json

INPUT_FILES = {
    "small": "data/inputs_small.txt",
    "medium": "data/inputs_medium.txt",
    "large": "data/inputs_large.txt"
}

def run_code_in_docker(code: str, timeout: int = 30):
    try:
        all_inputs = {}
        for size, path in INPUT_FILES.items():
            with open(path) as f:
                lines = f.read().strip().split("\n")
                arrs = [[int(x) for x in line.split(",")] for line in lines]
                all_inputs[size] = arrs

        input_str = json.dumps(all_inputs)

        # Wrap the user code with benchmarking logic + thread pool inside Docker
        wrapped_code = (
            code.strip()
            + "\n\n"
            + "import sys, json, time, concurrent.futures\n"
            + "input_data = json.loads(sys.stdin.read())\n"
            + "def run_sort(arr):\n"
            + " start = time.time()\n"
            + " result = sort_array(arr)\n"
            + " end = time.time()\n"
            + " if result != sorted(arr):\n"
            + "  return float('inf')\n"
            + " return end - start\n"
            + "def benchmark(arrs):\n"
            + " with concurrent.futures.ThreadPoolExecutor(max_workers=57) as executor:\n"
            + "  futures = [executor.submit(run_sort, arr) for arr in arrs]\n"
            + "  return [f.result() for f in concurrent.futures.as_completed(futures)]\n"
            + "results = {}\n"
            + "for key in ['small', 'medium', 'large']:\n"
            + " results[key] = benchmark(input_data[key])\n"
            + "print(json.dumps(results))"
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

        response = requests.post("http://localhost:8088/run", json=payload, headers=headers, timeout=timeout+20)
        if response.status_code != 200:
            print("Non-200 response:", response.status_code, response.text)
            return float("inf"), float("inf"), float("inf")
        
        data = response.json()

        if data.get("error") or data.get("stderr"):
            print("Runtime error:", data.get("error"))
            print("Runtime stderr:", data.get("stderr"))
            return float("inf"), float("inf"), float("inf")
        
        try:
            output = json.loads(data.get("stdout", "{}"))
            def sanitize(lst):
                valid = [x for x in lst if isinstance(x, (float, int)) and x != float("inf") and x == x]
                if not valid:
                    return 9999999.0
                return round(sum(valid) / len(valid), 6)

            return (
                sanitize(output.get("small", [])),
                sanitize(output.get("medium", [])),
                sanitize(output.get("large", []))
            )

        except Exception as e:
            print("Parse error:", str(e))
            return float("inf"), float("inf"), float("inf")

    except Exception as e:
        print("Docker runner error:", str(e))
        return float("inf"), float("inf"), float("inf")
