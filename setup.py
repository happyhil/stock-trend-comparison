from setuptools import setup, find_packages

setup(
    name='stock-trend-comparison',
    version='0.1.1',
    description='Python package used to compare stock trend performances',
    author='Simon Vreugdenhil',
    author_email='simon@simonvreugdenhil.com',
    packages=find_packages(),
    install_requires=[
        'numpy==1.20.3',
        'PyYAML==5.4.1',
        'requests==2.25.1',
    ],
    entry_points={
        'console_scripts': ['run-stock-comparison=src.cli:main']
    },
)
