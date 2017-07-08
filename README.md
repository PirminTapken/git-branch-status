Git Branch Status
=================

Basic idea:

    $ find $HOME -name '.git' | xargs -L1 git-branch-status.py | column -t -s:

Gives you a nice little overview of all your project branches.
