"""
Test for wfc binding with c++.
"""

from wfc_binding import run_wfc

run_wfc(10, 10, 1, periodic_output=True, symmetry=4, nb_samples=1, ground=False, periodic_input=False, N=3, test=b"helloworld")