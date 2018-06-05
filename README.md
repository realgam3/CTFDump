# CTFDump
![Logo](https://github.com/hendrykeren/CTFDump/blob/master/assets/logo/250%20px.png)

CTFd Dump Tool - When you want to have an offline copy of a CTF.

### Basic Usage

`python CTFDump.py -u username -p password https://demo.ctfd.io/`

### Command Line Flags

See `--help` for the complete list, but in short:

```sh
Usage: CTFDump.py [-h] [-v] -u USERNAME -p PASSWORD url

positional arguments:
  url                   CTFd URL (For example: https://demo.ctfd.io/)

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -u USERNAME, --username USERNAME CTF username (default: None)
  -p PASSWORD, --password PASSWORD CTF password. (default: None)
```
