# 🧠 Sort Bot Leaderboard

A FastAPI-based backend for submitting, benchmarking, and ranking user-submitted sorting algorithms on real-world datasets.

---

## 🚀 Basic Flow

1. **Create a user**
2. **Submit and run a sort bot**
3. **Get your leaderboard ranking**

---

## ⚙️ Setup Instructions (macOS)

```
git clone
cd glasgow
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

Then visit:  
👉 **http://127.0.0.1:8000/docs** to view the Swagger API docs

---

## 🧪 Example Usage

### 1. Create a user

**POST** `http://127.0.0.1:8000/api/v1/signup`

#### Body:
```json
{
  "username": "<your username>",
  "password": "<your password>"
}
```

---

### 2. Submit and run a sort bot

**POST** `http://127.0.0.1:8000/api/v1/submit-and-run-bot`

#### Headers:
```
username: <your username>
password: <your password>
bot-name: <bot name>
bot-description: <bot description>
```

#### Body:
```json
{
  "code": "def sort_array(arr):\n arr.sort()\n return arr"
}
```

> ⚠️ You **must** use a function named `sort_array(arr)` that returns a sorted list.  
> Use `\n` and **single spaces** for indentation inside the JSON string.

After submission, the API returns:
- `small_input_leaderboard`
- `medium_input_leaderboard`
- `large_input_leaderboard`

These show your algorithm’s rank in each category based on average runtime.

---

### 3. View the leaderboard

**GET** `http://127.0.0.1:8000/api/v1/get-leaderboard`

#### Headers:
```
username: <your username>
password: <your password>
```

#### Optional Query Parameters:
- `sort=asc` or `sort=desc`
- `board=small | medium | large`

> If omitted, defaults to:  
> `sort=asc` and `board=small`

---

## 🧵 How Code Execution Works

When you submit your code:
- Your `sort_array(arr)` function is run against **57 real test cases** (from `.txt` files).
- Each test case runs inside a sandboxed process with:
  - A **maximum timeout of 10 seconds per test case**
  - Up to **10 concurrent workers**, controlled via a thread pool
- **Your function must complete within 10 seconds per test case**, or it is considered invalid.
  - The runtime that will be reported if it reaches the timeout / is considere invalid is **9999999.0**

All inputs are arrays of integers, increasing in size from:
- `inputs_small.txt`
- `inputs_medium.txt`
- `inputs_large.txt`

Each file contains 19 different arrays for benchmarking.

---

## 🔐 Code Validation

To ensure safety:
- Your code is run in a restricted execution environment
- Built-in functions are limited (e.g. no `open`, `eval`, or `subprocess`)
- Output is checked to ensure sorting correctness

---

## 👨‍💻 Development Notes

- Developed in Python 3.11 using FastAPI
- Authentication is handled with simple header-based username/password
- Data is stored in JSON files locally
- Development process assisted by **ChatGPT 4o** via the web browser

---

Have fun building bots and climbing the leaderboard! 🏆

---

## 🐳 For Running the Isolated VM + Docker Code Runner (Colima + Docker-Run)

This feature enables secure and isolated benchmarking by spawning a single Docker container inside a lightweight Linux VM (via Colima). Great for sandboxing, safety, and reducing the load of running 57 containers.

---

You're now running **isolated, secure, parallelized Python code**...

...**inside a Linux sandbox**...

...**from a FastAPI app on macOS**...

...**via a Docker-run container inside an amd64 VM spun up by Colima on your ARM-based MacBook**. 🤯

---

### ⚙️ Setup Instructions (macOS)

> 💡 **Important:** Make sure Docker Desktop is fully quit/disabled before starting.

```bash
git clone <your-repo-url>
cd glasgow

# Install Colima + virtualization backend
brew install colima
brew install qemu

# Start the VM + launch docker-run container inside it
bash colima_runner.sh start

# (Optional) Stop it
bash colima_runner.sh stop

# Then run your app as usual:
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```

The `docker-run` container will be available at:
```
http://localhost:8088
```

---

### 🧠 Why This Setup?

- Previously, every test case (all 57) would spawn its own isolated Docker container. ✅ Very safe. ❌ But heavy.
- Now, we only spin up **one container** per submission. That container benchmarks **all 57 inputs in parallel** via an internal thread pool (inside the VM).
- If a submission crashes, runs too long, or errors out, it happens in a single place, quickly and securely.
- Much easier to monitor and manage! 👍

---

### ⏳ Timeout Considerations

- The default `docker-run` container from the public registry enforces a **30 second max execution time**.
- So: long-running sort algorithms (like recursive merge sort) **may timeout** before they finish.
- The timeout now applies to **the full submission**, not each individual test case.

> ⛓️ **Tradeoff**: You lose fine-grained control over each test's timeout, but you gain simpler, safer execution.

---

### 🔐 Additional Notes

- A basic validation step still runs before execution — we scan submitted code for banned keywords like:
  - `eval`, `exec`, `open(`, `__`, `subprocess`, etc.
- This allows us to **fail fast** without even invoking the Docker VM if something malicious is detected.

---

### 🐢 Performance Tradeoffs

- Because you're running ARM macOS → Colima VM (x86_64) → Docker container → Python code...
- There’s about a **5–10x slowdown** due to emulation and architecture translation.
- If this were running on a native Linux AMD64 host (or x86 VM), it would be much faster.
  - ✅ Faster responses
  - ✅ Lower timeout requirements
  - ✅ Possibly better throughput under load

---

### 🧪 Manual Test

Want to verify your setup?

```bash
curl --request POST http://localhost:8088/run \
  --header "Content-Type: application/json" \
  --header "X-Access-Token: my-token" \
  --data '{
    "image": "glot/python:latest",
    "payload": {
      "language": "python",
      "files": [
        { "name": "main.py", "content": "print([1,2,3])" }
      ],
      "stdin": "",
      "args": [],
      "compile_timeout": 2,
      "run_timeout": 2
    }
  }'
```

If it returns `[1, 2, 3]`, you're golden 🌟

---

### ✅ Summary

- ✅ Runs all test cases securely in a single container
- ✅ Uses a real VM to isolate user code
- ✅ Great for production safety + visibility
- ⚠️ Timeout affects the **entire batch** (not per test)
- ⚠️ Runs slower due to architecture emulation

---

🧠 Still — you now have a secure, isolated benchmarking engine for running untrusted Python code on real input data 🎉
