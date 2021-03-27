
import time
from lib20k.primitives import VERSION

VERSION3 = '{}.{}.{}'.format(*VERSION)
VERSION4 = VERSION3 + ".0"
VERSION4T = tuple(list(VERSION) + [0])
YEAR = str(time.localtime().tm_year)

open("version.nsh", "wt").write(f"""
!define VERSION4 {VERSION4}
!define VERSION3 {VERSION3}
!define YEAR {YEAR}

VIAddVersionKey /LANG=0 "ProductName" "20K Light Years Into Space"
VIAddVersionKey /LANG=0 "CompanyName" "Jack Whitham"
VIAddVersionKey /LANG=0 "FileDescription" "20K Light Years Into Space Installer"
VIAddVersionKey /LANG=0 "LegalCopyright" "(C) Jack Whitham 2006-{YEAR}"
VIAddVersionKey /LANG=0 "FileVersion" "{VERSION4}"
VIAddVersionKey /LANG=0 "ProductVersion" "{VERSION4}"
VIProductVersion {VERSION4}
VIFileVersion {VERSION4}
OutFile "dist\install-20kly-v{VERSION3}.exe"

""")

open("version.txt", "wt", encoding="utf-8").write(f"""# UTF-8
#
# For more details about fixed file info 'ffi' see:
# http://msdn.microsoft.com/en-us/library/ms646997.aspx
VSVersionInfo(
  ffi=FixedFileInfo(
    # filevers and prodvers should be always a tuple with four items: (1, 2, 3, 4)
    # Set not needed items to zero 0.
    filevers={VERSION4T},
    prodvers={VERSION4T},
    # Contains a bitmask that specifies the valid bits 'flags'r
    mask=0x0,
    # Contains a bitmask that specifies the Boolean attributes of the file.
    flags=0x0,
    # The operating system for which this file was designed.
    # 0x4 - NT and there is no need to change it.
    OS=0x4,
    # The general type of file.
    # 0x1 - the file is an application.
    fileType=0x1,
    # The function of the file.
    # 0x0 - the function is not defined for this fileType
    subtype=0x0,
    # Creation date and time stamp.
    date=(0, 0)
    ),
  kids=[
    StringFileInfo(
      [
      StringTable(
        u'000004b0',
        [StringStruct(u'CompanyName', u'Jack Whitham'),
        StringStruct(u'FileDescription', u'20K Light Years Into Space'),
        StringStruct(u'FileVersion', u'{VERSION4}'),
        StringStruct(u'LegalCopyright', u'(C) Jack Whitham 2006-{YEAR}'),
        StringStruct(u'ProductName', u'20K Light Years Into Space'),
        StringStruct(u'ProductVersion', u'{VERSION4}')])
      ]), 
    VarFileInfo([VarStruct(u'Translation', [0, 1200])])
  ]
)
""")
