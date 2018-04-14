import re
import os
import sys
import codecs
import logging
import requests
from os import path
from requests.sessions import urljoin, urlparse
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

__version__ = "0.1.0"

logger = logging.getLogger(__name__)
session = requests.Session()


def download_file(url, file_path):
    res = session.get(
        url,
        verify=False,
        stream=True,
    )
    with open(file_path, 'wb') as f:
        for chunk in res.iter_content(chunk_size=1024):
            if not chunk:
                continue
            f.write(chunk)
        f.flush()


def run(url, username, password):
    hostname = urlparse(url).hostname

    res = session.get(
        urljoin(url, "/login"),
        params={'next': 'challenges'}
    )
    nonce = re.search('<input type="hidden" name="nonce" value="(.*?)">', res.content)

    # Login
    session.post(
        urljoin(url, "/login"),
        params={'next': 'challenges'},
        data={
            'name': username,
            'password': password,
            'nonce': nonce.group(1)
        }
    )

    # Get Challenges
    res = session.get(urljoin(url, "/chals"))

    # Create hostname directory if not exist
    if not path.exists(hostname):
        os.mkdir(hostname)

    res_json = res.json()
    for challenge in res_json['game']:
        category_path = path.join(hostname, challenge['category'])
        if not path.exists(category_path):
            os.mkdir(category_path)

        challenge_path = path.join(category_path, re.sub('[^\w\-_. ]', '_', challenge['name'].strip()))
        if not path.exists(challenge_path):
            os.mkdir(challenge_path)
            with codecs.open(path.join(challenge_path, "ReadMe.md"), "wb", encoding='utf-8') as f:
                f.write(u"Name: %s\n" % challenge['name'])
                f.write(u"Value: %d\n" % challenge['value'])
                f.write(u"Description: %s\n" % challenge['description'])
                logger.info("Creating Challenge [%s] %s" % (challenge['category'] or "No Category", challenge['name']))

            file_names = re.findall("https?://\w+(?:\.\w+)+(?:/[\w._-]+)+", challenge['description'], re.DOTALL)
            for file_name in file_names:
                fn = path.basename(file_name)
                download_file(file_name, path.join(challenge_path, fn))

            for file_name in challenge['files']:
                fn = path.basename(file_name)
                download_file(urljoin(url, "/files/%s" % file_name), path.join(challenge_path, fn))

    session.get(urljoin(url, "/logout"))


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("-v", "--version", action="version", version="%(prog)s {ver}".format(ver=__version__))

    # Proxy Configuration
    parser.add_argument("url",
                        help="CTFd URL (For example: https://demo.ctfd.io/)")
    parser.add_argument("-u", "--username",
                        help="CTF username",
                        required=True)
    parser.add_argument("-p", "--password",
                        help="CTF password.",
                        required=True)

    sys_args = vars(parser.parse_args(args=args))

    # Configure Logger
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%d-%m-%y %H:%M:%S')

    # Run CTFDump
    run(**sys_args)


if __name__ == '__main__':
    main()
