import time
import functools

from app.utils.key_manager import gemini_key_manager

def retry_llm_call(max_retries=5, initial_delay=2, backoff_factor=2):
    """
    Decorator to retry a function (like an LLM API call) upon failure.
    Uses KeyManager to swap keys on Rate Limits.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries):
                client = gemini_key_manager.get_client()
                wait_time = gemini_key_manager.get_wait_time(client)
                if wait_time > 0:
                    print(f"All keys exhausted. Sleeping for {wait_time:.1f}s...")
                    time.sleep(wait_time + 1) # wait until cooldown is fully over + 1s buffer
                
                try:
                    return func(client, *args, **kwargs)
                except Exception as e:
                    last_exception = e
                    err_str = str(e)
                    print(f"LLM call failed (attempt {attempt + 1}/{max_retries}): {e}")
                    
                    if attempt < max_retries - 1:
                        if "429" in err_str or "RESOURCE_EXHAUSTED" in err_str:
                            print("Rate limit hit. Swapping API key...")
                            gemini_key_manager.mark_exhausted(client)
                            time.sleep(1) # tiny sleep before hitting new key
                        else:
                            print(f"Retrying in {delay} seconds...")
                            time.sleep(delay)
                            delay *= backoff_factor
                        
            # Exhausted all retries, raise the last exception
            print("Exhausted all retries. Raising exception.")
            raise RuntimeError(f"AI Generation failed after {max_retries} attempts: {str(last_exception)}")
        return wrapper
    return decorator
