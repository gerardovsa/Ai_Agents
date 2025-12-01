/**
 * Verify Module Manifest - Check if dependencies are declared
 * 
 * USAGE: Run this in browser console to verify the manifest is loaded correctly
 */

(async function verifyManifest() {
    console.log('\n' + '='.repeat(80));
    console.log('🔍 VSA MODULE MANIFEST VERIFICATION');
    console.log('='.repeat(80));

    try {
        // Fetch the module file directly
        console.log('\n📥 Fetching module file from server...');
        const response = await fetch('/external/modules/vsa-veterinary-alerts/vsa-veterinary-alerts.js?nocache=' + Date.now());
        const moduleCode = await response.text();

        // Check if dependencies exist in the code
        console.log('\n🔍 Searching for dependencies manifest...');

        const hasDependenciesBlock = moduleCode.includes('dependencies:');
        const hasUtilitiesArray = moduleCode.includes("utilities: ['dom', 'api', 'storage', 'events']");

        console.log('\n📋 Manifest Check Results:');
        console.log('  ✅ Has dependencies block:', hasDependenciesBlock);
        console.log('  ✅ Has utilities array:', hasUtilitiesArray);

        if (hasDependenciesBlock && hasUtilitiesArray) {
            console.log('\n✅ SUCCESS: Module manifest is correct on server!');
            console.log('\n💡 Next steps:');
            console.log('  1️⃣  Hard refresh browser: CTRL+SHIFT+R');
            console.log('  2️⃣  Or clear cache: DevTools → Network → Disable cache');
            console.log('  3️⃣  Click VSA button again');
            console.log('  4️⃣  Should see: "[UtilityComposer] Composing...requested: [\'dom\',\'api\',\'storage\',\'events\']"');
        } else {
            console.log('\n❌ PROBLEM: Manifest not found in module file!');
            console.log('\n🔧 Expected to find:');
            console.log('  dependencies: {');
            console.log("    utilities: ['dom', 'api', 'storage', 'events']");
            console.log('  }');
        }

        // Show first 50 lines to verify structure
        console.log('\n📄 First 50 lines of module file:');
        console.log('─'.repeat(80));
        const lines = moduleCode.split('\n').slice(0, 50);
        lines.forEach((line, i) => {
            if (line.includes('dependencies') || line.includes('utilities')) {
                console.log(`%c${i + 1}: ${line}`, 'background: #4CAF50; color: white; font-weight: bold;');
            } else {
                console.log(`${i + 1}: ${line}`);
            }
        });
        console.log('─'.repeat(80));

    } catch (error) {
        console.error('\n❌ Error fetching module:', error);
    }

    console.log('\n' + '='.repeat(80));
    console.log('✅ VERIFICATION COMPLETE');
    console.log('='.repeat(80) + '\n');
})();

console.log('🔧 Module manifest verification running...');
