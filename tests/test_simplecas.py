import pytest
from pytest import raises
from pytest import skip

from protosym.simplecas import Add
from protosym.simplecas import cos
from protosym.simplecas import Expr
from protosym.simplecas import ExprAtomType
from protosym.simplecas import expressify
from protosym.simplecas import ExpressifyError
from protosym.simplecas import Function
from protosym.simplecas import Integer
from protosym.simplecas import Mul
from protosym.simplecas import negone
from protosym.simplecas import one
from protosym.simplecas import Pow
from protosym.simplecas import sin
from protosym.simplecas import Symbol
from protosym.simplecas import x
from protosym.simplecas import y
from protosym.simplecas import zero


two = Integer(2)
f = Function("f")


def test_simplecas_types() -> None:
    """Basic tests for type of Expr."""
    assert type(x) == Expr
    assert type(Mul) == Expr
    assert type(Integer) == ExprAtomType
    assert type(Integer(1)) == Expr
    assert type(Mul(x, Integer(1))) == Expr
    raises(TypeError, lambda: Expr([]))  # type: ignore


def test_simplecas_equality() -> None:
    """Test equality of Expr."""
    unequal_pairs = [
        (x, y),
        (one, two),
        (sin(x), sin(y)),
    ]
    for e1, e2 in unequal_pairs:
        assert (e1 == e1) is True
        assert (e1 == e2) is False
        assert (e1 != e1) is False
        assert (e1 != e2) is True


def test_simplecas_identity() -> None:
    """Test that equal expressions are the same object."""
    identical_pairs = [
        (Symbol("x"), Symbol("x")),
        (Integer(3), Integer(3)),
        (sin(x), sin(x)),
    ]
    for e1, e2 in identical_pairs:
        assert e1 is e2


def test_simplecas_operations() -> None:
    """Test arithmetic operations with Expr."""
    assert +x == x
    assert -x == Mul(negone, x)
    assert x + x == Add(x, x)
    assert x - x == Add(x, Mul(negone, x))
    assert two * x == Mul(two, x)
    assert two / x == Mul(two, Pow(x, negone))
    assert two**x == Pow(two, x)


def test_simplecas_operations_expressify() -> None:
    """Test arithmetic operations with Expr."""
    assert x + 2 == x + two == Add(x, two)
    assert 2 + x == two + x == Add(two, x)
    assert x - 2 == x - two == Add(x, Mul(negone, two))
    assert 2 - x == two - x == Add(two, Mul(negone, x))
    assert x * 2 == x * two == Mul(x, two)
    assert 2 * x == two * x == Mul(two, x)
    assert x / 2 == x / two == Mul(x, Pow(two, negone))
    assert 2 / x == two / x == Mul(two, Pow(x, negone))
    assert x**2 == x**two == Pow(x, two)
    assert 2**x == two**x == Pow(two, x)


def test_simplecas_operations_bad_type() -> None:
    """Test arithmetic operations fail for Expr and other types."""
    bad_pairs = [(x, ()), ((), x)]
    for op1, op2 in bad_pairs:
        raises(TypeError, lambda: op1 + op2)  # type:ignore
        raises(TypeError, lambda: op1 - op2)  # type:ignore
        raises(TypeError, lambda: op1 * op2)  # type:ignore
        raises(TypeError, lambda: op1 / op2)  # type:ignore
        raises(TypeError, lambda: op1**op2)  # type:ignore


def test_simplecas_expressify() -> None:
    """Test that the expressify function works in basic cases."""
    assert expressify(1) == Integer(1)
    assert expressify(x) == x
    raises(ExpressifyError, lambda: expressify([]))


def test_simplecas_repr() -> None:
    """Test basic operations with simplecas."""
    assert str(Integer) == "Integer"
    assert str(x) == "x"
    assert str(y) == "y"
    assert str(f) == "f"
    assert str(sin) == "sin"
    assert str(sin(cos(x))) == "sin(cos(x))"
    assert str(x + y) == "(x + y)"
    assert str(one + two) == "(1 + 2)"
    assert str(x * y) == "(x*y)"
    assert str(x**two) == "x**2"
    assert str(x + x + x) == "((x + x) + x)"


@pytest.mark.xfail
def test_simplecas_repr_xfail() -> None:
    """Test printing an undefined function."""
    #
    # This fails because Evaluator expects every function to be defined. There
    # is a printing rule for Function but that only handles an uncalled
    # function like f rather than f(x). There needs to be a way to give a
    # default rule to an Evaluator for handling the cases where there is no
    # operation rule defined for the head.
    #
    assert str(f(x)) == "f(x)"
    assert repr(f(x)) == "f(x)"
    assert f(x).eval_latex() == "f(x)"


def test_simplecas_latex() -> None:
    """Test basic operations with simplecas."""
    assert x.eval_latex() == r"x"
    assert y.eval_latex() == r"y"
    assert sin(x).eval_latex() == r"\sin(x)"
    assert sin(cos(x)).eval_latex() == r"\sin(\cos(x))"
    assert (x + y).eval_latex() == r"(x + y)"
    assert (one + two).eval_latex() == r"(1 + 2)"
    assert (x * y).eval_latex() == r"(x \times y)"
    assert (x**two).eval_latex() == r"x^{2}"
    assert (x + x + x).eval_latex() == r"((x + x) + x)"


