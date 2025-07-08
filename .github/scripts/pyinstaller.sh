python3 .github/scripts/consts.py

if [ "$RUNNER_OS" == "Linux" ]; then
    pyinstaller --add-data 'nottodbox/color-schemes/:nottodbox/color-schemes' --add-data 'nottodbox/LICENSE.txt:nottodbox' -F -w -n nottodbox nottodbox/__main__.py
elif [ "$RUNNER_OS" == "macOS" ]; then
    pyinstaller --add-data 'nottodbox/color-schemes/:nottodbox/color-schemes' --add-data 'nottodbox/LICENSE.txt:nottodbox' -D -w -i share/icons/pyinstaller/io.github.mukonqi.nottodbox.icns -n nottodbox nottodbox/__main__.py 
elif [ "$RUNNER_OS" == "Windows" ]; then
    pyinstaller --add-data 'nottodbox/color-schemes/:nottodbox/color-schemes' --add-data 'nottodbox/LICENSE.txt:nottodbox' -F -w -i share/icons/pyinstaller/io.github.mukonqi.nottodbox.ico -n nottodbox nottodbox/__main__.py
fi