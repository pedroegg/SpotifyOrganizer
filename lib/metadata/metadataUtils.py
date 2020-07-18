import statistics

def recalculateDP(array: [], value: float) -> float:
    arr = array.copy()
    arr.append(value)
    return float("{:.3f}".format(statistics.pstdev(arr)))