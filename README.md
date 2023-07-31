# CTFDump
![Logo](https://github.com/hendrykeren/CTFDump/blob/master/assets/logo/250%20px.png)

CTFd Dump Tool - When you want to have an offline copy of a CTF.

### Basic Usage

`python CTFDump.py -u username -p password https://demo.ctfd.io/`

> or for rCTF platform

`python CTFDump.py -c rCTF -t [token-team] https://demo.ctfd.io/`

### Command Line Flags

See `--help` for the complete list, but in short:

```text
usage: CTFDump.py [-h] [-v] [-c {CTFd,rCTF}] [-n] [-u USERNAME] [-p PASSWORD] [-t TOKEN] url

positional arguments:
  url                   ctf url (for example: https://demo.ctfd.io/)

options:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -c {CTFd,rCTF}, --ctf-platform {CTFd,rCTF}
                        ctf platform (default: CTFd)
  -n, --no-login        login is not needed (default: False)
  -u USERNAME, --username USERNAME username (default: None)
  -p PASSWORD, --password PASSWORD password (default: None)
  -t TOKEN, --token TOKEN team token for rCTF (default: None)
```
