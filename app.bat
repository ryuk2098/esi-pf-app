@echo off
REM Minimize the batch window (suppress any output)
powershell -NoProfile -Command ^
  "& { $h = Get-Process -Id $PID; $sig = '[DllImport(\"user32.dll\")] public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);'; $t = Add-Type -MemberDefinition $sig -Name Win32ShowWindow -Namespace Win32Functions -PassThru; $null = $t::ShowWindow($h.MainWindowHandle, 6) }"

cd /d "D:\projects\papa\esi pf"
call ".venv\Scripts\activate.bat"
streamlit run app.py
