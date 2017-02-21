from setuptools import setup, find_packages

setup(
    name='pwf',
    version='0.1.0',
    description='A Python Web Framework',
    long_description='',
    url='https://github.com/victorkohler/pwf',
    author='Victor Kohler',
    author_email='victor@houseofradon.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
    ],
    keywords='pwf framework web development',
    packages=['pwf'],
    install_requires=[],
    entry_points={
        'console_scripts': [
        'pwf=pwf:main',
        ],
    },
)
