# todo.py

Manage todo on git repo.


## Usage

```bash
pip install git+https://github.com/wkentaro/todo.py

GITHUB_NAME=<YOUR GITHUB NAME>
REPO=todo
hub create -p $REPO
todo init https://github.com/$GITHUB_NAME/$REPO.git

todo edit
todo show
```
