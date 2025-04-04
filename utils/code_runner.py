from utils.docker_runner import run_code_in_docker

SAFE_BUILTINS = {
    "sorted": sorted,
    "range": range,
    "len": len,
    "enumerate": enumerate
}

def validate_code(code: str) -> bool:
    banned = ['import os', 'import sys', 'open(', 'eval(', 'exec(', '__', 'subprocess']
    return not any(b in code for b in banned)

def sanitize_runtime(value: float) -> float:
    # also checks for NaN
    if value == float("inf") or value != value:
        return 9999999.0
    return round(value, 6)

def run_code(code: str):
    return run_code_in_docker(code)
