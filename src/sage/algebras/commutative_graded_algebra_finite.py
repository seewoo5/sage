r"""
Finitely generated commutative graded algebras with finite degree

AUTHORS:

- Michael Jung (2021): initial version

"""

#*****************************************************************************
#       Copyright (C) 2021 Michael Jung <m.jung at vu.nl>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 2 of the License, or
# (at your option) any later version.
#                  http://www.gnu.org/licenses/
#*****************************************************************************

from sage.combinat.free_module import CombinatorialFreeModule
from sage.categories.all import Algebras
from sage.misc.cachefunc import cached_method
from sage.combinat.integer_vector_weighted import WeightedIntegerVectors
from sage.rings.ring import Algebra

class FiniteGCAlgebra(CombinatorialFreeModule, Algebra):
    r"""
    Finitely generated commutative graded algebras with finite degree.

    INPUT:

    - ``base`` -- the base field
    - ``max_degree`` -- the maximal degree of the graded algebra. For
      commutative graded algebras without maximal grading, use
      :class:`sage.algebras.commutative_dga.GCAlgebra` instead.
    - ``names`` -- (optional) names of the generators: a list of
      strings or a single string with the names separated by
      commas. If not specified, the generators are named "x0", "x1",...
    - ``degrees`` -- (optional) a tuple or list specifying the degrees
      of the generators; if omitted, each generator is given degree
      1, and if both ``names`` and ``degrees`` are omitted, an error is
      raised.

    EXAMPLES::

        sage: A.<p1,p2> = GradedCommutativeAlgebra(QQ, degrees=(4,8), max_degree=10)
        sage: A
        Graded commutative algebra with generators ('p1', 'p2') in degrees
         (4, 8) with maximal finite degree 10
        sage: p1*p2
        0

    """

    Element = CombinatorialFreeModule.Element

    @staticmethod
    def __classcall__(cls, base, max_degree, names=None, degrees=None,
                      category=None):
        r"""
        Normalize the input for the :meth:`__init__` method and the
        unique representation.

        INPUT:

        - ``base`` -- the base ring of the algebra
        - ``max_degree`` -- the maximal degree of the algebra
        - ``names`` -- the names of the variables; by default, set to ``x1``,
          ``x2``, etc.
        - ``degrees`` -- the degrees of the generators; by default, set to 1

        TESTS::

            sage: A1 = GradedCommutativeAlgebra(GF(2), 'x,y', (3, 6), max_degree=12)
            sage: A2 = GradedCommutativeAlgebra(GF(2), ['x', 'y'], [3, 6], max_degree=12)
            sage: A1 is A2
            True

        """
        if names is None:
            if degrees is None:
                raise ValueError("You must specify names or degrees")
            else:
                n = len(degrees)
            names = tuple('x{}'.format(i) for i in range(n))
        elif isinstance(names, str):
            names = tuple(names.split(','))
            n = len(names)
        else:
            n = len(names)
            names = tuple(names)
        if degrees is None:
            degrees = tuple([1 for i in range(n)])
        else:
            degrees = tuple(degrees)
        if max_degree < max(degrees):
            raise ValueError(f'max_degree must not deceed {max(degrees)}')

        return super(FiniteGCAlgebra, cls).__classcall__(cls, base=base,
                                                  names=names, degrees=degrees,
                                                  max_degree=max_degree,
                                                  category=category)

    def __init__(self, base, max_degree, names, degrees, category=None):
        r"""
        Construct a commutative graded algebra with finite degree.

        TESTS::

            sage: A.<x,y,z,t> = GradedCommutativeAlgebra(QQ, max_degree=6)
            sage: TestSuite(A).run()
            sage: A = GradedCommutativeAlgebra(QQ, ('x','y','z'), [2,3,4], max_degree=8)
            sage: TestSuite(A).run()
            sage: A = GradedCommutativeAlgebra(QQ, ('x','y','z','t'), [1,2,3,4], max_degree=10)
            sage: TestSuite(A).run()

        """
        from sage.arith.misc import gcd

        self._names = names
        self.__ngens = len(self._names)
        self._degrees = degrees
        self._max_deg = max_degree
        self._weighted_vectors = WeightedIntegerVectors(degrees)
        step = gcd(degrees)
        indices = [w for k in range(0, self._max_deg + 1, step)
                   for w in WeightedIntegerVectors(k, degrees)]
        sorting_key = self._weighted_vectors.grading
        if category is None:
            category = Algebras(base).WithBasis().Graded().FiniteDimensional()
        CombinatorialFreeModule.__init__(self, base, indices,
                                         sorting_key=sorting_key,
                                         category=category)

    def _repr_(self):
        """

        """
        desc = f'Graded commutative algebra with generators {self._names} in '
        desc += f'degrees {self._degrees} with maximal finite '
        desc += f'degree {self._max_deg}'
        return desc

    def ngens(self):
        r"""

        """
        return self.__ngens

    @cached_method
    def product_on_basis(self, w1, w2):
        r"""
        Return the product of two indices within the algebra.

        EXAMPLES::

            sage: A.<p1,p2,e> = GradedCommutativeAlgebra(QQ, degrees=(4,8,2), max_degree=10)
            sage: e*p1
            e*p1
            sage: p1^3
            0
            sage: 5*e + 4*e*p1
            5*e + 4*e*p1

        ::

            sage: A.<x,y,z> = GradedCommutativeAlgebra(QQ, degrees=(1,2,3), max_degree=5)
            sage: 2*x*y
            2*y*x
            sage: x^2
            0
            sage: x*z
            -z*x
            sage: z*x
            z*x
            sage: x*y*z
            0

        TESTS::

            sage: A.<p1,p2,e> = GradedCommutativeAlgebra(QQ, degrees=(4,8,2), max_degree=10)
            sage: weighted_vectors = A._weighted_vectors
            sage: w1 = A._weighted_vectors([1,0,1])
            sage: w2 = A._weighted_vectors([0,0,0])
            sage: A.product_on_basis(w1, w2)
            e*p1

        ::

            sage: A.<x,y,z> = GradedCommutativeAlgebra(QQ, degrees=(1,2,3), max_degree=5)
            sage: weighted_vectors = A._weighted_vectors
            sage: w1 = A._weighted_vectors([1,0,0])
            sage: w2 = A._weighted_vectors([0,0,1])
            sage: A.product_on_basis(w1, w2)
            -z*x
            sage: A.product_on_basis(w2, w1)
            z*x

        """
        grading = self._weighted_vectors.grading
        deg_left = grading(w1)
        deg_right = grading(w2)
        deg_tot = deg_left + deg_right
        if deg_tot > self._max_deg:
            return self.zero()
        w_tot = self._weighted_vectors([sum(w) for w in zip(w1, w2)])
        return self.basis()[w_tot]

    def degree_on_basis(self, i):
        r"""
        Return the degree of a homogeneous element with index `i`.

        EXAMPLES::

            sage: A.<c1,c2,c3> = GradedCommutativeAlgebra(QQ, degrees=(2,4,6), max_degree=7)
            sage: c1.degree()
            2
            sage: (2*c1*c2).degree()
            6
            sage: (c1+c2).degree()
            Traceback (most recent call last):
            ...
            ValueError: element is not homogeneous

        TESTS::

            sage: A.<c1,c2,c3> = GradedCommutativeAlgebra(QQ, degrees=(2,4,6), max_degree=7)
            sage: weighted_vectors = A._weighted_vectors
            sage: i = A._weighted_vectors([1,1,0])
            sage: A.degree_on_basis(i)
            6

        """
        return self._weighted_vectors.grading(i)

    def _repr_term(self, w):
        r"""

        """
        # Trivial case:
        if sum(w) == 0:
            return '1'
        # Non-trivial case:
        res = ''
        for i in range(len(w)):
            if w[i] == 0:
                continue
            elif w[i] == 1:
                res += self._names[i] + '*'
            else:
                res += self._names[i] + f'^{w[i]}*'
        return res[:-1]

    def _latex_term(self, w):
        r"""

        """
        # Trivial case:
        if sum(w) == 0:
            return '1'
        # Non-trivial case:
        res = ''
        for i in range(len(w)):
            if w[i] == 0:
                continue
            elif w[i] == 1:
                res += self._names[i]
            else:
                res += self._names[i] + f'^{{w[i]}}'
        return res

    def algebra_generators(self):
        r"""
        Return the generators of ``self`` as a
        :class:`sage.sets.family.Family`.

        """
        from sage.sets.family import Family

        return Family(self.gens())

    @cached_method
    def one_basis(self):
        r"""
        Return the index of the one element of ``self``.

        """
        n = len(self._degrees)
        return self._weighted_vectors([0 for _ in range(n)])

    def gens(self):
        r"""
        Return the generators of ``self`` as a list.

        """
        n = len(self._degrees)
        zero = [0 for _ in range(n)]
        indices = []
        for k in range(n):
            ind = list(zero)
            ind[k] = 1
            indices.append(self._weighted_vectors(ind))
        return [self.monomial(ind) for ind in indices]

    @cached_method
    def gen(self, i):
        r"""
        Return the `i`-th generator of ``self``.

        """
        return self.gens()[i]
