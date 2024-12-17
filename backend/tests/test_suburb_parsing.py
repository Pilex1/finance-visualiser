import unittest
from src.database import Database


class TestSuburbParsing(unittest.TestCase):

    def test_ultimo(self):
        self.assertTupleEqual(Database.get_suburb_info("TASTE LEGEND AUS ULTIMO NSW AU"),
                              ("TASTE LEGEND AUS", "ULTIMO NSW AU"))

    def test_cronullansw(self):
        self.assertTupleEqual(Database.get_suburb_info("LLOYDS IGA CRONULLANSW NS AUS"),
                              ("LLOYDS IGA", "CRONULLANSW NS AUS"))

    def test_edenhope(self):
        self.assertTupleEqual(Database.get_suburb_info("BENTLEYS FUEL SERVIC EDENHOPE AU"),
                              ("BENTLEYS FUEL SERVIC", "EDENHOPE AU"))

    def test_7fresh(self):
        self.assertTupleEqual(Database.get_suburb_info("7FRESH CAMPBELLTOWN7FRESHEPPING AU"),
                              ("7FRESH CAMPBELLTOWN7FRESH", "EPPING AU"))

    def test_wisemans_ferr(self):
        self.assertTupleEqual(Database.get_suburb_info("Q KHAN & M.T RANA WISEMANS FERR NS AUS"),
                              ("Q KHAN & M.T RANA", "WISEMANS FERR NS AUS"))

    def test_sydney_south(self):
        self.assertTupleEqual(Database.get_suburb_info("AMAZON AU SYDNEY SOUTH NS AUS"),
                              ("AMAZON AU SYDNEY SOUTH NS AUS", None))

    def test_wenworth_f(self):
        self.assertTupleEqual(Database.get_suburb_info("CONDITOREI PATISSERIE WENTWORTH F NSW AU"),
                              ("CONDITOREI PATISSERIE", "WENTWORTH F NSW AU"))

    def test_mangrove_moun(self):
        self.assertTupleEqual(Database.get_suburb_info("SMP*The Hub Of Mangro Mangrove Moun AU AUS"),
                              ("SMP*The Hub Of Mangro", "Mangrove Moun AU AUS"))

    def test_terrey_h(self):
        self.assertTupleEqual(Database.get_suburb_info("TERREY HILLS SUPERMARKET TERREY H NSW AU"),
                              ("TERREY HILLS SUPERMARKET", "TERREY H NSW AU"))
