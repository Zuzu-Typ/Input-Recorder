import sys, os, subprocess, re

if "py" in os.path.basename(sys.executable):
    requirements_file_path = os.environ.get("PyPI_REQUIREMENTS_PATH", os.path.realpath("requirements.txt"))

    if not os.path.exists(requirements_file_path) or not os.path.isfile(requirements_file_path):
        raise IOError("No requirements file was found at '{}'".format(requirements_file_path))

    requirements_file = open(requirements_file_path)

    requirements_file_content = requirements_file.read()

    requirements_file.close()

    requirement_pattern = re.compile("^\\s*([A-z0-9.\\-_]+)\\s*(?:(==|<=|>=)\\s*((?:[0-9]+!)?[0-9]+(?:\\.[0-9]+)*(?:(?:a|b|rc)[0-9]+)?(?:\\.post[0-9]+)?(?:\\.dev[0-9]+)?)\\s*)?$", re.MULTILINE)

    requirements = requirement_pattern.findall(requirements_file_content)

    site_packages_folder = None

    for folder in sys.path:
        if folder.endswith("site-packages"):
            site_packages_folder = folder
            break

    if not site_packages_folder:
        raise IOError("site-packages folder not found")

    site_packages_dist_infos = tuple(filter(lambda x: x.endswith(".dist-info"), os.listdir(site_packages_folder)))

    installed_packages = {}

    for dist_info in site_packages_dist_infos:
        dist_info = dist_info[:-len(".dist-info")]
        dash_pos = dist_info.rindex("-")
        version = dist_info[dash_pos + 1 : ]
        package_name = dist_info[:dash_pos]
        
        installed_packages[package_name] = version

    need_to_run = False

    for package_name, operator, version in requirements:
        if not package_name in installed_packages or (operator and version and installed_packages[package_name] != version):
            need_to_run = True
            break

    if need_to_run:
        install_command = "{} -m pip install -r {}".format(
            sys.executable,
            requirements_file_path
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
