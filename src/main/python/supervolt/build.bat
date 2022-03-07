echo on
pyinstaller --noconfirm --onedir --console^
 --add-data "windows-bin/pic_free;pic_free/"^
 --add-data "windows-bin/config.json;."^
 --add-binary "windows-dll/libcairo-2.dll;."^
 supervoltbatterygui.py
cd dist
jar -cMf ..\windows-bin\supervoltbatterygui.zip supervoltbatterygui
cd ..
REM copy .\dist\supervoltbatterygui.zip .\windows-bin\

REM pyinstaller --onefile --noconfirm --console --add-data "../pic_free;./pic_free" --add-binary "windows-dll/libcairo-2.dll;."  "supervoltbatterygui.py"
REM VIRUS found pyinstaller --onefile --clean --noconfirm --console --add-binary "windows-dll/libcairo-2.dll;."  "supervoltbatterygui.py"
REM copy .\dist\supervoltbatterygui.exe .\windows-bin\


REM nuitka does not work (yet)
REM python.exe -m nuitka --mingw64 --enable-plugin=tk-inter .\supervoltbatterygui.py --standalone --onefile

REM nuitka --mingw64 --enable-plugin=tk-inter --include-plugin-directory=windows-dll --follow-imports supervoltbatterygui.py --standalone --onefile

PAUSE