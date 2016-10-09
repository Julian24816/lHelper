# lHelper
python application for helping me learn Latin

## 0. Installation
- `git clone https://github.com/Julian24816/lHelper.git`
- `git fetch origin` for updates

## 1. Usage
run the program with `python <folder-name>` to start it with the commandline interface enabled.

The following commands are available in the CLI:

- `user <your-username>`: create new user or switch to existing one
- `show <group-name>`: list all cards in the given group
    some available groups are:
    - `adeo-9`, `adeo-11`, ..., `adeo-161`
    - `ratio-aa-1`, `ratio-aa-2`, ..., `ratio-aa-4`
- `use <group-name>`: add a group of cards to your personal cards (gives them a due date)
- `question <group-name>`: let the program question you over all cards in the given group
- `question [due]`: let the program question you over all due cards
- `lookup <string>`: print all cards matching string
    string can be a python regexp

The following commands are disabled by default as they modify the git-synchronised card-db:

- `add cards`: add new cards to the db
- `edit <card-id>`: edit a specific card in the db

## 2. Mistakes in Card-Data and other feedback
feel free to contact me at julian24816@gmail.com
