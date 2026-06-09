import os
from slack_sdk import WebClient
from dotenv import load_dotenv

load_dotenv()

slack_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])

def get_channel_history(query, limit=20):
    """Search recent messages from all channels"""
    try:
        print("💬 Getting channel history...")
        
        # Get list of all channels
        channels_result = slack_client.conversations_list(
            types="public_channel",
            limit=10
        )
        
        channels = channels_result["channels"]
        all_messages = []
        
        # Search each channel's history
        for channel in channels:
            try:
                history = slack_client.conversations_history(
                    channel=channel["id"],
                    limit=limit
                )
                
                for msg in history["messages"]:
                    text = msg.get("text", "")
                    # Only include messages relevant to query
                    if any(word.lower() in text.lower() 
                           for word in query.split()):
                        all_messages.append(
                            f"• [#{channel['name']}]: {text[:200]}"
                        )
                        
            except Exception:
                continue
        
        if not all_messages:
            return None
            
        return "\n".join(all_messages[:10])
        
    except Exception as e:
        print(f"❌ Channel history error: {e}")
        return None

def summarize_slack_results(query, results, openai_client):
    """Use OpenAI to summarize Slack results"""
    if not results:
        return None
        
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """You are LegacyBot. Summarize these 
                Slack conversation results clearly and concisely.
                Focus on the most relevant information."""
            },
            {
                "role": "user",
                "content": f"""Question: {query}
                
Slack conversations found:
{results}

Summarize the key points relevant to the question."""
            }
        ]
    )
    return response.choices[0].message.content