# Run from D:\Ecommerce\EVUE. Read-only checks except container startup.
$ErrorActionPreference = 'Stop'
Set-Location 'D:\Ecommerce\EVUE'
function RunChecked([string[]] $arguments) {
    & docker @arguments
    if ($LASTEXITCODE -ne 0) { throw "Command failed: docker $($arguments -join ' ')" }
}
RunChecked @('compose','config','--quiet')
RunChecked @('compose','ps','-a')
RunChecked @('compose','run','--rm','backend','python','manage.py','check','--deploy')
RunChecked @('compose','run','--rm','backend','python','manage.py','migrate','--check')
RunChecked @('compose','run','--rm','backend','python','manage.py','test','variantcommerce','paymentfulfillment','commercecontrol','--noinput')
RunChecked @('compose','run','--rm','backend','python','manage.py','evu_staging_audit','--json','--strict')
Write-Host 'Automated staging checks passed. Manual gateway, courier, restore and security tests are still required.'
