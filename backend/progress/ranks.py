# Umbrales de XP para cada rango. Son un punto de partida: se ajustan aquí.
RANKS = [
    {"id": "bronce", "name": "Bronce", "min_xp": 0},
    {"id": "plata", "name": "Plata", "min_xp": 150},
    {"id": "oro", "name": "Oro", "min_xp": 400},
    {"id": "diamante", "name": "Diamante", "min_xp": 800},
]


def rank_for_xp(xp) -> dict:
    xp = max(int(xp or 0), 0)

    current = RANKS[0]
    for rank in RANKS:
        if xp >= rank["min_xp"]:
            current = rank

    index = RANKS.index(current)
    next_rank = RANKS[index + 1] if index + 1 < len(RANKS) else None

    if next_rank:
        span = next_rank["min_xp"] - current["min_xp"]
        percent = round((xp - current["min_xp"]) / span * 100)
        xp_to_next = next_rank["min_xp"] - xp
    else:
        percent = 100
        xp_to_next = 0

    return {
        "id": current["id"],
        "name": current["name"],
        "xp": xp,
        "minXp": current["min_xp"],
        "nextRank": next_rank["name"] if next_rank else None,
        "xpToNext": xp_to_next,
        "progressPercent": percent,
    }


def tier_change(xp_before, xp_after):
    """Devuelve el rango actual y si el alumno acaba de subir de rango."""
    before = rank_for_xp(xp_before)
    after = rank_for_xp(xp_after)
    return after, before["id"] != after["id"]