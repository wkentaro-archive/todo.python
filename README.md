# todo.py

Manage todo on git repo.


## Usage



```bash
pip install git+https://github.com/wkentaro/todo.py

GITHUB_NAME=<YOUR GITHUB NAME>
REPO=todo
# https://github.com/github/hub
hub create -p $REPO  # Or create it on browser

todo init https://github.com/$GITHUB_NAME/$REPO.git
todo edit
todo show
```
