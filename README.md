# macOS firmware helper

Meanwhile trying to restore one of my systems, I realized how difficult
could to access some information and I decided to collect some of them
on this helper to get the firmware.

HTH other people!

Cheers!

## Getting started

If using [toolbox.sh](github.com/avisiedo/toolbox-sh):

```sh
$ cat > .envrc <<< 'export TOOLBOX="macos_restore"'
$ direnv allow
$ toolbox.sh create
$ toolbox.sh enter
```

## Download firmware

```sh
$ python3 -m macos_restore "MacBookPro17,2"
```

