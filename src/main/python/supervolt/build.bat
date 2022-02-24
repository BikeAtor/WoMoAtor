echo on
pyinstaller --noconfirm --onedir --console --add-data "../pic_free;pic_free/" --add-binary "windows-dll/libcairo-2.dll;."  "supervoltbatterygui.py"