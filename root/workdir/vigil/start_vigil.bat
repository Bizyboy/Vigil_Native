+  1 @echo off
+  2 title Vigil - The Watchful Guardian
+  3 echo.
+  4 echo ═══════════════════════════════════════════════════════════════
+  5 echo                    VIGIL - THE WATCHFUL GUARDIAN
+  6 echo ═══════════════════════════════════════════════════════════════
+  7 echo.
+  8 
+  9 :: Check if Python is installed
+ 10 python --version >nul 2>&1
+ 11 if errorlevel 1 (
+ 12     echo ERROR: Python is not installed or not in PATH
+ 13     echo Please install Python 3.10+ from https://www.python.org
+ 14     pause
+ 15     exit /b 1
+ 16 )
+ 17 
+ 18 :: Check if virtual environment exists
+ 19 if not exist "venv" (
+ 20     echo Creating virtual environment...
+ 21     python -m venv venv
+ 22     call venv\Scripts\activate.bat
+ 23     echo Installing dependencies...
+ 24     pip install -r requirements.txt
+ 25 ) else (
+ 26     call venv\Scripts\activate.bat
+ 27 )
+ 28 
+ 29 :: Check if .env exists
+ 30 if not exist "config\.env" (
+ 31     echo.
+ 32     echo WARNING: config\.env file not found!
+ 33     echo Please copy config\.env.example to config\.env
+ 34     echo and fill in your API keys.
+ 35     echo.
+ 36     pause
+ 37     exit /b 1
+ 38 )
+ 39 
+ 40 :: Run Vigil
+ 41 echo.
+ 42 echo Starting Vigil...
+ 43 echo.
+ 44 python vigil.py
+ 45 
+ 46 :: Keep window open if there's an error
+ 47 if errorlevel 1 (
+ 48     echo.
+ 49     echo Vigil exited with an error.
+ 50     pause
+ 51 )
