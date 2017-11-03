# This script uses the Duffy node management api to get fresh machines to run
# your CI tests on. Once allocated you will be able to ssh into that machine
# as the root user and setup the environ
#
# XXX: You need to add your own api key below, and also set the right cmd= line
#      needed to run the tests
#
# Please note, this is a basic script, there is no error handling and there are
# no real tests for any exceptions. Patches welcome!

import json
import os
import sys

from lib import _print, run_cmd, run_pre_build, setup_node, teardown

DEBUG = os.environ.get('ghprbCommentBody', None) == '#dotests-debug'
ver = "7"
arch = "x86_64"
count = 1
NFS_SHARE = "/nfsshare"


# repo_url = os.environ.get('ghprbAuthorRepoGitUrl') or \
#     os.environ.get('GIT_URL')
# repo_branch = os.environ.get('ghprbSourceBranch') or \
#     os.environ.get('ghprbTargetBranch') or 'master'


def get_node(ver="7", arch="x86_64", count=1):
    out = run_cmd(
        'export CICO_API_KEY=`cat ~/duffy.key` && '
        'cico node get --arch %s --release %s --count %s '
        '--format json' % (arch, ver, count))
    _print('Get nodes output: %s' % out)
    hosts = json.loads(out)

    with open('env.properties', 'a') as f:
        f.write('DUFFY_SSID=%s' % hosts[0]['comment'])
        f.close()

    return [host['hostname'] for host in hosts]


def print_nodes():
    with open('env.properties') as f:
        s = f.read()

    _print('\n'.join(s.splitlines()[3:]))


if __name__ == '__main__':
    try:
        args = sys.argv[1:]
        (git_repo, git_branch, script_path) = args
        node = get_node()
        data = setup_node(node)
        run_pre_build(node, git_repo,
                      git_branch, script_path)
        teardown()
    except Exception as e:
        _print('Build failed: %s' % e)
        sys.exit(1)
