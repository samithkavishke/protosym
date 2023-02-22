from pytest import raises

from protosym.simplecas import Add
from protosym.simplecas import cos
from protosym.simplecas import Expr
from protosym.simplecas import ExprAtomType
from protosym.simplecas import Integer
from protosym.simplecas import Mul
from protosym.simplecas import negone
from protosym.simplecas import one
from protosym.simplecas import Pow
from protosym.simplecas import sin
from protosym.simplecas import Symbol
from protosym.simplecas import x
from protosym.simplecas import y


two = Integer(2)


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


def test_simplecas_operations_bad_type() -> None:
    """Test arithmetic operations fail for Expr and other types."""
    bad_pairs = [(x, ()), ((), x)]
    for op1, op2 in bad_pairs:
        raises(TypeError, lambda: op1 + op2)  # type:ignore
        raises(TypeError, lambda: op1 - op2)  # type:ignore
        raises(TypeError, lambda: op1 * op2)  # type:ignore
        raises(TypeError, lambda: op1 / op2)  # type:ignore
        raises(TypeError, lambda: op1**op2)  # type:ignore


def test_simplecas_repr() -> None:
    """Test basic operations with simplecas."""
    assert str(Integer) == "Integer"
    assert str(x) == "x"
    assert str(y) == "y"
    assert str(sin) == "sin"
    assert str(sin(cos(x))) == "sin(cos(x))"
    assert str(x + y) == "(x + y)"
    assert str(one + two) == "(1 + 2)"
    assert str(x * y) == "(x*y)"
    assert str(x**two) == "x**2"
    assert str(x + x + x) == "((x + x) + x)"


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
