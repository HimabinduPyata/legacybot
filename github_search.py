import os
from github import Github
from dotenv import load_dotenv

load_dotenv()

def search_github_commits(query):
    """Search GitHub commit history for relevant changes"""
    try:
        print(f"🐙 Searching GitHub for: {query}")
        
        g = Github(os.environ["GITHUB_TOKEN"])
        repo_name = os.environ.get("GITHUB_REPO", "")
        
        if not repo_name:
            return None
            
        repo = g.get_repo(repo_name)
        
        # Get recent commits
        commits = repo.get_commits()
        
        relevant = []
        count = 0
        
        for commit in commits:
            if count >= 50:  # Check last 50 commits
                break
                
            message = commit.commit.message
            author = commit.commit.author.name
            date = commit.commit.author.date.strftime("%Y-%m-%d")
            sha = commit.sha[:7]
            
            # Check if commit is relevant to query
            if any(word.lower() in message.lower() 
                   for word in query.split()
                   if len(word) > 3):  # Skip short words
                relevant.append(
                    f"• [{sha}] {date} by {author}:\n  {message[:200]}"
                )
            
            count += 1
        
        if not relevant:
            return None
            
        return "\n".join(relevant[:5])  # Top 5 relevant commits
        
    except Exception as e:
        print(f"❌ GitHub search error: {e}")
        return None

def summarize_github_results(query, results, openai_client):
    """Use OpenAI to summarize GitHub commit results"""
    if not results:
        return None
        
    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """You are LegacyBot. You are analyzing 
                GitHub commit history to explain WHY code changes 
                were made. Be specific and technical but clear."""
            },
            {
                "role": "user",
                "content": f"""Question: {query}

Relevant commits found:
{results}

Explain what these commits tell us about the question.
Focus on WHY these changes were made."""
            }
        ]
    )
    return response.choices[0].message.content