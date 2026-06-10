"""PSR (Premise-Strategy-Result) decomposition subpackage.

Re-exports core functions for backward-compatible imports.
"""

from mira.psr.psr import _classify_claim, decompose_psr, route_vtype

__all__ = ["_classify_claim", "decompose_psr", "route_vtype"]
