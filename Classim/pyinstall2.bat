pyinstaller -y --onefile ^
--paths "%userprofile%\AppData\Local\conda\conda\envs\CondaInterface\Library\bin" ^
--upx-dir="%userprofile%\Source\Workspaces\ModelInterface\UPX\upx-3.96-win64"  ^
 crop_int.spec