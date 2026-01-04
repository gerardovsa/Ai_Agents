/**
 * LAYOUT DIAGNOSTIC TOOL
 * Paste this into browser console to get complete layout information
 */

console.log('🔍 LAYOUT DIAGNOSTIC REPORT\n' + '='.repeat(80));

// 1. Platform Container
const platformContainer = document.querySelector('.platform-container');
console.log('\n📦 PLATFORM CONTAINER:');
console.log('  Exists:', !!platformContainer);
console.log('  Classes:', platformContainer?.className);
console.log('  Display:', platformContainer ? getComputedStyle(platformContainer).display : 'N/A');
console.log('  Grid Template Columns:', platformContainer ? getComputedStyle(platformContainer).gridTemplateColumns : 'N/A');
console.log('  Grid Template Rows:', platformContainer ? getComputedStyle(platformContainer).gridTemplateRows : 'N/A');
console.log('  Width:', platformContainer ? getComputedStyle(platformContainer).width : 'N/A');
console.log('  Height:', platformContainer ? getComputedStyle(platformContainer).height : 'N/A');

// 2. Left Sidebar
const leftSidebar = document.querySelector('.sidebar');
console.log('\n📌 LEFT SIDEBAR (.sidebar):');
console.log('  Exists:', !!leftSidebar);
console.log('  Grid Column:', leftSidebar ? getComputedStyle(leftSidebar).gridColumn : 'N/A');
console.log('  Grid Row:', leftSidebar ? getComputedStyle(leftSidebar).gridRow : 'N/A');
console.log('  Width:', leftSidebar ? getComputedStyle(leftSidebar).width : 'N/A');
console.log('  Position:', leftSidebar ? getComputedStyle(leftSidebar).position : 'N/A');

// 3. Right Sidebar
const rightSidebar = document.querySelector('.right-sidebar');
console.log('\n📌 RIGHT SIDEBAR (.right-sidebar):');
console.log('  Exists:', !!rightSidebar);
console.log('  Grid Column:', rightSidebar ? getComputedStyle(rightSidebar).gridColumn : 'N/A');
console.log('  Grid Row:', rightSidebar ? getComputedStyle(rightSidebar).gridRow : 'N/A');
console.log('  Width:', rightSidebar ? getComputedStyle(rightSidebar).width : 'N/A');
console.log('  Position:', rightSidebar ? getComputedStyle(rightSidebar).position : 'N/A');

// 4. Top Header
const topHeader = document.querySelector('.top-header');
console.log('\n📋 TOP HEADER:');
console.log('  Exists:', !!topHeader);
console.log('  Grid Column:', topHeader ? getComputedStyle(topHeader).gridColumn : 'N/A');
console.log('  Grid Row:', topHeader ? getComputedStyle(topHeader).gridRow : 'N/A');
console.log('  Height:', topHeader ? getComputedStyle(topHeader).height : 'N/A');

// 5. Main Content Wrapper
const mainContentWrapper = document.querySelector('.main-content-wrapper');
console.log('\n📄 MAIN CONTENT WRAPPER:');
console.log('  Exists:', !!mainContentWrapper);
console.log('  Grid Column:', mainContentWrapper ? getComputedStyle(mainContentWrapper).gridColumn : 'N/A');
console.log('  Grid Row:', mainContentWrapper ? getComputedStyle(mainContentWrapper).gridRow : 'N/A');
console.log('  Display:', mainContentWrapper ? getComputedStyle(mainContentWrapper).display : 'N/A');
console.log('  Grid Template Columns:', mainContentWrapper ? getComputedStyle(mainContentWrapper).gridTemplateColumns : 'N/A');
console.log('  Width:', mainContentWrapper ? getComputedStyle(mainContentWrapper).width : 'N/A');
console.log('  Height:', mainContentWrapper ? getComputedStyle(mainContentWrapper).height : 'N/A');
console.log('  Overflow:', mainContentWrapper ? getComputedStyle(mainContentWrapper).overflow : 'N/A');

// 6. Main Content
const mainContent = document.querySelector('.main-content');
console.log('\n📝 MAIN CONTENT:');
console.log('  Exists:', !!mainContent);
console.log('  Grid Column:', mainContent ? getComputedStyle(mainContent).gridColumn : 'N/A');
console.log('  Width:', mainContent ? getComputedStyle(mainContent).width : 'N/A');
console.log('  Height:', mainContent ? getComputedStyle(mainContent).height : 'N/A');
console.log('  Padding:', mainContent ? getComputedStyle(mainContent).padding : 'N/A');
console.log('  Overflow Y:', mainContent ? getComputedStyle(mainContent).overflowY : 'N/A');

// 7. AI Chat Panel
const aiChatPanel = document.querySelector('.ai-chat-panel');
console.log('\n💬 AI CHAT PANEL:');
console.log('  Exists:', !!aiChatPanel);
console.log('  Grid Column:', aiChatPanel ? getComputedStyle(aiChatPanel).gridColumn : 'N/A');
console.log('  Width:', aiChatPanel ? getComputedStyle(aiChatPanel).width : 'N/A');
console.log('  Height:', aiChatPanel ? getComputedStyle(aiChatPanel).height : 'N/A');
console.log('  Overflow Y:', aiChatPanel ? getComputedStyle(aiChatPanel).overflowY : 'N/A');

