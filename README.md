## 🐳 Feature branch: Running the Isolated VM + Docker Code Runner (Colima + Docker-Run)

This feature enables isolated benchmarking by spawning a Docker container, inside a lightweight Linux VM (via Colima), in which to run all test case with untrusted code.

https://github.com/abiosoft/colima

https://github.com/glotcode/docker-run

---

You're now running **isolated and parallelized Python code**...

...**inside a Linux sandbox**...

...**from a FastAPI app on macOS**...

...**via a Docker-run container inside an amd64 VM spun up by Colima on an ARM-based MacBook**. 🤯

---

### ⚙️ Setup Instructions (macOS - ARM)

> 💡 **Important:** Make sure Docker Desktop is fully quit/disabled before starting.

```bash
git clone https://github.com/jsb7131/glasgow.git
git checkout colima/docker-run
cd glasgow

# Install Colima + virtualization backend
brew install colima
brew install qemu

# Start the VM + launch docker-run container inside it
bash colima_runner.sh start

# (Optional) Stop it
bash colima_runner.sh stop

# Then initialize and run your app as usual:
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

- The Docker container benchmarks **all 57 inputs in parallel** via an internal thread pool, inside the VM.
- Although it's possible to escape the Docker and a VM / exploit kernel vulnerabilities, you would ideally run any other system component on a separate machine altogether than the one that is running this VM -> and the attack vector would become enormously convoluted, greatly lowering the risk of an exploit.
- If a submission crashes, runs too long, or errors out, it happens in a single place and could get reported in a monitoring system immediately.
- Note: There is another technology out there called 'gVisor' that could be used in conjunction with this for even more security (https://gvisor.dev)

---

### ⏳ Timeout Considerations

- The default `docker-run` container from the public registry enforces a **30 second max execution time**. So, long-running sort algorithms **will timeout** before they finish. However, replacing `docker-run` with a manual implementation of an ephemeral code-runner Docker would remove this limitation.
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

Want to verify your setup after running bash colima_runner.sh start?

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
- ✅ Uses a Docker container inside a VM to isolate user code
- ✅ Great for production safety + visibility
- ⚠️ Timeout affects the **entire batch** (not per test)
- ⚠️ Runs slower due to architecture emulation
