import os
import shutil

source = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\COPIA BACKUP TUTORIAL DAS COISAS\APOLLO_EDIT_WEB 14\temp_restore\config_manager.py'
dest = r'E:\MEUS PROGRAMAS\APOLLO_EDIT_WEB\backend\services\settings_manager.py'
shutil.copy2(source, dest)
print("settings_manager.py created")
