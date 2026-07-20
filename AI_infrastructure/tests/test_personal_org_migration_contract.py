"""Regression contract for the personal-organisation corrective migration.

Migration 046 targeted ON CONFLICT (name), but organisations.name is not
unique. PostgreSQL therefore rejected every personal-org creation. These tests
keep the helper aligned with the table's real unique key without touching a
database.

Run:
    python AI_infrastructure/tests/test_personal_org_migration_contract.py
"""
import os
import re
import unittest

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
MIGRATION_PATH = os.path.join(
    REPO_ROOT,
    'AI_infrastructure',
    'migrations',
    '054_fix_personal_org_conflict_target_and_backfill.sql',
)
ORGANISATIONS_SCHEMA_PATH = os.path.join(
    REPO_ROOT,
    'AI_infrastructure',
    'migrations',
    'add_organisations_and_org_credentials.sql',
)


def _read(path):
    with open(path, 'r', encoding='utf-8') as file:
        return file.read()


def _section(sql, start_marker, end_marker):
    start = sql.find(start_marker)
    if start == -1:
        return ''
    end = sql.find(end_marker, start + len(start_marker))
    return sql[start:end] if end != -1 else sql[start:]


class TestOrganisationsConflictKey(unittest.TestCase):
    """The helper conflict target must match a real unique constraint."""

    @classmethod
    def setUpClass(cls):
        cls.schema = _read(ORGANISATIONS_SCHEMA_PATH)

    def test_slug_is_unique(self):
        slug_definition = re.search(
            r'^\s*slug\s+[^\n]+$',
            self.schema,
            flags=re.MULTILINE,
        )
        self.assertIsNotNone(slug_definition, 'organisations.slug must be defined')
        self.assertIn('UNIQUE', slug_definition.group(0).upper())

    def test_name_is_not_unique(self):
        name_definition = re.search(
            r'^\s*name\s+[^\n]+$',
            self.schema,
            flags=re.MULTILINE,
        )
        self.assertIsNotNone(name_definition, 'organisations.name must be defined')
        self.assertNotIn('UNIQUE', name_definition.group(0).upper())


class TestPersonalOrgMigrationContract(unittest.TestCase):
    """Migration 054 must be safe, idempotent, and fail loudly."""

    @classmethod
    def setUpClass(cls):
        cls.migration = _read(MIGRATION_PATH)
        cls.helper = _section(
            cls.migration,
            'CREATE OR REPLACE FUNCTION ai_infrastructure.create_personal_org(',
            'COMMENT ON FUNCTION ai_infrastructure.create_personal_org',
        )
        cls.backfill = _section(
            cls.migration,
            '-- 2. Backfill every eligible solo user as one atomic statement',
            '-- 3. Fail-loud verification',
        )

    def test_preserves_public_helper_signature(self):
        signature = re.compile(
            r'CREATE OR REPLACE FUNCTION\s+'
            r'ai_infrastructure\.create_personal_org\s*\(\s*'
            r'p_user_id\s+INT,\s*'
            r'p_username\s+TEXT,\s*'
            r'p_display_name\s+TEXT\s+DEFAULT\s+NULL\s*\)',
            flags=re.IGNORECASE | re.DOTALL,
        )
        self.assertRegex(self.migration, signature)

    def test_uses_unique_slug_conflict_target(self):
        self.assertTrue(self.helper, 'Replacement helper section must exist')
        self.assertIn('ON CONFLICT (slug) DO UPDATE', self.helper)
        self.assertNotIn('ON CONFLICT (name)', self.helper)

    def test_rejects_non_personal_slug_collisions(self):
        self.assertIn('existing_org.name = EXCLUDED.name', self.migration)
        self.assertIn('existing_org.is_personal_org IS TRUE', self.migration)
        self.assertIn('IF v_org_id IS NULL THEN', self.migration)

    def test_preserves_existing_user_assignments(self):
        self.assertIn('FOR UPDATE;', self.migration)
        self.assertIn('IF v_existing_org_id IS NOT NULL THEN', self.migration)
        self.assertIn('AND organisation_id IS NULL', self.migration)

    def test_backfill_does_not_swallow_row_errors(self):
        self.assertTrue(self.backfill, 'Atomic backfill section must exist')
        self.assertNotIn('EXCEPTION WHEN OTHERS', self.backfill)
        self.assertIn('PERFORM ai_infrastructure.create_personal_org', self.backfill)

    def test_backfill_fails_if_users_remain_unassigned(self):
        self.assertIn('IF v_remaining_count > 0 THEN', self.backfill)
        self.assertIn('RAISE EXCEPTION', self.backfill)


if __name__ == '__main__':
    unittest.main()
