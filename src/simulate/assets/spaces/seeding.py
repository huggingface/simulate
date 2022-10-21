# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import hashlib
import os
import struct
from typing import List, Optional, Tuple, Union

import numpy as np


def np_random(seed: Optional[Union[int, str]] = None) -> Tuple[np.random.RandomState, int]:
    """
    Create a numpy random state seeded from a random seed.

    Args:
        seed (`int` or `str`, *optional*, defaults to `None`):
            Random seed to use.

    Returns:
        rng (`numpy.random.RandomState`):
            Random state seeded from the given seed.
        seed (`int`):
            Seed used to seed the random state.
    """
    if seed is not None and not (isinstance(seed, int) and 0 <= seed):
        raise ValueError("Seed must be a non-negative integer or omitted, not {}".format(seed))

    seed = create_seed(seed)
    rng = np.random.RandomState()
    rng.seed(_int_list_from_bigint(hash_seed(seed)))
    return rng, seed


def hash_seed(seed: Optional[int] = None, max_bytes: int = 8) -> int:
    """
    Any given evaluation is likely to have many PRNG's active at
    once. (Most commonly, because the environment is running in
    multiple processes.) There's literature indicating that having
    linear correlations between seeds of multiple PRNG's can correlate
    the outputs:

    http://blogs.unity3d.com/2015/01/07/a-primer-on-repeatable-random-numbers/
    http://stackoverflow.com/questions/1554958/how-different-do-random-seeds-need-to-be
    http://dl.acm.org/citation.cfm?id=1276928

    Thus, for sanity we hash the seeds before using them. (This scheme
    is likely not crypto-strength, but it should be good enough to get
    rid of simple correlations.)

    Args:
        seed (`int`, *optional*, defaults to `None`):
            None seeds from an operating system specific randomness source.
        max_bytes (`int`, *optional*, defaults to `8`):
            Maximum number of bytes to use in the hashed seed.
    """
    if seed is None:
        seed = create_seed(max_bytes=max_bytes)
    seed_hash = hashlib.sha512(str(seed).encode("utf8")).digest()
    return _bigint_from_bytes(seed_hash[:max_bytes])


def create_seed(a: Optional[Union[int, str]] = None, max_bytes: int = 8) -> int:
    """
    Create a strong random seed. Otherwise, Python 2 would seed using
    the system time, which might be non-robust especially in the
    presence of concurrency.

    Args:
        a (`int` or `str`, *optional*, defaults to `None`):):
            None seeds from an operating system specific randomness source.
        max_bytes (`int`, *optional*, defaults to `8`)::
            Maximum number of bytes to use in the seed.

    Returns:
        seed (`int`):
            Seed used to seed the random state.
    """
    # Adapted from https://svn.python.org/projects/python/tags/r32/Lib/random.py
    if a is None:
        a = _bigint_from_bytes(os.urandom(max_bytes))
    elif isinstance(a, str):
        a = a.encode("utf8")
        a += hashlib.sha512(a).digest()
        a = _bigint_from_bytes(a[:max_bytes])
    elif isinstance(a, int):
        a = a % 2 ** (8 * max_bytes)
    else:
        raise ValueError("Invalid type for seed: {} ({})".format(type(a), a))
    return a


# TODO: don't hardcode sizeof_int here
def _bigint_from_bytes(bytes_data: bytes) -> int:
    """
    Convert a byte string to a big integer.

    Args:
        bytes_data (`bytes`):
            Bytes to convert to a big integer.

    Returns:
        bigint (`int`):
            Big integer representation of the given bytes.
    """
    sizeof_int = 4
    padding = sizeof_int - len(bytes_data) % sizeof_int
    bytes_data += b"\0" * padding
    int_count = int(len(bytes_data) / sizeof_int)
    unpacked = struct.unpack("{}I".format(int_count), bytes_data)
    accum = 0
    for i, val in enumerate(unpacked):
        accum += 2 ** (sizeof_int * 8 * i) * val
    return accum


def _int_list_from_bigint(bigint: int) -> List[int]:
    """
    Convert a big integer to a list of integers.

    Args:
        bigint (`int`):
            Big integer to convert.

    Returns:
        int_list (`list`):
            List of integers representation of the given big integer.
    """
    # Special case 0
    if bigint < 0:
        raise ValueError("Seed must be non-negative, not {}".format(bigint))
    elif bigint == 0:
        return [0]

    ints = []
    while bigint > 0:
        bigint, mod = divmod(bigint, 2**32)
        ints.append(mod)
    return ints
