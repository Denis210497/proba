@echo off
echo Creating Trading Journal Executable...

echo Step 0: Cleaning up previous builds...
rmdir /s /q "Trading Journal" 2>nul
rmdir /s /q build 2>nul
rmdir /s /q dist 2>nul
del /q "Trading Journal.spec" 2>nul
del /q app_icon.ico 2>nul

echo Step 1: Creating application icon...
python create_icon.py

echo Step 2: Installing requirements...
pip install --upgrade pip
pip install -r requirements.txt
pip install pyinstaller

echo Step 3: Building executable...
pyinstaller --noconfirm --onefile --windowed ^
    --icon=app_icon.ico ^
    --name="Trading Journal" ^
    --add-data "app_icon.ico;." ^
    --hidden-import tkcalendar ^
    --hidden-import babel.numbers ^
    trading_journal.py

echo Step 4: Creating installation directory...
mkdir "Trading Journal"
move "dist\Trading Journal.exe" "Trading Journal\"
copy "README.md" "Trading Journal\"
echo. > "Trading Journal\trades.csv"
echo {"account_balance": 0} > "Trading Journal\trading_config.json"

echo Step 5: Cleaning up build files...
rmdir /s /q build
rmdir /s /q dist
del /q "Trading Journal.spec"
del /q app_icon.ico

echo.
echo Installation Complete!
echo.
echo The Trading Journal application has been created in the "Trading Journal" folder.
echo You can now:
echo 1. Open the "Trading Journal" folder
echo 2. Double-click "Trading Journal.exe" to start the application
echo 3. First set your account balance in the Account Settings tab
echo 4. Start adding your trades!
echo.
echo Press any key to exit...
pause 