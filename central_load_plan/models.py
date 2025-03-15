import glob
import io
import os
import re
import xml.etree.ElementTree as ET
import zipfile

from abc import ABC
from abc import abstractmethod

class Source(ABC):

    @abstractmethod
    def paths(self, substitutions=None):
        """
        Generate paths to consume.
        """


class Reader(ABC):

    @abstractmethod
    def read(self, source):
        """
        Read xml from some source.
        """


class Archive(ABC):

    @abstractmethod
    def check(self, source):
        """
        Check if source is already processed.
        """

    @abstractmethod
    def save(self, source):
        """
        Save path to archive.
        """


class GlobSource(Source):
    """
    Generate paths from glob pattern.
    """

    def __init__(self, pathname, root_dir=None, recursive=False, include_hidden=False):
        self.pathname = pathname
        self.root_dir = root_dir
        self.recursive = recursive
        self.include_hidden = include_hidden

    def paths(self, substitutions=None):
        if substitutions is None:
            substitutions = {}
        pathname = self.pathname.format(**substitutions)

        root_dir = self.root_dir
        if root_dir is not None:
            root_dir = self.root_dir.format(**substitutions)

        kwargs = {
            'root_dir': root_dir,
            'recursive': self.recursive,
            'include_hidden': self.include_hidden,
        }

        for filename in glob.iglob(pathname, **kwargs):
            if kwargs['root_dir']:
                filename = os.path.join(kwargs['root_dir'], filename)
            filename = os.path.normpath(filename)
            yield filename


class XMLReader(Reader):
    """
    Read XML file.
    """
    # Returns the original source name for compatibility with EFFZipReader
    # which needs to report what name in the ZIP it is returning.

    def read(self, source):
        with open(source) as source_file:
            tree = ET.parse(source)
            root = tree.getroot()
            return (source, root)


class EFFZipReader(Reader):
    """
    Read the CLP XML file from EFF ZIP files.
    """

    xml_re = re.compile(r'[A-Z]{8}\-std\.xml$')

    def read(self, source):
        """
        Find a .dat file inside the source zip, then find the CLP xml file and
        parse it into an element tree.
        """
        # Open EFF as ZIP file (that is apparently what they really are).
        with zipfile.ZipFile(source, 'r') as eff_zip_file:
            # Find the .dat file which is another zip file inside.
            for name in eff_zip_file.namelist():
                # Check for .dat file.
                if not name.lower().endswith('.dat'):
                    continue

                # Open the .dat file as another zip.
                with eff_zip_file.open(name) as dat_zip_file_member:
                    dat_zip_bytes = io.BytesIO(dat_zip_file_member.read())
                    # Open the inner ZIP from bytes
                    with zipfile.ZipFile(dat_zip_bytes, 'r') as dat_zip_file:
                        # Find XML filename.
                        for xml_name in dat_zip_file.namelist():
                            if not self.xml_re.match(xml_name):
                                continue

                            # Open inner nested XML file.
                            with dat_zip_file.open(xml_name) as xml_file:
                                # Parse XML file inside nested ZIP file.
                                tree = ET.parse(xml_file)
                                root = tree.getroot()
                                return (xml_name, root)


class NullArchive(Archive):

    def check(self, path):
        """
        Always report path is not archived.
        """
        return False

    def save(self, path):
        """
        Do nothing with path.
        """
        return


class PathArchive(Archive):

    def __init__(self, archive_path):
        self.archive_path = archive_path
        self._paths = set(self._load_archive())

    def _load_archive(self):
        if os.path.exists(self.archive_path):
            with open(self.archive_path, 'r') as archive_file:
                for line in archive_file:
                    yield line.strip()

    def check(self, path):
        return path in self._paths

    def save(self, path):
        self._paths.add(os.path.normpath(path))
        with open(self.archive_path, 'a') as archive_file:
            archive_file.write(path + '\n')
