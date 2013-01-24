try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='whoops',
    version='0.1.0',
    description='WebHDFS client',
    long_description=open('README.rst').read(),
    author='Miki Tebeka',
    author_email='miki.tebeka@gmail.com',
    license='MIT',
    url='https://bitbucket.org/tebeka/whoops',
    packages=['whoops'],
    entry_points={
        'console_scripts': [
            'whoops = whoops.__main__:main',
        ]
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=['requests'],
)
