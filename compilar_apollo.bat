@echo off
echo ========================================================
echo        COMPILADOR DO APOLLO STUDIO (VERSAO DESKTOP)
echo ========================================================
echo.
echo Este script ira criar o executavel do Apollo Studio.
echo Para isso, certifique-se de que o PyInstaller esta instalado:
echo pip install pyinstaller
echo.
pause

rem O pyinstaller empacota o app. 
rem --noconsole oculta a tela preta do cmd (importante para visual profissional)
rem --icon define o icone do executavel
rem --add-data inclui o config.json, a logo e outras dependencias ocultas

pyinstaller --noconfirm --onedir --windowed --icon "icon.ico" ^
    --add-data "apollo_logo_padrao.png;." ^
    --add-data "icon.ico;." ^
    --add-data "web_ui;web_ui/" ^
    "apollo_studio.py"

echo.
echo Compilacao concluida! 
echo O seu produto final (o ApolloStudio.exe) esta dentro da pasta 'dist/apollo_studio'.
echo Copie a pasta 'bin' contendo o ffmpeg.exe para dentro da pasta 'dist/apollo_studio' para finalizar o pacote!
pause
