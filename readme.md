# DM Tools

Requires python >= 3.6 and a Bash shell

## Setup Instructions

### Method 1: Install Snap

```
sudo snap install --devmode --channel=edge dm-tools
```

Note that `--devmode --channel=edge` switches will not be necessary once the
snap is released to the stable channel.

Invoke with `dm-tools.live-game`, `dm-tools.plebs`, or `dm-tools.pockets`

### Method 2: Use Pip/Setuptools

* Create and activate a virtualenv that uses python >= 3.6
  * I like to use virtualenvwrapper
  * `mkvirtualenv -p $(which python3) venv`
  * `setvirtualenvproject`
* Install requirements: `pip install .`
* The easiest way to use each tool is to cd into its directory before calling

Invoke with `live-game`, `plebs`, or `pockets`

## Known Issues

If your terminal window is not big enough, when you try to start `live-game`,
you will get a crash with an error that says 'curses returned NULL'. Just
increase the size of your terminal window, or decrease the size of the text,
to alleviate this.

## live-game
A tool for tracking of a combat encounter.

### Live-Game Features

* Enter initiative for any character
* Sort characters by initiative in descending order
* Cycle through characters in initiative order
* Defer initiative until end of turn
* Add/remove characters to/from list on the fly
* Display and edit current and max HP for all combatants
* Display and edit combatant conditions
  * D&D 5e conditions, plus Inspiration, are supported
  * currently this requires typing in the full name of the condition; a better
    interface is forthcoming
* Automatically populates HP, Immunities, Resistances, and Vulnerabilities for
  D&D 5e SRD monsters

Also features a log of past commands.

### Future Goals
- [ ] live update characters' status
  - [ ] Add a legend for category symbols
  - [ ] Display names and creature type together
  - [ ] Add arbitrary emojis for conditions
  - [ ] Adjust HP for all combatants with a given name regex
  - [ ] Inventories
- [ ] roll dice
  - [ ] with modifiers
- [ ] generate random encounter by CR 

## plebs (and pockets)
Generate an arbitary number of NPCs from arbitrary races.
The generator can be configured by passing an alternate config.yaml, with
`default-config.yaml` as an example.

See available options with `plebs --help`.

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
