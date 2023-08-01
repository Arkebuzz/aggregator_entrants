from .mospolytech import mospolytech_parser as mospolytech
from .mirea import mirea_parser as mirea
from .mtuci import mtuci_parser as mtuci
from .mpei import mpei_parser as mpei
from .gubkin import gubkin_parser as gubkin
from .mai import mai_parser as mai
from .misis import misis_parser as misis
from .rea import rea_parser as rea
from .miigaik import miigaik_parser as miigaik
from .mephi import mephi_parser as mephi
from .bmstu import bmstu_parser_moscow as bmstu_moscow
from .bmstu import bmstu_parser_mitishi as bmstu_mitishi

parsers = [mtuci, mospolytech, mai, mirea, misis, mpei, gubkin, rea, miigaik, mephi, bmstu_moscow, bmstu_mitishi]
