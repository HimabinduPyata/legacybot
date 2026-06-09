# LegacyBot — AI Copilot for Legacy Codebases

> *"I joined NCR and inherited 16 years of undocumented legacy code. Every question I couldn't find in the docs meant waiting hours for a teammate. I built LegacyBot so no new engineer ever has to feel that way again."*
> — Himabindu Pyata, Builder

---

## What is LegacyBot?

LegacyBot is a **Slack AI assistant** that helps new engineers on legacy codebases get unblocked instantly — without waiting for a senior teammate.

Instead of:
```
 "I don't understand this code, let me wait for someone to be free..."
```

Engineers do:
```
 @LegacyBot why does the ATM reconciliation job run at 2am?
```

And get an instant answer from **3 sources simultaneously:**
- Company documents & runbooks (RAG pipeline)
- Past Slack discussions
- GitHub commit history — explains WHY code was written

---

## Built for Slack Agent Builder Challenge 2026

This project was built for the **Slack Agent Builder Challenge** hackathon.

- **Track:** New Slack Agent + Slack Agent for Good
- **Technologies used:** Slack Bolt SDK + MCP + Real-Time Search API
- **Problem solved:** New engineer onboarding on legacy codebases

---

## Features

| Feature | Description |
|---------|-------------|
| **Document Q&A** | Upload PDFs — LegacyBot answers from real company docs using RAG + FAISS |
| **Slack History Search** | Searches past channel discussions for relevant answers |
| **GitHub Commit Search** | Explains WHY code changes were made from git history |
| **AI Fallback** | Falls back to GPT-4o-mini general knowledge when no docs match |
| **Fast Startup** | FAISS index saved to disk — instant loading on restart |
| **Live Reload** | Add new docs without restarting: `@LegacyBot reload docs` |
| **Help Command** | `@LegacyBot help` shows all commands |

---

## Real World Example

```
New engineer: @LegacyBot what changes were made to the payment service?

LegacyBot: Here's what I found:
Searched: Documents | Slack | GitHub

From your documents:
The payment service was refactored in Q3 2022 to support
multi-currency transactions per compliance requirement...

From past Slack discussions:
Team discussed switching from synchronous to async
processing to handle peak load during holidays...

From GitHub commit history:
[abc1234] 2022-09-14 by John Smith:
"Migrated payment service to async — reduced timeout
errors by 40% during Black Friday load testing"
```

---

## Architecture

<img width="1164" height="1062" alt="image" src="https://github.com/user-attachments/assets/a498500b-e633-4a7a-81b3-3c4150cd069a" />

---

## Tech Stack

| Technology | Purpose |
|------------|---------|
| Python | Core language |
| Slack Bolt SDK | Slack app framework |
| OpenAI GPT-4o-mini | Answer generation |
| LangChain | RAG pipeline orchestration |
| FAISS | Vector similarity search |
| OpenAI Embeddings | Document vectorization |
| PyGithub | GitHub commit search |
| Slack SDK | Channel history search |
| python-dotenv | Environment management |

---

## Setup Instructions

### 1. Clone the repository
```bash
git clone https://github.com/HimabinduPyata/legacybot.git
cd legacybot
```

### 2. Create virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install slack-bolt openai faiss-cpu python-dotenv \
            pypdf langchain langchain-openai \
            langchain-community PyGithub
```

### 4. Set up environment variables
```bash
touch .env
```

Add to `.env`:
```
SLACK_BOT_TOKEN=xoxb-your-token
SLACK_SIGNING_SECRET=your-signing-secret
SLACK_APP_TOKEN=xapp-your-app-token
OPENAI_API_KEY=sk-your-openai-key
GITHUB_TOKEN=ghp-your-github-token
GITHUB_REPO=your-username/your-repo
```

### 5. Add your documents
```bash
mkdir documents
cp your-company-docs.pdf documents/
```

### 6. Run LegacyBot
```bash
python3 app.py
```

---

## Commands

| Command | Description |
|---------|-------------|
| `@LegacyBot <any question>` | Search all sources and answer |
| `@LegacyBot help` | Show all commands |
| `@LegacyBot reload docs` | Reload documents without restart |

---

## Project Structure

```
legacybot/
├── app.py              # Main Slack bot + event handler
├── rag.py              # RAG pipeline (FAISS + LangChain)
├── slack_search.py     # Slack channel history search
├── github_search.py    # GitHub commit history search
├── documents/          # Upload your PDFs here
├── .env                # Secret keys (never commit!)
├── .gitignore
└── README.md
```

---

## Slack Permissions Required

```
app_mentions:read
chat:write
channels:history
channels:read
files:read
groups:read
im:read
mpim:read
```

---

## Built By

**Himabindu Pyata** — Software Engineer with 5 years experience in Java, Python, and cloud systems.

- [LinkedIn](https://www.linkedin.com/in/himabindu-pyata-7b8a78bb/)
- [GitHub](https://github.com/HimabinduPyata)
- bindu.pyata@gmail.com

---

*Built with ❤️ for the Slack Agent Builder Challenge 2026*
