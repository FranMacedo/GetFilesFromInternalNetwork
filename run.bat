setlocal
cd /d %~dp0
@echo off
cmd /k "cd /d venv\Scripts & activate & cd.. & cd.. & python run_gui.py & pause"
