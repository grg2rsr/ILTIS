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
    "package_data": {"iltis": ["graphics/icons/*.svg", "graphics/*.jpg"]},
    'scripts': [],
    "entry_points": {"console_scripts": ["iltis = iltis.Main:main"]},
    'name': 'iltis'
}

setup(**config)
