Set-Location ([System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop))
if (-Not (Test-Path .\omnistreet)) {
    if (-Not (Test-Path  .\Installer)) {
        New-Item -Path .\Installer -ItemType Directory

        Set-Location Installer

        if (-Not(Test-Path .\Git-2.31.1-64-bit.exe)) {
            Write-Host 'Downloading Installers'
            Start-BitsTransfer -Source 'https://github.com/git-for-windows/git/releases/download/v2.31.1.windows.1/Git-2.31.1-64-bit.exe' -Destination '.\Git-2.31.1-64-bit.exe'
            Start-BitsTransfer -Source 'https://desktop.docker.com/win/stable/amd64/Docker%20Desktop%20Installer.exe' -Destination '.\DockerDesktopInstaller.exe'
        }

    
        Write-Host 'Installing Git'
        Start-Process -FilePath 'Git-2.31.1-64-bit.exe' -ArgumentList "/norestart", "/VERYSILENT", "/COMPONENTS=icons,icons\desktop,ext,ext\shellhere,ext\guihere,gitlfs,assoc,assoc_sh,autoupdate" -Wait
        Write-Host 'Installing Docker'
        Start-Process -FilePath 'DockerDesktopInstaller.exe' -Wait
    }
    
    Remove-Item .\Installer -Recurse

    Set-Location ([System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop))
    git clone https://sivasunken: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@github.com/anish-nagariya/Omni-Street.git omnistreet 2>&1 | Write-Host

    Set-Location omnistreet
    Start-Process docker-compose -ArgumentList 'up --build -d' -Wait
    $inspect = ""
    do {
        $inspect = Invoke-Expression "docker inspect -f='{{.State.Running}}' mongo"
        Start-Sleep -Seconds 1
    }while ($inspect -ne "true")
    Write-Host "Running Initial DB script"
    Invoke-Expression 'docker exec -it mongo mongo -u admin -p password /home/db/mongofirst.js'
    Write-Host "Reset"
    Start-Process docker-compose -ArgumentList 'down' -Wait
    Set-Location ([System.Environment]::GetFolderPath([System.Environment+SpecialFolder]::Desktop))
}


if (Test-Path .\omnistreet) {
    Set-Location omnistreet
    git pull 2>&1 | Write-Host
    Start-Process docker-compose -ArgumentList 'up --build -d' -Wait
}

Write-Host 'Script Complete'
# SIG # Begin signature block
# MIIFdgYJKoZIhvcNAQcCoIIFZzCCBWMCAQExCzAJBgUrDgMCGgUAMGkGCisGAQQB
# gjcCAQSgWzBZMDQGCisGAQQBgjcCAR4wJgIDAQAABBAfzDtgWUsITrck0sYpfvNR
# AgEAAgEAAgEAAgEAAgEAMCEwCQYFKw4DAhoFAAQUqQ1kXv0fHgV5yINJ5T9398iB
# jomgggMOMIIDCjCCAfKgAwIBAgIQegrd3EhqlI9AODQyG4TfiDANBgkqhkiG9w0B
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
# FgQUC6U8RWrqo/FCtI8pHpWLicBHLIswDQYJKoZIhvcNAQEBBQAEggEAkyeutZLW
# IR+VUs3u80GTzrYoxG4m3QEl2ihM613hljjpK+nz1xSMoIgfGF1wtgtDWN9SGXYV
# bQX5laPFKy97WfpVmycrRZ+AM/DXToqQP5Sm0oLXBnYmOPFmR03QaYcCO83Sm6uA
# Jbi3QSLBuo1UYMYiYI7RIExE78keQK2WxdjRVX5ChzS+/osLPe2pA3hJWEmaQdLk
# jC848bYiuidRARH95BlkFSfK7FInpgfAKGG6zDMwKjVo7aE1UzqweEBI0UZotB3/
# KnqAq365PNrOGcxhEyi91MujENdGEPr1ig94x/cd3DiLNbcHlpichoKPVLAKZ/qK
# tVax15m8PT5xfg==
# SIG # End signature block
