from .mospolytech import mospolytech_parser as mospolytech
from .mirea import mirea_parser as mirea
from .mtuci import mtuci_parser as mtuci
from .mpei import mpei_parser as mpei
from .gubkin import gubkin_parser as gubkin
from .mai import mai_parser as mai

parsers = [mtuci, mospolytech, mai, mirea, mpei, gubkin]
