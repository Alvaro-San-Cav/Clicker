@echo off
title Autoclicker - Build EXE
echo ============================================
echo   Autoclicker - Generador de ejecutable
echo ============================================
echo.

:: Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no esta instalado o no esta en el PATH.
    pause
    exit /b 1
)

:: Instalar/actualizar dependencias
echo [1/4] Instalando dependencias...
pip install -r ..\requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] No se pudieron instalar las dependencias.
    pause
    exit /b 1
)

:: Instalar PyInstaller
echo [2/4] Instalando PyInstaller...
pip install pyinstaller>=6.0.0 --quiet
if errorlevel 1 (
    echo [ERROR] No se pudo instalar PyInstaller.
    pause
    exit /b 1
)

:: Compilar
echo [3/4] Compilando el ejecutable...
cd ..
pyinstaller build\autoclicker.spec --noconfirm
if errorlevel 1 (
    echo [ERROR] La compilacion fallo. Revisa los errores de arriba.
    pause
    exit /b 1
)

:: Crear carpeta recordings junto al exe
if not exist "dist\recordings" mkdir "dist\recordings"

:: Resultado
echo.
echo [4/4] Listo!
echo ============================================
echo   El ejecutable esta en: dist\Autoclicker.exe
echo   Distribuye la carpeta dist\ completa.
echo ============================================
echo.
pause
pause
