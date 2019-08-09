from setuptools import setup
from setuptools import find_packages


with open("requirements.txt", "r") as f:
    requirements = f.read()

requirements = requirements.split("\n")

setup(
    name='octonag',
    version="2.0.0",
    packages=find_packages('src'),
    include_package_data=True,
    package_dir={'': 'src'},
    install_requires=requirements,
    entry_points='''
        [console_scripts]
        octonag=octonag.main:main
    '''
)
