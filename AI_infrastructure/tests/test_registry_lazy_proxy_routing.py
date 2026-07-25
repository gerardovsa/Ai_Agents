"""Regression tests for tool registry lazy-proxy dispatch.

Background
----------
``tools.registry_v3._LazyModuleProxy`` defers ``importlib.import_module()``
until first attribute access (the cold-start optimisation for Render). The
proxy used to re-raise the raw import error on attribute access, which broke
the Python ``module``-like contract: ``hasattr(proxy, "anything")`` was
propagating ``ModuleNotFoundError`` instead of returning ``False``.

That broke ``RegistryV3.get_tool_function("tavily_search")`` because the
iteration in get_tool_function probes every entry's ``impl_module`` for an
attribute named ``tavily_search`` via ``hasattr``. When the iteration reached
the proxy for ``tools.implementations.resend_email`` (which has
``import resend`` at module top), the materialization raised
``ModuleNotFoundError: No module named 'resend'``. ``hasattr`` only catches
``AttributeError``, so the exception bubbled up and crashed the dispatch
before the iteration reached the ``tavily_tools`` proxy.

The fix has two layers:

1. ``_LazyModuleProxy.__getattr__`` now converts non-``AttributeError``
   materialization failures into ``AttributeError``. ``hasattr`` then
   returns ``False`` for broken proxies and the iteration continues.
2. ``_load_from_implementations`` now honours
   ``_DISABLED_IMPLEMENTATION_STEMS`` so known-disabled platforms
   (``resend_email``, ``twilio``, ``adobe_indesign``, ...) never become
   proxies at all.

These tests pin both contracts.
"""

import sys
import types
import unittest
from pathlib import Path
from unittest import mock

REPO_ROOT = Path(__file__).resolve().parents[2]
AI_INFRA_DIR = Path(__file__).resolve().parents[1]
for p in (str(REPO_ROOT), str(AI_INFRA_DIR)):
    if p not in sys.path:
        sys.path.insert(0, p)

from tools.registry_v3 import (  # noqa: E402
    _DISABLED_IMPLEMENTATION_STEMS,
    _LazyModuleProxy,
)


class _FakeTavilyModule(types.ModuleType):
    """A stand-in for ``tools.implementations.tavily_tools``.

    Exposes the same public surface the registry cares about:
    a top-level ``tavily_search`` callable.
    """

    def __init__(self):
        super().__init__('tools.implementations.tavily_tools')

    def tavily_search(self, query, max_results=5, search_depth='basic', **_):
        return {'provider': 'tavily', 'query': query, 'max_results': max_results,
                'search_depth': search_depth, 'fake': True}


class _FakeResendModule(types.ModuleType):
    """Stand-in for a module whose top-level ``import resend`` fails.

    Importing this stub is impossible (mirrors what happens on a host
    where the optional SDK is not installed). The proxy should convert
    the resulting ModuleNotFoundError into AttributeError so that
    ``hasattr`` returns False.
    """

    def __init__(self):
        super().__init__('tools.implementations.resend_email')


