#!/usr/bin/env python3

from distutils.core import setup

import recolonyzer

_DESCRIPTION = """\
"""

setup(
    name='recolonyzer',
    version=recolonyzer.__version__,
    description='A very nice short description',
    author='Judith Bergada',
    author_email='judithbergada@gmail.com',
    url='https://github.com/judithbergada/recolonyzer',
    packages=['recolonyzer'],
    long_description=_DESCRIPTION,
    license='MIT',
    scripts=['recolonyzer/recolonyzer'],
    python_requires='>3.4, <4',
    install_requires=[
        'numpy>=1.13.0',
        'opencv-python>=4.0.0.21',
        'pandas>=0.21.1',
        'scipy>=1.0.0',
        'tqdm>=4.28.0',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Scientific/Engineering :: Bio-Informatics',
        'Topic :: Scientific/Engineering :: Image Recognition',
    ],
)
