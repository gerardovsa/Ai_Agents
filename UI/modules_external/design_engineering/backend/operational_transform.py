"""
CAD Collaboration - Operational Transformation Engine
Handles concurrent edits from multiple agents (human + AI)
"""

import json
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum


class PatchOperation(Enum):
    """JSON Patch operation types (RFC 6902)"""
    ADD = "add"
    REMOVE = "remove"
    REPLACE = "replace"
    MOVE = "move"
    COPY = "copy"
    TEST = "test"


class PatchActor(Enum):
    """Who made the change"""
    HUMAN = "human"
    AI = "ai"
    SYSTEM = "system"


@dataclass
class Patch:
    """
    JSON Patch structure
    See: https://tools.ietf.org/html/rfc6902
    """
    op: PatchOperation
    path: str
    value: Any = None
    from_path: str = None  # For move/copy operations
    actor: PatchActor = PatchActor.HUMAN
    timestamp: datetime = None
    reason: str = None  # AI explains why it made this change
    patch_id: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.patch_id is None:
            import uuid
            self.patch_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict:
        """Convert to JSON-serializable dict"""
        return {
            "op": self.op.value,
            "path": self.path,
            "value": self.value,
            "from": self.from_path,
            "actor": self.actor.value,
            "timestamp": self.timestamp.isoformat(),
            "reason": self.reason,
            "patch_id": self.patch_id
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Patch':
        """Parse from JSON"""
        return cls(
            op=PatchOperation(data["op"]),
            path=data["path"],
            value=data.get("value"),
            from_path=data.get("from"),
            actor=PatchActor(data.get("actor", "human")),
            timestamp=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            reason=data.get("reason"),
            patch_id=data.get("patch_id")
        )


class OperationalTransform:
    """
    Operational Transformation for concurrent edits
    Resolves conflicts when human and AI edit simultaneously
    """
    
    @staticmethod
    def paths_conflict(path1: str, path2: str) -> bool:
        """Check if two paths conflict"""
        # Same path = conflict
        if path1 == path2:
            return True
        
        # Parent-child relationship = conflict
        if path1.startswith(path2 + "/") or path2.startswith(path1 + "/"):
            return True
        
        return False
    
    @staticmethod
    def transform(patch_a: Patch, patch_b: Patch) -> Optional[Patch]:
        """
        Transform patch_b to account for patch_a having been applied first
        
        Returns:
            Transformed patch_b, or None if patch should be discarded
        """
        
        # No conflict - both can be applied as-is
        if not OperationalTransform.paths_conflict(patch_a.path, patch_b.path):
            return patch_b
        
        # CONFLICT RESOLUTION STRATEGIES
        
        # Strategy 1: Human always wins on direct conflicts
        if patch_a.actor == PatchActor.HUMAN and patch_b.actor == PatchActor.AI:
            if patch_a.path == patch_b.path:
                print(f"[OT] Discarding AI patch due to human override: {patch_b.path}")
                return None
        
        # Strategy 2: Both replace same value
        if (patch_a.op == PatchOperation.REPLACE and 
            patch_b.op == PatchOperation.REPLACE and
            patch_a.path == patch_b.path):
            
            # Human takes priority
            if patch_a.actor == PatchActor.HUMAN:
                return None
            
            # If both AI or both human, later timestamp wins
            if patch_a.timestamp > patch_b.timestamp:
                return None
        
        # Strategy 3: Add to array - adjust indices
        if patch_a.op == PatchOperation.ADD and patch_b.op == PatchOperation.ADD:
            # Both adding to same array
            parts_a = patch_a.path.split('/')
            parts_b = patch_b.path.split('/')
            
            if len(parts_a) == len(parts_b) and parts_a[:-1] == parts_b[:-1]:
                # Same array, different indices
                try:
                    idx_a = int(parts_a[-1])
                    idx_b = int(parts_b[-1])
                    
                    # If patch_a inserted before patch_b's position, increment patch_b index
                    if idx_a <= idx_b:
                        parts_b[-1] = str(idx_b + 1)
                        patch_b.path = '/'.join(parts_b)
                        return patch_b
                except ValueError:
                    pass
        
        # Strategy 4: Remove vs Replace on same path
        if patch_a.op == PatchOperation.REMOVE and patch_b.op == PatchOperation.REPLACE:
            if patch_a.path == patch_b.path:
                # Object was removed, can't replace it
                print(f"[OT] Cannot replace removed object: {patch_b.path}")
                return None
        
        # Strategy 5: Move operation adjustments
        if patch_a.op == PatchOperation.MOVE:
            # If patch_b targets the old location, update to new location
            if patch_b.path == patch_a.path:
                patch_b.path = patch_a.value  # New location
                return patch_b
        
        # Default: Keep patch_b as-is
        return patch_b
    
    @staticmethod
    def transform_series(base_patch: Patch, concurrent_patches: List[Patch]) -> List[Patch]:
        """
        Transform a series of concurrent patches against a base patch
        
        Args:
            base_patch: Patch that was applied first
            concurrent_patches: Patches that need to be transformed
        
        Returns:
            List of transformed patches (some may be None/discarded)
        """
        transformed = []
        
        for patch in concurrent_patches:
            transformed_patch = OperationalTransform.transform(base_patch, patch)
            if transformed_patch:
                transformed.append(transformed_patch)
        
        return transformed


class SceneGraphManager:
    """
    Manages the canonical scene graph state
    Applies patches with validation and conflict resolution
    """
    
    def __init__(self, initial_state: Dict = None):
        self.state = initial_state or self._create_empty_scene()
        self.version = 0
        self.history: List[Patch] = []
        self.pending_patches: Dict[str, List[Patch]] = {}
    
    def _create_empty_scene(self) -> Dict:
        """Create empty scene graph"""
        return {
            "metadata": {
                "version": 0,
                "created_at": datetime.now().isoformat(),
                "dimensions_unit": "mm"
            },
            "objects": {},
            "groups": {},
            "constraints": {},
            "camera": {
                "position": {"x": 1000, "y": 1000, "z": 1000},
                "target": {"x": 0, "y": 0, "z": 0},
                "fov": 45
            },
            "selections": {
                "human": [],
                "ai": []
            }
        }
    
    def get_state(self) -> Dict:
        """Get current scene state"""
        return json.loads(json.dumps(self.state))  # Deep copy
    
    def get_value_at_path(self, path: str) -> Any:
        """Get value at JSON path"""
        parts = path.strip('/').split('/')
        current = self.state
        
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list):
                current = current[int(part)]
            else:
                return None
        
        return current
    
    def set_value_at_path(self, path: str, value: Any):
        """Set value at JSON path"""
        parts = path.strip('/').split('/')
        current = self.state
        
        # Navigate to parent
        for part in parts[:-1]:
            if isinstance(current, dict):
                if part not in current:
                    current[part] = {}
                current = current[part]
            elif isinstance(current, list):
                current = current[int(part)]
        
        # Set final value
        final_key = parts[-1]
        if isinstance(current, dict):
            current[final_key] = value
        elif isinstance(current, list):
            current[int(final_key)] = value
    
    def delete_at_path(self, path: str):
        """Delete value at JSON path"""
        parts = path.strip('/').split('/')
        current = self.state
        
        # Navigate to parent
        for part in parts[:-1]:
            if isinstance(current, dict):
                current = current[part]
            elif isinstance(current, list):
                current = current[int(part)]
        
        # Delete final key
        final_key = parts[-1]
        if isinstance(current, dict):
            del current[final_key]
        elif isinstance(current, list):
            del current[int(final_key)]
    
    def validate_patch(self, patch: Patch) -> Tuple[bool, str]:
        """
        Validate patch before applying
        
        Returns:
            (is_valid, error_message)
        """
        
        # Check path exists for replace/remove
        if patch.op in [PatchOperation.REPLACE, PatchOperation.REMOVE]:
            value = self.get_value_at_path(patch.path)
            if value is None:
                return False, f"Path does not exist: {patch.path}"
        
        # Check parent exists for add
        if patch.op == PatchOperation.ADD:
            parts = patch.path.strip('/').split('/')
            parent_path = '/'.join(parts[:-1])
            if parent_path:
                parent = self.get_value_at_path(parent_path)
                if parent is None:
                    return False, f"Parent path does not exist: {parent_path}"
        
        # Validate value types for specific paths
        if patch.path.startswith('/objects/'):
            if patch.op == PatchOperation.ADD and patch.value:
                if not isinstance(patch.value, dict):
                    return False, "Object value must be a dictionary"
                if 'type' not in patch.value:
                    return False, "Object must have a 'type' field"
        
        return True, ""
    
    def apply_patch(self, patch: Patch) -> Tuple[bool, str]:
        """
        Apply patch to scene graph
        
        Returns:
            (success, error_message)
        """
        
        # Validate first
        is_valid, error = self.validate_patch(patch)
        if not is_valid:
            return False, error
        
        try:
            if patch.op == PatchOperation.ADD:
                self.set_value_at_path(patch.path, patch.value)
            
            elif patch.op == PatchOperation.REPLACE:
                self.set_value_at_path(patch.path, patch.value)
            
            elif patch.op == PatchOperation.REMOVE:
                self.delete_at_path(patch.path)
            
            elif patch.op == PatchOperation.MOVE:
                value = self.get_value_at_path(patch.path)
                self.delete_at_path(patch.path)
                self.set_value_at_path(patch.value, value)
            
            elif patch.op == PatchOperation.COPY:
                value = self.get_value_at_path(patch.from_path)
                self.set_value_at_path(patch.path, value)
            
            # Update version and history
            self.version += 1
            self.state['metadata']['version'] = self.version
            self.history.append(patch)
            
            return True, ""
        
        except Exception as e:
            return False, f"Error applying patch: {str(e)}"
    
    def apply_patches_with_ot(self, patches: List[Patch]) -> List[Tuple[Patch, bool, str]]:
        """
        Apply multiple patches with operational transformation
        
        Returns:
            List of (patch, success, error_message)
        """
        results = []
        
        for i, patch in enumerate(patches):
            # Transform against all previously applied patches in this batch
            transformed_patch = patch
            for prev_patch in patches[:i]:
                transformed_patch = OperationalTransform.transform(prev_patch, transformed_patch)
                if transformed_patch is None:
                    results.append((patch, False, "Discarded due to conflict"))
                    break
            
            if transformed_patch:
                success, error = self.apply_patch(transformed_patch)
                results.append((patch, success, error))
        
        return results
    
    def undo_last_patch(self) -> bool:
        """Undo the last applied patch"""
        if not self.history:
            return False
        
        last_patch = self.history.pop()
        
        # Create inverse patch
        if last_patch.op == PatchOperation.ADD:
            inverse = Patch(
                op=PatchOperation.REMOVE,
                path=last_patch.path,
                actor=PatchActor.SYSTEM
            )
        elif last_patch.op == PatchOperation.REMOVE:
            inverse = Patch(
                op=PatchOperation.ADD,
                path=last_patch.path,
                value=last_patch.value,
                actor=PatchActor.SYSTEM
            )
        elif last_patch.op == PatchOperation.REPLACE:
            # Need to get previous value from history
            # For now, just mark as system operation
            return False
        
        success, _ = self.apply_patch(inverse)
        return success
    
    def get_diff(self, from_version: int, to_version: int = None) -> List[Patch]:
        """Get patches between two versions"""
        if to_version is None:
            to_version = self.version
        
        return [p for p in self.history if from_version < self.history.index(p) <= to_version]


