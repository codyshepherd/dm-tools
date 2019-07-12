# DM Tools

## Setup Instructions

* Create an activate a virtualenv using python3
  * I like to use virtualenvwrapper
  * `mkvirtualenv -p $(which python3) venv`
  * `setvirtualenvproject`
* Install requirements: `pip install -r requirements.txt`
* The easiest way to use each tool is to cd into its directory before calling

## live-game
A tool for live tracking of a play session.

Note: This tool is 'working,' but is a work in progress.

* Define characters in a yaml file (formatted like `yamls/pcs.yaml`)
* Use `live-game.py` to print these definitions in a more readable format

### Future Goals
- [ ] runtime with command prompt to track session
- [ ] live update character HP, Conditions, and Inventories
- [ ] set initiative / sort characters by initiative
- [ ] roll dice
- [ ] ingest monster file and generate random encounter by CR 

## plebs
Call this script to generate an arbitary number of NPCs from arbitrary races.

Current produces:
- age
- name (very american-sounding names, sorry)
- race
- stats (D&D 5e standard stats)
- hp

### Goals
[ ] Adjustments of stats and hp for races
[ ] Allow modifiers
[ ] Better names
[ ] Occupations
[ ] Items carried
[ ] Attack & defense capabilities

## populate
A tool for inserting player- or situation-specific text into document
templates.

* Write your template document in plain text or markdown
* Leave bracketed labels where you want custom text inserted
  * e.g. `[Character-Past]`
  * see `template-example.md`
* Define custom text bits in a yaml file (see `flavortext-example.yaml`)
* Use `populate.py` to quickly generate complete text files with custom text
    included.
* Afterward, I like to render markdown to pdf using pandoc
