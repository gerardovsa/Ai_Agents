/**
 * CONSOLE DIAGNOSTIC SCRIPT
 * Paste this into browser console to diagnose chat input spacing
 * 
 * This will show you exactly what's causing the gap at the bottom
 */

(function () {
    console.log('\n' + '='.repeat(70));
    console.log('AI CHAT INPUT SPACING DIAGNOSTIC');
    console.log('='.repeat(70) + '\n');

    // Get elements
    const inputContainer = document.querySelector('.ai-chat-input-container');
    const messagesContainer = document.querySelector('.ai-chat-messages');
    const chatPanel = document.querySelector('.ai-chat-panel');
    const inputTextarea = document.querySelector('.ai-chat-input');

    if (!inputContainer) {
        console.error('❌ Could not find .ai-chat-input-container');
        return;
    }

    // Helper function to get computed style value
    function getStyle(element, property) {
        if (!element) return 'N/A';
        const value = window.getComputedStyle(element)[property];
        return value;
    }

    // Helper to get element position
    function getPosition(element) {
        if (!element) return 'N/A';
        const rect = element.getBoundingClientRect();
        return {
            top: Math.round(rect.top),
            bottom: Math.round(rect.bottom),
            height: Math.round(rect.height),
            windowHeight: window.innerHeight
        };
    }

    console.log('📊 ELEMENT MEASUREMENTS:\n');

    // Chat Panel
    if (chatPanel) {
        const panelPos = getPosition(chatPanel);
        console.log('🔷 Chat Panel (.ai-chat-panel):');
        console.log(`   Height: ${panelPos.height}px`);
        console.log(`   Top: ${panelPos.top}px`);
        console.log(`   Bottom: ${panelPos.bottom}px`);
        console.log(`   Padding: ${getStyle(chatPanel, 'padding')}`);
        console.log('');
    }

    // Messages Container
    if (messagesContainer) {
        const msgPos = getPosition(messagesContainer);
        console.log('💬 Messages Container (.ai-chat-messages):');
        console.log(`   Height: ${msgPos.height}px`);
        console.log(`   Top: ${msgPos.top}px`);
        console.log(`   Bottom: ${msgPos.bottom}px`);
        console.log(`   Padding: ${getStyle(messagesContainer, 'padding')}`);
        console.log(`   Padding-top: ${getStyle(messagesContainer, 'paddingTop')}`);
        console.log(`   Padding-bottom: ${getStyle(messagesContainer, 'paddingBottom')}`);
        console.log(`   Margin-bottom: ${getStyle(messagesContainer, 'marginBottom')}`);
        console.log('');
    }

    // Input Container
    const inputPos = getPosition(inputContainer);
    console.log('📝 Input Container (.ai-chat-input-container):');
    console.log(`   Position: ${getStyle(inputContainer, 'position')}`);
    console.log(`   Bottom: ${getStyle(inputContainer, 'bottom')}`);
    console.log(`   Height: ${inputPos.height}px`);
    console.log(`   Top: ${inputPos.top}px`);
    console.log(`   Bottom (screen): ${inputPos.bottom}px`);
    console.log(`   Padding: ${getStyle(inputContainer, 'padding')}`);
    console.log(`   Padding-top: ${getStyle(inputContainer, 'paddingTop')}`);
    console.log(`   Padding-bottom: ${getStyle(inputContainer, 'paddingBottom')}`);
    console.log(`   Margin: ${getStyle(inputContainer, 'margin')}`);
    console.log('');

    // Input Textarea
    if (inputTextarea) {
        const textareaPos = getPosition(inputTextarea);
        console.log('✏️  Input Textarea (.ai-chat-input):');
        console.log(`   Height: ${textareaPos.height}px`);
        console.log(`   Top: ${textareaPos.top}px`);
        console.log(`   Bottom (screen): ${textareaPos.bottom}px`);
        console.log(`   Margin: ${getStyle(inputTextarea, 'margin')}`);
        console.log(`   Padding: ${getStyle(inputTextarea, 'padding')}`);
        console.log('');
    }

    // Calculate actual distance from bottom
    const windowHeight = window.innerHeight;
    const inputBottom = inputPos.bottom;
    const distanceFromBottom = windowHeight - inputBottom;

    console.log('📏 SPACING CALCULATIONS:\n');
    console.log(`   Window Height: ${windowHeight}px`);
    console.log(`   Input Container Bottom: ${inputBottom}px`);
    console.log(`   🎯 Distance from bottom: ${distanceFromBottom}px`);
    console.log('');

    // Check for any elements between input and bottom
    console.log('🔍 SPACING BREAKDOWN:\n');

    if (inputTextarea) {
        const textareaBottom = getPosition(inputTextarea).bottom;
        const containerBottom = inputPos.bottom;
        const gapInsideContainer = containerBottom - textareaBottom;

        console.log(`   Textarea bottom: ${textareaBottom}px`);
        console.log(`   Container bottom: ${containerBottom}px`);
        console.log(`   Gap inside container: ${gapInsideContainer}px (padding-bottom)`);
        console.log(`   Gap to screen bottom: ${distanceFromBottom}px`);
        console.log('');
        console.log(`   ⚠️  TOTAL GAP: ${gapInsideContainer + distanceFromBottom}px`);
    }

    console.log('\n' + '='.repeat(70));
    console.log('VISUAL HIERARCHY:');
    console.log('='.repeat(70) + '\n');
    console.log('Screen top (0px)');
    console.log('    ↓');
    if (chatPanel) console.log(`    Chat Panel starts (${getPosition(chatPanel).top}px)`);
    if (messagesContainer) console.log(`    Messages Container (${getPosition(messagesContainer).top}px - ${getPosition(messagesContainer).bottom}px)`);
    console.log(`    Input Container (${inputPos.top}px - ${inputPos.bottom}px)`);
    if (inputTextarea) console.log(`    Input Textarea (${getPosition(inputTextarea).top}px - ${getPosition(inputTextarea).bottom}px)`);
    console.log(`    ↓`);
    console.log(`Screen bottom (${windowHeight}px)`);
    console.log('');

    // Suggestions
    console.log('💡 SUGGESTIONS:\n');

    if (distanceFromBottom > 15) {
        console.log(`   ⚠️  Gap is ${distanceFromBottom}px (target: 10px)`);
        console.log(`   → Need to reduce by ${distanceFromBottom - 10}px`);
        console.log('');
        console.log('   Possible causes:');

        const containerPaddingBottom = parseInt(getStyle(inputContainer, 'paddingBottom'));
        if (containerPaddingBottom > 10) {
            console.log(`   - Input container padding-bottom: ${containerPaddingBottom}px (should be 10px)`);
        }

        if (messagesContainer) {
            const msgPaddingBottom = parseInt(getStyle(messagesContainer, 'paddingBottom'));
            if (msgPaddingBottom > 0) {
                console.log(`   - Messages container padding-bottom: ${msgPaddingBottom}px (should be 0px)`);
            }
        }

        const containerMarginBottom = parseInt(getStyle(inputContainer, 'marginBottom'));
        if (containerMarginBottom > 0) {
            console.log(`   - Input container margin-bottom: ${containerMarginBottom}px (should be 0px)`);
        }
    } else {
        console.log(`   ✅ Gap looks good: ${distanceFromBottom}px`);
    }

    console.log('\n' + '='.repeat(70));
    console.log('END DIAGNOSTIC');
    console.log('='.repeat(70) + '\n');

    // Return values for further inspection
    return {
        inputContainer,
        messagesContainer,
        chatPanel,
        inputTextarea,
        measurements: {
            distanceFromBottom,
            windowHeight,
            inputBottom
        }
    };
})();
