@echo off
echo Installing required packages...
pip install -r requirements.txt
pip install pyinstaller

echo Building executable...
pyinstaller --noconfirm --onefile --windowed --icon=app_icon.ico --add-data "trading_journal.py;." trading_journal.py

echo Moving executable to main directory...
move dist\trading_journal.exe . 