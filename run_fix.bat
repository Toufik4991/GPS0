@echo off
cd /d "C:\Users\Jules\Desktop\GPS0"
python fix_n2.py > fix_n2_out.txt 2>&1
type fix_n2_out.txt
pause
