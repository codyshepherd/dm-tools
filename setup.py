"""
dm-tools: Command-line tools for the lazy DM
"""
import os
from setuptools import find_packages, setup

reqs_path = os.path.join(os.path.dirname(__file__), 'requirements.txt')

with open(reqs_path, 'r') as req_file:
    dependencies = req_file.readlines()

setup(
    name='dm-tools',
    version='0.1.0',
    license='MIT',
    author='Cody Shepherd',
    author_email='cody.shepherd@gmail.com',
    description='Command-line tools for the lazy DM.',
    long_description=__doc__,
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    python_requires='>=3.6',
    install_requires=dependencies,
    entry_points={
        'console_scripts': [
            'live-game = live_game.live_game:start',
            'plebs = plebs.plebs:plebs',
            'pockets = plebs.pockets:pockets',
        ],
    },
)
