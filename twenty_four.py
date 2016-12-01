#!/usr/bin/env python3

# NOTE: We cannot use new-style objects or import libraries
# due to limitations of Transcrypt.

N = 4
TARGET = 24


class Operator:
    """Represents an arithmetic operator."""
    none = 10000
    plus = 101
    minus = 102
    multiply = 201
    divide = 202

    @staticmethod
    def precedence(op):
        """
        :param op: Operator
        :return: int
        """
        return int(op / 100)

    @staticmethod
    def need_parentheses(op, sub_op, is_left):
        """
        :param op: Operator
        :param sub_op: Operator
        :param is_left: bool
        :return: bool
        """
        if Operator.precedence(op) < Operator.precedence(sub_op):
            return False
        if Operator.precedence(op) == Operator.precedence(sub_op):
            if op is Operator.plus or op is Operator.multiply:
                return False
            if op is Operator.minus and sub_op is Operator.plus and is_left:
                return False
            if op is Operator.divide and sub_op is Operator.multiply and is_left:
                return False
        return True


class Expression:
    """Represents an arithmetic expression."""

    def __init__(self, val, op, children):
        """
        :param val: float
        :param op: Operator
        :param children: [Expression]
        """
        self.val = val
        self.op = op
        self.children = children

    @staticmethod
    def make_init(num):
        """
        :param num: int
        :return: Expression
        """
        return Expression(float(num), Operator.none, [])

    @staticmethod
    def make(op, a, b):
        """
        :param op: Operator
        :param a: Expression
        :param b: Expression
        :return: Expression
        """
        children = [a, b]
        if op is Operator.plus:
            # Normalize (a + (b + c)) to (a + b + c)
            val = a.val + b.val
            children = Expression.flatten(children, op)
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
            children = Expression.flatten(children, op)
        elif op is Operator.divide:
            # Normalize (a / (b / c)) to (a * (c / b))
            val = a.val / b.val
            if b.op is op:
                op = Operator.multiply
                b.children.reverse()
                b.val = 1 / b.val
        else:
            raise AssertionError('Impossible operator')
        return Expression(val, op, children)

    @staticmethod
    def flatten(children, op):
        """
        :param children: [Expression]
        :param op: Operator
        :return: [Expression]
        """
        ret = []
        for c in children:
            if c.op is op:
                ret.extend(c.children)
            else:
                ret.append(c)
        ret.sort(key=lambda e: e.val)
        return ret

    def is_target(self):
        """
        :return: bool
        """
        diff = self.val - TARGET
        eps = 1e-9
        return diff < eps and diff > -eps

    def expr(self, need_parentheses=False):
        """
        :param need_parentheses: bool
        :return: str
        """
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
            s = str(int(self.val))
        else:
            raise AssertionError('Impossible operator')
        if need_parentheses:
            return '(' + s + ')'
        else:
            return s


class Aggregator:
    """An aggregator of the results from the solver. Keeps track of solutions to remove duplicates."""

    def __init__(self):
        self.pool = set()

    def add(self, e):
        """
        :param e: Expression
        :return: None
        """
        a = e.expr()
        if a not in self.pool:
            self.pool.add(a)

    def solutions(self):
        """
        :return: [str]
        """
        return list(self.pool)


def solve(agg, in_elems, new_elem):
    """
    :param agg: Aggregator
    :param in_elems: [Expression]
    :param new_elem: Expression option
    :return: bool
    """
    elems = list(in_elems)
    if new_elem is not None:
        elems.append(new_elem)
    n = len(elems)
    if n == 0:
        raise AssertionError('Impossible state: 0 elements')
    if n == 1:
        a = elems[0]
        if a.is_target():
            agg.add(a)
            return True
        else:
            return False
    else:
        ret = []
        for i in range(0, n):
            for j in range(i + 1, n):
                a = elems[i]
                b = elems[j]
                remainder = list(elems)
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


def solve_main(nums):
    """
    :param nums: [int]
    :return: [str]
    """
    elems = [Expression.make_init(i) for i in nums]
    agg = Aggregator()
    solve(agg, elems, None)
    return agg.solutions()


# def main():
#     ret = solve_main([1, 2, 3, 4])
#     if len(ret) == 0:
#         print('No solutions.')
#     else:
#         for s in ret:
#             print("{} = {}".format(s, TARGET))

# if __name__ == '__main__':
#     main()
