from setuptools import setup, find_packages

setup(
    name='pv_timelapse',
    version='1.0a',
    packages=find_packages(),
    author='Donald Dole',
    author_email='donald.dole@nist.gov',
    description='Generates time-lapse videos from sky camera images.', install_requires=['numpy', 'pandas',
                                                                                         'scikit-image', 'sk-video']
)
