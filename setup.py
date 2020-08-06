from setuptools import setup, find_packages

setup(
    name='prometheus-telegram-bot', version='1.0.0',
    description='A Telegram bot for predefined Prometheus queries',
    url='https://github.com/gjulianm/prometheus-telegram-bot',
    author='Guillermo Juli?n',
    author_email='guillermo@gjulianm.me',
    license='MIT',
    packages=find_packages(),
    entry_points={
        # You can add other entry points here.
        'console_scripts': [
            'prometheus-telegram-bot=prometheus_telegram_bot.__main__:main'
        ]
    },
    install_requires=[  # Add here requirements
        "python-telegram-bot",
        "coloredlogs",
        'requests'
    ],
    extras_require={
        'dev': [  # Requirements only needed for development
        ]
    },
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    zip_safe=False)
