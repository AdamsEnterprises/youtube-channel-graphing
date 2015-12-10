# Jenkins Server

## -----------------------------


## General Setup:

Installed on local Windows 10 development machine.

Installed with MSI available from [Jenkins Website](jenkins-ci.org).


## Relevant Plugins:

- Github API
- Github Pull Request Manager
- Python
- CCM
- Cobertura
- Coverage Scatter Plot
- Github authentication
- Junit
- Python Wrapper
- Script Security
- Violations


## Plugin Notes

- The Github API and pull request plugins do not work from dynamic IPs. The server source must have a static IP for webhooks to work correctly.

- CCM is intended for C++ or C#, but can be used with Junit style XML reports from Radon Python CCM.
 
 - Cobertura endances coverage reports for nosetests.
 
 - JUnit required for Nosetest test reporting.
  
  
## Python Scripting

set PYTHONPATH = "C:\Users\Roland\VirtualEnvs\Anaconda3-Master\Scripts"
set JENKINS_CURRENT_PROJECT = "Python-Youtube-Graph"
call C:\Users\Roland\VirtualEnvs\Anaconda3-Master\Scripts\activate
nosetests --stop --with-xunit --with-coverage --cover-inclusive --cover-branches
coverage xml --include=scripts\*.py -i
pylint -f parseable -d I0011 --ignore=tests scripts > pylint.out
radon cc -a -e tests\*.py --xml . > ccm.xml
call C:\Users\Roland\VirtualEnvs\Anaconda3-Master\Scripts\deactivate
set PYTHONPATH = ""
set JENKINS_CURRENT_PROJECT = ""


## Script Requirements

Requires Anaconda 3 Python to be installed.
Requires nosetests, coverage, pyline and radon to be installed from CLI (Not from pip or another package manager).
Execution of script actions must be from within an Anaconda 3 virtualenv.


## Project Settings

Git Repos: .git GIT url with credentials.
Branches: master, develop.
Periodic building: H H/8 * * * (cron job).
Build on Github push (currently not working due to webhook and dynamic IP issues).
CCM analysis Build Step: ccm.xml file.
Publish Cobertura Coverage report: coverage.xml file.
JUnit Test report XMLs: nosetests.xml, factor of 1.
Violations: pylint, pylint.out file.


