from .P61ANexusReader import P61ANexusReader
from .XSpressCSVReader import XSpressCSVReader
from .RawFileReader import RawFileReader
from .EDDIReader import EDDIReader
from .XYReader import XYReader

DatasetReaders = (
    P61ANexusReader,
    XSpressCSVReader,
    EDDIReader,
    XYReader,
    RawFileReader
)
