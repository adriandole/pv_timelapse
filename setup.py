from setuptools import setup, find_packages

setup(
    name='pv_timelapse',
    version='1.0.2a',
    packages=find_packages(),
    author='Donald Dole',
    author_email='donald.dole@nist.gov',
    license='CC0',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Science/Research',
        'Topic :: Scientific/Engineering :: Visualization',
        'Topic :: Multimedia :: Video',
        'License :: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication',
        'Programming Language :: Python :: 3 :: Only'
    ],
    description='Generates time-lapse videos from sky camera images.',
    python_requires='>=3.5',
    install_requires=['numpy', 'pandas', 'scikit-image', 'sk-video',
                      'matplotlib', 'mysqlclient', 'pvlib', 'ephem', 'scipy'],
    entry_points={
        'console_scripts': ['pv_timelapse=pv_timelapse:main']
    }
)
