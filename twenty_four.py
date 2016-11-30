#!/usr/bin/env python3

from enum import Enum
from itertools import combinations
from typing import List, Optional, Set
import math

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
    def need_parentheses(op: 'Operator', sub_op: 'Operator', is_left: bool) -> bool:
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


class Expression(object):
    """Represents an arithmetic expression."""

    def __init__(self, val: float, op: Operator, children: List['Expression']):
        super(Expression, self).__init__()
        self.val = val
        self.op = op
        self.children = children

    @classmethod
    def make_init(cls, num: int) -> 'Expression':
        return cls(float(num), Operator.none, [])

    @classmethod
    def make(cls, op: Operator, a: 'Expression', b: 'Expression') -> 'Expression':
        children = [a, b]
        if op is Operator.plus:
            # Normalize (a + (b + c)) to (a + b + c)
            val = a.val + b.val
            children = cls.flatten(children, op)
        elif op is Operator.minus:
            # Normalize (a - (b - c)) to (a + (c - b))
            val = a.val - b.val
            if b.op is op:
                op = Operator.plus
                b.children.reverse()
                b.val = -b.val
        elif op is Operator.multiply:
            # Normalize (a * (b * c)) to (a * b * c)
            val = a.val * b.val
            children = cls.flatten(children, op)
        elif op is Operator.divide:
            # Normalize (a / (b / c)) to (a * (c / b))
            val = a.val / b.val
            if b.op is op:
                op = Operator.multiply
                b.children.reverse()
                b.val = 1 / b.val
        else:
            raise AssertionError('Impossible operator')
        return cls(val, op, children)

    @staticmethod
    def flatten(children: List['Expression'], op: Operator) -> List['Expression']:
        ret = []
        for c in children:
            if c.op is op:
                ret.extend(c.children)
            else:
                ret.append(c)
        ret.sort(key=lambda e: e.val)
        return ret

    def is_target(self) -> bool:
        return math.isclose(self.val, TARGET)

    def expr(self, need_parentheses=False) -> str:
        is_left = True
        children = []
        for c in self.children:
            children.append(c.expr(Operator.need_parentheses(self.op, c.op, is_left)))
            is_left = False
        if self.op is Operator.plus:
            s = ' + '.join(children)
        elif self.op is Operator.minus:
            s = ' - '.join(children)
        elif self.op is Operator.multiply:
            s = ' * '.join(children)
        elif self.op is Operator.divide:
            s = ' / '.join(children)
        elif self.op is Operator.none:
            s = "{:.0f}".format(self.val)
        else:
            raise AssertionError('Impossible operator')
        if need_parentheses:
            return '(' + s + ')'
        else:
            return s


class Aggregator(object):
    """An aggregator of the results from the solver. Keeps track of solutions to remove duplicates."""

    def __init__(self):
        super(Aggregator, self).__init__()
        self.pool = set()  # type: Set[str]

    def add(self, e: 'Expression'):
        a = e.expr()
        if a in self.pool:
            # print(a + ' = DUP')
            return
        self.pool.add(a)
        print("{} = {}".format(a, TARGET))


def solve(agg: Aggregator, in_elems: List[Expression], new_elem: Optional[Expression]) -> bool:
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
            ret.append(solve(agg, remainder, Expression.make(Operator.plus, a, b)))
            if a.val >= b.val:
                ret.append(solve(agg, remainder, Expression.make(Operator.minus, a, b)))
            if b.val >= a.val:
                ret.append(solve(agg, remainder, Expression.make(Operator.minus, b, a)))
            ret.append(solve(agg, remainder, Expression.make(Operator.multiply, a, b)))
            if b.val != 0:
                ret.append(solve(agg, remainder, Expression.make(Operator.divide, a, b)))
            if a.val != 0:
                ret.append(solve(agg, remainder, Expression.make(Operator.divide, b, a)))
        return any(ret)


def solve_main(nums: List[int]):
    elems = [Expression.make_init(i) for i in nums]
    agg = Aggregator()
    ret = solve(agg, elems, None)
    if not ret:
        print('No solution.')


def main():
    solve_main([2,6,7,8])

if __name__ == '__main__':
    main()
