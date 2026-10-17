"""
Benchmarking Engine for Video Game Database Explorer.

Runs all eight sorting algorithms on equivalent copies of the dataset, collects
runtime, operation metrics, verifies output ordering, and reports detailed stats.
"""

from typing import List, Dict, Any, Callable, Optional
from models.filter_sort import SortResult
from algorithms.sorting import SORTING_ALGORITHMS, is_algorithm_compatible, get_sort_key_value


class BenchmarkService:
    @staticmethod
    def verify_sorted_order(data: List[Dict[str, Any]], column: str, reverse: bool) -> bool:
        """
        Verifies that a dataset is properly sorted according to column and direction.
        None values are expected to be at the end.
        """
        if len(data) <= 1:
            return True

        for i in range(len(data) - 1):
            val_a = get_sort_key_value(data[i], column)
            val_b = get_sort_key_value(data[i + 1], column)

            # If val_a is None and val_b is not None, order violated (None should be at end)
            if val_a is None and val_b is not None:
                return False
            if val_a is None and val_b is None:
                continue
            if val_b is None:
                continue

            if not reverse:
                if val_a > val_b:
                    return False
            else:
                if val_a < val_b:
                    return False

        return True

    @staticmethod
    def run_benchmark(
        data: List[Dict[str, Any]],
        column: str,
        reverse: bool = False,
        progress_callback: Optional[Callable[[str, int, int], None]] = None,
        should_cancel: Optional[Callable[[], bool]] = None
    ) -> List[SortResult]:
        """
        Executes benchmarks for all eight algorithms sequentially on identical input copies.
        Calls progress_callback(algorithm_name, current_step, total_steps).
        """
        results: List[SortResult] = []
        algo_names = list(SORTING_ALGORITHMS.keys())
        total_algos = len(algo_names)

        for idx, name in enumerate(algo_names):
            if should_cancel and should_cancel():
                break

            if progress_callback:
                progress_callback(name, idx + 1, total_algos)

            compat, reason = is_algorithm_compatible(name, column)
            if not compat:
                res = SortResult(
                    algorithm_name=name,
                    column=column,
                    direction="desc" if reverse else "asc",
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
                    sorted_data=[],
                    is_compatible=False,
                    error_message=reason
                )
                results.append(res)
                continue

            # Deep copy data so each algorithm receives fresh, untouched input
            input_copy = [dict(item) for item in data]
            algo_func = SORTING_ALGORITHMS[name]

            res = algo_func(input_copy, column, reverse=reverse)

            # Verification of ordering correctness
            is_valid = BenchmarkService.verify_sorted_order(res.sorted_data, column, reverse)
            if not is_valid:
                res.is_compatible = False
                res.error_message = "Verification failed: output was not in correct sorted order."

            results.append(res)

        return results

