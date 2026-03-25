@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo Uninstalling Brainless...

set "CLAUDE_DIR=%USERPROFILE%\.claude"

:: Step 1: Remove hook from settings.json FIRST (before deleting files)
echo [1/3] Removing hook from settings.json...
set "SETTINGS_FILE=%CLAUDE_DIR%\settings.json"
findstr /c:"bash_error_search" "%SETTINGS_FILE%" >nul 2>&1
if !errorlevel! equ 0 (
    python -c "import json;f=open(r'%SETTINGS_FILE%','r');s=json.load(f);f.close();hooks=s.get('hooks',{}).get('PostToolUse',[]);s['hooks']['PostToolUse']=[h for h in hooks if h.get('matcher')!='Bash' or not any('bash_error_search' in hk.get('command','') for hk in h.get('hooks',[]))];f=open(r'%SETTINGS_FILE%','w');json.dump(s,f,indent=2,ensure_ascii=False);f.close()" 2>nul || python3 -c "import json;f=open(r'%SETTINGS_FILE%','r');s=json.load(f);f.close();hooks=s.get('hooks',{}).get('PostToolUse',[]);s['hooks']['PostToolUse']=[h for h in hooks if h.get('matcher')!='Bash' or not any('bash_error_search' in hk.get('command','') for hk in h.get('hooks',[]))];f=open(r'%SETTINGS_FILE%','w');json.dump(s,f,indent=2,ensure_ascii=False);f.close()" 2>nul
    echo     Hook removed
) else (
    echo     No hook found, skipping
)

:: Step 2: Remove Brainless section from CLAUDE.md
echo [2/3] Cleaning CLAUDE.md...
set "CLAUDE_MD=%CLAUDE_DIR%\CLAUDE.md"
findstr /c:"Brainless Auto-Behaviors" "%CLAUDE_MD%" >nul 2>&1
if !errorlevel! equ 0 (
    python -c "import re;f=open(r'%CLAUDE_MD%','r');c=f.read();f.close();c=re.sub(r'\n*## Brainless Auto-Behaviors \(MANDATORY\).*?(?=\n## (?!Brainless)|$)','',c,flags=re.DOTALL).strip();f=open(r'%CLAUDE_MD%','w');f.write(c+'\n');f.close()" 2>nul || python3 -c "import re;f=open(r'%CLAUDE_MD%','r');c=f.read();f.close();c=re.sub(r'\n*## Brainless Auto-Behaviors \(MANDATORY\).*?(?=\n## (?!Brainless)|$)','',c,flags=re.DOTALL).strip();f=open(r'%CLAUDE_MD%','w');f.write(c+'\n');f.close()" 2>nul
    echo     CLAUDE.md cleaned
) else (
    echo     No brainless rules found, skipping
)

:: Step 3: Remove files
echo [3/3] Removing files...
if exist "%CLAUDE_DIR%\skills\brainless" rd /s /q "%CLAUDE_DIR%\skills\brainless"
for %%c in (brain-dump brain-search brain-stats brain-review brain-cheatsheet brain-rebuild) do (
    if exist "%CLAUDE_DIR%\commands\%%c.md" del /q "%CLAUDE_DIR%\commands\%%c.md"
)
if exist "%CLAUDE_DIR%\brainless" rd /s /q "%CLAUDE_DIR%\brainless"
echo     Files removed

echo.
echo Brainless uninstalled. Your brain is on your own now.

endlocal
pause
