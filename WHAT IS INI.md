# My camera isn't being selected! Why?
*have you checked config.ini?*

## What is config.ini
`config.ini` is a file that stores a bunch of settings. Things like camera info, window size, tracking sensitivity, and brush settings are stored in this file.

## But... why?
I'd rather not dig through the entire file to change a single value, especially if it's used in multiple places

Plus the file is `hot reloadable`, which means that you can change a value and save the file and the program will use that new value without having to restart

## How to use it
`[name]` indicates a section of the config
`prop = 0` indicates that the value "prop" is 0

Example:
```ini
[config]
camera_id = 1
debug = True
```
can be thought of like `config.camera_id` or `config.debug`

MAKE SURE TO CHECK `config-example.ini` REGULARY FOR CHANGES. IF YOU GET AN ERROR RELATED TO IT YOU'RE PROBABLY MISSING A PROPERTY