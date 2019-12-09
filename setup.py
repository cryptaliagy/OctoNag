from setuptools import setup
from setuptools import find_packages


with open("requirements.txt", "r") as f:
    requirements = f.read()

with open('README.md', 'r') as f:
    long_description = f.read()

requirements = requirements.split("\n")

setup(
    name='octonag',
    version="2.0.0",
    author='Natalia Maximo',
    email='iam@natalia.dev',
    description='A slack bot to remind developers of open PRs',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/taliamax/OctoNag',
    packages=find_packages('src'),
    include_package_data=True,
    package_dir={'': 'src'},
    install_requires=requirements,
    python_requires='>=3.5',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
    ],
    entry_points='''
        [console_scripts]
        octonag=octonag.main:main
    '''
)
