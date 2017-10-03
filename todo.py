#!/usr/bin/env python

import ConfigParser
import datetime
import os
import os.path as osp
import re
import shlex
import subprocess
import sys

import click


__author__ = 'Kentaro Wada <www.kentaro.wada@gmail.com>'
__version__ = '0.0.1'


GITHUB_URL = None
CACHE_DIR = osp.expanduser('~/.cache/todo')
CONFIG_FILE = osp.expanduser('~/.todo.py.cfg')


# -----------------------------------------------------------------------------


def parse_todo(content):
    date = None
    section = None
    todos = []
    for line in content.splitlines():
        line = line.rstrip()
        if not line:
            continue

        if line.startswith('# '):
            if date is None:
                date = datetime.datetime.strptime(line, '# %Y-%m-%d')
                date = datetime.date(date.year, date.month, date.day)
            else:
                raise ValueError
        elif line.startswith('## '):
            section = line  # todo section
        elif line.startswith('- '):
            m = re.match('^- \[( |x)\] (.*)$', line)
            assert len(m.groups()) == 2
            done = m.groups()[0] == 'x'
            text = m.groups()[1]
            todos.append([text, done, section, ''])
        else:
            todos[-1][3] += line  # detail

    date = date or datetime.date.today()

    return date, todos


def render_todo(date, todos):
    todo = []
    for text, done, section, detail in todos:
        if section is not None:
            if section not in todo:
                todo.append('')
                todo.append(section)
                todo.append('')
        cross = 'x' if done else ' '
        todo.append('- [{:s}] {:s}'.format(cross, text))
        if detail:
            todo.append('')
            todo.append(detail)
            todo.append('')
    todo = '\n'.join(todo)

    content = '''\
# {date}
{todo}
'''
    content = content.format(date=date.strftime('%Y-%m-%d'), todo=todo)

    return content


def _init(remote_url=None):
    global GITHUB_URL
    config = ConfigParser.ConfigParser()
    if osp.exists(CONFIG_FILE):
        if remote_url:
            print('Config file already exists: {:s}'.format(CONFIG_FILE))
            sys.exit(1)
        config.readfp(open(CONFIG_FILE))
        GITHUB_URL = config.get('remote', 'url')
    else:
        config.add_section('remote')
        if not remote_url:
            GITHUB_URL = raw_input('Remote Git URL?: ')
        config.set('remote', 'url', GITHUB_URL)
        config.write(open(CONFIG_FILE, 'w'))
    print('Remote URL: {:s}'.format(GITHUB_URL))


def _pull_cache_dir():
    print('Pulling from remote: {:s}'.format(GITHUB_URL))
    if not osp.exists(CACHE_DIR):
        cmd = 'git clone {url} {dir}'.format(url=GITHUB_URL, dir=CACHE_DIR)
        print('+ {cmd}'.format(cmd=cmd))
        subprocess.call(shlex.split(cmd))
    else:
        cmd = 'git pull origin master'
        subprocess.call(shlex.split(cmd), cwd=CACHE_DIR,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def _push_cache_dir():
    print('Pushing to remote: {:s}'.format(GITHUB_URL))
    assert osp.exists(CACHE_DIR)
    cmds = [
        'git add .',
        'git commit -m "Update todo"',
        'git push origin master',
    ]
    for cmd in cmds:
        ret = subprocess.call(
            shlex.split(cmd), cwd=CACHE_DIR,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if ret != 0:
            break


def _archive():
    _pull_cache_dir()

    readme_fn = osp.join(CACHE_DIR, 'README.md')
    date, todos = parse_todo(open(readme_fn).read())

    if date >= datetime.date.today():
        return

    todos_remain = []
    todos_archive = []
    for todo in todos[:]:
        text, done, section, detail = todo
        if done:
            todos_archive.append(todo)
        else:
            todos_remain.append(todo)
    content_archive = render_todo(date, todos_archive)

    if not content_archive:
        return

    # archive
    archive_dir = osp.join(CACHE_DIR, date.strftime('%Y'))
    if not osp.exists(archive_dir):
        os.makedirs(archive_dir)
    archive_fn = osp.join(archive_dir, date.strftime('%Y-%m.md'))
    print('Archiving completed TODO to: {:s}'.format(archive_fn))
    open(archive_fn, 'a').write(content_archive)

    # main
    content_remain = render_todo(datetime.date.today(), todos_remain)
    open(readme_fn, 'w').write(content_remain)

    _push_cache_dir()


# -----------------------------------------------------------------------------


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(__version__, '-V', '--version')
def cli():
    pass


@cli.command('init', help='Initialize')
@click.argument('remote_url', required=False)
def cmd_init(remote_url):
    _init(remote_url)


@cli.command('show', help='Show todo')
def cmd_show():
    _init()
    _archive()
    readme_fn = osp.join(CACHE_DIR, 'README.md')
    date, todos = parse_todo(open(readme_fn).read())
    content = render_todo(date, todos)
    print(content)


@cli.command('edit', help='Edit todo')
def cmd_edit():
    _init()
    _archive()
    readme_fn = osp.join(CACHE_DIR, 'README.md')
    date, todos = parse_todo(open(readme_fn).read())
    content = render_todo(date, todos)
    with open(readme_fn, 'w') as f:
        f.write(content)

    cmd = 'vim +{lineno} {fname}'.format(lineno=len(content.splitlines()),
                                         fname=readme_fn)
    subprocess.call(cmd, shell=True)
    _push_cache_dir()


@cli.command('open', help='Open Github')
def cmd_open():
    _init()
    _archive()
    readme_url = osp.join(osp.splitext(GITHUB_URL)[0], 'blob/master/README.md')
    cmd = 'open {url}'.format(url=readme_url)
    print('Opening {:s}'.format(readme_url))
    subprocess.call(cmd, shell=True)


if __name__ == '__main__':
    cli()
