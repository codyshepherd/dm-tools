# DM Tools

## Setup Instructions

* Create an activate a virtualenv using python3
  * I like to use virtualenvwrapper
  * `makvirtualenv -p \`which python3\` venv`
  * `setvirtualenvproject`
* Install requirements: `pip install -r requirements.txt`

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
