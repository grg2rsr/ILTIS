from setuptools import setup, find_packages

config = {
    'description': 'ILTIS - an interactive labeled-trial image stack slicer',
    'use_scm_version': True,
    'setup_requires': ['setuptools_scm'],
    'install_requires': ['scipy',
                         'pyqtgraph',
                         'nose',
                         'pandas',
                         'matplotlib',
                         'PyQt5',
                         'tifffile'],
    'python_requires': ">=3.7",
    "packages": find_packages(),
    'scripts': [],
    "entry_points": {"console_scripts": ["iltis = iltis2.Main:main"]},
    'name': 'ILTIS2'
}

setup(**config)
