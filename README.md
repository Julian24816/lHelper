# lHelper
python application for helping me learn Latin

## 0. Installation
- `git clone https://github.com/Julian24816/lHelper.git`
- `git pull master` for updates

## 1. Usage
run the program with `python <folder-name> -t` (use flag `-t` to start with a TextUI in the command-line).

Options in the TextUIs menu:

- To create a new user choose `user your-username` and confirm with `y`.
    - this also allows for user-switching
- To use a group of cards for questioning choose `use group-name`.
    - some available groups are:
        - adeo-9 to adeo-161
        - ratio-aa-1
- To question you over all due cards choose `question` or `question due`. 
    - You can also choose `question group-name` to question you over all cards in that group, provided you're using all of them.
    
Example:
```
[...]
$ user test
Username does not exist. Create new user? [y|n] y
test $ use adeo-9
[...]
test $ question
Shelf 1: 18 cards
Sum: 18 cards

[23, 1, adeo-9]
addere, addo, addidi, additum
: hinzufügen
Correct +1
New shelf: 2
Next questioning: 2016-10-10
17 cards left.

[...]
test $ exit
```
