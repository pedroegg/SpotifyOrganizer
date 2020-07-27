import statistics

def recalculateDP(array: list, value: float) -> float:
    arr = array.copy()
    arr.append(value)
    return float("{:.3f}".format(statistics.pstdev(arr)))