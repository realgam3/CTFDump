import re
import os
import sys
import codecs
import logging
from os import path
from getpass import getpass
from requests.utils import CaseInsensitiveDict
from requests.sessions import urljoin, urlparse, Session
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter

__version__ = "0.2.0"


class BadUserNameOrPasswordException(Exception):
    pass


class NotLoggedInException(Exception):
    pass


class UnknownFrameworkException(Exception):
    pass


class Challenge(object):
    def __init__(self, session, url, name, category="", description="", files=None, value=0):
        self.url = url
        self.name = name
        self.value = value
        self.session = session
        self.category = category
        self.description = description
        self.logger = logging.getLogger(__name__)
        self.files = self.collect_files(files, description)

    @staticmethod
    def collect_files(files, description=""):
        files = files or []
        files.extend(re.findall(r"https?://\w+(?:\.\w+)+(?:/[\w._-]+)+", description, re.DOTALL))
        return files

    @staticmethod
    def escape_filename(filename):
        return re.sub(r"[^\w\s\-.()]", "", filename.strip())

    def download_file(self, url, file_path):
        try:
            res = self.session.get(url, stream=True)
            with open(file_path, 'wb') as f:
                for chunk in res.iter_content(chunk_size=1024):
                    if not chunk:
                        continue
                    f.write(chunk)
                f.flush()
        except Exception as ex:
            print(ex)

    def dump(self):
        # Create challenge directory if not exist
        challenge_path = path.join(
            self.escape_filename(urlparse(self.url).hostname),
            self.escape_filename(self.category),
            self.escape_filename(self.name)
        )
        os.makedirs(challenge_path, exist_ok=True)

        with codecs.open(path.join(challenge_path, "ReadMe.md"), "wb", encoding='utf-8') as f:
            f.write(f"Name: {self.name}\n")
            f.write(f"Value: {self.value}\n")
            f.write(f"Description: {self.description}\n")
            self.logger.info(f"Creating Challenge [{self.category or 'No Category'}] {self.name}")

        for file_url in self.files:
            file_path = path.join(challenge_path, self.escape_filename(path.basename(urlparse(file_url).path)))
            self.download_file(file_url, file_path)


class CTF(object):
    def __init__(self, url):
        self.url = url
        self.session = Session()
        self.logger = logging.getLogger(__name__)

    def iter_challenges(self):
        raise NotImplementedError()

    def login(self, username, password):
        raise NotImplementedError()

    def logout(self):
        raise NotImplementedError()


class CTFd(CTF):
    def __init__(self, url):
        super().__init__(url)

    @property
    def version(self):
        # CTFd >= v2
        res = self.session.get(urljoin(self.url, "/api/v1/challenges"))
        if res.status_code == 403:
            # Unknown (Not logged In)
            return -1

        if res.status_code != 404:
            return 2

        # CTFd  >= v1.2
        res = self.session.get(urljoin(self.url, "/chals"))
        if res.status_code == 403:
            # Unknown (Not logged In)
            return -1

        if 'description' not in res.json()['game'][0]:
            return 1

        # CTFd  <= v1.1
        return 0

    def __get_nonce(self):
        res = self.session.get(urljoin(self.url, "/login"))
        return re.search('<input type="hidden" name="nonce" value="(.*?)">', res.text).group(1)

    def login(self, username, password):
        next_url = '/challenges'
        res = self.session.post(
            url=urljoin(self.url, "/login"),
            params={'next': next_url},
            data={
                'name': username,
                'password': password,
                'nonce': self.__get_nonce()
            }
        )
        if res.ok and urlparse(res.url).path == next_url:
            return True
        return False

    def logout(self):
        self.session.get(urljoin(self.url, "/logout"))

    def __get_file_url(self, file_name):
        if not file_name.startswith('/files/'):
            file_name = f"/files/{file_name}"
        return urljoin(self.url, file_name)

    def __iter_challenges(self):
        version = self.version
        if version < 0:
            raise NotLoggedInException()

        if version >= 2:
            res_json = self.session.get(urljoin(self.url, "/api/v1/challenges")).json()
            challenges = res_json['data']
            for challenge in challenges:
                challenge_json = self.session.get(urljoin(self.url, f"/api/v1/challenges/{challenge['id']}")).json()
                yield challenge_json['data']

            return

        res_json = self.session.get(urljoin(self.url, "/chals")).json()
        challenges = res_json['game']
        for challenge in challenges:
            if version >= 1:
                yield self.session.get(urljoin(self.url, f"/chals/{challenge['id']}")).json()
                continue

            yield challenge

    def iter_challenges(self):
        for challenge in self.__iter_challenges():
            yield Challenge(
                session=self.session, url=self.url,
                name=challenge['name'], category=challenge['category'],
                description=challenge['description'],
                files=list(map(self.__get_file_url, challenge.get('files', [])))
            )


def get_credentials(username=None, password=None):
    username = username or os.environ.get('CTF_USERNAME', input('User: '))
    password = password or os.environ.get('CTF_PASSWORD', getpass('Password: ', stream=False))

    return username, password


CTFs = CaseInsensitiveDict(data={
    "CTFd": CTFd
})


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument("-v", "--version", action="version", version="%(prog)s {ver}".format(ver=__version__))

    # Proxy Configuration
    parser.add_argument("url",
                        help="ctf url (for example: https://demo.ctfd.io/)")
    parser.add_argument("-c", "--ctf-platform",
                        choices=CTFs,
                        help="ctf platform",
                        default="CTFd")
    parser.add_argument("-n", "--no-login",
                        action="store_true",
                        help="login is not needed")
    parser.add_argument("-u", "--username",
                        help="username")
    parser.add_argument("-p", "--password",
                        help="password")

    sys_args = vars(parser.parse_args(args=args))

    # Configure Logger
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s %(levelname)s %(message)s',
                        datefmt='%d-%m-%y %H:%M:%S')

    ctf = CTFs.get(sys_args['ctf_platform'])(sys_args['url'])
    if not sys_args['no_login'] or not os.environ.get('CTF_NO_LOGIN'):
        print(get_credentials(sys_args['username'], sys_args['password']))
        if not ctf.login(*get_credentials(sys_args['username'], sys_args['password'])):
            raise BadUserNameOrPasswordException()

    for challenge in ctf.iter_challenges():
        challenge.dump()

    if not sys_args['no_login'] or not os.environ.get('CTF_NO_LOGIN'):
        ctf.logout()


if __name__ == '__main__':
    main()
