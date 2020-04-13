import numpy as np

from ..core import ProxyTypeError
from ..core.promote import _promote
from ..primitives import Float, Int, Bool
from ..array import Array, MaskedArray, BaseArray


def _ufunc_result_type(obj, other=None, return_type_override=None):
    if other is None:
        if return_type_override is None:
            return type(obj)
        return return_type_override if not isinstance(obj, BaseArray) else type(obj)

    if return_type_override is not None:
        dtype = return_type_override
    else:
        obj_dtype, other_dtype = (
            Float if isinstance(a, BaseArray) else type(a) for a in (obj, other)
        )

        # If either are Float, the result is a Float
        if obj_dtype is Float or other_dtype is Float:
            dtype = Float
        # Neither are Float, so if either are Int, the result is an Int
        elif obj_dtype is Int or other_dtype is Int:
            dtype = Int
        # Neither are Float, neither are Int, they must be Bool, so the result is Bool
        else:
            dtype = Bool

    if isinstance(obj, MaskedArray) or isinstance(other, MaskedArray):
        return MaskedArray
    elif isinstance(obj, Array) or isinstance(other, Array):
        return Array
    else:
        return dtype


def derived_from(original_method):
    """Decorator to attach original method's docstring to the wrapped method"""

    def wrapper(method):
        doc = original_method.__doc__.replace("*,", "\*,")  # noqa
        doc = doc.replace(
            ":ref:`ufunc docs <ufuncs.kwargs>`.",
            "`ufunc docs <https://docs.scipy.org/doc/numpy/reference/ufuncs.html#ufuncs-kwargs>`_.",
        )

        # remove examples
        doc = doc.split("\n\n    Examples\n")[0]

        # remove references
        doc = [a for a in doc.split("\n\n") if "References\n----------\n" not in a]

        # remove "See Also" section
        doc = [a for a in doc if "See Also\n" not in a]

        l1 = "This docstring was copied from numpy.{}".format(original_method.__name__)
        l2 = "Some inconsistencies with the Workflows version may exist"

        if isinstance(original_method, np.ufunc):
            # what the function does
            info = doc[1]

            # parameters (sometimes listed on separate lines, someimtes not)
            parameters = [a for a in doc if "Parameters\n" in a][0].split("\n")
            if parameters[4][0] == "x":
                parameters = "\n".join(parameters[:6])
            else:
                parameters = "\n".join(parameters[:4])

            # return value
            returns = [a for a in doc if "Returns\n" in a][0]

            # final docstring
            doc = "\n\n".join([info, l1, l2, parameters, returns])
        else:
            # does the first line contain the function signature? (not always the case)
            if doc[0][-1] == ")":
                doc = (
                    [doc[1]]
                    + ["\n\n" + "    {}\n\n    {}\n\n".format(l1, l2)]
                    + doc[2:]
                )
            else:
                doc = (
                    [doc[0]]
                    + ["\n\n" + "    {}\n\n    {}\n\n".format(l1, l2)]
                    + doc[1:]
                )
            doc = "\n\n".join(doc)

        method.__doc__ = doc
        return method

    return wrapper


HANDLED_UFUNCS = {}

##################
# ufunc operations
##################


class ufunc:
    _forward_attrs = {
        "nin",
        "nargs",
        "nout",
        "ntypes",
        "identity",
        "signature",
        "types",
    }

    def __init__(self, ufunc, return_type_override=None):
        if not isinstance(ufunc, np.ufunc):
            raise TypeError(
                "Must be an instance of `np.ufunc`, got {}".format(type(ufunc))
            )

        self._ufunc = ufunc
        self.__name__ = ufunc.__name__
        self._return_type_override = return_type_override

        if isinstance(ufunc, np.ufunc):
            derived_from(ufunc)(self)

        HANDLED_UFUNCS[ufunc.__name__] = self

    def __call__(self, *args, **kwargs):
        if len(args) != self._ufunc.nin:
            raise TypeError(
                "Invalid number of arguments to function `{}`".format(self.__name__)
            )

        # Since typecheck_promote doesn't support variadic arguments, manually
        # attempt to promote each argument to an Array or scalar
        promoted = []
        for i, arg in enumerate(args):
            try:
                if isinstance(arg, BaseArray):
                    promoted.append(arg)
                elif isinstance(arg, np.ma.core.MaskedArray):
                    promoted.append(MaskedArray._promote(arg))
                elif isinstance(arg, np.ndarray):
                    promoted.append(Array._promote(arg))
                else:
                    promoted.append(_promote(arg, (Bool, Int, Float), i, self.__name__))
                    # TODO(gabe) not great to be relying on internal `_promote` here
            except (ProxyTypeError, TypeError):
                raise ProxyTypeError(
                    "Argument {} to function {} must be a Workflows Array, Int, Float, Bool, or "
                    "a type promotable to one of those, not {}".format(
                        i + 1, self.__name__, type(arg)
                    )
                )

        return_type = _ufunc_result_type(
            *promoted, return_type_override=self._return_type_override
        )
        return return_type._from_apply(self.__name__, *promoted)

    def reduce(self):
        raise NotImplementedError(
            "The `reduce` ufunc method is not supported by Workflows types"
        )

    def reduceat(self):
        raise NotImplementedError(
            "The `reduceat` ufunc method is not supported by Workflows types"
        )

    def accumulate(self):
        raise NotImplementedError(
            "The `accumulate` ufunc method is not supported by Workflows types"
        )

    def outer(self):
        raise NotImplementedError(
            "The `outer` ufunc method is not supported by Workflows types"
        )


