from distutils.core import setup
import glob
import re

##First, get version from Ungribwrapper/_version.py.  Don't important here
#as doing this in the setup.py can be problematic
VERSION_FILE='./plot_obs/_version.py'
matched = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                    open(VERSION_FILE, "rt").read(), re.M)
if matched:
    version_str = matched.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." %(VERSION_FILE))

def main():
    dist = setup(
        name = 'plot_obs',
        version = version_str,
        description  = 'A package containing scripts and libraries '+\
            'for plotting DDB from AWS and Little_r ',
        author       = 'Sijin Zhang',
        author_email = 'sijin.zhang@metservice.com',
        package_dir = {"plot_obs": "plot_obs"},
        packages = ["plot_obs"],
        scripts = glob.glob('scripts/*'),
        )

if __name__=='__main__':
    main()
