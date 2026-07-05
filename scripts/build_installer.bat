@echo off
REM Full release build pipeline for Windows.
REM Prerequisites: Python 3.12+, Inno Setup 6+ installed at default path.

echo ========================================
echo  Exam Email Automation — Release Build
echo ========================================
echo.

echo [1/2] Building PyInstaller executable...
call "%~dp0build_exe.bat"
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: PyInstaller build failed.
    exit /b %ERRORLEVEL%
)

echo.
echo [2/2] Building Inno Setup installer...
if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" "%~dp0..\installer\ExamEmailAutomation.iss"
) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
    "C:\Program Files\Inno Setup 6\ISCC.exe" "%~dp0..\installer\ExamEmailAutomation.iss"
) else (
    echo ERROR: Inno Setup 6 not found. Install from https://jrsoftware.org/isinfo.php
    exit /b 1
)

echo.
echo ========================================
echo  Build complete!
echo  Installer: dist\installer\ExamEmailAutomation-Setup-v1.0.0.exe
echo ========================================
