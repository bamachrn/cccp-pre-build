import os
import yaml


project=[{'project':{}}]
project[0]['project']['project_git_url']="https://github.com/container-images/tools"
project[0]['project']['project_git_branch']="master"
project[0]['project']['script_path']="hooks/pre_build_centos"

print "project is {}".format(project)

with open('pre-build-test.yaml','w') as outfile:
    yaml.dump(project,outfile,default_flow_style=False)
