# Fix Microsoft Tools Credential Checking
# Removes environment variable checks from __init__ and updates tools to use credential injection

Write-Host "`n=== FIXING MICROSOFT TOOLS CREDENTIALS ===" -ForegroundColor Cyan

$toolsPath = "tools\implementations"
$microsoftTools = Get-ChildItem -Path $toolsPath -Filter "microsoft_*.py"

$fixCount = 0

foreach ($tool in $microsoftTools) {
    Write-Host "`nProcessing: $($tool.Name)" -ForegroundColor Yellow
    
    $content = Get-Content $tool.FullName -Raw
    
    # Check if it has the warning in __init__
    if ($content -match "⚠️ Warning: MICROSOFT_GRAPH_ACCESS_TOKEN not set") {
        Write-Host "  Found environment variable check - fixing..." -ForegroundColor Gray
        
        # Replace the __init__ method to NOT check environment variables
        $oldInit = @'
    def __init__(self):
        self.access_token = os.getenv('MICROSOFT_GRAPH_ACCESS_TOKEN')
        self.graph_api_base = 'https://graph.microsoft.com/v1.0'
        
        if not self.access_token:
            print("⚠️ Warning: MICROSOFT_GRAPH_ACCESS_TOKEN not set. .* tools will not function.")
'@
        
        $newInit = @'
    def __init__(self):
        # Credentials are injected dynamically per-user via credential_injector
        # No need to check environment variables at init time
        self.graph_api_base = 'https://graph.microsoft.com/v1.0'
'@
        
        $content = $content -replace [regex]::Escape($oldInit -replace '\.\*', '.*'), $newInit
        
        # Also update _get_headers to accept token parameter
        $oldHeaders = @'
    def _get_headers(self) -> Dict[str, str]:
        """Get authorization headers for Microsoft Graph API"""
        return {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json'
        }
'@
        
        $newHeaders = @'
    def _get_headers(self, access_token: str = None, **kwargs) -> Dict[str, str]:
        """Get authorization headers for Microsoft Graph API"""
        # Get access token from credential injector if not provided
        if not access_token and '_user_id' in kwargs:
            from auth.credential_injector import get_microsoft_access_token
            access_token = get_microsoft_access_token(**kwargs)
        
        if not access_token:
            raise Exception("No access token provided. User must be authenticated.")
        
        return {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
'@
        
        if ($content -match [regex]::Escape($oldHeaders)) {
            $content = $content -replace [regex]::Escape($oldHeaders), $newHeaders
            Write-Host "  Updated _get_headers method" -ForegroundColor Green
        }
        
        # Save the file
        Set-Content -Path $tool.FullName -Value $content -NoNewline
        Write-Host "  Fixed: $($tool.Name)" -ForegroundColor Green
        $fixCount++
    } else {
        Write-Host "  No environment variable check found - skipping" -ForegroundColor Gray
    }
}

Write-Host "`n=== FIX COMPLETE ===" -ForegroundColor Cyan
Write-Host "Fixed $fixCount Microsoft tool files" -ForegroundColor Green
