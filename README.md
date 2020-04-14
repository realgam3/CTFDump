# CTFDump
![Logo](https://github.com/hendrykeren/CTFDump/blob/master/assets/logo/250%20px.png)

CTFd Dump Tool - When you want to have an offline copy of a CTF.

### Basic Usage

`python CTFDump.py -u username -p password https://demo.ctfd.io/`

### Command Line Flags

See `--help` for the complete list, but in short:

```sh
usage: CTFDump.py [-h] [-v] [-c {CTFd}] [-n] [-u USERNAME] [-p PASSWORD] url  

positional arguments:
  url                   ctf url (for example: https://demo.ctfd.io/)

optional arguments:
  -h, --help            show this help message and exit  
  -v, --version         show program's version number and exit  
  -c {CTFd}, --ctf-platform {CTFd}  ctf platform (default: CTFd)
  -u USERNAME, --username USERNAME  username (default: None)
  -p PASSWORD, --password PASSWORD  password (default: None)  
```
