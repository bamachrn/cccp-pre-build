import os
import select
import subprocess
import sys


def _print(msg):
    print msg
    sys.stdout.flush()


def run_cmd(cmd, user='root', host=None, private_key='', stream=False):
    _print('=' * 30 + 'RUN COMMAND' + "=" * 30)
    _print({
        'cmd': cmd,
        'user': user,
        'host': host,
        'private_key': private_key,
        'stream': stream
    })
    if host:
        private_key_args = ''
        if private_key:
            private_key_args = '-i {path}'.format(
                path=os.path.expanduser(private_key))
        _cmd = (
            "ssh -t -o UserKnownHostsFile=/dev/null -o "
            "StrictHostKeyChecking=no {private_key_args} {user}@{host} '"
            "{cmd}"
            "'"
        ).format(user=user, cmd=cmd, host=host,
                 private_key_args=private_key_args)
    else:
        _cmd = cmd

    p = subprocess.Popen(_cmd, shell=True,
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE)
    out, err = "", ""
    if stream:
        def read(out, err):
            reads = [p.stdout.fileno(), p.stderr.fileno()]
            ret = select.select(reads, [], [], 0.0)

            for fd in ret[0]:
                if fd == p.stdout.fileno():
                    c = p.stdout.read(1)
                    sys.stdout.write(c)
                    out += c
                if fd == p.stderr.fileno():
                    c = p.stderr.read(1)
                    sys.stderr.write(c)
                    err += c
            return out, err

        while p.poll() is None:
            out, err = read(out, err)

        # Retrieve remaining data from stdout, stderr
        for fd in select.select([p.stdout.fileno(), p.stderr.fileno()],
                                [], [], 0.0)[0]:
            if fd == p.stdout.fileno():
                for c in iter(lambda: p.stdout.read(1), ''):
                    sys.stdout.write(c)
                    out += c
            if fd == p.stderr.fileno():
                for c in iter(lambda: p.stderr.read(1), ''):
                    sys.stderr.write(c)
                    err += c
        sys.stdout.flush()
        sys.stderr.flush()
    else:
        out, err = p.communicate()
    if p.returncode is not None and p.returncode != 0:
        if not stream:
            _print("=" * 30 + "ERROR" + "=" * 30)
            _print('ERROR: %s\nOUT: %s' % (err, out))
        raise Exception('Run Command Error for: %s\n%s' % (_cmd, err))
    return out


def get_project_code(pre_build_node, work_dir,
                     git_repo, git_branch,  stream=False):
    run_cmd(
        "cd %s && "
        "git clone %s && "
        "git checkout %s" % (
            work_dir, git_repo, git_branch),
        host=pre_build_node, stream=stream)


def setup_node(pre_build_node):
    # provision controller
    run_cmd(
        "yum install -y git && "
        "yum install -y rsync && "
        "yum install -y gcc libffi-devel python-devel openssl-devel && "
        "yum install -y epel-release && "
        "yum install -y docker distgen",
        host=pre_build_node)


def run_pre_build(pre_build_node, git_repo, git_branch, script_path='/'):
    work_dir = '/root/cccp_pre_build'
    get_project_code(pre_build_node, work_dir, git_repo, git_branch)
    path = os.path.join(work_dir, script_path)
    run_cmd(
        '/bin/bash %s' % (path),
        host=pre_build_node, stream=True)


def teardown():
    pass
