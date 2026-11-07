from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import unittest


class HoldStatus(str, Enum):
    HELD = "held"
    CAPTURED = "captured"
    VOIDED = "voided"


@dataclass
class Hold:
    hold_id: str
    account_id: str
    amount: int
    status: HoldStatus


class WalletService:
    """A wallet with authorization holds. Funds are authorized (reserved), then
    either captured (settled out of the balance) or voided (released). All amounts
    are integer cents. Available funds are the balance minus active holds."""

    def __init__(self) -> None:
        # Create the in-memory state for balances, active holds, and hold IDs.
        self._balance: dict[str, int] = {}
        self._holds: dict[str, Hold] = {}
        self._seq = 0

    def open_account(self, account_id: str, cents: int) -> None:
        # Create a new account with an initial balance measured in cents.
        if cents < 0:
            raise ValueError("opening balance must be non-negative")
        self._balance[account_id] = cents

    def balance(self, account_id: str) -> int:
        # Return the raw account balance without subtracting any active holds.
        return self._require(account_id)

    def available(self, account_id: str) -> int:
        # Return the funds that are currently spendable after active holds.
        bal = self._require(account_id)
        return bal - self._active_holds(account_id)

    def authorize(self, account_id: str, cents: int) -> Hold:
        # Reserve funds by creating a held authorization for the requested amount.
        self._require(account_id)
        if cents <= 0:
            raise ValueError("amount must be positive")
        if self.available(account_id) < cents:
            raise ValueError("insufficient available funds")
        self._seq += 1
        hid = f"H{self._seq}"
        h = Hold(hid, account_id, cents, HoldStatus.HELD)
        self._holds[hid] = h
        return h

    def capture(self, hold_id: str) -> Hold:
        # Settle an active hold by reducing the account balance and marking it captured.
        h = self._get(hold_id)
        if h.status != HoldStatus.HELD:
            raise ValueError(f"cannot capture a hold with status {h.status.value}")
        self._balance[h.account_id] -= h.amount
        h.status = HoldStatus.CAPTURED
        return h

    def void(self, hold_id: str) -> Hold:
        # Release an active hold without affecting the balance.
        h = self._get(hold_id)
        if h.status != HoldStatus.HELD:
            raise ValueError(f"cannot void a hold with status {h.status.value}")
        h.status = HoldStatus.VOIDED
        return h

    def _active_holds(self, account_id: str) -> int:
        # Sum the amounts on all currently active holds for a specific account.
        return sum(h.amount for h in self._holds.values()
                   if h.account_id == account_id and h.status == HoldStatus.HELD)

    def _require(self, account_id: str) -> int:
        # Validate that the account exists and return its balance.
        if account_id not in self._balance:
            raise ValueError("unknown account")
        return self._balance[account_id]

    def _get(self, hold_id: str) -> Hold:
        # Fetch a hold by ID and raise an error if the hold does not exist.
        h = self._holds.get(hold_id)
        if h is None:
            raise ValueError("hold not found")
        return h


class WalletServiceTests(unittest.TestCase):
    def test_authorized_funds_cannot_be_spent_twice(self) -> None:
        wallet = WalletService()
        wallet.open_account("customer-1", 1_000)

        wallet.authorize("customer-1", 700)

        self.assertEqual(wallet.balance("customer-1"), 1_000)
        self.assertEqual(wallet.available("customer-1"), 300)

        with self.assertRaisesRegex(ValueError, "insufficient available funds"):
            wallet.authorize("customer-1", 301)

    def test_voiding_an_already_voided_hold_raises_error(self) -> None:
        wallet = WalletService()
        wallet.open_account("customer-1", 1_000)
        hold = wallet.authorize("customer-1", 700)

        wallet.void(hold.hold_id)
        with self.assertRaisesRegex(ValueError, "cannot void a hold with status voided"):
            wallet.void(hold.hold_id)

        self.assertEqual(wallet.balance("customer-1"), 1_000)
        self.assertEqual(wallet.available("customer-1"), 1_000)
        self.assertEqual(hold.status, HoldStatus.VOIDED)

    def test_voiding_a_captured_hold_raises_error(self) -> None:
        wallet = WalletService()
        wallet.open_account("customer-1", 1_000)
        hold = wallet.authorize("customer-1", 700)
        wallet.capture(hold.hold_id)

        with self.assertRaisesRegex(ValueError, "cannot void a hold with status captured"):
            wallet.void(hold.hold_id)

        self.assertEqual(wallet.balance("customer-1"), 300)
        self.assertEqual(hold.status, HoldStatus.CAPTURED)

    def test_cannot_capture_a_voided_hold(self) -> None:
        wallet = WalletService()
        wallet.open_account("customer-1", 1_000)
        hold = wallet.authorize("customer-1", 700)
        wallet.void(hold.hold_id)

        with self.assertRaisesRegex(ValueError, "cannot capture a hold with status voided"):
            wallet.capture(hold.hold_id)

        self.assertEqual(wallet.balance("customer-1"), 1_000)
        self.assertEqual(wallet.available("customer-1"), 1_000)
        self.assertEqual(hold.status, HoldStatus.VOIDED)


if __name__ == "__main__":
    unittest.main()
