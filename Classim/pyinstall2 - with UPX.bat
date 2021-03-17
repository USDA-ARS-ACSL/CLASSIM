pyinstaller -y --onefile ^
--paths "%userprofile%\AppData\Local\conda\conda\envs\CondaInterface\Library\bin" ^
--upx-dir="%userprofile%\Source\Workspaces\ModelInterface\UPX\upx-3.96-win64"  --upx-exclude python36.dll --upx-exclude vcruntime140.dll^
 crop_int.spec

# produces an executable but has lots of missing modules