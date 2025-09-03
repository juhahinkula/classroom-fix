# Github Classroom Fix

Python script to fix Github Classroom [Repository Access Issue](https://github.com/orgs/community/discussions/72283)

## Required Installations
1. Install [GH CLI](https://cli.github.com/)
2. Install GH Github Classroom extension
```
gh extension install github/gh-classroom
```
3. Download `classroom-fix.py` from this repository

## Usage
1. Login GH CLI
```
gh auth login
```
2. Run the script
```
python3 classroom-fix.py
```
3. Select classroom
4. Select assignment

Script will fix all assignment repositories that have student with pending invitation. 