class LazyProxyAttributeContractTests(unittest.TestCase):
    """``_LazyModuleProxy`` must look like a real module to ``hasattr``
    even when the underlying import fails for any reason other than a
    genuine missing attribute.
    """

    def test_hasattr_returns_false_for_unimportable_module(self):
        # ``tools.does_not_exist_anywhere_xyz123`` cannot be imported.
        proxy = _LazyModuleProxy('tools.does_not_exist_anywhere_xyz123')
        # hasattr MUST return False; the proxy must NOT raise.
        self.assertFalse(hasattr(proxy, 'anything'))
        self.assertFalse(hasattr(proxy, 'tavily_search'))

    def test_attribute_access_on_unimportable_module_raises_attribute_error(self):
        # ``getattr`` on a broken proxy must raise AttributeError, not
        # the original ImportError/ModuleNotFoundError. This is what
        # makes ``hasattr`` work and lets ``get_tool_function`` iterate
        # safely across a registry that contains broken siblings.
        proxy = _LazyModuleProxy('tools.does_not_exist_anywhere_xyz123')
        with self.assertRaises(AttributeError) as cm:
            proxy.tavily_search
        # Original cause preserved as __cause__/__context__ for debugging
        self.assertIsInstance(cm.exception.__cause__, (ImportError, ModuleNotFoundError))

    def test_hasattr_returns_false_after_failed_materialisation(self):
        # A proxy that failed to materialise must keep returning False
        # for subsequent attribute probes (error is cached).
        proxy = _LazyModuleProxy('tools.does_not_exist_anywhere_xyz123')
        try:
            proxy.anything
        except AttributeError:
            pass
        # Second access: still AttributeError, not a re-attempted import.
        self.assertFalse(hasattr(proxy, 'another_attr'))

    def test_attribute_error_message_mentions_fq_name_and_attribute(self):
        proxy = _LazyModuleProxy('tools.does_not_exist_anywhere_xyz123')
        try:
            proxy.tavily_search
        except AttributeError as e:
            msg = str(e)
        else:
            self.fail('expected AttributeError')
        self.assertIn('tools.does_not_exist_anywhere_xyz123', msg)
        self.assertIn('tavily_search', msg)

    def test_genuine_attribute_missing_still_raises_attribute_error(self):
        # When the module DOES import but simply lacks the attribute, the
        # proxy must still raise AttributeError (so getattr-with-default
        # callers see the same behaviour they would for a real module).
        proxy = _LazyModuleProxy('tools.registry_v3')  # exists; no 'tavily_search'
        self.assertFalse(hasattr(proxy, 'tavily_search'))
        with self.assertRaises(AttributeError):
            proxy.tavily_search

    def test_real_attribute_access_works_after_successful_materialisation(self):
        # The proxy must still surface real attributes from the
        # materialised module — the hardening is additive, not breaking.
        proxy = _LazyModuleProxy('pathlib')
        self.assertTrue(hasattr(proxy, 'Path'))
        self.assertIs(proxy.Path, __import__('pathlib').Path)


class DisabledImplementationStemsFilterTests(unittest.TestCase):
    """``_DISABLED_IMPLEMENTATION_STEMS`` must cover every stem whose
    platform is in the schema-level disabled list, mapped from schema
    platform name to file stem. The mapping is intentionally explicit
    (see the comment in ``registry_v3.py``).
    """

    def test_resend_email_is_disabled(self):
        # resend platform is disabled at the schema level; the file stem
        # 'resend_email' must also be in the implementation-level list.
        self.assertIn('resend_email', _DISABLED_IMPLEMENTATION_STEMS)

    def test_other_disabled_platforms_are_listed(self):
        # Each disabled schema platform whose Python implementation lives
        # in tools/implementations/ should appear here.
        expected = {
            'resend_email', 'sendgrid_email_fallback', 'twilio',
            'twilio_veterinary', 'ngrok', 'cloudflare', 'cloudconvert',
            'github', 'render', 'adobe_indesign', 'inhouse_query',
            'xero_quotes', 'xero_quotes_smart',
        }
        self.assertTrue(
            expected.issubset(_DISABLED_IMPLEMENTATION_STEMS),
            f'missing from _DISABLED_IMPLEMENTATION_STEMS: '
            f'{expected - _DISABLED_IMPLEMENTATION_STEMS}'
        )

    def test_tavily_tools_is_NOT_disabled(self):
        # Tavily is the very tool this fix unblocks. Make absolutely sure
        # nobody accidentally adds it to the disabled list.
        self.assertNotIn('tavily_tools', _DISABLED_IMPLEMENTATION_STEMS)
        self.assertNotIn('tavily_search', _DISABLED_IMPLEMENTATION_STEMS)


