from __future__ import annotations
import math
from typing import Tuple, Optional, Dict

def american_to_decimal(american: float) -> float:
    if american > 0:
        return 1 + american / 100.0
    else:
        return 1 + 100.0 / abs(american)

def decimal_to_american(decimal_odds: float) -> int:
    if decimal_odds >= 2.0:
        return int(round((decimal_odds - 1.0) * 100))
    else:
        return int(round(-100.0 / (decimal_odds - 1.0)))

def implied_prob_from_decimal(decimal_odds: float) -> float:
    return 1.0 / decimal_odds

def implied_prob_from_american(american: float) -> float:
    return implied_prob_from_decimal(american_to_decimal(american))

def remove_vig_two_way(p1: float, p2: float) -> Tuple[float, float]:
    """De-vig 2-way market given sportsbook implied probs p1+p2>1.
    Returns normalized fair probabilities that sum to 1.
    """
    total = p1 + p2
    if total <= 0:
        return (0.0, 0.0)
    return (p1 / total, p2 / total)

def remove_vig_three_way(p1: float, p2: float, p3: float) -> Tuple[float, float, float]:
    total = p1 + p2 + p3
    if total <= 0:
        return (0.0, 0.0, 0.0)
    return (p1 / total, p2 / total, p3 / total)

def fair_odds_from_true_prob(p: float) -> float:
    if p <= 0: 
        return math.inf
    return 1.0 / p

def edge_decimal(offer_decimal: float, true_prob: float) -> float:
    """Expected return per $1 staked in decimal odds space minus 1.
    EV% ~ (offer_decimal * true_prob) - 1.
    """
    return (offer_decimal * true_prob) - 1.0

def kelly_fraction(true_prob: float, offer_decimal: float) -> float:
    """Full Kelly fraction for decimal odds; b = offer_decimal - 1.
    f* = (bp - q)/b where q=1-p. If negative, return 0.
    """
    b = offer_decimal - 1.0
    p = true_prob
    q = 1.0 - p
    if b <= 0: 
        return 0.0
    f = (b * p - q) / b
    return max(0.0, f)

def estimate_true_prob_from_ref(american_ref: Optional[float], fallback_margin: float, side_implied: float, opp_implied: float) -> float:
    """If a sharp reference price is available (american_ref), use its implied prob.
    Otherwise, de-vig using the market pair and return the fair prob for the side.
    fallback_margin is unused here except to allow future adjustments.
    """
    if american_ref is not None:
        return implied_prob_from_american(american_ref)
    # fallback to de-vig between the two sides
    fair1, fair2 = remove_vig_two_way(side_implied, opp_implied)
    return fair1
