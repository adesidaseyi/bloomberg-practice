import pytest

from gameserver.errors import ValidationError


def collect_remaining(api, first_page, limit):
    seen = [item["player_id"] for item in first_page["items"]]
    cursor = first_page["next_cursor"]
    while cursor is not None:
        page = api.list_pairs(cursor=cursor, limit=limit)
        seen.extend(item["player_id"] for item in page["items"])
        cursor = page["next_cursor"]
    return seen


def test_single_traversal_returns_every_paired_player_once(server, pair_up):
    pair_up(server, [f"a{i}" for i in range(6)])
    seen = collect_remaining(server.api, server.api.list_pairs(limit=4), limit=4)
    assert sorted(seen) == [f"a{i}" for i in range(6)]


def test_list_pairs_validates_limit(server):
    with pytest.raises(ValidationError):
        server.api.list_pairs(limit=0)


def test_no_duplicates_when_new_pairs_form_between_pages(server, clock, pair_up):
    pair_up(server, [f"a{i}" for i in range(6)])
    page1 = server.api.list_pairs(limit=4)

    clock.advance(10)
    pair_up(server, ["b0", "b1"])  # newest pairing sorts to the head of the list

    seen = collect_remaining(server.api, page1, limit=4)
    assert len(seen) == len(set(seen)), f"duplicates in {seen}"
    assert {f"a{i}" for i in range(6)} <= set(seen)


def test_no_skips_when_a_player_is_unpaired_between_pages(server, pair_up):
    pair_up(server, [f"a{i}" for i in range(6)])
    page1 = server.api.list_pairs(limit=3)  # a0, a1, a2

    server.lobby_service.unpair("a0")  # already returned on page 1

    seen = collect_remaining(server.api, page1, limit=3)
    assert {"a3", "a4", "a5"} <= set(seen), f"skipped players in {seen}"
    assert len(seen) == len(set(seen))
