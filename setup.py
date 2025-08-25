from setuptools import setup, find_packages

setup(
    name='pcm_startlist',
    version='0.2.1',
    author='benvneal88',
    author_email='benvneal88@example.com',
    description='A Python package for generating start lists for Pro Cycling Manager from online data.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/benvneal88/pcm_startlist',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)