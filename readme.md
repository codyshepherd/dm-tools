# DM Tools

## Setup Instructions

* Create an activate a virtualenv using python3
  * I like to use virtualenvwrapper
  * `makvirtualenv -p \`which python3\` venv`
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
* (Optional) Render markdown to pdf with pandoc
