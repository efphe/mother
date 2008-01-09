#!/usr/bin/env python

from distutils.core import setup


__version__ = '0.6.4-r3'

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
    author_email='efphe@freaknet.org',
    maintainer= 'Federico Tomassini aka efphe',
    maintainer_email='efphe@freaknet.org',
    url='http://www.dbmother.org',
    packages=['mother', 'mother.plugins'],
    scripts= ['mothermapper'],
    classifiers= mo_classifiers,
    description= mo_desc,
    long_description= mo_long_desc,
    license= "BSD",
    platforms = ["any"],
)

from os import name as _osname
if _osname == 'posix':
    import shutil
    try:
        os.system('mkdir -p /usr/local/share/man/man1/')
        shutil.copy('doc/mothermapper.1', '/usr/local/share/man/man1/')
        print ' \033[0;32m*\033[0m Mothermapper Man Page installed.'
    except Exception, ss:
        print " \033[0;31m*\033[0m ERROR installing mothermapper man page:", str(ss)

