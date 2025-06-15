# 🐦 X-Autobot

**X-Autobot** is an AI-powered autoposting bot for [X.com (formerly Twitter)](https://x.com) that generates and posts hourly tweets in a specific community using Google's Gemini AI and Selenium.

---

## 🚀 Features

- 🤖 Automatically generates tweets using Gemini (`gemini-2.0-flash`)
- 📌 Posts to a specific X Community
- 🔐 Secure login with cookie/session saving
- 🕒 Posts every hour
- ⚙️ Credentials and config saved locally
- 🖥️ Runs continuously in a background screen session

---

## 🛠 Setup Instructions

### 1. Start a Background Screen (Optional but Recommended)

```bash
screen -S x
```
### 2. Clone the Repository

```bash
git clone https://github.com/krrpatel/X-Autobot.git
```

### 3. Navigate to the Project Directory

```bash
cd X-Autobot
```

### 4. Set Up a Virtual Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 5. Install Required Python Packages

```bash
pip install selenium google-generativeai
```

### 6. Run the Bot

```bash
python3 main.py
```

On the first run:
	•	You’ll be prompted for your X (Twitter) username and password.
	•	These will be saved securely in a local config.json file for future use.
	•	You’ll also need to input a prompt for tweet generation (used hourly).

⸻

🧠 Requirements
	•	Python 3.8+
	•	Google Gemini API Key – already embedded in the script (you may customize it).
	•	Chrome + ChromeDriver installed and accessible.
