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
    logger.info("Downloading file \"%s\" -> \"%s\"", url, file_path)
    try:
        res = session.get(url, stream=True)
        with open(file_path, 'wb') as f:
            for chunk in res.iter_content(chunk_size=1024):
                if not chunk:
                    continue
                f.write(chunk)
            f.flush()
    except Exception as ex:
        print(ex)


def get_nonce(url):
    logger.debug("Getting nonce")
    res = session.get(
        urljoin(url, "/login"),
        params={'next': 'challenges'}
    )
    return re.search('<input type="hidden" name="nonce" value="(.*?)">', res.text).group(1)


def login(url, nonce, username, password):
    logger.info("Logging in as \"%s\"", username)
    session.post(
        urljoin(url, "/login"),
        params={'next': 'challenges'},
        data={
            'name': username,
            'password': password,
            'nonce': nonce
        }
    )


def logout(url):
    logger.info("Logging out",)
    session.get(urljoin(url, "/logout"))


def iter_challenges(url):
    # CTFD 2.0
    logger.info("Getting challenges")
    res = session.get(urljoin(url, "/api/v1/challenges"))
    if res.ok:
        res_json = res.json()
        challenges = res_json['data']
        for challenge in challenges:
            challenge_json = session.get(urljoin(url, "/api/v1/challenges/%d" % challenge['id'])).json()
            yield challenge_json['data']
        return

    res_json = session.get(urljoin(url, "/chals")).json()
    challenges = res_json['game']
    for challenge in challenges:
        if 'description' in challenges:
            yield challenge
            continue

        yield session.get(urljoin(url, "/chals/%d" % challenge['id'])).json()


def run(url, username, password, cookie):
    hostname = urlparse(url).hostname

    if cookie is not None:
        for one_cookie in cookie:
            split_cookie = one_cookie.split("=", 1)
            if len(split_cookie) != 2:
                logger.error("Invalid cookie: %r", one_cookie)
                continue
            name, value = split_cookie
            session.cookies.set(name, value)

    # Login
    login(url, get_nonce(url), username, password)

    # Create hostname directory if not exist
    if not path.exists(hostname):
        os.mkdir(hostname)

    # Get Challenges
    for challenge in iter_challenges(url):
        category_path = path.join(hostname, re.sub('[^\w\-_ ]', '', challenge['category'].strip()))
        if not path.exists(category_path):
            os.mkdir(category_path)

        challenge_path = path.join(category_path, re.sub('[^\w\-_ ]', '', challenge['name'].strip()))
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
                fn = path.basename(urlparse(file_name).path)
                if not file_name.startswith('/files/'):
                    file_name = "/files/%s" % file_name

                download_file(urljoin(url, file_name), path.join(challenge_path, fn))

    # Logout
    logout(url)


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
    parser.add_argument("-C", "--cookie",
                        help="Add cookie before trying to access CTFd",
                        action='append')
    parser.add_argument("-D", "--debug",
                        help="Print debug messages",
                        action="store_true")

    sys_args = vars(parser.parse_args(args=args))

    # Configure Logger
    if sys_args.pop("debug"):
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO
    logging.basicConfig(level=log_level,
                        format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%d-%m-%y %H:%M:%S')

    # Run CTFDump
    run(**sys_args)


if __name__ == '__main__':
    main()
