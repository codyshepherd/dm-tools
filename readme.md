# DM Tools

Welcome to the source repository for `dm-tools`, the command-line toolset for
lazy DMs!

These tools are targeted for use with the D&D 5e rule set, for use in any
terminal environment that can run Python or Snap packages.

[![dm-tools](https://snapcraft.io//dm-tools/badge.svg)](https://snapcraft.io/dm-tools)

## Install the Snap

[![Get it from the Snap Store](https://snapcraft.io/static/images/badges/en/snap-store-black.svg)](https://snapcraft.io/dm-tools)

```
snap install dm-tools
```

| :zap:  Invoke with `dm-tools.live-game`, `dm-tools.plebs`, or `dm-tools.pockets`  not with `dm-tools` |
|-------------------------------------------------------------------------------------------------------|

## Development

### Virtualenv and Pip/Setuptools

Requires python >= 3.6 to support f-strings and type hints

* Clone this repository
* Create and activate a virtualenv that uses python >= 3.6
  * I like to use virtualenvwrapper
  * `mkvirtualenv -p $(which python3) venv`
  * `setvirtualenvproject`
* Install in virtual environment: `pip install -e .`

Invoke with `live-game`, `plebs`, or `pockets`

## :warning: Known Issues

If your terminal window is not big enough, when you try to start `live-game`,
you will get a crash with an error that says 'curses returned NULL'. Just
increase the size of your terminal window, or decrease the size of the text,
to alleviate this.

## live-game

A curses-like terminal GUI tool for tracking a combat encounter

### Live-Game Features

* Initiative and turn order tracking
* Tracking of combatant initiative bonus
* Auto-roll and sort initiative scores for all combatants, taking initiative
  bonuses into account
* Initiative deferral
* Add/remove characters to/from list on the fly
* Automatically populates HP, Immunities, Resistances, and Vulnerabilities for
  D&D 5e SRD monsters
* Display and edit current and max HP for all combatants
* Display and edit combatant conditions
  * D&D 5e conditions, plus Inspiration, are supported

Also features a log of past commands.

### Development To-Dos

- [ ] Edit Immunities, Resistances, and Vulnerabilities
- [ ] Undo last action
- [ ] Long-term save and load custom combatants
- [ ] Display names and creature type together
- [ ] Add arbitrary emojis for conditions
- [ ] Adjust HP for all combatants with a given name regex
- [ ] roll dice

## Plebs (and Pockets)

Plebs is command-line tool for generating plebeian NPCs

Currently produces the following stats for a given NPC:

- age
- name
- race
- stats (D&D 5e standard stats)
- hp
- gender
- occupation
- trinkets carried

Plebs also generates some random cues to assist with role-playing the NPC:

- three adjectives describing personality
- a personal problem that the NPC is dealing with

### Development To-Dos

- [ ] Attack & defense capabilities
- [ ] More content for trinkets / personalities / problems

The random values used by Plebs can be configured by passing it an alternate
config.yaml file. Use `default-config.yaml` as an example.

### Pockets

Pockets generates N random trinkets, most made up, but some inspired by
trinkets from the PHB and Curse of Strahd lists.
