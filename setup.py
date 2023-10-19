# -*- coding: utf-8 -*-


from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

setup(
    name='festo-cpx-io',
    description='Library to control and access festo CPX modules',
    long_description=readme,
    long_description_content_type="text/markdown",
    author='Martin Wiesner, Elias Rosch',
    author_email='martin.wiesner@festo.com, elias.rosch@festo.com',
    url='https://gitlab.festo.company/maws/festo-cpx-io',
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    use_scm_version=True,
    python_requires=">= 3.10",
    setup_requires=["setuptools_scm"],
    install_requires=['pymodbus>=3.0.0,<4.0.0', 'rich'],
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    entry_points={
        'console_scripts': ['festo-cpx-io = cpx_io.cli.cli:main']
    }
)