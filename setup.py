try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'ILTIS - an interactive labeled-trial image stack slicer',
    'author': 'Georg Raiser',
    'url': 'https://github.com/grg2rsr/ILTIS',
    'download_url': 'https://github.com/grg2rsr/ILTIS.git.',
    'author_email': 'grg2rsr@gmail.com.',
    'version': '0.1dev',
    'install_requires': ['scipy','pyqtgraph','nose'],
    'packages': ['ILTIS'],
    'scripts': [],
    'name': 'ILTIS'
}

setup(**config)
