# DM Tools

Requires python >= 3.6

## Setup Instructions

* Create and activate a virtualenv that uses python >= 3.6
  * I like to use virtualenvwrapper
  * `mkvirtualenv -p $(which python3.7) venv`
  * `setvirtualenvproject`
* Install requirements: `pip install -r requirements.txt`
* The easiest way to use each tool is to cd into its directory before calling

### Suite Goals

- [ ] Top-level api (e.g. `dm-tools live-game`)
- [ ] Package as snap

## live-game
A tool for tracking of a play session.

Run with `./live-game.py` at the command line. Requires a yaml file
like mine called `pcs.yaml` sitting in a subdirectory, called `yamls/` by
default.

### Live-Game Features

* Enter initiative for any character
* Sort characters by initiative in descending order
* Cycle through characters in initiative order
* Defer initiative until end of turn
* Add/remove characters to/from list on the fly

Also features a log of past commands.

### Future Goals
- [x] interactive runtime to track session
- [ ] live update characters' status
  - [x] HP
  - [ ] Conditions
  - [ ] Inventories
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
