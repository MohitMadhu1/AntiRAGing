import os
import shutil
import git
from tempfile import mkdtemp
from urllib.parse import urlparse

class GitHubService:
    @staticmethod
    def clone_repo(repo_url: str, token: str | None = None) -> str:
        """
        Clones a repository to a temporary directory and returns the path.
        If a token is provided, uses it for authentication (private repos).
        """
        temp_dir = mkdtemp(prefix="antiraging_")
        
        parsed_url = urlparse(repo_url)
        if token:
            # Inject token into URL for authenticated clone
            auth_url = f"{parsed_url.scheme}://oauth2:{token}@{parsed_url.netloc}{parsed_url.path}"
        else:
            auth_url = repo_url
            
        try:
            repo = git.Repo.clone_from(auth_url, temp_dir, depth=1)
            return temp_dir
        except git.GitCommandError as e:
            # Clean up on failure
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
            raise RuntimeError(f"Failed to clone repo: {e}")

    @staticmethod
    def get_latest_commit_sha(repo_path: str) -> str:
        """Returns the latest commit SHA of the cloned repo."""
        repo = git.Repo(repo_path)
        return repo.head.commit.hexsha

    @staticmethod
    def cleanup_repo(repo_path: str):
        """Removes the temporary cloned repository."""
        if os.path.exists(repo_path):
            # Windows sometimes locks files, so ignore_errors is useful here
            shutil.rmtree(repo_path, ignore_errors=True)

    @staticmethod
    def get_remote_commit_sha(repo_url: str, token: str | None = None) -> str | None:
        """Uses git ls-remote to fetch the latest commit SHA without cloning."""
        parsed_url = urlparse(repo_url)
        if token:
            auth_url = f"{parsed_url.scheme}://oauth2:{token}@{parsed_url.netloc}{parsed_url.path}"
        else:
            auth_url = repo_url
            
        try:
            # git ls-remote https://... HEAD
            env = os.environ.copy()
            env["GIT_TERMINAL_PROMPT"] = "0"
            output = git.cmd.Git().ls_remote(auth_url, "HEAD", env=env)
            if output:
                # Output looks like: `commit_sha\tHEAD`
                return output.split()[0]
            return None
        except git.GitCommandError:
            return None