def test_simplecas_repr_latex() -> None:
    """Test IPython/Jupyter hook."""
    assert sin(x)._repr_latex_() == r"$\sin(x)$"


def test_simplecas_to_sympy() -> None:
    """Test converting a simplecas expression to a SymPy expression."""
    try:
        import sympy
    except ImportError:
        skip("SymPy not installed")

    x_sym = sympy.Symbol("x")
    sinx_sym = sympy.sin(x_sym)
    cosx_sym = sympy.cos(x_sym)

    test_cases = [
        (sin(x), sinx_sym),
        (cos(x), cosx_sym),
        (cos(x) ** 2 + sin(x) ** 2, cosx_sym**2 + sinx_sym**2),
        (cos(x) * sin(x), cosx_sym * sinx_sym),
    ]
    for expr, sympy_expr in test_cases:
        # XXX: Converting to SymPy and back does not in general round-trip
        # unless evaluate=False is used because SymPy otherwise modifies the
        # expression implicitly. for now it is useful to be able to convert to
        # SymPy and have it perform automatic evaluation but really there
        # should be a way to create a SymPy expression passing evaluate=False.
        #
        # Provided SymPy's automatic evaluation is idempotent an evaluated
        # SymPy expression will always round-trip through Expr though.
        assert expr.to_sympy() == sympy_expr
        assert Expr.from_sympy(sympy_expr) == expr
        assert expr == Expr.from_sympy(expr.to_sympy())
        assert sympy_expr == Expr.from_sympy(sympy_expr).to_sympy()

        # _sympy_ is used by sympify
        assert expr._sympy_() == sympy_expr
        assert sympy.sympify(expr) == sympy_expr

        # XXX: Ideally these would not compare equal because it could get
        # confusing. Unfortunately if sympify works then __eq__ will use it and
        # then compare the two objects. Maybe allowing sympify is a bad idea...
        assert expr == sympy_expr

    # No reason why li(x) in particular should be considered invalid. This test
    # just chooses an example of an expression that is not (yet) supported by
    # simplecas to verify that the appropriate error is raised. If this passes
    # in future because li support is added then a different example should be
    # chosen.
    raises(NotImplementedError, lambda: Expr.from_sympy(sympy.li(x_sym)))
    raises(NotImplementedError, lambda: Expr.from_sympy(sympy.ord0))


def test_simplecas_eval_f64() -> None:
    """Test basic float evaluation with eval_f64."""
    assert sin(cos(x)).eval_f64({x: 1.0}) == 0.5143952585235492
    assert (x + one).eval_f64({x: 1.0}) == 2.0
    assert (x - one).eval_f64({x: 1.0}) == 0.0
    assert (x / two).eval_f64({x: 1.0}) == 0.5
    assert (x * two).eval_f64({x: 1.0}) == 2.0
    assert (x**two).eval_f64({x: 2.0}) == 4.0
    assert x.eval_f64({x: 1.0}) == 1.0
    assert one.eval_f64() == 1.0


def test_simplecas_count_ops() -> None:
    """Test count_ops_graph and count_ops_tree."""

    def make_expression(n: int) -> Expr:
        e = x**2 + x
        for _ in range(n):
            e = e**2 + e
        return e

    test_cases = [
        (x, 1, 1),
        (one, 1, 1),
        (sin(x), 2, 2),
        (sin(sin(x)) + sin(x), 4, 6),
        (sin(x) ** 2 + sin(x), 5, 7),
        (make_expression(10), 24, 8189),
        (make_expression(20), 44, 8388605),
        (make_expression(100), 204, 10141204801825835211973625643005),
    ]

    for expr, ops_graph, ops_tree in test_cases:
        assert expr.count_ops_graph() == ops_graph
        assert expr.count_ops_tree() == ops_tree


def test_simplecas_differentation() -> None:
    """Test derivatives of simplecas expressions."""
    assert one.diff(x) == zero
    assert x.diff(x) == one
    assert sin(1).diff(x) == zero
    assert (2 * sin(x)).diff(x) == 2 * cos(x)
    assert (x**3).diff(x) == 3 * x ** (Add(3, -1))
    assert sin(x).diff(x) == cos(x)
    assert cos(x).diff(x) == -sin(x)
    assert (sin(x) + cos(x)).diff(x) == cos(x) + -1 * sin(x)
    assert (sin(x) ** 2).diff(x) == 2 * sin(x) ** Add(2, -1) * cos(x)
    assert (x * sin(x)).diff(x) == 1 * sin(x) + x * cos(x)


def test_simplecas_bin_expand() -> None:
    """Test Expr.bin_expand()."""
    expr1 = Add(1, 2, 3, 4)
    assert expr1.bin_expand() == Add(Add(Add(1, 2), 3), 4)
    assert str(expr1) == "(1 + 2 + 3 + 4)"
    assert str(expr1.bin_expand()) == "(((1 + 2) + 3) + 4)"

    expr2 = Add(x, y, Mul(x, y, 1, f(x)))
    assert expr2.bin_expand() == Add(Add(x, y), Mul(Mul(Mul(x, y), 1), f(x)))
    # Fails because f(x) cannot be printed:
    # assert str(expr2) == "(x + y + x*y*1*f(x))"
    # assert str(expr2.bin_expand()) == "((x + y) + ((x*y)*1)*f(x))"
