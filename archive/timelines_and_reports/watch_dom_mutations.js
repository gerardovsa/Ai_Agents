// TEST: Watch DOM mutations to see if something is reordering messages
const container = document.querySelector('#agent-column-2 .agent-messages-container');

if (container) {
    console.log('🔍 Setting up MutationObserver to watch for reordering...');

    const observer = new MutationObserver((mutations) => {
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList') {
                if (mutation.addedNodes.length > 0) {
                    mutation.addedNodes.forEach((node) => {
                        if (node.classList && node.classList.contains('ai-message')) {
                            const role = node.classList.contains('user') ? 'USER' :
                                node.classList.contains('assistant') ? 'ASSISTANT' : 'UNKNOWN';
                            const position = Array.from(container.children).indexOf(node);
                            const totalMessages = container.querySelectorAll('.ai-message').length;
                            console.log(`➕ Added ${role} message at position ${position}/${totalMessages}`);
                        }
                    });
                }

                if (mutation.removedNodes.length > 0) {
                    mutation.removedNodes.forEach((node) => {
                        if (node.classList && node.classList.contains('ai-message')) {
                            const role = node.classList.contains('user') ? 'USER' :
                                node.classList.contains('assistant') ? 'ASSISTANT' : 'UNKNOWN';
                            console.log(`➖ Removed ${role} message`);
                        }
                    });
                }
            }
        });

        // After each mutation, log current order
        const messages = container.querySelectorAll('.ai-message');
        const order = Array.from(messages).map((msg, i) => {
            const role = msg.classList.contains('user') ? 'U' : 'A';
            return role;
        }).join('');
        console.log(`📊 Current order: ${order}`);
    });

    observer.observe(container, {
        childList: true,
        subtree: false
    });

    console.log('✅ MutationObserver active. Now reload the thread to watch order changes.');
    console.log('Run this to reload: MultiAgent.loadThreadIntoAgent(2, { id: 2112 })');
} else {
    console.error('❌ Container not found!');
}
