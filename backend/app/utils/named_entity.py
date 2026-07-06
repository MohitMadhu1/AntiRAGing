import re

def extract_named_entity(question: str) -> str | None:
    """
    Attempts to extract a specific function, class, or module name from a question.
    E.g. "How does login_user work?" -> "login_user"
    E.g. "Where is the User model defined?" -> "User"
    """
    # Simple regex to look for camelCase, PascalCase, or snake_case words
    # that might represent symbols. 
    # In a full app, this could use an NLP model or LLM.
    
    # Matches words with underscores or camel/pascal casing (min length 3 to avoid noise)
    matches = re.findall(r'\b([a-zA-Z_][a-zA-Z0-9_]*_[a-zA-Z0-9_]+|[A-Z][a-z0-9]+[A-Z][a-z0-9]+[a-zA-Z0-9]*)\b', question)
    
    if matches:
        return matches[0] # Return the first strong match
        
    # Check for backticks (e.g. `login_user`)
    backticks = re.findall(r'`([^`]+)`', question)
    if backticks:
        return backticks[0]
        
    return None
