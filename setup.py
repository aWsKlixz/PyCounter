from setuptools import setup, find_packages
from pathlib import Path

def parse_requirements():
    requirements = Path(__file__).parent.joinpath('requirements.txt').open('r').readlines()
    return requirements

setup(
    name='pycounter',
    version='0.1',
    packages=find_packages(),
    install_requires=parse_requirements(),
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "pycounter = pycounter.main:main"
        ]
    }
)