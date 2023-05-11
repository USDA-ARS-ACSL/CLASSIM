import os
import winreg as wrg

def getClassimDir():
    # Check where classim is installed
    # Store location of HKEY_CURRENT_USER
    location = wrg.HKEY_CURRENT_USER
    # Find path for documents
    keyPath = wrg.OpenKeyEx(location,r'SOFTWARE\Microsoft\Windows\CurrentVersion\Explorer\User Shell Folders',0,wrg.KEY_READ)
    # Query keyPath
    dirPath, reg = wrg.QueryValueEx(keyPath,r'Personal')
    if "OneDrive" in dirPath:
        classimDir = dirPath+'\\classim'
    else:
        envPathKey = dirPath.split('\\')
        classimDir = os.getenv(envPathKey[0].replace('%',''))+'\\'+'\\'.join(envPathKey[1:])+'\\classim'

    if not os.path.exists(classimDir):
        messageUserInfo(classimDir+' folder with databases and programs is missing.  Please check your setup or ontact the developers at ars-classim-help@usda.gov.')
    return classimDir
