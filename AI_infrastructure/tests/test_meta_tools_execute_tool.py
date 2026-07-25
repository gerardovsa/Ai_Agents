"""Regression tests for ``tools.implementations.meta_tools.execute_tool``.

Background
----------
The MCP server that exposes ``execute_tool`` to AI clients generates its
JSON schema from the Python function signature. When the original
signature was::

    def execute_tool(tool_name: str = None, **tool_params) -> Dict[str, Any]:

``**tool_params`` is *invisible* to the generated schema, so any keyword
argument the AI passed at the top level was silently dropped by MCP
validation before reaching the function body. Only the values auto-injected
by the MCP auth layer (``_user_id`` and ``_injected_credentials``) survived
— and even those were added *after* the schema check, not because the
schema accepted them.

Concrete reproduction::

    execute_tool(tool_name="gmail_get_message", message_id="19f993e672f4c126")
        -> TypeError: gmail_get_message() missing 1 required positional
                       argument: 'message_id'

The fix exposes ``parameters`` as a typed ``Optional[Dict]`` parameter so
the MCP-generated schema contains it as a JSON object property. AI clients
now pass tool arguments under ``parameters={"message_id": "..."}`` and the
values reach the inner tool via ``registry.execute_tool(**params)``.

These tests pin the new contract.
"""

