import os
import yaml


project={}
project['project_git_url']="https://github.com/container-images/tools"
project['project_git_branch']="master"
project['script_path']="hooks/pre_build_centos"

with open('pre-build-test.yaml','w') as outfile:
    yaml.dump(project,outfile)
