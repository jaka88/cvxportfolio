"""
Copyright 2016 Stephen Boyd, Enzo Busseti, Steven Diamond, Blackrock Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


from abc import ABCMeta, abstractmethod
import cvxpy as cvx
import pandas as pd

__all__ = ['LongOnly', 'LeverageLimit', 'LongCash', 'MaxTrade']


class BaseConstraint(object):
    __metaclass__ = ABCMeta

    @abstractmethod
    def estimate(self, t, w_plus, w_bench, z, v):
        """Returns a list of trade constraints.

        Args:
          t: time
          w_plus: post-trade weights
          w_bench: benchmark weights
          z: trade weights
          v: portfolio value
        """
        pass


class MaxTrade(BaseConstraint):
    """A limit on maximum trading size.
    """
    def __init__(self, ADVs, max_fraction=0.05):
        self.ADVs = ADVs
        self.max_fraction = max_fraction

    def estimate(self, t, w_plus, w_bench, z, v):
        """Returns a list of trade constraints.

        Args:
          t: time
          w_plus: post-trade weights
          w_bench: benchmark weights
          z: trade weights
          v: portfolio value
        """
        return cvx.abs(z[:-1])*v <= self.ADVs.loc[t].values * self.max_fraction  # TODO check [:-1] and fix pandas <=


class LongOnly(BaseConstraint):
    """A long only constraint.
    """

    def estimate(self, t, w_plus, w_bench, z, v):
        """Returns a list of holding constraints.

        Args:
          t: time
          wplus: holdings
        """
        return w_plus >= 0


class LeverageLimit(BaseConstraint):
    """A limit on leverage.

    Attributes:
      limit: A series or number giving the leverage limit.
    """
    def __init__(self, limit):
        self.limit = limit

    def estimate(self, t, w_plus, w_bench, z, v):
        """Returns a list of holding constraints.

        Args:
          t: time
          wplus: holdings
        """
        if isinstance(self.limit, pd.Series):
            limit = self.limit.loc[t]
        else:
            limit = self.limit
        return cvx.norm(w_plus, 1) <= limit


class LongCash(BaseConstraint):
    """Requires that cash be non-negative.
    """

    def estimate(self, t, w_plus, w_bench, z, v):
        """Returns a list of holding constraints.

        Args:
          t: time
          wplus: holdings
        """
        return w_plus[-1] >= 0
