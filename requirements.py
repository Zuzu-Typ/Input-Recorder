import sys, os, subprocess

install_command = "{} -m pip install -r {}".format(
    sys.executable,
    os.environ.get("PyPI_REQUIREMENTS_PATH", os.path.realpath("requirements.txt"))
)

popen = subprocess.Popen(install_command,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE,
                         universal_newlines=True,
                         shell=True)

for stdout_line in iter(popen.stdout.readline, ""):
    if os.environ.get("PyPI_REQUIREMENTS_OUTPUT", "OFF").upper() == "ON": print(stdout_line, end="")

for stdout_line in iter(popen.stderr.readline, ""):
    if os.environ.get("PyPI_REQUIREMENTS_OUTPUT", "OFF").upper() == "ON": print(stdout_line, end="", file=sys.stderr)
    
popen.stdout.close()

popen.wait()
