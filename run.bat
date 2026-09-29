@echo off
title Phần mềm So Sánh CTTT
cd /d "%~dp0"

echo ========================================================
echo   Đang khởi động Phần mềm So Sánh CTTT (Python)...
echo ========================================================

python main.py

if %errorlevel% neq 0 (
    echo.
    echo [LỖI] Chương trình gặp lỗi hoặc dừng đột ngột (Mã lỗi: %errorlevel%).
    pause
)
