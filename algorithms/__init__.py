"""
Algorithms package for Video Game Database Explorer.
Contains 8 sorting algorithms and composite search filter engine.
"""

from algorithms.sorting import (
    insertion_sort,
    selection_sort,
    merge_sort,
    bubble_sort,
    quick_sort,
    counting_sort,
    bucket_sort,
    radix_sort,
    execute_sort,
    SORTING_ALGORITHMS,
    is_algorithm_compatible,
)
from algorithms.searching import (
    apply_composite_filters,
    evaluate_condition,
    BUILTIN_PRESETS,
)

__all__ = [
    "insertion_sort",
    "selection_sort",
    "merge_sort",
    "bubble_sort",
    "quick_sort",
    "counting_sort",
    "bucket_sort",
    "radix_sort",
    "execute_sort",
    "SORTING_ALGORITHMS",
    "is_algorithm_compatible",
    "apply_composite_filters",
    "evaluate_condition",
    "BUILTIN_PRESETS",
]

