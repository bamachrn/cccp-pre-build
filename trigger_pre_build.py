import subprocess
import sys

import yaml


def build_project(args):
    (git_url, git_branch, script_path) = args
    project = [{'project': {}}]
    project[0]['project'][
        'project_git_url'] = git_url
    project[0]['project']['project_git_branch'] = git_branch
    project[0]['project']['script_path'] = script_path

    print "project is {}".format(project)

    with open('pre-build-generator.yaml', 'w') as outfile:
        yaml.dump(project, outfile, default_flow_style=False)

    myargs = ['jenkins-jobs',
              '--ignore-cache',
              'update',
              ':'.join(
                  ['pre-build-job.yml', 'pre-build-generator.yaml'])]

    _, error = run_command(myargs)


def run_command(command):
    """
    runs the given shell command using subprocess
    """
    proc = subprocess.Popen(command,
                            stdout=subprocess.PIPE)
    return proc.communicate()


if __name__ == '__main__':
    build_project(sys.argv[1:])
