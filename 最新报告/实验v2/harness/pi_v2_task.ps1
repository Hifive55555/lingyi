param([string]$Bat, [string]$Name='PiV2', [int]$Minutes=600)
$sid  = [Security.Principal.WindowsIdentity]::GetCurrent().User.Value
$act  = New-ScheduledTaskAction -Execute $Bat
$prin = New-ScheduledTaskPrincipal -UserId $sid -LogonType Interactive -RunLevel Highest
$set  = New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Minutes $Minutes) -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries -DisallowHardTerminate
Register-ScheduledTask -TaskName $Name -Action $act -Principal $prin -Settings $set -Force | Out-Null
Start-ScheduledTask -TaskName $Name
"task $Name started -> $Bat"
