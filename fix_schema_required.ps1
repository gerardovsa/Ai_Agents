# Fix JSON Schema "required": true inside properties
# This is invalid in JSON Schema 2020-12

Write-Host "`nFixing JSON Schema 'required' syntax..." -ForegroundColor Cyan

$schemaDir = "tools\schemas"
$fixedCount = 0
$filesProcessed = 0

Get-ChildItem "$schemaDir\*.json" | ForEach-Object {
    $file = $_.FullName
    $content = Get-Content $file -Raw
    
    # Check if file has invalid syntax
    if ($content -match '"required":\s*true') {
        $filesProcessed++
        Write-Host "`nProcessing: $($_.Name)" -ForegroundColor Yellow
        
        # Remove all instances of "required": true from inside properties
        $newContent = $content -replace ',\s*"required":\s*true', ''
        $newContent = $newContent -replace '"required":\s*true,\s*', ''
        $newContent = $newContent -replace '"required":\s*true\s*\r?\n', "`n"
        
        # Count changes
        $changes = ([regex]::Matches($content, '"required":\s*true')).Count
        $fixedCount += $changes
        
        # Write back
        Set-Content $file $newContent -NoNewline
        
        Write-Host "  [OK] Fixed $changes instances" -ForegroundColor Green
    }
}

Write-Host "`n[OK] COMPLETE!" -ForegroundColor Green
Write-Host "   Files processed: $filesProcessed" -ForegroundColor White
Write-Host "   Total fixes: $fixedCount" -ForegroundColor White
Write-Host "`nNext step: Restart Flask server (BISTART)" -ForegroundColor Cyan
