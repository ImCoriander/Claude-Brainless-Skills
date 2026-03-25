@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

echo.
echo   ____            _       _
echo  ^| __ ^) _ __ __ _^(_^)_ __ ^| ^| ___  ___ ___
echo  ^|  _ \^| '__/ _` ^| ^| '_ \^| ^|/ _ \/ __/ __^|
echo  ^| ^|_^) ^| ^| ^| ^(_^| ^| ^| ^| ^| ^|  __/\__ \__ \
echo  ^|____/^|_^|  \__,_^|_^|_^| ^|_^|_^|\___^|^|___/___/
echo.
echo  "You don't need a brain. I remember everything for you."
echo.

set "CLAUDE_DIR=%USERPROFILE%\.claude"
set "SCRIPT_DIR=%~dp0"

if not exist "%CLAUDE_DIR%" (
    echo [!] Claude Code not found at %CLAUDE_DIR%
    exit /b 1
)

echo [1/7] Creating brain structure...
for %%d in (skills\brainless commands brainless\hooks) do (
    if not exist "%CLAUDE_DIR%\%%d" mkdir "%CLAUDE_DIR%\%%d"
)
for %%d in (build runtime config network dependency permission logic ctf reversing exploit tricks tools other _cheatsheets) do (
    if not exist "%CLAUDE_DIR%\brainless\%%d" mkdir "%CLAUDE_DIR%\brainless\%%d"
)

echo [2/7] Installing skill...
copy /y "%SCRIPT_DIR%skills\brainless\SKILL.md" "%CLAUDE_DIR%\skills\brainless\SKILL.md" >nul

echo [3/7] Installing commands...
for %%c in (brain-dump brain-search brain-review brain-cheatsheet brain-stats brain-rebuild) do (
    copy /y "%SCRIPT_DIR%commands\%%c.md" "%CLAUDE_DIR%\commands\%%c.md" >nul
)

echo [4/7] Installing auto-search hook...
copy /y "%SCRIPT_DIR%hooks\bash_error_search.py" "%CLAUDE_DIR%\brainless\hooks\bash_error_search.py" >nul

:: Inject hook into settings.json using helper script
set "SETTINGS_FILE=%CLAUDE_DIR%\settings.json"
findstr /c:"bash_error_search.py" "%SETTINGS_FILE%" >nul 2>&1
if !errorlevel! neq 0 (
    python "%SCRIPT_DIR%hooks\install_hook.py" 2>nul || python3 "%SCRIPT_DIR%hooks\install_hook.py" 2>nul
) else (
    echo     Hook already configured in settings.json
)

echo [5/7] Initializing knowledge base...
if not exist "%CLAUDE_DIR%\brainless\INDEX.md" (
    copy /y "%SCRIPT_DIR%brainless\INDEX.md" "%CLAUDE_DIR%\brainless\INDEX.md" >nul
    copy /y "%SCRIPT_DIR%brainless\_cache.json" "%CLAUDE_DIR%\brainless\_cache.json" >nul
    for %%d in (build runtime config network dependency permission logic ctf reversing exploit tricks tools other) do (
        if not exist "%CLAUDE_DIR%\brainless\%%d\_index.md" (
            copy /y "%SCRIPT_DIR%brainless\%%d\_index.md" "%CLAUDE_DIR%\brainless\%%d\_index.md" >nul
        )
    )
    echo     Fresh brain initialized — ready to absorb knowledge
) else (
    echo     Existing brain found — preserving memories, updating skill only
)

echo [6/7] Injecting auto-behaviors into CLAUDE.md...
set "CLAUDE_MD=%CLAUDE_DIR%\CLAUDE.md"
set "MARKER=## Brainless Auto-Behaviors (MANDATORY)"

:: Check if CLAUDE.md exists and already has brainless section
set "HAS_MARKER=0"
if exist "%CLAUDE_MD%" (
    findstr /c:"%MARKER%" "%CLAUDE_MD%" >nul 2>&1 && set "HAS_MARKER=1"
)

if "!HAS_MARKER!"=="1" (
    :: Remove old brainless section, keep everything before it
    set "TEMP_FILE=%CLAUDE_DIR%\CLAUDE.md.tmp"
    set "SKIP=0"
    (
        for /f "usebackq delims=" %%L in ("%CLAUDE_MD%") do (
            set "LINE=%%L"
            if "!LINE!"=="!MARKER!" (
                set "SKIP=1"
            ) else if "!SKIP!"=="1" (
                :: Check if we hit a new ## section (not Brainless)
                echo !LINE! | findstr /b /c:"## " >nul 2>&1
                if !errorlevel!==0 (
                    set "SKIP=0"
                    echo %%L
                )
            ) else (
                echo %%L
            )
        )
    ) > "!TEMP_FILE!"
    move /y "!TEMP_FILE!" "%CLAUDE_MD%" >nul
    echo     Updated existing brainless rules
) else (
    echo     Adding brainless rules to CLAUDE.md
)

:: Append the brainless auto-behavior rules
(
    echo.
    echo ## Brainless Auto-Behaviors ^(MANDATORY^)
    echo.
    echo These rules apply to EVERY conversation, regardless of whether the brainless skill is loaded.
    echo They ensure Claude automatically records and recalls knowledge from `~/.claude/brainless/`.
    echo.
    echo ### Auto-Search: Before fixing ANY error
    echo When encountering a non-zero exit code or unexpected error:
    echo 1. Read `~/.claude/brainless/_cache.json` FIRST
    echo 2. Search for matching keywords/tags in the entries
    echo 3. If a match is found, read the full entry and apply the known solution
    echo 4. Only if no match exists, proceed with normal debugging
    echo.
    echo ### Auto-Record: After resolving ANY non-trivial error
    echo After successfully resolving an error that was NOT a simple typo:
    echo 1. Immediately invoke `/brain-dump` to record the problem and solution
    echo 2. Do this BEFORE continuing to the next task
    echo 3. Do NOT ask permission — just record it
    echo 4. Do NOT batch recordings — record each issue individually as it is resolved
    echo 5. Skip ONLY if: it was a trivial typo, OR an identical entry already exists
    echo.
    echo ### What counts as "non-trivial"
    echo - Any non-zero exit code that required investigation
    echo - Environment/config issues
    echo - Build errors that weren't obvious typos
    echo - Any situation where multiple approaches were tried
    echo - CTF challenges, RE findings, exploit techniques
) >> "%CLAUDE_MD%"

echo     Done — auto-behaviors will now work in every conversation

echo [7/7] Verifying...
echo     Skill:    %CLAUDE_DIR%\skills\brainless\SKILL.md
echo     Commands: brain-dump, brain-search, brain-stats, brain-review, brain-cheatsheet, brain-rebuild
echo     Hook:     %CLAUDE_DIR%\brainless\hooks\bash_error_search.py
echo     Brain:    %CLAUDE_DIR%\brainless\
echo     Rules:    %CLAUDE_MD%
echo.
echo === Brainless installed! ===
echo.
echo Commands:   /brain-dump  /brain-search  /brain-stats  /brain-review  /brain-cheatsheet
echo Categories: build runtime config network dependency permission logic
echo             ctf reversing exploit tricks tools
echo.
echo Auto: search brain before fixing ^| record after resolving
echo Optimization: 3-level search (JSON cache -^> sub-index -^> full entry)
echo.
echo Now go be brainless. I'll remember everything for you.

endlocal
pause
