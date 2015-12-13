# youtube-channel-graphing

A graphing script to analyze associations between Youtube Users.

## Purpose

This script is primarily to practise development with a TDD approach, using a Jenkins CI Server
To perform automated testing, and coverage, metrics and style quality reporting. It is also to
practise multiprocessing development.

## Requirements

This script requires the networkX and matplotlib modules, and the google clientapi module for python.

## Installation

Download and unzip the repository files.
From the command line, in the folder you unzipped the files to, type "pip install --upgrade -r requirements.txt". this should install the requirements to your local python distribution.

If you are having problems with module installation, consider obtaining a distribution of Anaconda Python. This will contain pre-installations of some required modules and an improved package manager.

## Features

- Primarily, generate a graph of youtube users and relationships, given the URL for an initial channel.
- A degree of separation can be specified - for example, a degree of 1 collects direct associates, while a degree of 2 collects associates of associates, and so on.
- format the collected data into one of several known graphing formats, including YAML, JSON and XML.
- record the data to file.
- display the data in a diagram after collection.

## Ethics Note

For privacy reasons, only publicly available data is used (visible in a web browser without credentials). 
Only the featured channels a user has agreed to publicly list are used.

## Usage

From the windows CLI, in the folder you unzipped the files to, type the command "python scripts\yt-script.py -h" to see possible options.
From the linux CLI, in the folder you unzipped the files to, type the command "./scripts/yt-script.py -h", assuming the correct permissions are in place.
Currently you will require an developer API-Key with Google Inc.

You can run tests with the commands "python tests\tests.py" and "./tests/tests.py". 

The channel IDs required in the CLI options are in the modern form - Legacy channel names will not be recognised.
If you do not know the channel ID for the channel you wish to analyze, visit the channel on youtube, and look for "channel/???" in the Url. The "???" will be the Channel ID. 