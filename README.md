# youtube-channel-graphing

A graphing script to analyze associations between Youtube Users.

## Purpose

This script is primarily to practise development with a TDD approach, using a Jenkins CI Server
To perform automated testing, and coverage, metrics and style quality reporting. It is also to
practise multiprocessing development.

## Requirements

This script requires the networkX and matplotlib modules, and the google clientapi module for python.

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

From the windows CLI type the command "python youtube-graphing.py -h" to see possible options.
From the linux CLI type the command "./youtube-graphing.py -h", assuming the correct permissions are in place.

