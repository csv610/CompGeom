def compute_min_singularity_patch(l1: int, l2: int, l3: int) -> list[int]:
def compute_min_singularity_patch_5(l1: int, l2: int, l3: int):
    """
    Compute min singularity patch for 3 edges (triangle case).
    Returns [a1, a2, b1, b2, c1, c2] edge length decomposition.
    """
    if (l1 + l2 + l3) % 2 != 0:
        return []

    a1 = (l1 + l2 - l3) / 2
    b1 = (l2 - l1 + l3) / 2
    c1 = (l1 - l2 + l3) / 2

    a2 = l1 - a1
    b2 = l2 - b1
    c2 = l3 - c1

    values = [a1, a2, b1, b2, c1, c2]
    if not all(isinstance(v, int) and v > 0 for v in values):
        return []

    return values


def compute_min_singularity_patch_5(l1: int, l2: int, l3: int, l4: int, l5: int):
    """
    Compute min singularity patch for 5 edges (pentagon case).
    Returns [a1, a2, b1, b2, c1, c2, d1, d2, e1, e2] edge length decomposition.
    """
    if (l1 + l2 + l3 + l4 + l5) % 2 != 0:
        return []

    a1 = (l1 - l2 - l3 + l4 + l5) / 2
    b1 = (l1 + l2 - l3 - l4 + l5) / 2
    c1 = (l1 + l2 + l3 - l4 - l5) / 2
    d1 = (-l1 + l2 + l3 + l4 - l5) / 2
    e1 = (-l1 - l2 + l3 + l4 + l5) / 2

    a2 = l1 - a1
    b2 = l2 - b1
    c2 = l3 - c1
    d2 = l4 - d1
    e2 = l5 - e1

    values = [a1, a2, b1, b2, c1, c2, d1, d2, e1, e2]
    if not all(isinstance(v, int) and v > 0 for v in values):
        return []

    return values


def is_valid_min_singularity_patch(l1: int, l2: int, l3: int, l4: int) -> bool:
    """
    Check if 4 edges form a valid min singularity patch.
    """
    result = compute_min_singularity_patch(int(l1 - l3), l2, l4)
    return len(result) > 0
