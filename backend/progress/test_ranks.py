import pytest
from progress.ranks import rank_for_xp, tier_change


@pytest.mark.parametrize('xp,rank', [(-1,'bronce'),(0,'bronce'),(499,'bronce'),(500,'plata'),
                                    (1199,'plata'),(1200,'oro'),(2499,'oro'),(2500,'diamante')])
def test_rank_boundaries(xp, rank):
    result = rank_for_xp(xp)
    assert result['id'] == rank
    assert 0 <= result['progressPercent'] <= 100 and result['xpToNext'] >= 0


def test_tier_change_requires_crossing_threshold():
    assert tier_change(499, 500)[1] is True
    assert tier_change(500, 501)[1] is False
    assert rank_for_xp(3000)['nextRank'] is None
