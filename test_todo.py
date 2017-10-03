import datetime
import os
import os.path as osp
import shutil
import tempfile

import six


todo = None
TMP_DIR = None


def setup_module(module):
    global todo
    global TMP_DIR
    TMP_DIR = tempfile.mkdtemp()
    os.environ['HOME'] = TMP_DIR
    import todo  # NOQA


def teardown_module(module):
    shutil.rmtree(TMP_DIR)


# -----------------------------------------------------------------------------


def test__get_open_cmd():
    cmd = todo._get_open_cmd()
    assert cmd in ['open', 'gnome-open']


def test__init():
    todo._init(remote_url='https://github.com/wkentaro/todo.python.sample.git')
    print(todo.CONFIG_FILE)
    assert osp.isfile(todo.CONFIG_FILE)


def test__pull_cache_dir():
    todo._pull_cache_dir()
    print(todo.CACHE_DIR)
    assert osp.isdir(todo.CACHE_DIR)


def test_parse_todo():
    readme_fn = osp.join(todo.CACHE_DIR, 'README.md')
    date, todos = todo.parse_todo(open(readme_fn).read())
    print(date)
    print(todos)
    assert isinstance(date, datetime.date)
    assert isinstance(todos, list)


def test_render_todo():
    todos = [
        ('Survey', True, '### Research', '  THIS IS MEMO.\n  THIS IS MEMO.'),
        ('Implementation', False, '### Research',
         '  - Reference: https://github.com/wkentaro/todo.python'),
    ]
    content = todo.render_todo(datetime.date.today(), todos)
    print(content)
    assert isinstance(content, six.string_types)
