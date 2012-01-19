from setuptools import setup, find_packages
import os

version = '1.0'

setup(name='experimental.shoppingbehavior',
    version=version,
    description="Plone behavior to support price assignment on dexterity content",
    long_description=open("README.txt").read() + "\n" +
                   open(os.path.join("docs", "HISTORY.txt")).read(),
    # Get more strings from
    # http://pypi.python.org/pypi?:action=list_classifiers
    classifiers=[
    "Framework :: Plone",
    "Programming Language :: Python",
    ],
    keywords='',
    author='Jesse Snyder',
    author_email='jsnyder@wesleyan.edu',
    url='https://github.com/jessesnyder/experimental.shoppingbehavior',
    license='GPL',
    packages=find_packages(exclude=['ez_setup']),
    namespace_packages=['experimental'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
      'setuptools',
      'Products.CMFPlone',
    ],
    extras_require={
      'test': ['plone.app.testing', 'mock']
    },
    entry_points="""
    # -*- Entry points: -*-

    [z3c.autoinclude.plugin]
    target = plone
    """,
    # setup_requires=["PasteScript"],
    # paster_plugins=["ZopeSkel"],
    )
