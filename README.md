# todo.python

[![](https://img.shields.io/pypi/v/todo.python.svg)](https://pypi.python.org/pypi/todo.python)
<!-- [![](https://travis-ci.org/wkentaro/todo.python.svg?branch=master)](https://travis-ci.org/wkentaro/todo.python) -->

Manage todo on git repo.

It uses Git repo for the database,
and has feature of automated **sync** and **archive**.  
The sample database is here: https://github.com/wkentaro/todo.python.sample.

The difference from its alternatives such as Evernote and iOS todo list
is the feature of auto archiving.
todo.py is designed for use of daily report on your work,
and you can easily look back **what you completed at each day**
[as shown in the sample](https://github.com/wkentaro/todo.python.sample/blob/master/2017/2017-10.md).


## Usage


```bash
pip install git+https://github.com/wkentaro/todo.python

GITHUB_NAME=<YOUR GITHUB NAME>
REPO=todo
# https://github.com/github/hub
hub create -p $REPO  # Or create it on browser (private repo is recommended)

todo init https://github.com/$GITHUB_NAME/$REPO.git
EDITOR=emacs todo edit  # pull -> archive -> edit -> push
todo show  # pull -> archive -> push -> show
todo open  # pull -> archive -> push -> open
```


## Demonstration

Here, we demonstrate its feature with [the sample database](https://github.com/wkentaro/todo.python.sample).

```bash
$ todo deinit

$ todo init https://github.com/wkentaro/todo.python.sample.git
Remote URL: https://github.com/wkentaro/todo.python.sample.git
Pulling from remote: https://github.com/wkentaro/todo.python.sample.git
+ git clone https://github.com/wkentaro/todo.python.sample.git /Users/minerva/.cache/todo
Cloning into '/Users/minerva/.cache/todo'...
remote: Counting objects: 46, done.
remote: Total 46 (delta 0), reused 0 (delta 0), pack-reused 46
Unpacking objects: 100% (46/46), done.

$ todo show
Remote URL: https://github.com/wkentaro/todo.python.sample.git
Pulling from remote: https://github.com/wkentaro/todo.python.sample.git
# 2017-10-04

## School

- [ ] Report of cs.1002

$ todo open
```
