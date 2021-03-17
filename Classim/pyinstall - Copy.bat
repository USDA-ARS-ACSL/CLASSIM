pyinstaller --onefile ^
--add-data \\images\\*;images ^
--paths C:\\Users\dennis.timlin\\AppData\\Local\\conda\\conda\\envs\\CondaInterface\\Library\\bin ^
--add-binary \\helper\\module_soiltriangle.pyd;helper ^
 crop_int.spec