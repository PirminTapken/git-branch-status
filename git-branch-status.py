#!/usr/bin/env python

"""check if dir passed as parameter is in sync"""

import argparse
import sys

from git import Repo


class NoRemoteError(Exception):
    """Raised when no remote is found"""
    pass


class BranchReport(object):
    """Relevant data for a branch.

    Relevant: Is it up to date?

    Attributes:
        name: name/path of the branch
        has_remote: True when it has a remote, False when it doesn't. None when
            it was never checked.
        up_to_date: True when its equal to it's remote, False when not. None when it wasn't checked.
    """

    def __init__(self, name):
        self.name = name
        self._up_to_date = None
        self.has_remote = None

    def set_up_to_date(self, value):
        """Setter for up_to_date."""
        if value == True:
            self._up_to_date = value
            self.has_remote = True
        elif value == False or value == None:
            self._up_to_date = value
        else:
            raise ValueError

    def get_up_to_date(self):
        """Getter for up_to_date."""
        return self._up_to_date

    up_to_date = property(get_up_to_date, set_up_to_date)


class Report(dict):
    """Report about a repository and it's branches.

    Attributes:
        path: path to repository
        is_dead: True, when repo has no branches
    """

    def __init__(self, path):
        self.path = path
        self.is_dead = False
        super(Report, self).__init__(self)

    def up_to_date():
        """Checks if all branches are matching their remote.

        Returns:
            boolean
        """
        for name, branch in self.iteritems():
            if branch.has_remote and not branch.up_to_date:
                return False
        return True

    def set_repo_dead(self):
        """Check that repo has no branches."""
        self.is_dead = True


def is_up_to_date(branch):
    """Check if branch is up to date.

    Compares remote and local branch commit, if they differ, returns false,
    else true.  If the branch has no remote, NoRemoteError is raised.

    Args:
        branch: git.refs.symbolic.SymbolicReference

    Returns:
        boolean

    Raises:
        NoRemoteError when there's no remote branch.
    """
    remote_branch = branch.tracking_branch()
    local_commit = branch.commit
    try:
        remote_commit = remote_branch.commit
    except AttributeError:
        raise NoRemoteError()
    return remote_commit == local_commit


def check_repo_status(repo):
    """Checks if all branches are up to date.

    Args:
        repo: git.Repo

    Returns:
        A Report filled with branch informations.
    """
    report = Report(repo.working_tree_dir)
    heads = repo.heads
    if len(heads) == 0:
        report.set_repo_dead()
    for head in repo.heads:
        branch_report = BranchReport(head.name)
        try:
            if is_up_to_date(head):
                branch_report.up_to_date = True
        except NoRemoteError:
            branch_report.has_remote = False

        report[head.name] = branch_report

    return report


def write_report(out, report):
    """Write out the report to output.

    Args:
        out: File-like
        report: Report object
    """
    tmpl = "{path}[{branch_name}]: {status}\n"
    if report.is_dead:
        out.write("repository {} is dead\n".format(report.path))
        out.flush()
        return
    for name, branch in report.iteritems():
        if branch.up_to_date:
            status = 'up to date'
        elif not branch.has_remote:
            status = 'no remote'
        else:
            Exception("Unexpected branch status")
        msg = tmpl.format(branch_name=name, status=status, path=report.path)
        out.write(msg)

    out.flush()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='path to a git directory')
    args = parser.parse_args()

    repo = Repo(args.path)
    report = check_repo_status(repo)
    write_report(sys.stdout, report)
    if not report.up_to_date:
        sys.exit(1)


if __name__ == '__main__':
    main()
