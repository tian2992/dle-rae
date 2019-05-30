import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='rae',
    version='0.0.9',
    author='Ángel Carmona Galán',
    author_email='angel@angelcarmona.com',
    description='Consulta los diccionarios de la RAE',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://www.angelcarmona.com',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
    ],
    install_requires=[
        "requests",
        "bs4",
        "lxml",
    ],
)
