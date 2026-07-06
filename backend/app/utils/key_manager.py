import time
from google import genai
from app.config import settings

class GeminiKeyManager:
    def __init__(self):
        self.keys = settings.gemini_keys
        if not self.keys:
            raise ValueError("No GEMINI_API_KEY provided in environment.")
            
        self.clients = [{"key": k, "client": genai.Client(api_key=k), "cooldown_until": 0} for k in self.keys]
        self.current_index = 0

    def get_client(self):
        """Returns a non-exhausted client, or if all are exhausted, returns the one that cools down soonest."""
        now = time.time()
        
        # Try to find a ready client starting from current index
        for i in range(len(self.clients)):
            idx = (self.current_index + i) % len(self.clients)
            if self.clients[idx]["cooldown_until"] <= now:
                self.current_index = idx
                return self.clients[idx]["client"]
                
        # If we reach here, all clients are on cooldown. Return the one that cools down soonest.
        # It's up to the caller's retry logic to sleep if it hits a 429 again.
        best_idx = min(range(len(self.clients)), key=lambda i: self.clients[i]["cooldown_until"])
        self.current_index = best_idx
        return self.clients[best_idx]["client"]

    def get_wait_time(self, client) -> float:
        """Returns how many seconds until this client is off cooldown (0 if ready)."""
        now = time.time()
        for c in self.clients:
            if c["client"] == client:
                wait = c["cooldown_until"] - now
                return max(0.0, wait)
        return 0.0

    def mark_exhausted(self, client):
        """Marks a client as exhausted and puts it on a 60-second cooldown."""
        for c in self.clients:
            if c["client"] == client:
                c["cooldown_until"] = time.time() + 60
                print(f"Key {c['key'][:8]}... marked as exhausted. Cooldown for 60s.")
                break
                
        # Advance to next key immediately
        self.current_index = (self.current_index + 1) % len(self.clients)

# Singleton instance
gemini_key_manager = GeminiKeyManager()
