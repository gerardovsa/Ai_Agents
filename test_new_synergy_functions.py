import sys
sys.path.insert(0, 'tools/implementations')

from synergy import (
    synergy_remove_document,
    synergy_remove_link,
    synergy_remove_tag,
    synergy_delete_milestone,
    synergy_delete_task,
    synergy_delete_subtask,
    synergy_set_milestone_blocker,
    synergy_set_task_blocker
)

print("All 8 new functions imported successfully!")
print("\nNew DELETE/REMOVE operations:")
print("1. synergy_remove_document - Remove document by index")
print("2. synergy_remove_link - Remove link by index")
print("3. synergy_remove_tag - Remove tag by name")
print("4. synergy_delete_milestone - Delete milestone + tasks + subtasks")
print("5. synergy_delete_task - Delete task + subtasks")
print("6. synergy_delete_subtask - Delete subtask")
print("7. synergy_set_milestone_blocker - Block/unblock milestone")
print("8. synergy_set_task_blocker - Block/unblock task")
print("\nImplementation complete!")
