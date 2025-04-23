from typing import List, Tuple
from itertools import combinations
from collections import Counter


RANK_VALUE = {
        '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
        '8': 8, '9': 9, 'T': 10, 'J': 11, 'Q': 12, 'K': 13, 'A': 14
    }
    

def evaluate_5card_hand_detailed(cards: List[Tuple[str, str]]) -> Tuple[int, List[int]]:
    """
    Evaluate exactly 5 cards. Return (category, tiebreakers).

    category is an int in [1..9], where lower is better:
        1 = Straight Flush
        2 = Four of a Kind
        3 = Full House
        4 = Flush
        5 = Straight
        6 = Three of a Kind
        7 = Two Pair
        8 = One Pair
        9 = High Card

    tiebreakers is a list of integers (descending significance),
    e.g. for a Full House: [rank_of_trips, rank_of_pair].
    For a Flush or High Card: sorted ranks descending, etc.

    We compare two hands by:
    1. category ascending (1 is best)
    2. if category ties, compare tiebreakers lexicographically, where bigger is better.
    """
    rank_vals = [RANK_VALUE[r] for (r, s) in cards]
    suits = [s for (r, s) in cards]

    rank_vals.sort(reverse=True)
    freq = Counter(rank_vals)  # e.g. {14:4, 9:1} for four Aces
    counts_desc = sorted(freq.values(), reverse=True)

    # Check for flush
    is_flush = (len(set(suits)) == 1)

    # Check for straight (including special A-2-3-4-5)
    def is_consecutive(vals: List[int]) -> bool:
        return all(vals[i] == vals[i+1] + 1 for i in range(len(vals)-1))
    is_straight = is_consecutive(rank_vals)

    # Special case: A-2-3-4-5 => treat top card as 5
    if not is_straight and set(rank_vals) == {14, 5, 4, 3, 2}:
        is_straight = True

    if is_straight:
        # The "top" card in a normal straight is rank_vals[0].
        # But for A-2-3-4-5, we treat top_straight=5
        if set(rank_vals) == {14, 5, 4, 3, 2}:
            top_straight = 5
        else:
            top_straight = rank_vals[0]

    # Sort freq by (count DESC, rank_val DESC)
    freq_sorted = sorted(freq.items(), key=lambda x: (x[1], x[0]), reverse=True)

    # 1) Straight Flush
    if is_straight and is_flush:
        return (1, [top_straight])

    # 2) Four of a Kind
    if counts_desc[0] == 4:
        # freq_sorted[0] => (rank_of_quads, 4)
        # freq_sorted[1] => (kicker, 1)
        rank_of_quads = freq_sorted[0][0]
        kicker = freq_sorted[1][0]
        return (2, [rank_of_quads, kicker])

    # 3) Full House (3 + 2)
    if counts_desc == [3, 2]:
        rank_of_trips = freq_sorted[0][0]
        rank_of_pair = freq_sorted[1][0]
        return (3, [rank_of_trips, rank_of_pair])

    # 4) Flush
    if is_flush:
        # Just compare the five ranks in descending order
        return (4, rank_vals)

    # 5) Straight
    if is_straight:
        return (5, [top_straight])

    # 6) Three of a Kind
    if counts_desc[0] == 3:
        # freq_sorted[0] => (trip_rank, 3)
        trip_rank = freq_sorted[0][0]
        # The other two are kickers
        kickers = sorted((r for (r, c) in freq_sorted[1:] for _ in range(c)), reverse=True)
        return (6, [trip_rank] + kickers)

    # 7) Two Pair
    if len(counts_desc) >= 2 and counts_desc[0] == 2 and counts_desc[1] == 2:
        # freq_sorted[0] => (highPair, 2)
        # freq_sorted[1] => (lowPair, 2)
        # freq_sorted[2] => (kicker, 1)
        high_pair = freq_sorted[0][0]
        low_pair = freq_sorted[1][0]
        kicker = freq_sorted[2][0]
        return (7, [high_pair, low_pair, kicker])

    # 8) One Pair
    if counts_desc[0] == 2:
        pair_rank = freq_sorted[0][0]
        # The rest are kickers
        kickers = sorted((r for (r, c) in freq_sorted[1:] for _ in range(c)), reverse=True)
        return (8, [pair_rank] + kickers)

    # 9) High Card
    return (9, rank_vals)


def evaluate_7card_hand_detailed(seven_cards: List[Tuple[str, str]]) -> Tuple[int, List[int]]:
    """
    Evaluate 7 cards (2 hole + 5 community) by picking the best 5-card subset.
    Returns (category, tiebreakers).
    """
    best = (9, [-1, -1, -1, -1, -1])  # something "worst" by default
    for combo in combinations(seven_cards, 5):
        cat, tie = evaluate_5card_hand_detailed(list(combo))
        # Compare to current best:
        #  - cat ascending
        #  - if cat ties, tiebreak descending
        if cat < best[0]:
            best = (cat, tie)
        elif cat == best[0] and tie > best[1]:
            best = (cat, tie)
    return best



