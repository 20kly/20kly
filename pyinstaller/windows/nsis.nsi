
!include "MUI2.nsh"

Unicode True
Name "20K Light Years Into Space"
caption "20K Light Years Into Space Installer"

VIAddVersionKey /LANG=0 "ProductName" "20K Light Years Into Space"
VIAddVersionKey /LANG=0 "CompanyName" "Jack Whitham"
VIAddVersionKey /LANG=0 "LegalCopyright" "(C) Jack Whitham 2006-2021"
VIAddVersionKey /LANG=0 "FileDescription" "20K Light Years Into Space Installer"
VIAddVersionKey /LANG=0 "FileVersion" "1.5.0.0"
VIAddVersionKey /LANG=0 "ProductVersion" "1.5.0.0"
VIProductVersion 1.5.0.0
VIFileVersion 1.5.0.0

RequestExecutionLevel user
ShowInstDetails show
OutFile "dist\install-20kly-v1.5.0.exe"
InstallDir "$APPDATA\20kly"
SetCompressor /SOLID lzma

InstallDirRegKey HKCU "Software\20K Light Years" "Install_Dir"
LicenseData "LICENSE.txt" 


!define MUI_ICON "pyinstaller\windows\32.ico"
!insertmacro MUI_PAGE_LICENSE "LICENSE.txt"
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
 	!define MUI_FINISHPAGE_NOAUTOCLOSE
 	!define MUI_FINISHPAGE_RUN
 	!define MUI_FINISHPAGE_RUN_NOTCHECKED
 	!define MUI_FINISHPAGE_RUN_TEXT "Start the game now"
 	!define MUI_FINISHPAGE_RUN_FUNCTION "LaunchLink"
 	!define MUI_FINISHPAGE_SHOWREADME_NOTCHECKED
 	!define MUI_FINISHPAGE_SHOWREADME $INSTDIR\manual\index.html
!insertmacro MUI_PAGE_FINISH

!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES
  
!insertmacro MUI_LANGUAGE "English"




# default section start
Section ""

    SetOverwrite on 
    SetOutPath $INSTDIR
    File "dist\20kly.exe"
    File "README.txt"
    File "LICENSE.txt"
    File "THANKS.txt"
    SetOutPath $INSTDIR\manual
    File "manual\*.*"
     
    SetOutPath "$SMPROGRAMS\20K Light Years"

    SetOutPath $INSTDIR
    createShortcut "$SMPROGRAMS\20K Light Years\20K Light Years.lnk" "$INSTDIR\20kly.exe" 
    createShortcut "$SMPROGRAMS\20K Light Years\Manual.lnk" "$INSTDIR\manual\index.html"
    createShortcut "$SMPROGRAMS\20K Light Years\Uninstall.lnk" "$INSTDIR\uninstall.exe" 

    ; Write the installation path into the registry
    WriteRegStr HKCU "Software\20K Light Years" "Install_Dir" "$INSTDIR"

    ; Write the uninstall keys for Windows
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\20K Light Years" "DisplayName" "20K Light Years"
    WriteRegStr HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\20K Light Years" "UninstallString" '"$INSTDIR\uninstall.exe"'
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\20K Light Years" "NoModify" 1
    WriteRegDWORD HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\20K Light Years" "NoRepair" 1
    WriteUninstaller "$INSTDIR\uninstall.exe"

    # Clean up files from previous version if present
    SetOutPath $INSTDIR
    Delete "lightyears.20k"
    Delete "zlib1.dll"
    Delete "SDL.dll"
    Delete "SDL_ttf.dll"
    Delete "libogg-0.dll"
    Delete "libfreetype-6.dll"

    ; clean up more old files
    RMDir /R $INSTDIR\audio
    RMDir /R $INSTDIR\code
    RMDir /R $INSTDIR\data
 
# default section end
sectionEnd
 
# create a section to define what the uninstaller does.
# the section will always be named "Uninstall"
section "Uninstall"


    ; Remove registry keys
    DeleteRegKey HKCU "Software\Microsoft\Windows\CurrentVersion\Uninstall\20K Light Years"
    DeleteRegKey HKCU "Software\20K Light Years"

    ; Remove files and uninstaller
    Delete $INSTDIR\README.txt
    Delete $INSTDIR\THANKS.txt
    Delete $INSTDIR\LICENSE.txt
    Delete $INSTDIR\20kly.exe
    Delete $INSTDIR\uninstall.exe
    RMDir /R $INSTDIR\manual

    ; Remove shortcuts, if any
    Delete "$SMPROGRAMS\20K Light Years\*.lnk"

    ; Remove directories
    RMDir "$SMPROGRAMS\20K Light Years"
    RMDir "$INSTDIR" 

sectionEnd

Function LaunchLink
    ExecShell "" "$SMPROGRAMS\20K Light Years\20K Light Years.lnk"
FunctionEnd

