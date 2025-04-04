from concurrent.futures import ThreadPoolExecutor, as_completed
from utils.docker_runner import run_code_in_docker

SAFE_BUILTINS = {
    "sorted": sorted,
    "range": range,
    "len": len,
    "enumerate": enumerate
}

INPUT_FILES = {
    "small": "data/inputs_small.txt",
    "medium": "data/inputs_medium.txt",
    "large": "data/inputs_large.txt"
}

def validate_code(code: str) -> bool:
    banned = ['import os', 'import sys', 'open(', 'eval(', 'exec(', '__', 'subprocess']
    return not any(b in code for b in banned)

def run_code_snippet(code: str, arr: list, timeout: int = 10) -> float:
    return run_code_in_docker(code, arr, timeout)

def sanitize_runtime(value: float) -> float:
    # also checks for NaN
    if value == float("inf") or value != value:
        return 9999999.0
    return round(value, 6)

def run_all_benchmarks(code: str):
    results = {"small": [], "medium": [], "large": []}

    for size in ["small", "medium", "large"]:
        with open(INPUT_FILES[size]) as f:
            lines = f.read().strip().split("\n")
            arrs = [[int(x) for x in line.split(",")] for line in lines]

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(run_code_snippet, code, arr) for arr in arrs]
            for future in as_completed(futures):
                results[size].append(future.result())

    avg_small = sanitize_runtime(sum(results["small"]) / len(results["small"]))
    avg_medium = sanitize_runtime(sum(results["medium"]) / len(results["medium"]))
    avg_large = sanitize_runtime(sum(results["large"]) / len(results["large"]))
    return avg_small, avg_medium, avg_large
