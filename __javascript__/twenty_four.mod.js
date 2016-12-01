	(function () {
		var N = 4;
		var TARGET = 24;
		var Operator = __class__ ('Operator', [object], {
			none: 10000,
			plus: 101,
			minus: 102,
			multiply: 201,
			divide: 202,
			get precedence () {return __get__ (this, function (op) {
				return int (op / 100);
			});},
			get need_parentheses () {return __get__ (this, function (op, sub_op, is_left) {
				if (Operator.precedence (op) < Operator.precedence (sub_op)) {
					return false;
				}
				if (Operator.precedence (op) == Operator.precedence (sub_op)) {
					if (op == Operator.plus || op == Operator.multiply) {
						return false;
					}
					if (op == Operator.minus && sub_op == Operator.plus && is_left) {
						return false;
					}
					if (op == Operator.divide && sub_op == Operator.multiply && is_left) {
						return false;
					}
				}
				return true;
			});}
		});
		var Expression = __class__ ('Expression', [object], {
			get __init__ () {return __get__ (this, function (self, val, op, children) {
				self.val = val;
				self.op = op;
				self.children = children;
			});},
			get make_init () {return __get__ (this, function (num) {
				return Expression (float (num), Operator.none, list ([]));
			});},
			get make () {return __get__ (this, function (op, a, b) {
				var children = list ([a, b]);
				if (op == Operator.plus) {
					var val = a.val + b.val;
					var children = Expression.flatten (children, op);
				}
				else {
					if (op == Operator.minus) {
						var val = a.val - b.val;
						if (b.op == op) {
							var b1 = Expression (op, -(b.val), py_reversed (b.children));
							var children = list ([a, b1]);
						}
					}
					else {
						if (op == Operator.multiply) {
							var val = a.val * b.val;
							var children = Expression.flatten (children, op);
						}
						else {
							if (op == Operator.divide) {
								var val = a.val / b.val;
								if (b.op == op) {
									var b1 = Expression (op, 1 / b.val, py_reversed (b.children));
									var children = list ([a, b1]);
								}
							}
							else {
								var __except0__ = AssertionError ('Impossible operator');
								__except0__.__cause__ = null;
								throw __except0__;
							}
						}
					}
				}
				return Expression (val, op, children);
			});},
			get flatten () {return __get__ (this, function (children, op) {
				var ret = list ([]);
				var __iterable0__ = children;
				for (var __index0__ = 0; __index0__ < __iterable0__.length; __index0__++) {
					var c = __iterable0__ [__index0__];
					if (c.op == op) {
						ret.extend (c.children);
					}
					else {
						ret.append (c);
					}
				}
				ret.py_sort (__kwargdict__ ({key: (function __lambda__ (e) {
					return e.val;
				})}));
				return ret;
			});},
			get is_target () {return __get__ (this, function (self) {
				var diff = self.val - TARGET;
				var eps = 1e-09;
				return diff < eps && diff > -(eps);
			});},
			get expr () {return __get__ (this, function (self, need_parentheses) {
				if (typeof need_parentheses == 'undefined' || (need_parentheses != null && need_parentheses .__class__ == __kwargdict__)) {;
					var need_parentheses = false;
				};
				var is_left = true;
				var children = list ([]);
				var __iterable0__ = self.children;
				for (var __index0__ = 0; __index0__ < __iterable0__.length; __index0__++) {
					var c = __iterable0__ [__index0__];
					children.append (c.expr (Operator.need_parentheses (self.op, c.op, is_left)));
					var is_left = false;
				}
				if (self.op == Operator.plus) {
					var s = ' + '.join (children);
				}
				else {
					if (self.op == Operator.minus) {
						var s = ' - '.join (children);
					}
					else {
						if (self.op == Operator.multiply) {
							var s = ' * '.join (children);
						}
						else {
							if (self.op == Operator.divide) {
								var s = ' / '.join (children);
							}
							else {
								if (self.op == Operator.none) {
									var s = str (int (self.val));
								}
								else {
									var __except0__ = AssertionError ('Impossible operator');
									__except0__.__cause__ = null;
									throw __except0__;
								}
							}
						}
					}
				}
				if (need_parentheses) {
					return ('(' + s) + ')';
				}
				else {
					return s;
				}
			});}
		});
		var Aggregator = __class__ ('Aggregator', [object], {
			get __init__ () {return __get__ (this, function (self) {
				self.pool = set ();
			});},
			get add () {return __get__ (this, function (self, e) {
				var a = e.expr ();
				if (!__in__ (a, self.pool)) {
					self.pool.add (a);
				}
			});},
			get solutions () {return __get__ (this, function (self) {
				return list (self.pool);
			});}
		});
		var solve = function (agg, in_elems, new_elem) {
			var elems = list (in_elems);
			if (new_elem !== null) {
				elems.append (new_elem);
			}
			var n = len (elems);
			if (n == 0) {
				var __except0__ = AssertionError ('Impossible state: 0 elements');
				__except0__.__cause__ = null;
				throw __except0__;
			}
			if (n == 1) {
				var a = elems [0];
				if (a.is_target ()) {
					agg.add (a);
					return true;
				}
				else {
					return false;
				}
			}
			else {
				var ret = list ([]);
				for (var i = 0; i < n; i++) {
					for (var j = i + 1; j < n; j++) {
						var a = elems [i];
						var b = elems [j];
						var remainder = list (elems);
						remainder.remove (a);
						remainder.remove (b);
						ret.append (solve (agg, remainder, Expression.make (Operator.plus, a, b)));
						if (a.val >= b.val) {
							ret.append (solve (agg, remainder, Expression.make (Operator.minus, a, b)));
						}
						if (b.val >= a.val) {
							ret.append (solve (agg, remainder, Expression.make (Operator.minus, b, a)));
						}
						ret.append (solve (agg, remainder, Expression.make (Operator.multiply, a, b)));
						if (b.val != 0) {
							ret.append (solve (agg, remainder, Expression.make (Operator.divide, a, b)));
						}
						if (a.val != 0) {
							ret.append (solve (agg, remainder, Expression.make (Operator.divide, b, a)));
						}
					}
				}
				return any (ret);
			}
		};
		var solve_main = function (nums) {
			var elems = function () {
				var __accu0__ = [];
				var __iterable0__ = nums;
				for (var __index0__ = 0; __index0__ < __iterable0__.length; __index0__++) {
					var i = __iterable0__ [__index0__];
					__accu0__.append (Expression.make_init (i));
				}
				return __accu0__;
			} ();
			var agg = Aggregator ();
			solve (agg, elems, null);
			return agg.solutions ();
		};
		__pragma__ ('<all>')
			__all__.Aggregator = Aggregator;
			__all__.Expression = Expression;
			__all__.N = N;
			__all__.Operator = Operator;
			__all__.TARGET = TARGET;
			__all__.solve = solve;
			__all__.solve_main = solve_main;
		__pragma__ ('</all>')
	}) ();
