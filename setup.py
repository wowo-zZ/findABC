from setuptools import setup, find_packages

setup(
    name='findabc',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
    ],
    entry_points={
        'console_scripts': [
            'perf=src.cli.commands:cli',
        ],
    },
    python_requires='>=3.6',
    author='Your Name',
    author_email='your.email@example.com',
    description='员工绩效跟踪系统',
    keywords='performance tracking, employee management',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'Topic :: Office/Business :: Human Resources',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
)