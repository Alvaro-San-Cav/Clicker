' Script para crear un acceso directo a Autoclicker en el escritorio con su icono
Set objShell = CreateObject("WScript.Shell")
Set fso = CreateObject("Scripting.FileSystemObject")

strDesktop = objShell.SpecialFolders("Desktop")
myDir = fso.GetParentFolderName(WScript.ScriptFullName)

strShortcutPath = fso.BuildPath(strDesktop, "Autoclicker.lnk")
Set objShortcut = objShell.CreateShortcut(strShortcutPath)

objShortcut.TargetPath = fso.BuildPath(myDir, "Autoclicker.vbs")
objShortcut.WorkingDirectory = myDir
objShortcut.IconLocation = fso.BuildPath(myDir, "assets/iconoclick.ico")
objShortcut.Description = "Lanzador de Autoclicker"
objShortcut.Save

WScript.Echo "Acceso directo creado con exito en el escritorio con el icono personalizado."
