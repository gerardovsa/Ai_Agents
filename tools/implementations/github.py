"""
GitHub Tool Implementations
============================

This module provides tool implementations for GitHub repository management.

NOTE: Uses per-user GitHub credentials from database.
Each user connects their own GitHub Personal Access Token via Account Settings.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for credential injection
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from github import Github
from AI_infrastructure.auth.credential_injector import get_github_credentials


def _get_github_client(user_id: int, **kwargs) -> Github:
    """
    Get user-specific GitHub client with their Personal Access Token
    
    Args:
        user_id: User ID for credential lookup
        **kwargs: Additional parameters (for credential injection)
    
    Returns:
        Github: Authenticated GitHub client for this user
    """
    github_creds = get_github_credentials(user_id=user_id, **kwargs)
    return Github(github_creds['access_token'])


def github_create_repo(name: str, description: str = None, private: bool = False, **kwargs):
    """
    Create a new GitHub repository under the authenticated user's account.
    
    Args:
        name: Repository name
        description: Repository description
        private: Make repository private
        **kwargs: Credential injection parameters (_user_id)
    
    Returns:
        Created repository details
    """
    user_id = kwargs.get('_user_id')
    if not user_id:
        raise Exception("User authentication required for GitHub tools. Please log in.")
    
    print(f"🔧 [User {user_id}] Creating GitHub repository: {name}")
    
    try:
        g = _get_github_client(user_id, **kwargs)
        user = g.get_user()
        repo = user.create_repo(
            name=name,
            description=description or "",
            private=private
        )
        
        return {
            'name': repo.name,
            'full_name': repo.full_name,
            'clone_url': repo.clone_url,
            'html_url': repo.html_url,
            'private': repo.private,
            'owner': user.login,
            'created': True
        }
        
    except Exception as e:
        print(f"❌ Failed to create repository: {e}")
        raise


def github_commit_file(repo: str, file_path: str, content: str, message: str, **kwargs):
    """
    Commit a file to a GitHub repository under the authenticated user's account.
    
    Args:
        repo: Repository name (owner/repo)
        file_path: Path within repository
        content: File content
        message: Commit message
        **kwargs: Credential injection parameters (_user_id)
    
    Returns:
        Commit details
    """
    user_id = kwargs.get('_user_id')
    if not user_id:
        raise Exception("User authentication required for GitHub tools. Please log in.")
    
    print(f"🔧 [User {user_id}] Committing file to {repo}: {file_path}")
    
    try:
        g = _get_github_client(user_id, **kwargs)
        repository = g.get_repo(repo)
        
        # Try to get existing file
        try:
            existing_file = repository.get_contents(file_path)
            # Update existing file
            result = repository.update_file(
                file_path,
                message,
                content,
                existing_file.sha
            )
        except:
            # Create new file
            result = repository.create_file(
                file_path,
                message,
                content
            )
        
        return {
            'path': file_path,
            'commit_sha': result['commit'].sha,
            'committed': True
        }
        
    except Exception as e:
        print(f"❌ Failed to commit file: {e}")
        raise


def github_create_pr(repo: str, title: str, head: str, base: str, body: str = None, **kwargs):
    """
    Create a pull request under the authenticated user's account.
    
    Args:
        repo: Repository name (owner/repo)
        title: PR title
        head: Head branch
        base: Base branch
        body: PR description
        **kwargs: Credential injection parameters (_user_id)
    
    Returns:
        Created PR details
    """
    user_id = kwargs.get('_user_id')
    if not user_id:
        raise Exception("User authentication required for GitHub tools. Please log in.")
    
    print(f"🔧 [User {user_id}] Creating pull request in {repo}: {title}")
    
    try:
        g = _get_github_client(user_id, **kwargs)
        repository = g.get_repo(repo)
        pr = repository.create_pull(
            title=title,
            body=body or "",
            head=head,
            base=base
        )
        
        return {
            'number': pr.number,
            'title': pr.title,
            'html_url': pr.html_url,
            'state': pr.state,
            'created': True
        }
        
    except Exception as e:
        print(f"❌ Failed to create PR: {e}")
        raise


def github_get_issues(repo: str, state: str = "open", limit: int = 30, **kwargs):
    """
    List issues from a repository using the authenticated user's access.
    
    Args:
        repo: Repository name (owner/repo)
        state: Issue state ('open', 'closed', 'all')
        limit: Maximum number of issues
        **kwargs: Credential injection parameters (_user_id)
    
    Returns:
        List of issues
    """
    user_id = kwargs.get('_user_id')
    if not user_id:
        raise Exception("User authentication required for GitHub tools. Please log in.")
    
    print(f"🔧 [User {user_id}] Fetching issues from {repo} (state: {state})")
    
    try:
        g = _get_github_client(user_id, **kwargs)
        repository = g.get_repo(repo)
        issues = repository.get_issues(state=state)
        
        issue_list = []
        for i, issue in enumerate(issues):
            if i >= limit:
                break
            
            issue_list.append({
                'number': issue.number,
                'title': issue.title,
                'state': issue.state,
                'html_url': issue.html_url,
                'created_at': str(issue.created_at),
                'updated_at': str(issue.updated_at)
            })
        
        return {
            'issues': issue_list,
            'count': len(issue_list)
        }
        
    except Exception as e:
        print(f"❌ Failed to fetch issues: {e}")
        raise


if __name__ == "__main__":
    print("GitHub tools loaded")
