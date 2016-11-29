#!/usr/bin/env python3

from enum import Enum
from itertools import combinations
from typing import List, Optional, Set
import math
import sys

N = 4
TARGET = 24


class Operator(Enum):
    """Represents an arithmetic operator."""
    none = 10000
    plus = 101
    minus = 102
    multiply = 201
    divide = 202

    def precedence(self) -> int:
        return int(self.value / 100)

    @staticmethod
    def need_brackets(op: 'Operator', sub_op: 'Operator', is_left: bool) -> bool:
        if op.precedence() < sub_op.precedence():
            return False
        if op.precedence() == sub_op.precedence():
            if op is Operator.plus or op is Operator.multiply:
                return False
            if op is Operator.minus and sub_op is Operator.plus and is_left:
                return False
            if op is Operator.divide and sub_op is Operator.multiply and is_left:
                return False
        return True


class Aggregator(object):
    """An aggregator of the results from the solver. Handles duplicates."""

    def __init__(self):
        super(Aggregator, self).__init__()
        self.pool = set()  # type: Set[str]

    def add(self, a: 'Element'):
        a.normalize()
        if a.exp in self.pool:
            # print(a.exp + ' = DUP')
            return
        self.pool.add(a.exp)
        print("{} = {}".format(a.exp, TARGET))


class Element(object):
    """Represents an element in the expression."""

    def __init__(self, val: float, exp: str, op: Operator, left: 'Element', right: 'Element'):
        super(Element, self).__init__()
        self.val = val
        self.exp = exp
        self.op = op
        self.left = left
        self.right = right

    @classmethod
    def make_init(cls, num: int) -> 'Element':
        return cls(float(num), str(num), Operator.none, None, None)

    @classmethod
    def make(cls, a: 'Element', b: 'Element', op: Operator) -> 'Element':
        if op is Operator.plus:
            val = a.val + b.val
            fmt = '{} + {}'
        elif op is Operator.minus:
            val = a.val - b.val
            fmt = '{} - {}'
        elif op is Operator.multiply:
            val = a.val * b.val
            fmt = '{} × {}'
        elif op is Operator.divide:
            val = a.val / b.val
            fmt = '{} ÷ {}'
        else:
            raise AssertionError('Impossible operator')
        exp = fmt.format(a.expr(op, True), b.expr(op, False))
        return cls(val, exp, op, a, b)

    def __str__(self) -> str:
        return "{:.0f}".format(self.val)

    def expr(self, parent_op: Operator, is_left: bool) -> str:
        if Operator.need_brackets(parent_op, self.op, is_left):
            fmt = "({0})"
        else:
            fmt = "{0}"
        return fmt.format(self.exp)

    def is_target(self) -> bool:
        return math.isclose(self.val, TARGET)

    def normalize(self):
        """Turns the expression tree into a canonical form for ordering."""
        if (self.op is Operator.plus or self.op is Operator.multiply) \
                and (self.left is not None and self.right is not None):
            self.left.normalize()
            self.right.normalize()
            if self.left.val > self.right.val:
                self.left, self.right = self.right, self.left


def solve(agg: Aggregator, in_elems: List[Element], new_elem: Optional[Element]) -> bool:
    elems = in_elems.copy()
    if new_elem is not None:
        elems.append(new_elem)
    if len(elems) == 0:
        raise AssertionError('Impossible state: 0 elements')
    if len(elems) == 1:
        a = elems[0]
        if a.is_target():
            agg.add(a)
            return True
        else:
            return False
    else:
        ret = []  # type: List[bool]
        for a, b in combinations(elems, 2):
            remainder = elems.copy()
            remainder.remove(a)
            remainder.remove(b)
            ret.append(solve(agg, remainder, Element.make(a, b, Operator.plus)))
            if a.val >= b.val:
                ret.append(solve(agg, remainder, Element.make(a, b, Operator.minus)))
            if b.val >= a.val:
                ret.append(solve(agg, remainder, Element.make(b, a, Operator.minus)))
            ret.append(solve(agg, remainder, Element.make(a, b, Operator.multiply)))
            if b.val != 0:
                ret.append(solve(agg, remainder, Element.make(a, b, Operator.divide)))
            if a.val != 0:
                ret.append(solve(agg, remainder, Element.make(b, a, Operator.divide)))
        return any(ret)


def solve_wrapper(ss: List[str]):
    elems = [Element.make_init(int(s)) for s in ss]
    agg = Aggregator()
    ret = solve(agg, elems, None)
    if not ret:
        print('No solution.')


def main():
    if len(sys.argv) > 1:
        if len(sys.argv) == N + 1:
            solve_wrapper(sys.argv[1:])
        else:
            print('Wrong number of arguments. Ignore.', file=sys.stderr)
    while True:
        try:
            print("\n> Input {} integers: ".format(N), end='', file=sys.stderr)
            raw = input()  # type: str
            if raw == 'q':
                quit_program()
            solve_wrapper(raw.split())
        except (KeyboardInterrupt, EOFError):
            quit_program()


def quit_program():
    print('\nBye bye', file=sys.stderr)
    sys.exit()

if __name__ == '__main__':
    main()
