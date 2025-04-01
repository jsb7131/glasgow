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
