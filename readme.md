# DM Tools

## Setup Instructions

* Create an activate a virtualenv using python3
  * I like to use virtualenvwrapper
  * `mkvirtualenv -p $(which python3) venv`
  * `setvirtualenvproject`
* Install requirements: `pip install -r requirements.txt`
* The easiest way to use each tool is to cd into its directory before calling

## live-game
A tool for tracking of a play session.

Run with `./live-game.py` in the command line. Best if you have a yaml file
like mine called `pcs.yaml` in a subdirectory, called `yamls/` by default.

Currently supports displaying loaded characters' positions in iniative order,
setting initiative, and cycling through initiative via a keyboard-based
interactive menu.

* Define characters in a yaml file (formatted like `yamls/pcs.yaml`)
* Use 'live-game.py' to show the status of these characters

### Live-Game Options

* Enter initiative for any character
* Sort characters by initiative in descending order
* Cycle through characters

Also features a log of past commands.

### Future Goals
- [x] runtime with command prompt to track session
- [ ] live update character HP, Conditions, and Inventories
- [x] set initiative / sort characters by initiative
- [ ] roll dice
- [ ] ingest monster file and generate random encounter by CR 

## plebs
Call this script to generate an arbitary number of NPCs from arbitrary races.
The generator can be configured by passing an alternate config.yaml, with
`default-config.yaml` as an example.

This tool is best used by cd-ing into the `plebs/` directory and then calling
`./plebs.py` with options.

See available options with `./plebs --help`.

Currently produces the following stats for a given NPC:
- age
- name
- race
- stats (D&D 5e standard stats)
- hp
- gender

### Goals
- [ ] Adjustments of stats and hp for races
- [ ] Allow modifiers
- [x] Better names
- [ ] Occupations
- [ ] Items carried
- [ ] Attack & defense capabilities

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
