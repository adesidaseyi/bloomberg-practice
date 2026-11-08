import unittest

from ratelimit import RateLimiter, _Window


class TestRateLimiter(unittest.TestCase):
    def test_allow_allows_after_stale_window_for_exceeded_existing_key(self):
        now = 1000.0

        def fake_clock():
            return now

        limiter = RateLimiter(limit=2, window_seconds=10, clock=fake_clock)
        limiter._state["existing_key"] = _Window(start=now - 11, count=2)

        now = 1020.0

        self.assertTrue(limiter.allow("existing_key"))


if __name__ == "__main__":
    unittest.main()
