import pytest

from match import Match


class TestNeedsConfirmation:
    @pytest.fixture
    def a_match(self) -> Match:
        return Match()

    def test_no_confirm_if_both_set(self, a_match: Match):
        a_match.conf1 = "A_USER"
        a_match.conf2 = "ANOTHER_USER"

        assert not a_match.needs_confirmations()

    def test_needs_confirm_if_first_not_set(self, a_match: Match):
        a_match.conf1 = ""
        a_match.conf2 = "ANOTHER_USER"

        assert a_match.needs_confirmations()

    def test_needs_confirm_if_second_not_set(self, a_match: Match):
        a_match.conf2 = ""
        a_match.conf1 = "A_USER"

        assert a_match.needs_confirmations()


class TestCanBeDeleted:
    @pytest.fixture
    def sig(self) -> [Match, str, list[str]]:
        m = Match()
        m.score_posted = False
        m.clans1_ids = ["FIRST_CLAN", "SECOND_CLAN"]
        m.clans2_ids = ["SECOND_CLAN"]
        return [m, "A_USER_ID"]

    def test_member_of_first_clans(self, sig: [Match, str]):
        m, user_id = sig

        assert m.can_be_deleted(user_id, m.clans1_ids)

    def test_member_of_second_clans(self, sig: [Match, str]):
        m, user_id = sig

        assert m.can_be_deleted(user_id, m.clans2_ids)

    def test_confirmer_of_first_clan(self, sig: [Match, str]):
        m, user_id = sig
        m.conf1 = user_id

        assert m.can_be_deleted(user_id, [])

    def test_confirmer_of_second_clan(self, sig: [Match, str]):
        m, user_id = sig
        m.conf2 = user_id

        assert m.can_be_deleted(user_id, [])

    def test_no_permission_to_delete(self, sig: [Match, str]):
        m, user_id = sig

        assert not m.can_be_deleted(user_id, [])
