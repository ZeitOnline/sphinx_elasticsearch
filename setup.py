from setuptools import setup, find_packages


setup(
    name='sphinx_elasticsearch',
    version='1.0.0',
    author='Zeit Online',
    author_email='zon-backend@zeit.de',
    url='https://github.com/zeitonline/sphinx_elasticsearch',
    description="Indexes documentation build via Sphinx into elasticsearch",
    long_description='\n\n'.join(
        open(x).read() for x in ['README.rst', 'CHANGES.txt']),
    packages=find_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    license='BSD',
    classifiers=[
        'Programming Language :: Python :: 3',
    ],
    install_requires=[
        'click',
        'elasticsearch',
        'pyquery',
        'setuptools',
    ],
    extras_require={'test': [
        'pytest',
    ]},
    entry_points={
        'console_scripts': [
            'sphinx-elasticsearch = sphinx_elasticsearch.index:cli',
        ]
    }
)
