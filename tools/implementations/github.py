"""
GitHub Tool Implementations
============================

This module provides tool implementations for GitHub repository management.
"""

import os
from github import Github

try:
    from config import get_api_key_enhanced
    github_token = get_api_key_enhanced('GITHUB_TOKEN') or get_api_key_enhanced('GITHUB_PASSWORD')
except ImportError:
    github_token = os.getenv('GITHUB_TOKEN') or os.getenv('GITHUB_PASSWORD')

# Initialize GitHub client
g = Github(github_token)


def github_create_repo(name: str, description: str = None, private: bool = False):
    """
    Create a new GitHub repository.
    
    Args:
        name: Repository name
        description: Repository description
        private: Make repository private
    
    Returns:
        Created repository details
    """
    print(f"🔧 Creating GitHub repository: {name}")
    
    try:
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
            'created': True
        }
        
    except Exception as e:
        print(f"❌ Failed to create repository: {e}")
        raise


def github_commit_file(repo: str, file_path: str, content: str, message: str):
    """
    Commit a file to a GitHub repository.
    
    Args:
        repo: Repository name (owner/repo)
        file_path: Path within repository
        content: File content
        message: Commit message
    
    Returns:
        Commit details
    """
    print(f"🔧 Committing file to {repo}: {file_path}")
    
    try:
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


def github_create_pr(repo: str, title: str, head: str, base: str, body: str = None):
    """
    Create a pull request.
    
    Args:
        repo: Repository name (owner/repo)
        title: PR title
        head: Head branch
        base: Base branch
        body: PR description
    
    Returns:
        Created PR details
    """
    print(f"🔧 Creating pull request in {repo}: {title}")
    
    try:
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


def github_get_issues(repo: str, state: str = "open", limit: int = 30):
    """
    List issues from a repository.
    
    Args:
        repo: Repository name (owner/repo)
        state: Issue state ('open', 'closed', 'all')
        limit: Maximum number of issues
    
    Returns:
        List of issues
    """
    print(f"🔧 Fetching issues from {repo} (state: {state})")
    
    try:
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
