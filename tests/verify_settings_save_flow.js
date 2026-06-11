// Smoke test: simulate a user changing AI settings in the Account Profile
// modal and verify the new debounced save flow sends the right payload to
// /api/user/preferences.

const fs = require('fs');
const path = require('path');

const state = { localStorage: {}, fetchCalls: [] };
global.localStorage = {
    getItem: (k) => state.localStorage[k] || null,
    setItem: (k, v) => { state.localStorage[k] = v; }
};
global.fetch = async (url, opts) => {
    state.fetchCalls.push({ url, body: JSON.parse(opts.body), headers: opts.headers });
    return { ok: true, json: async () => ({ success: true }) };
};
global.API_BASE_URL = 'http://localhost:5001';

// Mock DOM with the AI settings fields populated to user-chosen values
const mockEls = {
    'modelSelect':           { value: 'MiniMax-M3' },
    'temperature':           { value: '1.0' },
    'topP':                  { value: '1.0' },
    'maxTokens':             { value: '16000' },
    'enableThinking':        { checked: true, value: '' },
    'thinkingBudgetSlider':  { value: '10000' },
    'enableStreaming':       { checked: true, value: '' },
    'maxRounds':             { value: '20' },
    'roundTimeout':          { value: '30' },
    'userNickname':          { value: 'GP' },
    'communicationStyle':    { value: 'professional' },
    'authPlatform':          { value: 'auto' }
};
global.document = {
    getElementById: (id) => mockEls[id] || null,
    querySelector: (sel) => sel === 'input[name="detailLevel"]:checked' ? { value: 'standard' } : null,
    querySelectorAll: () => [],
    createElement: () => ({ style: {}, innerHTML: '', classList: { add: () => {}, remove: () => {} } })
};
global.window = { addEventListener: () => {} };

const html = fs.readFileSync(path.resolve(__dirname, '../UI/business-ai-platform-v2.html'), 'utf8');

function extractFn(name) {
    const re = new RegExp('(async\\s+)?function\\s+' + name + '\\s*\\(', 'g');
    const start = re.exec(html);
    if (!start) throw new Error('function not found: ' + name);
    const open = html.indexOf('{', start.index);
    let depth = 0, i = open;
    for (; i < html.length; i++) {
        if (html[i] === '{') depth++;
        else if (html[i] === '}') { depth--; if (depth === 0) break; }
    }
    return html.slice(start.index, i + 1);
}

const collected = extractFn('_collectSettingsFromUI');
const saver = extractFn('saveSettings');
const indicator = extractFn('_setSaveIndicator');

// Replace the inner _pushSettingsToBackend call with a mock that calls fetch
const saverMocked = saver.replace(
    '_pushSettingsToBackend(settings);',
    'fetch(API_BASE_URL + "/api/user/preferences", { method: "POST", headers: { Authorization: "Bearer " + "test-token", "Content-Type": "application/json" }, body: JSON.stringify(settings) });'
);

// Pre-declare the module-level let bindings used by saveSettings so the
// extracted function body can reference them in isolation.
const prelude = 'let _settingsSaveTimer = null;\nlet _settingsLastPayload = null;\nconst SETTINGS_SAVE_DEBOUNCE_MS = 600;\n';

const code = prelude + indicator + '\n\n' + collected + '\n\n' + saverMocked + '\nreturn { collected: _collectSettingsFromUI(), run: saveSettings };';
const fn = new Function('fetch', 'localStorage', 'document', 'window', 'API_BASE_URL', 'setTimeout', code);

const result = fn(global.fetch, global.localStorage, global.document, global.window, global.API_BASE_URL, setTimeout);

console.log('--- Collected payload (what the UI would send) ---');
console.log(JSON.stringify(result.collected, null, 2));

console.log('\n--- Calling saveSettings() then waiting 700ms for debounce ---');
result.run();
setTimeout(() => {
    console.log('Number of fetch calls: ' + state.fetchCalls.length);
    if (state.fetchCalls[0]) {
        console.log('\n--- POST body to /api/user/preferences ---');
        console.log(JSON.stringify(state.fetchCalls[0].body, null, 2));
        console.log('\n--- Headers ---');
        console.log('  Authorization: present=' + !!state.fetchCalls[0].headers.Authorization);
    }
    console.log('\n--- localStorage value ---');
    console.log(state.localStorage.accountSettings);

    // Assertions
    const b = state.fetchCalls[0]?.body || {};
    const ok =
        b.ai_model === 'MiniMax-M3' &&
        b.ai_max_tokens === 16000 &&
        b.ai_temperature === 1.0 &&
        b.ai_thinking_enabled === 1 &&
        b.ai_streaming_enabled === 1 &&
        b.nickname === 'GP' &&
        state.fetchCalls.length === 1;
    console.log('\n=== ' + (ok ? '✅ PASS' : '❌ FAIL') + ' ===');
    process.exit(ok ? 0 : 1);
}, 800);
