# DM Tools

Requires python >= 3.6 and a Bash shell

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

Run with `./live-game.py` at the command line.

### Live-Game Features

* Enter initiative for any character
* Sort characters by initiative in descending order
* Cycle through characters in initiative order
* Defer initiative until end of turn
* Add/remove characters to/from list on the fly
* Display and edit current and max HP for all combatants
  * HP is automatically populated from the web for D&D 5e SRD monsters
* Display and edit combatant conditions
  * D&D 5e conditions, plus Inspiration, are supported
  * currently this requires typing in the full name of the condition; a better
    interface would be nice

Also features a log of past commands.

### Future Goals
- [x] interactive runtime to track session
- [ ] collapsible column entries
- [x] scrollable column text
- [ ] live update characters' status
  - [x] Max and current HP
  - [ ] Display names and creature type together
  - [x] add and remove Conditions
  - [ ] Some type of menu for adding conditions
  - [ ] Clear all conditions
  - [ ] Inventories
- [x] set initiative / sort characters by initiative
- [ ] roll dice
  - [ ] with modifiers
- [ ] generate random encounter by CR 

## plebs (and pockets)
Call `./plebs.py` to generate an arbitary number of NPCs from arbitrary races.
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
- occupation
- trinkets carried

### Goals
- [ ] Adjustments of stats and hp for races
- [ ] Allow modifiers
- [x] Better names
- [x] Occupations
- [x] Items carried
- [ ] Attack & defense capabilities

### pockets

This script generates N random trinkets, most made up, but some inspired by
trinkets from the PHB and Curse of Strahd lists.

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
