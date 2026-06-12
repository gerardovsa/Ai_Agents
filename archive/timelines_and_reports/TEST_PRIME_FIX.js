// Quick Test: Prime Card Expansion After Fix

console.log('%c=== TESTING PRIME EXPANSION FIX ===', 'color: #FFD93D; font-weight: bold; font-size: 14px;');
console.log('');

// Get the elements
const primeContainer = document.getElementById('prime-thread-info');
const primeCard = document.querySelector('[data-location="prime"], [data-location="prime-loaded"]');
const expandBtn = primeCard?.querySelector('button[class*="expand"]');
const expandContent = primeCard?.querySelector('.thread-expand-on-hover');

console.log('Before Click:');
console.log('  Card has .expanded?', primeCard?.classList.contains('expanded'));
console.log('  Container has .expanded?', primeContainer?.classList.contains('expanded'));
console.log('  Content visible?', window.getComputedStyle(expandContent).opacity === '1' ? 'YES' : 'NO');
console.log('');

// Click the expand button
console.log('Clicking expand button...');
expandBtn?.click();

// Check state after click
setTimeout(() => {
    console.log('After Click:');
    console.log('  Card has .expanded?', primeCard?.classList.contains('expanded'));
    console.log('  Container has .expanded?', primeContainer?.classList.contains('expanded'));

    const style = window.getComputedStyle(expandContent);
    console.log('  Content opacity:', style.opacity);
    console.log('  Content display:', style.display);
    console.log('  Content visible?', style.opacity === '1' && style.display !== 'none' ? 'YES ✅' : 'NO ❌');

    if (style.opacity === '1' && style.display !== 'none') {
        console.log('%c✅ SUCCESS! Prime expansion is now working!', 'color: #00AA00; font-weight: bold;');
    } else {
        console.log('%c❌ Expansion still not working', 'color: #FF0000; font-weight: bold;');
    }
}, 100);
