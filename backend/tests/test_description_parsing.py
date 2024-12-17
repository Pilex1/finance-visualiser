import unittest
from src.database import Database


class TestDescriptionParsing(unittest.TestCase):

    def test_direct_debit_paypal(self):
        self.assertTupleEqual(Database.process_description(
            "Direct Debit 617704 PAYPAL AUSTRALIA 1033287233710"), ("Paypal", True))

    def test_refund_purchase_beem(self):
        self.assertTupleEqual(Database.process_description(
            "Refund Purchase Beem A187D0759D174397Aca54F5Bcda5C1C0"), ("Beem", True))
