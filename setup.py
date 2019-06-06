from setuptools import setup, find_packages

config = {
    'description': 'ILTIS - an interactive labeled-trial image stack slicer',
    'use_scm_version': True,
    'setup_requires': ['setuptools_scm'],
    'install_requires': ['scipy',
                         'pyqtgraph',
                         'pandas',
                         'matplotlib',
                         'PyQt5>=5.11.2',
                         'tifffile'],
    'python_requires': ">=3.7",
    "packages": find_packages(),
    "package_data": {"iltis2": ["graphics/icons/*.svg", "graphics/*.jpg"]},
    'scripts': [],
    "entry_points": {"console_scripts": ["iltis = iltis2.Main:main"]},
    'name': 'iltis2'
}

setup(**config)
