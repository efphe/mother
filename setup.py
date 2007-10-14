#!/usr/bin/env python

from distutils.core import setup

__version__ = '0.6.2'

mo_desc="""Mother is a Python Orm oriented to introspection and self autoadaption."""

mo_long_desc="""\
Mother is a python module that hides SQL syntax and gives 
you a set of intelligent classes and methods. With `intelligent` 
we mean the capability of self-adaption, understanding various 
situations.
Mother could be considered as a Object Relational Mapper with a 
strong introspection. 
In fact, configuration files, tables, fields and keys declarations 
are not needed, because Mother knows the database structure herself.
Mother works with PostgreSQL and SQlite.
BSD License."""

mo_classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Database',
        'Topic :: Software Development :: Libraries :: Python Modules'
]

setup(
    name='Mother',
    version= __version__,
    author='Federico Tomassini aka efphe',
    author_email='efphe@dbmother.org',
    maintainer= 'Federico Tomassini aka efphe',
    maintainer_email='efphe@dbmother.org',
    url='http://www.dbmother.org',
    packages=['mother', 'mother.plugins'],
    scripts= ['mothermapper'],
    classifiers= mo_classifiers,
    description= mo_desc,
    long_description= mo_long_desc,
    license= "BSD",
    platforms = ["any"],
)
