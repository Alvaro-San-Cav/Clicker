Set objShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

' Carpeta donde esta este archivo .vbs
myDir = fso.GetParentFolderName(WScript.ScriptFullName)

' Python del venv (esta en la carpeta padre)
py = fso.BuildPath(myDir, "..\.venv\Scripts\python.exe")

' Si no existe el venv, intentar con python del sistema
If Not fso.FileExists(py) Then py = "python"

' launcher.py esta en la misma carpeta
launcher = fso.BuildPath(myDir, "launcher.py")

' Cambiar directorio de trabajo al proyecto
objShell.CurrentDirectory = myDir

' Ejecutar sin ventana de consola (0 = oculta)
objShell.Run """" & py & """ """ & launcher & """", 0, False
