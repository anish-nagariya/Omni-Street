Set-Location ([System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop))
if (-Not (Test-Path .\omnistreet)) {
    Write-Host 'Create Temp Path'
    Set-Location ([System.Io.Path]::GetTempPath())
    if (-Not (Test-Path  .\stockInstaller)) {
        New-Item -Path .\stockInstaller -ItemType Directory
    }
    Set-Location stockInstaller

    if (-Not(Test-Path .\mongodb-windows-x86_64-4.4.5-signed.msi) -or -Not(Test-Path .\node-v14.16.1-x64.msi) -or -Not(Test-Path .\python-3.8.9-amd64.exe) -or -Not(Test-Path .\Git-2.31.1-64-bit.exe)) {
        Write-Host 'Downloading Installers'
        Start-BitsTransfer -Source 'https://fastdl.mongodb.org/windows/mongodb-windows-x86_64-4.4.5-signed.msi' -Destination '.\mongodb-windows-x86_64-4.4.5-signed.msi'
        Start-BitsTransfer -Source 'https://nodejs.org/dist/v14.16.1/node-v14.16.1-x64.msi' -Destination '.\node-v14.16.1-x64.msi'
        Start-BitsTransfer -Source 'https://www.python.org/ftp/python/3.8.9/python-3.8.9-amd64.exe' -Destination '.\python-3.8.9-amd64.exe'
        Start-BitsTransfer -Source 'https://github.com/git-for-windows/git/releases/download/v2.31.1.windows.1/Git-2.31.1-64-bit.exe' -Destination '.\Git-2.31.1-64-bit.exe'
    }

    Write-Host 'Installing MongoDB'
    Start-Process -FilePath 'mongodb-windows-x86_64-4.4.5-signed.msi' -ArgumentList "/norestart", "/l*v mongo-installer.txt" -Wait
    Write-Host 'Installing Node'
    Start-Process -FilePath 'node-v14.16.1-x64.msi' -ArgumentList "/norestart", "/lv node-installer.txt", "/passive" -Wait
    Write-Host 'Installing Python 3.8'
    Start-Process -FilePath 'python-3.8.9-amd64.exe' -ArgumentList "/passive", "PrependPath=1" -Wait
    Write-Host 'Installing Git'
    Start-Process -FilePath 'Git-2.31.1-64-bit.exe' -ArgumentList "/norestart", "/VERYSILENT", "/COMPONENTS=icons,icons\desktop,ext,ext\shellhere,ext\guihere,gitlfs,assoc,assoc_sh,autoupdate" -Wait

    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1')) 
    choco install memurai-developer -y

    Set-Location ..
    Remove-Item .\stockInstaller -Recurse


    Set-Location ([System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop))
    git clone https://sivasunken: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@github.com/anish-nagariya/Omni-Street.git omnistreet 2>&1 | Write-Host
}


if (Test-Path .\omnistreet) {
    Set-Location omnistreet

    git pull 2>&1 | Write-Host
    Write-Host "Installing frontend"
    Set-Location frontend
    npm install
    npm install -g @angular/cli@7.3.9
    Write-Host "Installing backend"
    Set-Location ..\backend
    pip install --upgrade pip
    pip install waitress
    pip install -r requirements.txt
    Set-Location ..
    Start-Process cmd -ArgumentList "/k 'C:\Program Files\Memurai\memurai.exe'"
    Set-Location backend
    Start-Process cmd -ArgumentList "/k server.bat"
    Start-Process cmd -ArgumentList "/k celery.bat"
    Set-Location ..\frontend
    Start-Process cmd -ArgumentList "/k web.bat"
}

