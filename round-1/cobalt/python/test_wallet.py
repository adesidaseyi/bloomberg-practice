import unittest

from wallet import WalletService


class WalletServiceTests(unittest.TestCase):
    def test_authorized_funds_cannot_be_spent_twice(self) -> None:
        wallet = WalletService()
        wallet.open_account("customer-1", 1_000)

        wallet.authorize("customer-1", 700)

        self.assertEqual(wallet.balance("customer-1"), 1_000)
        self.assertEqual(wallet.available("customer-1"), 300)

        with self.assertRaisesRegex(ValueError, "insufficient available funds"):
            wallet.authorize("customer-1", 301)






