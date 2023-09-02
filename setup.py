import subprocess

dependencies = ["pygame","ffmpeg-python","youtube-dl","pytube"]

def install(package):
    try:
        subprocess.check_call(["pip","install",package,"--user"])
        print(f"Installed package {package}")
    except Exception as e:
        print(f"Error occured while installing {package}: {e}")

for package in dependencies:
    install(package)
