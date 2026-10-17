"""
Sorting Service orchestrating single-column and multi-level sorting operations.
"""

from typing import List, Dict, Any, Tuple
from models.filter_sort import SortLevel, SortResult
from algorithms.sorting import (
    execute_sort,
    SORTING_ALGORITHMS,
    is_algorithm_compatible,
    get_sort_key_value,
    compare_keys,
    MetricsTracker,
    is_smaller_or_equal,
    is_strictly_smaller
)
import time


class SortService:
    @staticmethod
    def sort_single_column(
        data: List[Dict[str, Any]],
        algorithm_name: str,
        column: str,
        reverse: bool = False
    ) -> SortResult:
        """Sorts data by a single column using the chosen algorithm."""
        return execute_sort(algorithm_name, data, column, reverse=reverse)

    @staticmethod
    def sort_multi_level(
        data: List[Dict[str, Any]],
        primary_algorithm: str,
        levels: List[SortLevel]
    ) -> SortResult:
        """
        Executes multi-level sorting across multiple columns with tie resolution.
        
        Strategy:
        1. If primary algorithm is stable (Merge Sort, Insertion Sort, Bubble Sort):
           Classic DSA Multi-pass (Radix principle): Sort from lowest-priority key
           up to primary key. The stable primary sort guarantees that ties in the primary
           key remain strictly ordered by secondary/tertiary keys!
        2. If primary algorithm is unstable (Quick Sort, Selection Sort):
           Sorts using a composite comparison key across all levels so that every level
           is evaluated during element comparison.
        """
        if not levels:
            return SortResult(
                algorithm_name=primary_algorithm,
                column="None",
                direction="asc",
                dataset_size=len(data),
                elapsed_ms=0.0,
                comparisons=0,
                swaps=0,
                movements=0,
                stability="N/A",
                time_complexity_best="N/A",
                time_complexity_avg="N/A",
                time_complexity_worst="N/A",
                space_complexity="N/A",
                sorted_data=list(data),
                is_compatible=True
            )

        if len(levels) == 1:
            return SortService.sort_single_column(
                data,
                primary_algorithm,
                levels[0].column,
                reverse=(levels[0].direction.lower() == "desc")
            )

        # Primary level
        primary_level = levels[0]
        primary_reverse = (primary_level.direction.lower() == "desc")

        # Stable algorithms list
        stable_algos = {"Merge Sort", "Insertion Sort", "Bubble Sort", "Counting Sort", "Bucket Sort", "Radix Sort"}

        start_time = time.perf_counter()
        total_comparisons = 0
        total_swaps = 0
        total_movements = 0

        current_data = [dict(x) for x in data]

        if primary_algorithm in stable_algos:
            # Multi-pass backwards: start from lowest priority to primary
            for lvl in reversed(levels):
                rev = (lvl.direction.lower() == "desc")
                # Secondary passes use Merge Sort for O(n log n) efficiency,
                # while primary pass uses the chosen primary_algorithm!
                algo_to_use = primary_algorithm if lvl == primary_level else "Merge Sort"
                compat, _ = is_algorithm_compatible(algo_to_use, lvl.column)
                if not compat:
                    algo_to_use = "Merge Sort"

                res = execute_sort(algo_to_use, current_data, lvl.column, reverse=rev)
                current_data = res.sorted_data
                total_comparisons += res.comparisons
                total_swaps += res.swaps
                total_movements += res.movements

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            return SortResult(
                algorithm_name=f"{primary_algorithm} (Stable Multi-Pass)",
                column=" > ".join([f"{l.column} ({l.direction})" for l in levels]),
                direction=primary_level.direction,
                dataset_size=len(data),
                elapsed_ms=elapsed_ms,
                comparisons=total_comparisons,
                swaps=total_swaps,
                movements=total_movements,
                stability="Stable",
                time_complexity_best="O(n log n)",
                time_complexity_avg="O(n log n)",
                time_complexity_worst="O(n log n)" if primary_algorithm == "Merge Sort" else "O(n²)",
                space_complexity="O(n)",
                sorted_data=current_data,
                is_compatible=True
            )

        else:
            # Composite comparator sort for Quick Sort / Selection Sort
            # Implemented with recursion-safe iterative quicksort with multi-level comparator
            tracker = MetricsTracker()
            arr = [dict(x) for x in current_data]
            n = len(arr)

            def _compare_multi(rec_a: Dict[str, Any], rec_b: Dict[str, Any]) -> int:
                """Compares two records through each sort level in priority order."""
                for lvl in levels:
                    val_a = get_sort_key_value(rec_a, lvl.column)
                    val_b = get_sort_key_value(rec_b, lvl.column)
                    rev = (lvl.direction.lower() == "desc")
                    cmp = compare_keys(val_a, val_b, rev, tracker)
                    if cmp != 0:
                        return cmp
                return 0

            if primary_algorithm == "Quick Sort":
                def _partition_multi(low: int, high: int) -> int:
                    mid = (low + high) // 2
                    # Median of three
                    if _compare_multi(arr[mid], arr[low]) < 0:
                        arr[low], arr[mid] = arr[mid], arr[low]
                        tracker.swaps += 1
                    if _compare_multi(arr[high], arr[low]) < 0:
                        arr[low], arr[high] = arr[high], arr[low]
                        tracker.swaps += 1
                    if _compare_multi(arr[high], arr[mid]) < 0:
                        arr[mid], arr[high] = arr[high], arr[mid]
                        tracker.swaps += 1

                    arr[mid], arr[high] = arr[high], arr[mid]
                    tracker.swaps += 1
                    pivot = arr[high]

                    i = low - 1
                    for j in range(low, high):
                        if _compare_multi(arr[j], pivot) <= 0:
                            i += 1
                            if i != j:
                                arr[i], arr[j] = arr[j], arr[i]
                                tracker.swaps += 1

                    arr[i + 1], arr[high] = arr[high], arr[i + 1]
                    tracker.swaps += 1
                    return i + 1

                if n > 1:
                    stack = [(0, n - 1)]
                    while stack:
                        low, high = stack.pop()
                        if low < high:
                            p = _partition_multi(low, high)
                            if p - 1 - low < high - (p + 1):
                                stack.append((p + 1, high))
                                stack.append((low, p - 1))
                            else:
                                stack.append((low, p - 1))
                                stack.append((p + 1, high))

            elif primary_algorithm == "Selection Sort":
                for i in range(n - 1):
                    min_idx = i
                    for j in range(i + 1, n):
                        if _compare_multi(arr[j], arr[min_idx]) < 0:
                            min_idx = j
                    if min_idx != i:
                        arr[i], arr[min_idx] = arr[min_idx], arr[i]
                        tracker.swaps += 1

            elapsed_ms = (time.perf_counter() - start_time) * 1000.0

            return SortResult(
                algorithm_name=f"{primary_algorithm} (Composite Comparator)",
                column=" > ".join([f"{l.column} ({l.direction})" for l in levels]),
                direction=primary_level.direction,
                dataset_size=n,
                elapsed_ms=elapsed_ms,
                comparisons=tracker.comparisons,
                swaps=tracker.swaps,
                movements=tracker.movements,
                stability="Unstable",
                time_complexity_best="O(n log n)" if primary_algorithm == "Quick Sort" else "O(n²)",
                time_complexity_avg="O(n log n)" if primary_algorithm == "Quick Sort" else "O(n²)",
                time_complexity_worst="O(n²)",
                space_complexity="O(log n)" if primary_algorithm == "Quick Sort" else "O(1)",
                sorted_data=arr,
                is_compatible=True
            )

