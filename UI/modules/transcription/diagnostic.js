// =====================================
// TRANSCRIPTION SYSTEM DIAGNOSTIC
// Paste this into browser console (F12) to check system status
// =====================================

console.log('🔍 ===== TRANSCRIPTION SYSTEM DIAGNOSTIC =====');

// Check if files loaded
console.log('\n📁 FILE LOADING STATUS:');
console.log('  STT Module:', typeof window.STTModule !== 'undefined' ? '✅ Loaded' : '❌ Not loaded');
console.log('  Streaming Controller:', typeof window.TranscriptionStreaming !== 'undefined' ? '✅ Loaded' : '❌ Not loaded');
console.log('  Toggle Function:', typeof window.toggleTranscriptionRecording === 'function' ? '✅ Available' : '❌ Not available');

// Check if elements exist
console.log('\n🎯 DOM ELEMENTS:');
const micBtn = document.getElementById('ai-chat-mic-btn');
console.log('  Microphone Button:', micBtn ? '✅ Found' : '❌ Not found');
if (micBtn) {
    console.log('    - classList:', Array.from(micBtn.classList));
    console.log('    - onclick:', micBtn.onclick ? 'Set' : 'Not set');
    console.log('    - visible:', window.getComputedStyle(micBtn).display !== 'none');
}

const container = document.getElementById('ai-transcription-container');
console.log('  Streaming Container:', container ? '✅ Found' : '❌ Not found');
if (container) {
    console.log('    - classList:', Array.from(container.classList));
    console.log('    - visible:', !container.classList.contains('hidden'));
}

const chatInput = document.getElementById('ai-chat-input');
console.log('  Chat Input:', chatInput ? '✅ Found' : '❌ Not found');

// Check console for errors
console.log('\n🐛 CONSOLE ERRORS:');
console.log('  Check above for any red error messages starting with [TRANSCRIPTION]');

// Test functions
console.log('\n🧪 MANUAL TESTS:');
console.log('  1. Click microphone button or run: toggleTranscriptionRecording()');
console.log('  2. Check if container appears: document.getElementById("ai-transcription-container").classList.contains("hidden")');
console.log('  3. Manually show container: window.TranscriptionStreaming.show()');
console.log('  4. Test stream text: window.TranscriptionStreaming.streamText("Hello world", true)');

// Try to manually show container
if (window.TranscriptionStreaming) {
    console.log('\n🎬 ATTEMPTING TO SHOW CONTAINER...');
    try {
        window.TranscriptionStreaming.show();
        window.TranscriptionStreaming.streamText('🎉 Test message - if you see this, the system is working!', true);
        console.log('✅ Container should now be visible at bottom of page');
    } catch (error) {
        console.error('❌ Failed to show container:', error);
    }
}

console.log('\n📝 NEXT STEPS:');
console.log('  1. If container appeared, click microphone button to test recording');
console.log('  2. If not appearing, check Network tab for failed file loads');
console.log('  3. Make sure Whisper backend is running: http://localhost:3001/api/v1/system/check');
console.log('  4. Hard refresh browser: Ctrl+Shift+R');

console.log('\n✅ DIAGNOSTIC COMPLETE');
