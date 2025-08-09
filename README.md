# macOS firmware helper

Meanwhile trying to restore one of my systems, I realized how difficult
could be to access to some information and I decided to collect some of
them on this helper to get the firmware.

HTH other people!

Cheers!

## Getting started

On **Linux** you can do:
`curl -L "https://github.com/little-engineer-2025/macos_restore/raw/refs/heads/main/launcher.sh" | /bin/bash - `

On **Windows**: (require python installed)

- Download [this ZIP](#) and unpack it.
- Run the below:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -U pip
pip install -r requirements.txt
python3 -m macos_restore "MacBookPro18,2"
```

## Restore by using idevicerestore

Install dependencies:

- Fedora: `sudo dnf install usbmuxd usbutils idevicerestore`

NOTE: You could need to build and install:

- [libtatsu](https://github.com/libimobiledevice/libtatsu).
- [libirecovery](https://github.com/libimobiledevice/libirecovery).

Put your mac in DFU mode: https://support.apple.com/en-us/108900

Start the restore steps:

```sh
# Start usbmuxd in the background
$ usbmuxd -f &
# idevicerestore UniversalMac(...).ipsw
```

## References

- [github - idevicerestore](https://github.com/libimobiledevice/idevicerestore)
- [DFU Restore M1, M2 or M3](https://www.youtube.com/watch?v=q-FsB2onSx0).
- [Tutorial: Mac DFU restore from a Linux machine](https://www.youtube.com/watch?v=IzMa-f6u_YM).
- [How to revive or restore Mac firmware](https://support.apple.com/en-us/108900).

