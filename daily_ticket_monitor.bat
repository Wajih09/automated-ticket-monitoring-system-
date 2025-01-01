@echo off

:: Set the environment variables for PowerShell
powershell -Command "$env:DESIRED_START_DATE='20/01/2025'; $env:DESIRED_END_DATE='26/01/2025'; python D:\DEV\Python\ticket-monitor.py"
