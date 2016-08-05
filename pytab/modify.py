# @author = 'Simon Dirmeier'
# @email = 'rafstraumur@simon-dirmeier.net'
from pytab._check import _is_table, _is_callable, _has_elements, _is_none
from pytab._callable import Callable


def modify(obj, f, new_col=None, *args):
    if _is_table(obj):
        return _modify_plain_table(obj, f, new_col, *args)

def _modify_plain_table(obj, f, new_col, *args):
    if _is_callable(f) and not _is_none(new_col) and _has_elements(*args):
        __do_modify(obj, f, new_col, *args)
    return obj

def __do_modify(obj, f, new_col, *col_names):
    colvals = [obj[x] for x in col_names]
    if colvals is None:
        return
    res = f()(colvals)
    if res.size != len(colvals):
       raise ValueError("The function you provided yields an array of false length!")
    obj._cbind(**{new_col: res})
    return obj
