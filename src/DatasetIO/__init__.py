from .P61ANexusReader import P61ANexusReader
from .XSpressCSVReader import XSpressCSVReader
from .RawFileReader import RawFileReader

DatasetReaders = (
    P61ANexusReader,
    XSpressCSVReader,
    RawFileReader
)
