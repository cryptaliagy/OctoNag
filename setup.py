from setuptools import setup


setup(
    name='slack-pull-reminders',
    py_modules=['pr_reminders'],
    install_requires=[
        'requests==2.21.0',
        'github3.py==1.0.0a4'
    ],
    entry_points='''
        [console_scripts]
        pr_reminders=pr_reminders:cli
    '''
)