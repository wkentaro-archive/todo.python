# todo.py

Manage todo on git repo.

It use Git repo for the database,
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
