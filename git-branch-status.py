#!/usr/bin/env python

'''check if dir passed as parameter is in sync'''

import argparse
import sys

from git import Repo

class NoRemoteError(Exception):
    pass


class BranchReport(object):
    def __init__(self, name):
        self.name = name
        self._up_to_date = None
        self.has_remote = None

    def set_up_to_date(self, v):
        if v == True:
            self._up_to_date = v
            self.has_remote = True
        elif v == False or v == None:
            self._up_to_date = v
        else:
            raise ValueError

    def get_up_to_date(self):
        return self._up_to_date

    up_to_date = property(get_up_to_date, set_up_to_date)


class Report(dict):

    def __init__(self, path):
        self.path = path
        self.is_dead = False
        super(Report, self).__init__(self)

    def up_to_date():
        for name, branch in self.iteritems():
            if branch.has_remote and not branch.up_to_date:
                return False
        return True

    def set_repo_dead(self):
        self.is_dead = True


def is_up_to_date(branch):
    remote_branch = branch.tracking_branch()
    local_commit = branch.commit
    try:
        remote_commit = remote_branch.commit
    except AttributeError:
        raise NoRemoteError()
    return remote_commit == local_commit

def check_repo_status(repo):
    '''checks if all branches are up to date

    returns Report
    '''
    report = Report(repo.working_tree_dir)
    current = repo.active_branch
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