# Example usage
if __name__ == "__main__":
    # Create scene manager
    scene = SceneGraphManager()
    
    # User adds a beam
    user_patch = Patch(
        op=PatchOperation.ADD,
        path="/objects/beam_001",
        value={
            "type": "t-slot-beam",
            "profile": "40x40_standard",
            "position": {"x": 0, "y": 0, "z": 0},
            "length": 1800
        },
        actor=PatchActor.HUMAN,
        reason="User created main bed frame beam"
    )
    
    success, error = scene.apply_patch(user_patch)
    print(f"Applied user patch: {success}")
    
    # AI suggests upgrading profile (same beam)
    ai_patch = Patch(
        op=PatchOperation.REPLACE,
        path="/objects/beam_001/profile",
        value="60x60_heavy",
        actor=PatchActor.AI,
        reason="Beam deflection exceeds L/240 limit"
    )
    
    success, error = scene.apply_patch(ai_patch)
    print(f"Applied AI patch: {success}")
    
    # Simulate conflict: User and AI edit simultaneously
    user_patch2 = Patch(
        op=PatchOperation.REPLACE,
        path="/objects/beam_001/length",
        value=2000,
        actor=PatchActor.HUMAN,
        timestamp=datetime.now()
    )
    
    ai_patch2 = Patch(
        op=PatchOperation.REPLACE,
        path="/objects/beam_001/length",
        value=1900,
        actor=PatchActor.AI,
        timestamp=datetime.now(),
        reason="Optimized length for minimal material waste"
    )
    
    # Apply with OT
    results = scene.apply_patches_with_ot([user_patch2, ai_patch2])
    for patch, success, error in results:
        print(f"Patch by {patch.actor.value}: {success} - {error if error else 'OK'}")
    
    # Check final state
    print("\nFinal beam state:")
    print(json.dumps(scene.state['objects']['beam_001'], indent=2))
    
    print(f"\nTotal version: {scene.version}")
    print(f"History length: {len(scene.history)}")
