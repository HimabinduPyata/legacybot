import os
from dotenv import load_dotenv
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from openai import OpenAI
from rag import load_documents, ask_documents
from slack_search import get_channel_history, summarize_slack_results
from github_search import search_github_commits, summarize_github_results

load_dotenv()

app = App(token=os.environ["SLACK_BOT_TOKEN"])
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])

# Load documents when bot starts
print("📚 Loading documents...")
docs_loaded = load_documents()

HELP_MESSAGE = """
👋 *Hi! I'm LegacyBot — your AI assistant for legacy codebases!*

Here's what I can help you with:

🔍 *Knowledge Search*
Ask me anything about the codebase:
`@LegacyBot how does the ATM reconciliation job work?`

📄 *Document Search*
I search company docs and runbooks:
`@LegacyBot what does the onboarding doc say about VPN?`

💬 *Slack History*
I search past team discussions:
`@LegacyBot what did the team discuss about deployments?`

🐙 *GitHub History*
I explain why code changes were made:
`@LegacyBot what changes were made to the payment service?`

🔄 *Reload Documents*
Add new PDFs and reload without restarting:
`@LegacyBot reload docs`

💡 *Tips:*
- Be specific in your questions
- I search ALL sources and combine answers
- The more docs you upload, the smarter I get!

_Built with ❤️ by Himabindu — LegacyBot v1.0_
"""

def ask_openai(question):
    """Fallback to OpenAI general knowledge"""
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": """You are LegacyBot, an AI assistant
                    that helps engineers understand legacy codebases.
                    Be helpful, clear and concise.
                    When you don't know something, say so honestly."""
                },
                {
                    "role": "user",
                    "content": question
                }
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        print(f"❌ OpenAI error: {e}")
        return None

@app.event("app_mention")
def handle_mention(event, say):
    user = event["user"]
    text = event["text"]

    print(f"\n{'='*50}")
    print(f"📩 Message from {user}: {text}")
    print(f"{'='*50}")

    # Clean the message — remove @LegacyBot mention
    clean_text = text.split(">", 1)[-1].strip()

    # Handle help command
    if clean_text.lower() in ["help", "hi", "hello", "hey"]:
        say(HELP_MESSAGE)
        return

    # Handle reload command
    if clean_text.lower() in ["reload", "reload docs"]:
        say("🔄 Reloading documents...")
        from rag import reload_documents
        success = reload_documents()
        if success:
            say("✅ Documents reloaded successfully!")
        else:
            say("❌ No documents found to reload!")
        return

    # Show loading message
    say(
        f"🔍 Searching all knowledge sources for "
        f"*\"{clean_text}\"* <@{user}>...\n"
        f"_This may take a few seconds_"
    )

    answers = []
    sources_searched = []

    # Source 1 — Search documents (RAG)
    try:
        if docs_loaded:
            print("📄 Searching documents...")
            sources_searched.append("📄 Documents")
            doc_answer = ask_documents(clean_text)
            if doc_answer and len(doc_answer) > 20:
                answers.append(
                    f"📄 *From your documents:*\n{doc_answer}"
                )
    except Exception as e:
        print(f"❌ Document search error: {e}")

    # Source 2 — Search Slack history
    try:
        print("💬 Searching Slack history...")
        sources_searched.append("💬 Slack")
        slack_results = get_channel_history(clean_text)
        if slack_results:
            slack_summary = summarize_slack_results(
                clean_text,
                slack_results,
                client
            )
            if slack_summary:
                answers.append(
                    f"💬 *From past Slack discussions:*\n{slack_summary}"
                )
    except Exception as e:
        print(f"❌ Slack search error: {e}")

    # Source 3 — Search GitHub commits
    try:
        print("🐙 Searching GitHub history...")
        sources_searched.append("🐙 GitHub")
        github_results = search_github_commits(clean_text)
        if github_results:
            github_summary = summarize_github_results(
                clean_text,
                github_results,
                client
            )
            if github_summary:
                answers.append(
                    f"🐙 *From GitHub commit history:*\n{github_summary}"
                )
    except Exception as e:
        print(f"❌ GitHub search error: {e}")

    # Source 4 — Fallback to OpenAI
    if not answers:
        try:
            print("🧠 Using OpenAI general knowledge...")
            general = ask_openai(clean_text)
            if general:
                answers.append(
                    f"🧠 *From general knowledge:*\n{general}"
                )
        except Exception as e:
            print(f"❌ OpenAI fallback error: {e}")

    # Build final response
    if answers:
        sources_line = " | ".join(sources_searched)
        final = "\n\n---\n\n".join(answers)
        say(
            f"💡 *Here's what I found for <@{user}>:*\n"
            f"_Searched: {sources_line}_\n\n"
            f"{final}\n\n"
            f"_Type `@LegacyBot help` to see all commands_"
        )
    else:
        say(
            f"😕 Sorry <@{user}>, I couldn't find anything about "
            f"*\"{clean_text}\"*.\n\n"
            f"Try rephrasing your question or upload more docs!\n"
            f"_Type `@LegacyBot help` to see what I can do_"
        )

    print("✅ Reply sent!\n")

if __name__ == "__main__":
    print("⚡️ LegacyBot is starting...")
    print("📚 Loaded docs:", "✅ Yes" if docs_loaded else "❌ No docs found")
    print("🤖 OpenAI: ✅ Connected")
    print("="*50)
    handler = SocketModeHandler(
        app,
        os.environ["SLACK_APP_TOKEN"]
    )
    handler.start()