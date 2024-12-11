from cx_Freeze import setup, Executable
import sys

base = None

target = Executable(
    script="app.py",
    icon="icon.ico",
    base=base
)

setup(
    name="CYCU-Auto-Survey",
    version="1.1",
    description="cycu-auto-survey-app",
    author="MO7YW4NG",
    options={'bdist_msi': {'initial_target_dir': r'[DesktopFolder]\\CYCU-Auto-Survey'},'bdist_mac': {'initial_target_dir': r'[DesktopFolder]\\CYCU-Auto-Survey'}},
    executables=[target],
)

options={
    'build_exe': {
        'packages': ['requests','json','getpass','os'],
        'include_files': ['icon.ico']
    }
}