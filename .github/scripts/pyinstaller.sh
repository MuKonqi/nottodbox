if [ "$RUNNER_OS" == "Linux" ]; then
    sed -i "s/APP_BUILD = .*/APP_BUILD = 'AppImage'/" nottodbox/scripts/consts.py
    pyinstaller --add-data 'nottodbox/color-schemes/:nottodbox/color-schemes' --add-data 'nottodbox/LICENSE.txt:nottodbox' -F -w -n nottodbox nottodbox/__main__.py

elif [ "$RUNNER_OS" == "macOS" ]; then
    sed -i "s/APP_BUILD = .*/APP_BUILD = 'PyInstaller'/" nottodbox/scripts/consts.py
    pyinstaller --add-data 'nottodbox/color-schemes/:nottodbox/color-schemes' --add-data 'nottodbox/LICENSE.txt:nottodbox' -D -w -i share/icons/pyinstaller/io.github.mukonqi.nottodbox.icns -n nottodbox nottodbox/__main__.py
    
elif [ "$RUNNER_OS" == "Windows" ]; then
    sed -i "s/APP_BUILD = .*/APP_BUILD = 'PyInstaller'/" nottodbox/scripts/consts.py
    pyinstaller --add-data 'nottodbox/color-schemes/:nottodbox/color-schemes' --add-data 'nottodbox/LICENSE.txt:nottodbox' -F -w -i share/icons/pyinstaller/io.github.mukonqi.nottodbox.ico -n nottodbox nottodbox/__main__.py
fi