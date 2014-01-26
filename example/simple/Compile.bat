@echo off

call Cleanup.bat
python ../../twee2sam.py tw/Simple.txt sam
if errorlevel 1 goto :twee2sam_error

cd sam
call Compile.bat
cd..

goto end

:twee2sam_error

echo twee2sam returned an error
pause

:end