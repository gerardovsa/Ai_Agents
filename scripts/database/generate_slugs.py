"""
Generate Slugs Script - Populate slug columns for existing data

Generates unique slugs for workspaces and threads that don't have them yet.

Usage:
    python scripts/database/generate_slugs.py
    python scripts/database/generate_slugs.py --dry-run
"""

import sqlite3
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from AI_infrastructure.workspace.slug_generator import SlugGenerator


class SlugGenerationScript:
    """
    Slug Generation Script
    
    Generates slugs for existing workspaces and threads.
    """
    
    def __init__(self, dry_run: bool = False):
        """
        Initialize slug generation
        
        Args:
            dry_run: If True, show what would be done without making changes
        """
        root_dir = Path(__file__).parent.parent.parent
        self.db_path = root_dir / 'data' / 'ai_infrastructure.db'
        self.dry_run = dry_run
        self.slug_gen = SlugGenerator(str(self.db_path))
        
        print(f"Database: {self.db_path}")
        print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (will make changes)'}")
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn
    
    def generate_workspace_slugs(self) -> int:
        """
        Generate slugs for workspaces missing them
        
        Returns:
            int: Number of slugs generated
        """
        print("\n[1/2] Generating workspace slugs...")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get workspaces without slugs
        cursor.execute("""
            SELECT id, name FROM workspaces 
            WHERE slug IS NULL OR slug = ''
        """)
        
        workspaces = cursor.fetchall()
        count = len(workspaces)
        
        if count == 0:
            print("  - All workspaces already have slugs")
            conn.close()
            return 0
        
        print(f"  - Found {count} workspace(s) without slugs")
        
        generated = 0
        for workspace in workspaces:
            workspace_id = workspace['id']
            name = workspace['name']
            
            try:
                # Generate slug
                slug = self.slug_gen.generate_workspace_slug(name)
                
                if self.dry_run:
                    print(f"    [DRY RUN] Workspace {workspace_id}: '{name}' -> '{slug}'")
                else:
                    # Update workspace
                    cursor.execute("""
                        UPDATE workspaces SET slug = ? WHERE id = ?
                    """, (slug, workspace_id))
                    print(f"    Generated: Workspace {workspace_id}: '{name}' -> '{slug}'")
                
                generated += 1
            
            except Exception as e:
                print(f"    ERROR: Workspace {workspace_id} ({name}): {e}")
        
        if not self.dry_run:
            conn.commit()
        
        conn.close()
        
        print(f"  - Generated {generated} slug(s)")
        return generated
    
    def generate_thread_slugs(self) -> int:
        """
        Generate slugs for threads missing them
        
        Returns:
            int: Number of slugs generated
        """
        print("\n[2/2] Generating thread slugs...")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get threads without slugs
        cursor.execute("""
            SELECT id, workspace_id, title FROM threads 
            WHERE slug IS NULL OR slug = ''
        """)
        
        threads = cursor.fetchall()
        count = len(threads)
        
        if count == 0:
            print("  - All threads already have slugs")
            conn.close()
            return 0
        
        print(f"  - Found {count} thread(s) without slugs")
        
        generated = 0
        for thread in threads:
            thread_id = thread['id']
            workspace_id = thread['workspace_id']
            title = thread['title']
            
            try:
                # Generate slug
                slug = self.slug_gen.generate_thread_slug(title, workspace_id)
                
                if self.dry_run:
                    print(f"    [DRY RUN] Thread {thread_id}: '{title}' -> '{slug}'")
                else:
                    # Update thread
                    cursor.execute("""
                        UPDATE threads SET slug = ? WHERE id = ?
                    """, (slug, thread_id))
                    print(f"    Generated: Thread {thread_id}: '{title}' -> '{slug}'")
                
                generated += 1
            
            except Exception as e:
                print(f"    ERROR: Thread {thread_id} ({title}): {e}")
        
        if not self.dry_run:
            conn.commit()
        
        conn.close()
        
        print(f"  - Generated {generated} slug(s)")
        return generated
    
    def verify_slugs(self):
        """Verify all slugs are generated"""
        print("\n[3/3] Verifying slugs...")
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Check workspaces
        cursor.execute("""
            SELECT COUNT(*) as count FROM workspaces 
            WHERE slug IS NULL OR slug = ''
        """)
        workspace_missing = cursor.fetchone()['count']
        
        # Check threads
        cursor.execute("""
            SELECT COUNT(*) as count FROM threads 
            WHERE slug IS NULL OR slug = ''
        """)
        thread_missing = cursor.fetchone()['count']
        
        conn.close()
        
        print(f"  - Workspaces without slugs: {workspace_missing}")
        print(f"  - Threads without slugs: {thread_missing}")
        
        return workspace_missing == 0 and thread_missing == 0
    
    def run(self):
        """Run complete slug generation"""
        print("\n" + "="*60)
        print("SLUG GENERATION SCRIPT")
        print("="*60)
        
        try:
            # Generate slugs
            workspace_count = self.generate_workspace_slugs()
            thread_count = self.generate_thread_slugs()
            
            total = workspace_count + thread_count
            
            # Verify
            if not self.dry_run:
                all_good = self.verify_slugs()
            else:
                all_good = True
            
            print("\n" + "="*60)
            if all_good:
                if self.dry_run:
                    print(f" DRY RUN - Would generate {total} slug(s)")
                    print("="*60)
                    print("  Run without --dry-run to apply changes")
                else:
                    print(f" SUCCESS - Generated {total} slug(s)")
                    print("="*60)
            else:
                print(" WARNING - Some slugs may be missing")
                print("="*60)
            
            return True
        
        except Exception as e:
            print(f"\n ERROR: Slug generation failed: {e}")
            return False


def main():
    """Main entry point"""
    # Check for dry-run flag
    dry_run = len(sys.argv) > 1 and sys.argv[1] == '--dry-run'
    
    script = SlugGenerationScript(dry_run=dry_run)
    script.run()


if __name__ == '__main__':
    main()
