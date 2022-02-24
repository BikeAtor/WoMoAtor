echo on
REM pyinstaller --noconfirm --onedir --console --add-data "../pic_free;pic_free/" --add-binary "windows-dll/libcairo-2.dll;."  "supervoltbatterygui.py"

REM pyinstaller --onefile --noconfirm --console --add-data "../pic_free;./pic_free" --add-binary "windows-dll/libcairo-2.dll;."  "supervoltbatterygui.py"
pyinstaller --onefile --clean --noconfirm --console --add-binary "windows-dll/libcairo-2.dll;."  "supervoltbatterygui.py"

copy .\dist\supervoltbatterygui.exe .\windows-bin\


REM nuitka does not work (yet)
REM python.exe -m nuitka --mingw64 --enable-plugin=tk-inter .\supervoltbatterygui.py --standalone --onefile

REM nuitka --mingw64 --enable-plugin=tk-inter --include-plugin-directory=windows-dll --follow-imports supervoltbatterygui.py --standalone --onefile