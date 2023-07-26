from .mospolytech import mospolytech_parser as mospolytech
from .mirea import mirea_parser as mirea
from .mtuci import mtuci_parser as mtuci
from .mpei import mpei_parser as mpei
from .gubkin import gubkin_parser as gubkin
from .mai import mai_parser as mai
from .misis import misis_parser as misis
from .rea import rea_parser as rea
from .miigaik import miigaik_parser as miigaik

parsers = [mtuci, mospolytech, mai, mirea, misis, mpei, gubkin, rea, miigaik]
