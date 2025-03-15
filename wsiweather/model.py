import ftplib
import glob

from abc import ABC
from abc import abstractmethod

class PathGenerator(ABC):

    @abstractmethod
    def paths(self, substitutions=None):
        pass


class Client(ABC):
    pass


class Output(ABC):
    pass


class Glob(PathGenerator):
    """
    Glob path generator.
    """

    def __init__(self, pathname):
        self.pathname = pathname

    def paths(self, substitutions=None):
        """
        Generate paths from glob pattern.
        """
        if substitutions is None:
            substitutions = {}
        pathname = self.pathname.format(**substitutions)
        for path in glob.iglob(pathname):
            yield path


class FTPClient(Client):
    """
    Client interface for FTP.
    """

    def __init__(
        self,
        host = '',
        user = '',
        passwd = '',
        acct = '',
    ):
        self.host = host
        self.user = user
        self.passwd = passwd
        self.acct = acct

    def _ftp_kwargs(self):
        return {
            'host': self.host,
            'user': self.user,
            'passwd': self.passwd,
            'acct': self.acct,
        }

    def write(self, bytes_data, remote_path):
        """
        Write bytes data to remote FTP path.
        """
        with ftplib.FTP(**self._ftp_kwargs()) as ftp:
            ftp.storbinary(f'STOR {remote_path}', bytes_data)


class PathOutput(Output):

    def __init__(self, filename):
        self.filename = filename
