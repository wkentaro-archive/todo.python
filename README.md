# todo.py

Manage todo on git repo.

It uses Git repo for the database,
and has feature of automated **sync** and **archive**.  
The sample database is here: https://github.com/wkentaro/todo.py.sample.


## Usage


```bash
pip install git+https://github.com/wkentaro/todo.py

GITHUB_NAME=<YOUR GITHUB NAME>
REPO=todo
# https://github.com/github/hub
hub create -p $REPO  # Or create it on browser (private repo is recommended)

todo init https://github.com/$GITHUB_NAME/$REPO.git
todo edit  # pull -> archive -> edit -> push
todo show  # pull -> archive -> push -> show
todo open  # pull -> archive -> push -> open
```


## Demonstration

Here, we demonstrate its feature with [the sample database](https://github.com/wkentaro/todo.py.sample).

```bash
$ rm -f ~/.todo.py.cfg
$ rm -rf ~/.cache/todo

$ todo init https://github.com/wkentaro/todo.py.sample.git
Remote URL: https://github.com/wkentaro/todo.py.sample.git
Pulling from remote: https://github.com/wkentaro/todo.py.sample.git
+ git clone https://github.com/wkentaro/todo.py.sample.git /Users/minerva/.cache/todo
Cloning into '/Users/minerva/.cache/todo'...
remote: Counting objects: 46, done.
remote: Total 46 (delta 0), reused 0 (delta 0), pack-reused 46
Unpacking objects: 100% (46/46), done.

$ todo show
Remote URL: https://github.com/wkentaro/todo.py.sample.git
Pulling from remote: https://github.com/wkentaro/todo.py.sample.git
# 2017-10-04

## School

- [ ] Report of cs.1002

$ todo open
```
