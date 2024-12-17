from typing import Sequence

import numpy as np


def convolve_smooth(x: Sequence[float]) -> float:
    """

    Args:
        x: assumed to be equidistant points in [-1, 1]
    """

    def bump(y): return np.exp(-1/(1-y**2))
    n = len(x)
    # scaling should be done in a way so that if the inputs are all 1s, then the output should be 1
    scaling = np.sum(np.ones(n) * bump(np.linspace(1, -1, n, endpoint=True)))

    return np.sum(x * bump(np.linspace(1, -1, n, endpoint=True))) / scaling