# math operations
add = ufunc(np.add)
subtract = ufunc(np.subtract)
multiply = ufunc(np.multiply)
divide = ufunc(np.divide)
logaddexp = ufunc(np.logaddexp, return_type_override=Float)
logaddexp2 = ufunc(np.logaddexp2, return_type_override=Float)
true_divide = ufunc(np.true_divide, return_type_override=Float)
floor_divide = ufunc(np.floor_divide)
negative = ufunc(np.negative)
power = ufunc(np.power)
float_power = ufunc(np.float_power, return_type_override=Float)
remainder = ufunc(np.remainder)
mod = ufunc(np.mod)
conj = conjugate = ufunc(np.conj)
exp = ufunc(np.exp, return_type_override=Float)
exp2 = ufunc(np.exp2, return_type_override=Float)
log = ufunc(np.log, return_type_override=Float)
log2 = ufunc(np.log2, return_type_override=Float)
log10 = ufunc(np.log10, return_type_override=Float)
log1p = ufunc(np.log1p, return_type_override=Float)
expm1 = ufunc(np.expm1, return_type_override=Float)
sqrt = ufunc(np.sqrt, return_type_override=Float)
square = ufunc(np.square)
cbrt = ufunc(np.cbrt, return_type_override=Float)
reciprocal = ufunc(np.reciprocal)

# trigonometric functions
sin = ufunc(np.sin, return_type_override=Float)
cos = ufunc(np.cos, return_type_override=Float)
tan = ufunc(np.tan, return_type_override=Float)
arcsin = ufunc(np.arcsin, return_type_override=Float)
arccos = ufunc(np.arccos, return_type_override=Float)
arctan = ufunc(np.arctan, return_type_override=Float)
arctan2 = ufunc(np.arctan2, return_type_override=Float)
# hypot = ufunc(np.hypot)
sinh = ufunc(np.sinh, return_type_override=Float)
cosh = ufunc(np.cosh, return_type_override=Float)
tanh = ufunc(np.tanh, return_type_override=Float)
arcsinh = ufunc(np.arcsinh, return_type_override=Float)
arccosh = ufunc(np.arccosh, return_type_override=Float)
arctanh = ufunc(np.arctanh, return_type_override=Float)
deg2rad = ufunc(np.deg2rad, return_type_override=Float)
rad2deg = ufunc(np.rad2deg, return_type_override=Float)

# bit-twiddling functions
# bitwise_and = ufunc(np.bitwise_and)
# bitwise_or = ufunc(np.bitwise_or)
# bitwise_xor = ufunc(np.bitwise_xor)
# bitwise_not = ufunc(np.bitwise_not)
# TODO: invert

# comparision functions
greater = ufunc(np.greater, return_type_override=Bool)
greater_equal = ufunc(np.greater_equal, return_type_override=Bool)
less = ufunc(np.less, return_type_override=Bool)
less_equal = ufunc(np.less_equal, return_type_override=Bool)
not_equal = ufunc(np.not_equal, return_type_override=Bool)
equal = ufunc(np.equal, return_type_override=Bool)
# isneginf = partial(equal, -np.inf)
# isposinf = partial(equal, np.inf)
logical_and = ufunc(np.logical_and, return_type_override=Bool)
logical_or = ufunc(np.logical_or, return_type_override=Bool)
logical_xor = ufunc(np.logical_xor, return_type_override=Bool)
logical_not = ufunc(np.logical_not, return_type_override=Bool)
maximum = ufunc(np.maximum)
minimum = ufunc(np.minimum)
fmax = ufunc(np.fmax)
fmin = ufunc(np.fmin)

# floating functions
isfinite = ufunc(np.isfinite, return_type_override=Bool)
isinf = ufunc(np.isinf, return_type_override=Bool)
isnan = ufunc(np.isnan, return_type_override=Bool)
signbit = ufunc(np.signbit, return_type_override=Bool)
copysign = ufunc(np.copysign, return_type_override=Float)
nextafter = ufunc(np.nextafter, return_type_override=Float)
spacing = ufunc(np.spacing, return_type_override=Float)
# modf = ufunc(np.modf) # has multiple outputs
# ldexp = ufunc(np.ldexp)
# frexp = ufunc(np.frexp) # has multiple outputs
fmod = ufunc(np.fmod)
floor = ufunc(np.floor)
ceil = ufunc(np.ceil)
trunc = ufunc(np.trunc)

degrees = ufunc(np.degrees, return_type_override=Float)
radians = ufunc(np.radians, return_type_override=Float)
rint = ufunc(np.rint, return_type_override=Float)
fabs = ufunc(np.fabs, return_type_override=Float)
sign = ufunc(np.sign)
absolute = ufunc(np.absolute)