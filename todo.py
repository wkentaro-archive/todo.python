#!/usr/bin/env python

try:
    import ConfigParser as configparser
except ImportError:
    import configparser
import datetime
import os
import os.path as osp
import pkg_resources
import platform
import re
import shlex
import shutil
import subprocess
import sys

import click
import six
import yaml


__author__ = 'Kentaro Wada <www.kentaro.wada@gmail.com>'
__version__ = pkg_resources.get_distribution('todo.python').version


GITHUB_URL = None
CACHE_DIR = osp.expanduser('~/.cache/todo')
CONFIG_FILE = osp.expanduser('~/.todo.python.cfg')


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
            m = re.match('^## (.*)$', line)
            section = m.groups()[0]
        elif line.startswith('- '):
            m = re.match('^- \[( |x)\] (.*)$', line)
            assert len(m.groups()) == 2
            done = m.groups()[0] == 'x'
            title = m.groups()[1]
            todos.append({
                'title': title,
                'done': done,
                'section': section,
                'detail': [],
            })
        else:
            todos[-1]['detail'].append(line)

    date = date or datetime.date.today()

    return date, todos


def render_todo(date, todos, color=False):
    date = date.strftime('# %Y-%m-%d')
    if color:
        date = click.style(date, 'green')

    content_todo = []
    for todo in todos:
        title = todo['title']
        done = todo['done']
        section = todo['section']
        detail = todo['detail']

        if section is not None:
            section = '## {:s}'.format(section)
            if color:
                section = click.style(section, 'blue')
            if section not in content_todo:
                content_todo.append('')
                content_todo.append(section)
                content_todo.append('')

        cross = 'x' if done else ' '
        if color and not done:
            title = click.style(title, underline=True)
        content_todo.append('- [{:s}] {:s}'.format(cross, title))

        if detail:
            content_todo.append('')
            content_todo.append('\n'.join(detail))
            content_todo.append('')

    content = '''\
{date}
{todo}
'''
    content = content.format(date=date, todo='\n'.join(content_todo))

    return content


def _init(remote_url=None):
    global GITHUB_URL
    config = configparser.ConfigParser()
    if osp.exists(CONFIG_FILE):
        if remote_url:
            print('Config file already exists: {:s}'.format(CONFIG_FILE))
            sys.exit(1)
        config.readfp(open(CONFIG_FILE))
        GITHUB_URL = config.get('remote', 'url')
    else:
        config.add_section('remote')
        if remote_url:
            GITHUB_URL = remote_url
        else:
            GITHUB_URL = six.moves.input('Remote Git URL?: ')
        config.set('remote', 'url', GITHUB_URL)
        config.write(open(CONFIG_FILE, 'w'))
    print('Remote URL: {:s}'.format(GITHUB_URL))


def _pull_cache_dir():
    print('Pulling from remote: {:s}'.format(GITHUB_URL))
    if not osp.exists(CACHE_DIR):
        cmd = 'git clone {url} {dir}'.format(url=GITHUB_URL, dir=CACHE_DIR)
        print('+ {cmd}'.format(cmd=cmd))
        ret = subprocess.call(shlex.split(cmd))
    else:
        cmd = 'git pull origin master'
        ret = subprocess.call(shlex.split(cmd), cwd=CACHE_DIR,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    if ret != 0:
        print('Failed to pull from remote: {:s}'.format(GITHUB_URL))


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


def _archive(push=True):
    _pull_cache_dir()

    readme_fn = osp.join(CACHE_DIR, 'README.md')
    date, todos = parse_todo(open(readme_fn).read())

    if date >= datetime.date.today():
        return

    todos_remain = []
    todos_archive = []
    for todo in todos:
        if todo['done']:
            todos_archive.append(todo)
        else:
            todos_remain.append(todo)
    del todos

    # archive
    data = []
    archive_fn = osp.join(CACHE_DIR, 'archive.yaml')
    if osp.exists(archive_fn):
        data = yaml.load(open(archive_fn))
    data.append({date.strftime('%Y-%m-%d'): todos_archive})
    print('Archiving completed TODOs to: {:s}'.format(archive_fn))
    yaml.safe_dump(data, open(archive_fn, 'w'), default_flow_style=False)

    # main
    content_remain = render_todo(datetime.date.today(), todos_remain)
    open(readme_fn, 'w').write(content_remain)

    if push:
        _push_cache_dir()


def _get_open_cmd():
    if platform.uname()[0] == 'Linux':
        return 'gnome-open'
    elif platform.uname()[0] == 'Darwin':
        return 'open'
    else:
        raise RuntimeError('Unsupported OS for open command')


# -----------------------------------------------------------------------------


@click.group(context_settings={'help_option_names': ['-h', '--help']})
@click.version_option(__version__, '-V', '--version')
def cli():
    pass


@cli.command('init', help='Initialize')
@click.argument('remote_url', required=False)
def cmd_init(remote_url):
    _init(remote_url)
    _pull_cache_dir()


@cli.command('deinit', help='Uninitialize')
def cmd_deinit():
    if osp.exists(CONFIG_FILE):
        prompt = 'Can I remove config file "{:s}"? [y/n]: '.format(CONFIG_FILE)
        if click.confirm(prompt):
            os.remove(CONFIG_FILE)

    if osp.exists(CACHE_DIR):
        prompt = 'Can I remove cache dir "{:s}"? [y/n]: '.format(CACHE_DIR)
        if click.confirm(prompt):
            shutil.rmtree(CACHE_DIR)


@cli.command('view', help='Show todo')
def cmd_view():
    _init()
    _archive()
    _view()


def _view():
    readme_fn = osp.join(CACHE_DIR, 'README.md')
    date, todos = parse_todo(open(readme_fn).read())
    content = render_todo(date, todos, color=True)
    if six.PY2:
        content = content.decode('utf-8')
    click.echo_via_pager(content, color=True)


@cli.command('edit', help='Edit todo')
def cmd_edit():
    _init()
    _archive(push=False)
    readme_fn = osp.join(CACHE_DIR, 'README.md')
    date, todos = parse_todo(open(readme_fn).read())
    content = render_todo(date, todos)
    with open(readme_fn, 'w') as f:
        f.write(content)

    editor = os.environ.get('EDITOR', 'vim')
    cmd = '{editor} {fname}'.format(editor=editor, fname=readme_fn)
    subprocess.call(cmd, shell=True)
    _push_cache_dir()

    _view()


@cli.command('open', help='Open Github')
def cmd_open():
    _init()
    _archive()
    readme_url = osp.join(GITHUB_URL.rstrip('.git'), 'blob/master/README.md')
    readme_url += datetime.date.today().strftime('#%Y-%m-%d')
    cmd = '{cmd} {url}'.format(cmd=_get_open_cmd(), url=readme_url)
    print('Opening {:s}'.format(readme_url))
    subprocess.call(cmd, shell=True)


if __name__ == '__main__':
    cli()
