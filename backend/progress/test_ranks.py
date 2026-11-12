import pytest
from progress.ranks import rank_for_xp, tier_change


@pytest.mark.parametrize('xp,rank', [(-1,'bronce'),(0,'bronce'),(149,'bronce'),(150,'plata'),
                                    (399,'plata'),(400,'oro'),(799,'oro'),(800,'diamante')])
def test_rank_boundaries(xp, rank):
    result = rank_for_xp(xp)
    assert result['id'] == rank
    assert 0 <= result['progressPercent'] <= 100 and result['xpToNext'] >= 0


def test_tier_change_requires_crossing_threshold():
    assert tier_change(149,150)[1] is True
    assert tier_change(150,151)[1] is False
    assert rank_for_xp(1000)['nextRank'] is None
