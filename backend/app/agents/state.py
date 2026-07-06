from typing import TypedDict, List, Dict, Any

class OnboardingState(TypedDict):
    job_id: str
    repo_path: str
    architecture_overview: str
    key_modules: List[Dict[str, Any]]
    docs_health: List[Dict[str, Any]]
    getting_started: str
    env_vars: List[str]
    guide_assembled: bool