class GetToolFunctionTavilyRoutingTests(unittest.TestCase):
    """End-to-end: ``RegistryV3.get_tool_function('tavily_search')`` must
    return the tavily_search function even when an unrelated sibling
    implementation (resend_email) raises ModuleNotFoundError on import.
    This is the exact failure mode the production trace showed.
    """

    def setUp(self):
        from tools.registry_v3 import RegistryV3
        # Build a fresh registry and override `implementations` to mimic
        # the production state where resend_email and tavily_tools are
        # both registered as proxies. We bypass the real filesystem scan
        # so the test is hermetic.
        self.registry = RegistryV3.__new__(RegistryV3)
        self.registry.tools = {}
        self.registry.implementations = {}

        # The fake broken proxy — same fq_name shape as the real one.
        self.broken = _LazyModuleProxy('tools.implementations.resend_email')
        self.registry.implementations['resend_email'] = self.broken

        # The fake healthy proxy — we patch importlib.import_module so
        # that resolving 'tools.implementations.tavily_tools' returns our
        # _FakeTavilyModule instead of trying to load the real one
        # (which would import optional SDKs not installed in CI).
        self.fake_tavily_mod = _FakeTavilyModule()

        real_import_module = __import__('importlib').import_module

        def fake_import_module(name, *args, **kwargs):
            if name == 'tools.implementations.tavily_tools':
                return self.fake_tavily_mod
            return real_import_module(name, *args, **kwargs)

        self._import_patch = mock.patch(
            'tools.registry_v3.importlib.import_module',
            side_effect=fake_import_module,
        )
        self._import_patch.start()
        self.addCleanup(self._import_patch.stop)

        self.healthy = _LazyModuleProxy('tools.implementations.tavily_tools')
        self.registry.implementations['tavily_tools'] = self.healthy

    def test_tavily_search_resolves_past_broken_sibling(self):
        # The exact reproduction: lookup must not raise. Before the fix,
        # the iteration over implementations would materialise the
        # resend_email proxy first, hit `import resend`, and the
        # ModuleNotFoundError would bubble up.
        func = self.registry.get_tool_function('tavily_search')
        self.assertIsNotNone(func, 'tavily_search must resolve to a callable')
        self.assertTrue(callable(func))

    def test_tavily_search_executes_with_user_args(self):
        # The function must also execute correctly — the registry must
        # forward kwargs, not just return the callable.
        func = self.registry.get_tool_function('tavily_search')
        result = func(query='weather in Brisbane', max_results=3)
        self.assertEqual(result['provider'], 'tavily')
        self.assertEqual(result['query'], 'weather in Brisbane')
        self.assertEqual(result['max_results'], 3)

    def test_broken_sibling_is_skipped_silently_by_iteration(self):
        # Probing the broken proxy must NOT raise — it must report
        # "no such attribute" so the iteration in get_tool_function can
        # continue past it.
        self.assertFalse(hasattr(self.broken, 'tavily_search'))

    def test_healthy_sibling_resolves_on_attribute_access(self):
        # And the healthy proxy must expose tavily_search normally.
        # Note: bound methods are recreated on each attribute access, so
        # compare the underlying __func__ rather than the bound method
        # itself with `is`.
        self.assertTrue(hasattr(self.healthy, 'tavily_search'))
        self.assertIs(
            self.healthy.tavily_search.__func__,
            self.fake_tavily_mod.tavily_search.__func__,
        )

    def test_unknown_tool_returns_none(self):
        # Sanity: the fallback path still returns None for truly
        # unknown tools (not raise).
        self.assertIsNone(self.registry.get_tool_function('definitely_not_a_tool'))


class ResendEmailImportFailureIsolatedTests(unittest.TestCase):
    """Reproduces the *exact* production failure: a top-level
    ``import resend`` inside resend_email.py raises ModuleNotFoundError,
    the registry proxies it, and any tool that triggers the dispatch
    iteration must not crash.

    These tests force the import failure via ``mock.patch`` on
    ``importlib.import_module`` so the suite is hermetic regardless of
    whether the ``resend`` SDK happens to be installed locally (it IS
    installed on this dev box, but it is NOT on the Render production
    instance where the original bug was reported).
    """

    def _force_resend_import_failure(self):
        """Patch importlib.import_module so the resend_email module
        fails to import, mimicking a host without the optional SDK."""
        real_import_module = __import__('importlib').import_module

        def fake_import_module(name, *args, **kwargs):
            if name == 'tools.implementations.resend_email':
                raise ModuleNotFoundError(
                    "No module named 'resend' (forced by test)"
                )
            return real_import_module(name, *args, **kwargs)

        return mock.patch(
            'tools.registry_v3.importlib.import_module',
            side_effect=fake_import_module,
        )

    def test_importing_resend_email_raises_module_not_found_error(self):
        # Sanity check that, in production, the file's top-level
        # ``import resend`` would raise. Forced via mock so we don't
        # depend on the local SDK being installed.
        with self._force_resend_import_failure():
            from tools import registry_v3 as reg
            with self.assertRaises(ModuleNotFoundError):
                reg.importlib.import_module('tools.implementations.resend_email')

    def test_resend_email_proxy_attribute_access_is_attribute_error(self):
        # The proxy must surface the underlying import failure as
        # AttributeError, so hasattr() returns False and iteration is
        # safe.
        with self._force_resend_import_failure():
            proxy = _LazyModuleProxy('tools.implementations.resend_email')
            self.assertFalse(hasattr(proxy, 'anything'))
            with self.assertRaises(AttributeError):
                proxy.resend_send_email


if __name__ == '__main__':
    unittest.main()
