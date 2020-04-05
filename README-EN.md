# MangaLib Notifier

[Switch to Russian version](README.md)

> :warning: **Unofficial** This script wasn't made by MangaLib themselves, I just made parser and based on it I made this webhook.

This script will send request on your WebHook server, whenever new translation for manga added to MangaLib.

## Installation (Windows)

> :warning: Builds work 2-3 times slower than script.

1. Download last build from Releases tab.
2. Run `mangalib.exe`
3. Setup listening using `setnode` (all commands and examples will be below)
4. Run listening using command `listen`.

## Installation (Linux/MacOS)
1. Download **Python 3.7+** and install it
2. Download last `source` archive from Releases tab (for stability), or clone `master` branch. (for latest)
3. Install dependecies using `pip install -r requirements.txt` or `pip3 install -r requirements.txt`
4. Run script using `python manga.py`, or `python3 manga.py`
5. Setup listening using the `setnode` command (all commands and examples below)
6. Run listening by typing `listen` command.

## Commands
| Command | Description                    | Example |
| ------------- | ----------------------- | --------------------- |
| `help`      | Display GitHub link      | `help` |
| `setnode`   | Set new setting node value    | `setnode manga naruto` |
| `autonode`   | Step-by-step node setup (easier than `setnode`)    | `autonode` |
| `save`   | Save file to *.ml-cfg    | `save filename` |
| `load`   | Load the settings from file    | `load filename` |
| `exit`   | Exit    | `exit` |

## Nodes (Settings)
| Node  | Description    | Possible values |
| ------------- | ----------------------- | --------------------- |
| `manga`      | Manga ID      | Any manga ID (text) |
| `chapter`      | Last chapter ID (may be not set)      | Any integer |
| `delay`      | Delay between checks      | Any integer |
| `url`      | Webhook link     | Any link |
| `method`      | Sending Protocol     | `GET`, `POST`, `PUT`, `discord` lowercased |
| `sendto`      | **Deprecated method** Use `url`     |  |

## Discord Webhook Setup
1. `method` must be `discord`;
2. `url` must be link to Discord webhook.

## Discord Webhook Demonstration
![Demo](https://i.imgur.com/gC4scNu.png "Demo")

## Heroku, Now, AWS, etc. deployment
For deploying on cloud services you don't need to do much, Heroku especially:
1. Downloading last release `source` archive, or `master` development branch.
2. Run `manga.py`
3. Use `autonode` to fill all fields (if you want chapter to be autoupdated to last use `-1` in `chapter`)
4. Saving it with any name using `save` (except autoload & autolisten)
5. Exit (`exit` or `Ctrl+^C`)
6. Rename new file to `autolisten.ml-cfg`
7. Create new app and deploy to Heroku.

### AWS and other dedicated cloud servers (Azure, Google Cloud, ...) on Linux
There's even simpler, because dedicated servers can be used as PC:
1. Follow the instructions above to create `autolisten.ml-cfg` file
2. Install `screen` (`sudo apt install screen`)
3. Create new env `screen -S mangalibenv`
4. Run script
5. Close connection
Webhook will still work and send data while you're asleep.