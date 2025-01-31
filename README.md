# SSH Honeypot

A simple ssh server built with python

## Usage

Generate host key with

```bash
mkdir -p keys
ssh-keygen -t rsa -f keys/host_key
```

Start the server by running

```bash
python3 ./honeypot.py
```
