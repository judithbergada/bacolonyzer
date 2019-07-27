#!/usr/bin/env python3

from distutils.core import setup

import recolonyzer

setup(
    name='recolonyzer',
    version=recolonyzer.__version__,
    description='A very nice short description',
    author='Judith Bergada',
    author_email='judithbergada@gmail.com',
    url='https://github.com/judithbergada/recolonyzer',
    packages=['recolonyzer'],
    long_description=open('README.md').read(),
    scripts=['recolonyzer/recolonyzer'],
    python_requires='>3.4, <4',
    install_requires=[
        'numpy>=1.13.0',
        'opencv-python>=4.0.0.21',
        'pandas>=0.21.1',
        'scipy>=1.0.0',
        'tqdm>=4.28.0',
    ],
)