Write-Host 'Script Complete'
# SIG # Begin signature block
# MIIFdgYJKoZIhvcNAQcCoIIFZzCCBWMCAQExCzAJBgUrDgMCGgUAMGkGCisGAQQB
# gjcCAQSgWzBZMDQGCisGAQQBgjcCAR4wJgIDAQAABBAfzDtgWUsITrck0sYpfvNR
# AgEAAgEAAgEAAgEAAgEAMCEwCQYFKw4DAhoFAAQUeQ70SGIHeK9IWo/d6IQRfl50
# QwigggMOMIIDCjCCAfKgAwIBAgIQegrd3EhqlI9AODQyG4TfiDANBgkqhkiG9w0B
# AQUFADAdMRswGQYDVQQDDBJMb2NhbCBDb2RlIFNpZ25pbmcwHhcNMjEwNDMwMTE0
# MzUzWhcNMjIwNDMwMTIwMzUzWjAdMRswGQYDVQQDDBJMb2NhbCBDb2RlIFNpZ25p
# bmcwggEiMA0GCSqGSIb3DQEBAQUAA4IBDwAwggEKAoIBAQDsCBaYejWmce/yypLJ
# WYy/7I8IXBxkM1cABBD0t6pfdghvJAj0tzadyiRSjOKb2W4T6gOGRs3Pax+uQQKU
# rwFa6/PPvHlLPde/r/Z+8vfDmvM4NQ6jKuaSyVHiwIMjxULkOFBnEKdjuldx24rY
# 8U6uwkyv8jkUkQwQMYUBvE+kVgdtS/QJPQW6LFsjZ6IEeFj4DIIPOcw2nzyZ7MSs
# YvzQiqXyYfXfRHSlaWYx0c/Yi63EajFeymWKqrH4UdrjyDCPWfRT4ZKz6ZauGkbB
# odEbjsAzv5+wOQFXgFTSl2/eJ9+SDQAnJYWXdzV9dFwo3SM+j6vI4Rltp7vZHLd+
# InlRAgMBAAGjRjBEMA4GA1UdDwEB/wQEAwIHgDATBgNVHSUEDDAKBggrBgEFBQcD
# AzAdBgNVHQ4EFgQU2IvlcFTFmfnX4c/XaEJhDI6HW0YwDQYJKoZIhvcNAQEFBQAD
# ggEBAOlHJ3O6f/nemU1IQr7v6GSWmk4UTT0CWcN+e+0UBzDxajywMyZzHItk9eO+
# HXv4K4FwJAESFxpnuy8sFLo9t0WSVT6JfZRxXCRFqXh9iSQlovctkCAsUr/1YQ+I
# EW4J7bLm4LcckHwcXenm8tCVPyi6Dc8c5g8FRueURP7bIrggNdJ7gVaKFkg5XxsH
# wLSYrLzWyu9A+Pmr0tpXJIe2uu414poi+foAIniP25GeKDxcezRRNCws9fvqqzSf
# i2s74WRW33swU3Q2hv0/Cq80KE+qLT7V70nU6fQ64SEnto6qeFKcFJ98eZiYMuUy
# f0KRjUN8lIn/0C5NxkcOH7qfuZIxggHSMIIBzgIBATAxMB0xGzAZBgNVBAMMEkxv
# Y2FsIENvZGUgU2lnbmluZwIQegrd3EhqlI9AODQyG4TfiDAJBgUrDgMCGgUAoHgw
# GAYKKwYBBAGCNwIBDDEKMAigAoAAoQKAADAZBgkqhkiG9w0BCQMxDAYKKwYBBAGC
# NwIBBDAcBgorBgEEAYI3AgELMQ4wDAYKKwYBBAGCNwIBFTAjBgkqhkiG9w0BCQQx
# FgQUxmftwi9nvWJ6nvgQtlXS9kYvz3cwDQYJKoZIhvcNAQEBBQAEggEAWNDrafef
# +vb904v1meTMJa9Iuq7kV+YNxzCCuEJ8a5sZb/VT5uLNToJgGb/kaKc+9AsxKYOy
# zOz03l5HVINFenneRxvXkcu4WOintnlCeQ+ky6zxYxuvKWO2q+EP0K448LDAV/48
# 0g0ZLw4pv4QYpngbF8q5igjS9aRjVb9tmpXdhwi9BNyZvkR/wgbApBEbHQeSI5OU
# KZ120e+b++s41nOoyGaha5mk8LeRUmqJxf8fn8k/wP3qZTbLqY7vQe9pTwabdvNF
# YZPOwvlAs1RqJxwflAtrdux3cymPRgYHMqRJ6ak/NlV9JF8V2J7uuZAcps+Tu62L
# mWrEn8OltevxZQ==
# SIG # End signature block