import json
import sys
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
AI_INFRA_DIR = Path(__file__).resolve().parents[1]
for p in (str(REPO_ROOT), str(AI_INFRA_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from tools.implementations import meta_tools  # noqa: E402


class _RecordingRegistry:
    """Stub for ``tools.registry_v3.RegistryV3`` that records every call.

    The real ``registry.execute_tool()`` signature is
    ``execute_tool(tool_name, **kwargs)`` — the same one used by the meta
    proxy. We only need to capture what is forwarded, not actually run any
    real tool, because the meta proxy is the layer under test.

    A ``tools`` dict is exposed so the proxy's pre-flight existence check
    (``if extracted_tool_name not in registry.tools``) succeeds for the
    tool names the tests request. Any tool name in this set is considered
    "known" by the stub; any other name falls through to the TOOL_NOT_FOUND
    branch (which is itself covered by ``test_missing_tool_name_returns_documented_error``).
    """

    def __init__(self, known_tools=('gmail_get_message', 'search_tools')):
        self.calls = []  # list of (tool_name, params_dict)
        self.tools = {name: {'platform': 'stub'} for name in known_tools}

    def execute_tool(self, tool_name=None, **kwargs):
        self.calls.append((tool_name, dict(kwargs)))
        return {"success": True, "echo": tool_name, "received": dict(kwargs)}


class ExecuteToolParametersContractTests(unittest.TestCase):
    """The new typed ``parameters`` argument must reach the inner tool.

    These are the tests the previous AI session's attempts implicitly
    needed: with the bug, ``message_id`` never made it to the inner call.
    """

    def setUp(self):
        self.registry = _RecordingRegistry()

    def _patch_registry(self):
        return mock.patch(
            'tools.registry_v3.get_registry',
            return_value=self.registry,
        )

    def test_parameters_dict_forwards_message_id(self):
        """The exact failing case from production: gmail_get_message.

        Before the fix, ``message_id`` was dropped by MCP validation and
        the inner call crashed with ``missing 1 required positional
        argument``. With the fix, the value passes through untouched.
        """
        with self._patch_registry():
            result = meta_tools.execute_tool(
                tool_name='gmail_get_message',
                parameters={'message_id': '19f993e672f4c126', 'format': 'full'},
            )
        # Inner call received message_id
        self.assertEqual(len(self.registry.calls), 1)
        forwarded_name, forwarded_params = self.registry.calls[0]
        self.assertEqual(forwarded_name, 'gmail_get_message')
        self.assertEqual(forwarded_params.get('message_id'), '19f993e672f4c126')
        self.assertEqual(forwarded_params.get('format'), 'full')
        # Inner call succeeded (our stub is permissive)
        self.assertTrue(result['success'])

    def test_parameters_json_string_is_parsed(self):
        """Some MCP clients serialise the dict as a JSON string. The proxy
        must accept that shape as well — it is documented behaviour."""
        json_payload = json.dumps(
            {'message_id': 'abc123', 'format': 'metadata'}
        )
        with self._patch_registry():
            meta_tools.execute_tool(
                tool_name='gmail_get_message',
                parameters=json_payload,
            )
        _, forwarded_params = self.registry.calls[0]
        self.assertEqual(forwarded_params['message_id'], 'abc123')
        self.assertEqual(forwarded_params['format'], 'metadata')

    def test_invalid_json_string_returns_error(self):
        """A malformed JSON string must be reported, not crash."""
        with self._patch_registry():
            result = meta_tools.execute_tool(
                tool_name='gmail_get_message',
                parameters='{not valid json',
            )
        self.assertFalse(result['success'])
        self.assertIn('Failed to parse', result['error'])
        # Inner tool must not have been invoked.
        self.assertEqual(self.registry.calls, [])

    def test_parameters_of_wrong_type_returns_error(self):
        """A list/int passed as ``parameters`` must be rejected with a
        clear error rather than crashing later."""
        with self._patch_registry():
            result = meta_tools.execute_tool(
                tool_name='gmail_get_message',
                parameters=['message_id', '19f993e672f4c126'],
            )
        self.assertFalse(result['success'])
        self.assertIn("'parameters' must be a dict or JSON string",
                      result['error'])
        self.assertEqual(self.registry.calls, [])

    def test_parameters_values_win_over_kwargs_on_conflict(self):
        """If the same key is in both ``parameters`` and ``**kwargs``,
        ``parameters`` (the explicit, MCP-safe path) wins. This avoids
        silent override bugs when the AI and the auth layer both set a
        key."""
        with self._patch_registry():
            meta_tools.execute_tool(
                tool_name='gmail_get_message',
                parameters={'format': 'full'},
                format='metadata',  # would-be conflict
            )
        _, forwarded_params = self.registry.calls[0]
        self.assertEqual(forwarded_params['format'], 'full')

    def test_injected_auth_keys_survive_the_merge(self):
        """``_user_id`` and ``_injected_credentials`` are auto-injected by
        the MCP auth layer post-validation. They must survive the merge
        so the inner tool can use them."""
        with self._patch_registry():
            meta_tools.execute_tool(
                tool_name='gmail_get_message',
                parameters={'message_id': 'msg-1'},
                _user_id=42,
                _injected_credentials={'access_token': 'redacted'},
            )
        _, forwarded_params = self.registry.calls[0]
        self.assertEqual(forwarded_params['_user_id'], 42)
        self.assertEqual(
            forwarded_params['_injected_credentials'],
            {'access_token': 'redacted'},
        )
        self.assertEqual(forwarded_params['message_id'], 'msg-1')

    def test_none_parameters_is_ignored(self):
        """When the AI doesn't supply ``parameters`` at all (None), the
        function must still work — the old ``**kwargs`` extraction paths
        must remain functional."""
        with self._patch_registry():
            result = meta_tools.execute_tool(
                tool_name='search_tools',
                query='gmail',
            )
        self.assertTrue(result['success'])
        _, forwarded_params = self.registry.calls[0]
        self.assertEqual(forwarded_params['query'], 'gmail')

    def test_missing_tool_name_returns_documented_error(self):
        """No ``tool_name`` and no auth-layer fallback → the documented
        'MISSING PARAMETER' error, which must point at the new
        ``parameters`` convention (not the old ``**params`` one)."""
        with self._patch_registry():
            result = meta_tools.execute_tool()
        self.assertFalse(result['success'])
        self.assertIn('tool_name', result['error'])
        # Error response must show the new convention, not the old one.
        correct_usage = result.get('correct_usage', '')
        self.assertIn('parameters=', correct_usage)
        self.assertNotIn('**params', correct_usage)


class PreExistingFourShapeExtractionTests(unittest.TestCase):
    """The original 4-shape parameter extraction patterns (Anthropic,
    OpenAI, API wrapper, plain kwargs) must keep working alongside the
    new typed ``parameters`` path. Regression coverage so we don't break
    providers that already pass through.
    """

    def setUp(self):
        self.registry = _RecordingRegistry()

    def _patch_registry(self):
        return mock.patch(
            'tools.registry_v3.get_registry',
            return_value=self.registry,
        )

    def test_anthropic_input_shape_still_works(self):
        with self._patch_registry():
            meta_tools.execute_tool(
                input={'tool_name': 'search_tools', 'query': 'gmail'},
            )
        forwarded_name, forwarded_params = self.registry.calls[0]
        self.assertEqual(forwarded_name, 'search_tools')
        self.assertEqual(forwarded_params['query'], 'gmail')

    def test_openai_arguments_json_shape_still_works(self):
        with self._patch_registry():
            meta_tools.execute_tool(
                arguments=json.dumps(
                    {'tool_name': 'search_tools', 'query': 'calendar'}
                ),
            )
        forwarded_name, forwarded_params = self.registry.calls[0]
        self.assertEqual(forwarded_name, 'search_tools')
        self.assertEqual(forwarded_params['query'], 'calendar')

    def test_direct_tool_name_kwarg_still_works(self):
        with self._patch_registry():
            meta_tools.execute_tool(
                tool_name='search_tools',
                query='tasks',
            )
        forwarded_name, forwarded_params = self.registry.calls[0]
        self.assertEqual(forwarded_name, 'search_tools')
        self.assertEqual(forwarded_params['query'], 'tasks')

    def test_typed_parameters_combined_with_anthropic_input_shape(self):
        """When both are present, the typed ``parameters`` value must
        win (it's the only MCP-safe surface)."""
        with self._patch_registry():
            meta_tools.execute_tool(
                input={'tool_name': 'search_tools', 'query': 'fallback'},
                parameters={'query': 'winner'},
            )
        forwarded_name, forwarded_params = self.registry.calls[0]
        self.assertEqual(forwarded_name, 'search_tools')
        self.assertEqual(forwarded_params['query'], 'winner')


class UserFacingErrorMessageMentionsNewConventionTests(unittest.TestCase):
    """The user-facing error messages in ``meta_tools.execute_tool`` and
    ``get_tool_schema`` must reference the new ``parameters={...}`` shape.
    If they still advertise ``**params``, the next AI client will hit the
    same bug we just fixed.
    """

    def _strings_in_execute_tool_error_responses(self):
        """Collect every string returned by meta_tools.execute_tool error
        responses (when ``tool_name`` is missing) so we can assert they
        all mention the new convention."""
        with mock.patch('tools.registry_v3.get_registry') as gr:
            gr.return_value = _RecordingRegistry()
            err = meta_tools.execute_tool()
        return json.dumps(err)

    def test_execute_tool_error_response_uses_parameters_convention(self):
        text = self._strings_in_execute_tool_error_responses()
        self.assertIn('parameters=', text)
        # And does NOT contain the old broken convention.
        self.assertNotIn('**params', text)

    def test_execute_tool_error_response_documents_the_pitfall(self):
        text = self._strings_in_execute_tool_error_responses()
        # The warning explicitly tells the AI WHY the kwargs path is bad,
        # so the next agent reading the error doesn't repeat the mistake.
        self.assertIn('MCP', text)
        self.assertIn('tool_name', text)


if __name__ == '__main__':
    unittest.main()
