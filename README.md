# Github Classroom Fix

Python script to fix Github Classroom [Repository Access Issue](https://github.com/orgs/community/discussions/72283)

## Required Installations
1. Install [GH CLI](https://cli.github.com/)
2. Install GH Github Classroom extension
```
gh extension install github/gh-classroom
```
3. Download `classroom_fix.py` from this repository

## Usage
1. Login GH CLI
```
gh auth login
```
2. Run the script
```
python3 classroom_fix.py
```
3. Select classroom
4. Select assignment

Script will resolve repository access issues for selected assignment where students have pending invitations.
