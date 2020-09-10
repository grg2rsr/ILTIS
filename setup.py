from setuptools import setup, find_packages

install_requires = [
                       'scipy',
                       'pyqtgraph',
                       'pandas',
                       'matplotlib',
                       'tifffile',
                       'scikit-image'
                   ],

try:
    import PyQt5
except ModuleNotFoundError as mnfe:
    install_requires += ["PyQt5>=5.12.2,<5.13"]

config = {
    'description': 'ILTIS - an interactive labeled-trial image stack slicer',
    'use_scm_version': True,
    'setup_requires': ['setuptools_scm'],
    'install_requires': install_requires,
    'python_requires': ">=3.7",
    "packages": find_packages(),
    "package_data": {"iltis": ["graphics/icons/*.svg", "graphics/*.jpg"]},
    'scripts': [],
    "entry_points": {"console_scripts": ["iltis = iltis.Main:main"]},
    'name': 'iltis'
}

setup(**config)
