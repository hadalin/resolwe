"""Workflow expression engines."""
from __future__ import absolute_import, division, print_function, unicode_literals

from resolwe.flow.engine import BaseEngine


class BaseExpressionEngine(BaseEngine):
    """A workflow expression engine."""

    def evaluate_block(self, template, context=None):
        """Evaluate a template block."""
        raise NotImplementedError

    def evaluate_inline(self, expression, context=None):
        """Evaluate an inline expression."""
        raise NotImplementedError