// 8. Universal Sidebars
console.log('\n🎯 UNIVERSAL SIDEBARS:');
const universalSidebars = document.querySelectorAll('.universal-sidebar');
universalSidebars.forEach((sidebar, index) => {
    const styles = getComputedStyle(sidebar);
    console.log(`  [${index}] ${sidebar.id || 'unnamed'}:`);
    console.log(`      Classes: ${sidebar.className}`);
    console.log(`      Position: ${styles.position}`);
    console.log(`      Top: ${styles.top}`);
    console.log(`      Left: ${styles.left}`);
    console.log(`      Right: ${styles.right}`);
    console.log(`      Width: ${styles.width}`);
    console.log(`      Height: ${styles.height}`);
    console.log(`      Transform: ${styles.transform}`);
    console.log(`      Z-index: ${styles.zIndex}`);
    console.log(`      Display: ${styles.display}`);
});

// 9. Synergy Sidebar
const synergySidebar = document.getElementById('synergy-sidebar');
console.log('\n🔮 SYNERGY SIDEBAR:');
console.log('  Exists:', !!synergySidebar);
if (synergySidebar) {
    const styles = getComputedStyle(synergySidebar);
    console.log('  Classes:', synergySidebar.className);
    console.log('  Data-side:', synergySidebar.getAttribute('data-side'));
    console.log('  Position:', styles.position);
    console.log('  Top:', styles.top);
    console.log('  Left:', styles.left);
    console.log('  Right:', styles.right);
    console.log('  Width:', styles.width);
    console.log('  Height:', styles.height);
    console.log('  Transform:', styles.transform);
    console.log('  Z-index:', styles.zIndex);
}

// 10. Automations Sidebar
const automationsSidebar = document.getElementById('automations-sidebar');
console.log('\n🤖 AUTOMATIONS SIDEBAR:');
console.log('  Exists:', !!automationsSidebar);
if (automationsSidebar) {
    const styles = getComputedStyle(automationsSidebar);
    console.log('  Classes:', automationsSidebar.className);
    console.log('  Data-side:', automationsSidebar.getAttribute('data-side'));
    console.log('  Position:', styles.position);
    console.log('  Top:', styles.top);
    console.log('  Left:', styles.left);
    console.log('  Right:', styles.right);
    console.log('  Width:', styles.width);
    console.log('  Height:', styles.height);
    console.log('  Transform:', styles.transform);
    console.log('  Z-index:', styles.zIndex);
}

// 11. Account Sidebar
const accountSidebar = document.getElementById('account-sidebar');
console.log('\n👤 ACCOUNT SIDEBAR:');
console.log('  Exists:', !!accountSidebar);
if (accountSidebar) {
    const styles = getComputedStyle(accountSidebar);
    console.log('  Classes:', accountSidebar.className);
    console.log('  Data-side:', accountSidebar.getAttribute('data-side'));
    console.log('  Position:', styles.position);
    console.log('  Top:', styles.top);
    console.log('  Left:', styles.left);
    console.log('  Right:', styles.right);
    console.log('  Width:', styles.width);
    console.log('  Height:', styles.height);
    console.log('  Transform:', styles.transform);
    console.log('  Z-index:', styles.zIndex);
}

// 12. DOM Hierarchy Check
console.log('\n🌳 DOM HIERARCHY:');
if (platformContainer) {
    console.log('  Platform Container Children:');
    Array.from(platformContainer.children).forEach((child, i) => {
        console.log(`    [${i}] <${child.tagName.toLowerCase()}> .${child.className.split(' ').join('.')}`);
    });
}

if (mainContentWrapper) {
    console.log('  Main Content Wrapper Children:');
    Array.from(mainContentWrapper.children).forEach((child, i) => {
        console.log(`    [${i}] <${child.tagName.toLowerCase()}> .${child.className.split(' ').join('.')}`);
    });
}

// 13. CSS Variables
console.log('\n🎨 CSS VARIABLES:');
const rootStyles = getComputedStyle(document.documentElement);
console.log('  --sidebar-width:', rootStyles.getPropertyValue('--sidebar-width'));
console.log('  --header-height:', rootStyles.getPropertyValue('--header-height'));
console.log('  --chat-width:', rootStyles.getPropertyValue('--chat-width'));

// 14. Viewport
console.log('\n🖥️ VIEWPORT:');
console.log('  Window Width:', window.innerWidth + 'px');
console.log('  Window Height:', window.innerHeight + 'px');
console.log('  Document Width:', document.documentElement.scrollWidth + 'px');
console.log('  Document Height:', document.documentElement.scrollHeight + 'px');

// 15. Visible Tab
console.log('\n📑 ACTIVE TAB:');
const activeTab = document.querySelector('.tab-content.active');
console.log('  Active Tab ID:', activeTab?.id || 'None');
console.log('  Display:', activeTab ? getComputedStyle(activeTab).display : 'N/A');

console.log('\n' + '='.repeat(80));
console.log('✅ DIAGNOSTIC COMPLETE - Copy this output for debugging');
