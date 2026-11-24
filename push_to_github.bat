@echo off
title Push to GitHub - Cloud-Based Student Management System
color 0b
echo =================================================================
echo   PUSHING TO PUBLIC GITHUB REPOSITORY
echo   Aditya Patel (3CSE23) - IILM University
echo =================================================================
powershell -ExecutionPolicy Bypass -File "%~dp0push_to_github.ps1"
pause
