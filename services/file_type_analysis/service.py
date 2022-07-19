from cryptography import x509
from cryptography.hazmat.backends import default_backend
import subprocess
from zipfile import ZipFile

from ace2 import *

# maps non linux platform mime type to linux mime type
mime_type_conversion_map = {
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation': 'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'application/msword',
}

# maps non linux platform file type to linux file type
file_type_conversion_map = {
    'OLE 2 Compound Document': 'Microsoft Office Document',
}

class FileTypeAnalysis(Module):
    ''' Determines the type of a file '''

    class Details(Module.Details):
        file_type: Optional[str] = Field(default=None, description='human readable file type of the target')
        mime_type: Optional[str] = Field(default=None, description='mime type of the target')

    def should_run(self):
        return isinstance(self.target, File)

    def execute(self):
        persistent_data.set('file_type_analysis.foo', 'bar')
        foo = persistent_data.get('file_type_analysis.foo')
        logging.info(f'loaded foo = {foo}')
        hello = persistent_data.get('file_type_analysis.hello')
        logging.info(f'loaded hello = {hello}')

        # get the human readable type
        process = subprocess.run(['file', '-b', '-L', self.target.path], capture_output=True, text=True)
        if process.stderr:
            logging.warning(f'failed to get file_type of {self.target.value}: {process.stderr}')
        self.details.file_type = process.stdout.strip()

        # convert non linux file types to linux file type so we get the same result regardless platform
        if self.details.file_type in file_type_conversion_map:
            self.details.file_type = file_type_conversion_map[self.details.file_type]

        # get the mime type
        process = subprocess.run(['file', '-b', '--mime-type', '-L', self.target.path], capture_output=True, text=True)
        if process.stderr:
            logging.warning(f'failed to get mime_type of {self.target.value}: {process.stderr}')
        self.details.mime_type = process.stdout.strip()

        # convert non linux mime types to linux mime type so we get the same result regardless of platform
        if self.details.mime_type in mime_type_conversion_map:
            self.details.mime_type = mime_type_conversion_map[self.details.mime_type]

        # determine if file is ole
        with open(self.target.path, 'rb') as f:
            if f.read(8) == b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1':
                self.target.add(Tag, 'ole')

        # determine if file is rtf
        with open(self.target.path, 'rb') as f:
            data = f.read(4)
            if data[:3] == b'\\rt' or data == b'{\\rt':
                self.target.add(Tag, 'rtf')

        # determine if file is pdf
        with open(self.target.path, 'rb') as f:
            if b'%PDF-' in f.read(1024):
                self.target.add(Tag, 'pdf')

        # determine if file is an executable
        with open(self.target.path, 'rb') as f:
            if f.read(2) == b'MZ':
                self.target.add(Tag, 'executable')

        # determine if file is a jar or zip file by attempting to read the namelist
        try:
            with ZipFile(self.target.path, 'r') as f:
                if f.namelist():
                    self.target.add(Tag, 'zip')
        except:
            pass

        # determine if file is a lnk
        with open(self.target.path, 'rb') as f:
            if f.read(8) == b'\x4C\x00\x00\x00\x01\x14\x02\x00':
                self.target.add(Tag, 'lnk')

        # determine if file is x509
        with open(self.target.path, 'rb') as f:
            data = f.read()
            try:
                x509.load_pem_x509_certificate(data, backend=default_backend())
                is_x509 = True
            except:
                try:
                    x509.load_der_x509_certificate(data, backend=None)
                    is_x509 = True
                except:
                    is_x509 = False
            if is_x509:
                self.target.add(Tag, 'x509')
                if self.details.file_type in ['data', 'Certificate, Version=3']:
                    self.details.file_type = 'DER certificate'

        # determine if file is jar
        try:
            with ZipFile(self.target.path, 'r') as f:
                if 'META-INF/MANIFEST.MF' in f.namelist():
                    self.target.add(Tag, 'jar')
        except:
            pass

        # determine if file is office document
        is_office_document = self.target.extension in [
            # see https://en.wikipedia.org/wiki/List_of_Microsoft_Office_filename_extensions
            # 2/19/2018 - removed MSO file ext (relying on OLE format instead)
            # 6/29/2018 - https://docs.google.com/spreadsheets/d/1LXneVF8VxmOgkt2W_NG5Kl3lzWW45prE7gxtuPcO-4o/edit#gid=1950593040
            # Microsoft Word
            'doc',
            'docb',
            'dochtml',
            'docm',
            'docx',
            'docxml',
            'dot',
            'dothtml',
            'dotm',
            'dotx',
            'odt',
            'rtf',
            'wbk',
            'wiz',
            # Microsoft Excel
            'csv',
            'dqy',
            'iqy',
            'odc',
            'ods',
            'slk',
            'xla',
            'xlam',
            'xlk',
            'xll',
            'xlm',
            'xls',
            'xlsb',
            'xlshtml',
            'xlsm',
            'xlsx',
            'xlt',
            'xlthtml',
            'xltm',
            'xltx',
            'xlw',
            # Microsoft Powerpoint
            'odp',
            'pot',
            'pothtml',
            'potm',
            'potx',
            'ppa',
            'ppam',
            'pps',
            'ppsm',
            'ppsx',
            'ppt',
            'ppthtml',
            'pptm',
            'pptx',
            'pptxml',
            'pwz',
            'sldm',
            'sldx',
            'thmx',
            # OpenOffice
            'odt',
        ]
        is_office_document |= 'microsoft powerpoint' in self.details.file_type.lower()
        is_office_document |= 'microsoft excel' in self.details.file_type.lower()
        is_office_document |= 'microsoft word' in self.details.file_type.lower()
        is_office_document |= 'microsoft ooxml' in self.details.file_type.lower()
        is_office_document |= 'ole' in self.target.tags
        is_office_document |= 'rtf' in self.target.tags
        if is_office_document:
            self.target.add(Tag, 'microsoft_office')

        # set the summary
        self.summary = f'FileType: ({self.details.file_type}) ({self.details.mime_type})'

        # submit analysis
        self.submit()
