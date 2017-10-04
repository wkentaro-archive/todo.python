#!/usr/bin/env python

import os
import platform
import subprocess
import sys

from setuptools import setup


version = '0.2.2'


def get_data_files():

    def get_completion_install_location(shell):
        uname = platform.uname()[0]
        is_root = (os.geteuid() == 0)
        prefix = ''
        if is_root:
            # this is system install
            if uname == 'Linux' and shell == 'bash':
                prefix = '/'
            elif uname == 'Linux' and shell == 'zsh':
                prefix = '/usr/local'
            elif uname == 'Darwin' and shell == 'bash':
                prefix = '/'
            elif uname == 'Darwin' and shell == 'zsh':
                prefix = '/usr'
        if shell == 'bash':
            location = os.path.join(prefix, 'etc/bash_completion.d')
        elif shell == 'zsh':
            location = os.path.join(prefix, 'share/zsh/site-functions')
        else:
            raise ValueError('unsupported shell: {0}'.format(shell))
        return location

    loc = {'bash': get_completion_install_location(shell='bash'),
           'zsh': get_completion_install_location(shell='zsh')}
    files = dict(bash=['completion/todo-completion.bash'],
                 zsh=['completion/todo-completion.bash',
                      'completion/_todo'])
    data_files = []
    data_files.append((loc['bash'], files['bash']))
    data_files.append((loc['zsh'], files['zsh']))
    return data_files


# publish helper
if sys.argv[-1] == 'release':
    for cmd in [
            'python setup.py sdist',
            'twine upload dist/todo.python-%s.tar.gz' % version,
            'git tag %s' % version,
            'git push origin master --tags',
            ]:
        subprocess.check_call(cmd, shell=True)
    sys.exit(0)

setup(
    name='todo.python',
    version=version,
    packages=[''],
    description='Manage todo on git repo.',
    long_description=open('README.md').read(),
    author='Kentaro Wada',
    author_email='www.kentaro.wada@gmail.com',
    url='http://github.com/wkentaro/todo.python',
    install_requires=open('requirements.txt').readlines(),
    license='MIT',
    keywords='utility',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX',
        'Topic :: Internet :: WWW/HTTP',
    ],
    entry_points={'console_scripts': ['todo=todo:cli']},
    data_files=get_data_files(),
)
