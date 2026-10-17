"""
Core Sorting Algorithms Module for Video Game Database Explorer.

Implements all eight required sorting algorithms from scratch:
1. Insertion Sort
2. Selection Sort
3. Merge Sort
4. Bubble Sort (with early-exit optimization)
5. Quick Sort (with median-of-three pivot and recursion depth limit protection)
6. Counting Sort (with negative range offset and stable cumulative accumulation)
7. Bucket Sort (with normalized distribution and stable internal insertion sorting)
8. Radix Sort (LSD digit-by-digit stable counting passes with negative offset handling)

CRITICAL DESIGN RULES:
- No use of Python's built-in sorted() or list.sort().
- Preserves entire game records (dictionaries), never discarding attributes.
- Measures comparisons, swaps, and movements/shifts accurately.
- Handles missing (None) values consistently without throwing TypeErrors.
"""

import time
import math
from typing import List, Dict, Any, Tuple, Optional
from models.filter_sort import SortResult


class MetricsTracker:
    """Thread-safe counter for algorithm operations."""
    __slots__ = ("comparisons", "swaps", "movements")

    def __init__(self):
        self.comparisons = 0
        self.swaps = 0
        self.movements = 0

    def reset(self):
        self.comparisons = 0
        self.swaps = 0
        self.movements = 0


# ============================================================================
# HELPER FUNCTIONS: Key Extraction, Null Handling, and Comparison
# ============================================================================

def get_sort_key_value(record: Dict[str, Any], column: str) -> Any:
    """
    Extracts the key value from a record, standardizing types.
    Handles numeric columns, dates, strings, and missing (None) values.
    """
    val = record.get(column)
    if val is None or val == "":
        return None

    # Handle numeric columns
    if column in ("rating", "price"):
        try:
            return float(val)
        except (ValueError, TypeError):
            return None
    elif column in ("game_id", "rating_count", "metacritic_score"):
        try:
            return int(float(val))
        except (ValueError, TypeError):
            return None
    elif column == "multiplayer":
        if isinstance(val, bool):
            return 1 if val else 0
        s = str(val).lower()
        if s in ("1", "true", "yes"):
            return 1
        elif s in ("0", "false", "no"):
            return 0
        return None
    elif column == "release_date":
        return str(val).strip()
    else:
        # String columns: case-folded for natural alphabetical sorting
        return str(val).casefold()


def compare_keys(val_a: Any, val_b: Any, reverse: bool, tracker: MetricsTracker) -> int:
    """
    Compares two values with consistent None handling.
    Convention:
      None is always placed at the end of the sorted sequence.
      If reverse=False (ascending): regular values < None.
      If reverse=True (descending): regular values > None.
    Returns:
      -1 if val_a precedes val_b
       0 if val_a equals val_b
       1 if val_a succeeds val_b
    """
    tracker.comparisons += 1

    if val_a is None and val_b is None:
        return 0
    if val_a is None:
        # None goes to the end
        return 1
    if val_b is None:
        return -1

    if val_a == val_b:
        return 0

    if not reverse:
        return -1 if val_a < val_b else 1
    else:
        return -1 if val_a > val_b else 1


def is_smaller_or_equal(val_a: Any, val_b: Any, reverse: bool, tracker: MetricsTracker) -> bool:
    """Returns True if val_a should come before or at the same position as val_b."""
    return compare_keys(val_a, val_b, reverse, tracker) <= 0


def is_strictly_smaller(val_a: Any, val_b: Any, reverse: bool, tracker: MetricsTracker) -> bool:
    """Returns True if val_a should strictly come before val_b."""
    return compare_keys(val_a, val_b, reverse, tracker) < 0


# ============================================================================
# 1. INSERTION SORT
# ============================================================================

def insertion_sort(data: List[Dict[str, Any]], column: str, reverse: bool = False) -> SortResult:
    """
    Insertion Sort:
    Iterates through the list, consuming one element per iteration and growing a sorted output list.
    At each iteration, removes one element from the input data, finds the location it belongs within
    the sorted list, and inserts it there.
    
    Time Complexity: Best O(n), Average O(n^2), Worst O(n^2)
    Space Complexity: O(1) auxiliary
    Stability: Stable (equal elements retain their original relative order)
    """
    arr = [dict(item) for item in data]
    n = len(arr)
    tracker = MetricsTracker()
    start_time = time.perf_counter()

    for i in range(1, n):
        key_item = arr[i]
        key_val = get_sort_key_value(key_item, column)
        j = i - 1

        # Shift elements of arr[0..i-1] that are greater than key_val to one position ahead
        while j >= 0:
            val_j = get_sort_key_value(arr[j], column)
            if is_strictly_smaller(key_val, val_j, reverse, tracker):
                arr[j + 1] = arr[j]
                tracker.movements += 1
                j -= 1
            else:
                break
        
        arr[j + 1] = key_item
        tracker.movements += 1

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    return SortResult(
        algorithm_name="Insertion Sort",
        column=column,
        direction="desc" if reverse else "asc",
        dataset_size=n,
        elapsed_ms=elapsed_ms,
        comparisons=tracker.comparisons,
        swaps=tracker.swaps,
        movements=tracker.movements,
        stability="Stable",
        time_complexity_best="O(n)",
        time_complexity_avg="O(n²)",
        time_complexity_worst="O(n²)",
        space_complexity="O(1)",
        sorted_data=arr,
        is_compatible=True
    )


# ============================================================================
# 2. SELECTION SORT
# ============================================================================

def selection_sort(data: List[Dict[str, Any]], column: str, reverse: bool = False) -> SortResult:
    """
    Selection Sort:
    Divides the input list into two parts: a sorted sublist of items built up from left to right
    and a sublist of the remaining unsorted items. In each iteration, finds the smallest (or largest)
    element from the unsorted sublist and swaps it with the leftmost unsorted element.
    
    Time Complexity: Best O(n^2), Average O(n^2), Worst O(n^2)
    Space Complexity: O(1) auxiliary
    Stability: Unstable (swapping can change the relative order of equal keys)
    """
    arr = [dict(item) for item in data]
    n = len(arr)
    tracker = MetricsTracker()
    start_time = time.perf_counter()

    for i in range(n - 1):
        target_idx = i
        target_val = get_sort_key_value(arr[target_idx], column)

        for j in range(i + 1, n):
            val_j = get_sort_key_value(arr[j], column)
            if is_strictly_smaller(val_j, target_val, reverse, tracker):
                target_idx = j
                target_val = val_j

        if target_idx != i:
            arr[i], arr[target_idx] = arr[target_idx], arr[i]
            tracker.swaps += 1

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    return SortResult(
        algorithm_name="Selection Sort",
        column=column,
        direction="desc" if reverse else "asc",
        dataset_size=n,
        elapsed_ms=elapsed_ms,
        comparisons=tracker.comparisons,
        swaps=tracker.swaps,
        movements=tracker.movements,
        stability="Unstable",
        time_complexity_best="O(n²)",
        time_complexity_avg="O(n²)",
        time_complexity_worst="O(n²)",
        space_complexity="O(1)",
        sorted_data=arr,
        is_compatible=True
    )


# ============================================================================
# 3. MERGE SORT
# ============================================================================

def merge_sort(data: List[Dict[str, Any]], column: str, reverse: bool = False) -> SortResult:
    """
    Merge Sort:
    A divide and conquer algorithm that recursively halves the array until subarrays of size 1
    are reached, then merges the sorted subarrays in a stable manner.
    
    Time Complexity: Best O(n log n), Average O(n log n), Worst O(n log n)
    Space Complexity: O(n) auxiliary
    Stability: Stable (items with equal keys retain original ordering by taking left item first on <=)
    """
    arr = [dict(item) for item in data]
    n = len(arr)
    tracker = MetricsTracker()
    start_time = time.perf_counter()

    def _merge(left: int, mid: int, right: int, temp: List[Any]):
        i = left
        j = mid + 1
        k = left

        while i <= mid and j <= right:
            val_i = get_sort_key_value(arr[i], column)
            val_j = get_sort_key_value(arr[j], column)

            # <= ensures stability: equal items from left array are picked first
            if is_smaller_or_equal(val_i, val_j, reverse, tracker):
                temp[k] = arr[i]
                tracker.movements += 1
                i += 1
            else:
                temp[k] = arr[j]
                tracker.movements += 1
                j += 1
            k += 1

        while i <= mid:
            temp[k] = arr[i]
            tracker.movements += 1
            i += 1
            k += 1

        while j <= right:
            temp[k] = arr[j]
            tracker.movements += 1
            j += 1
            k += 1

        for idx in range(left, right + 1):
            arr[idx] = temp[idx]
            tracker.movements += 1

    def _sort(left: int, right: int, temp: List[Any]):
        if left < right:
            mid = (left + right) // 2
            _sort(left, mid, temp)
            _sort(mid + 1, right, temp)
            _merge(left, mid, right, temp)

    if n > 1:
        temp_arr = [None] * n
        _sort(0, n - 1, temp_arr)

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    return SortResult(
        algorithm_name="Merge Sort",
        column=column,
        direction="desc" if reverse else "asc",
        dataset_size=n,
        elapsed_ms=elapsed_ms,
        comparisons=tracker.comparisons,
        swaps=0,  # Merge sort does element movements into auxiliary buffer, not pairwise swaps
        movements=tracker.movements,
        stability="Stable",
        time_complexity_best="O(n log n)",
        time_complexity_avg="O(n log n)",
        time_complexity_worst="O(n log n)",
        space_complexity="O(n)",
        sorted_data=arr,
        is_compatible=True
    )


# ============================================================================
# 4. BUBBLE SORT (WITH EARLY EXIT)
# ============================================================================

def bubble_sort(data: List[Dict[str, Any]], column: str, reverse: bool = False) -> SortResult:
    """
    Bubble Sort:
    Repeatedly steps through the list, compares adjacent elements and swaps them if they are in the
    wrong order. Features an early-exit optimization that stops if no swaps occurred in a pass.
    
    Time Complexity: Best O(n) (already sorted), Average O(n^2), Worst O(n^2)
    Space Complexity: O(1) auxiliary
    Stability: Stable (equal elements are not swapped)
    """
    arr = [dict(item) for item in data]
    n = len(arr)
    tracker = MetricsTracker()
    start_time = time.perf_counter()

    for i in range(n):
        swapped = False
        for j in range(0, n - i - 1):
            val_a = get_sort_key_value(arr[j], column)
            val_b = get_sort_key_value(arr[j + 1], column)

            # Strictly smaller check: if arr[j+1] is strictly smaller than arr[j], swap them
            if is_strictly_smaller(val_b, val_a, reverse, tracker):
                arr[j], arr[j + 1] = arr[j + 1], arr[j]
                tracker.swaps += 1
                swapped = True

        if not swapped:
            # Early exit: list is already fully sorted
            break

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    return SortResult(
        algorithm_name="Bubble Sort",
        column=column,
        direction="desc" if reverse else "asc",
        dataset_size=n,
        elapsed_ms=elapsed_ms,
        comparisons=tracker.comparisons,
        swaps=tracker.swaps,
        movements=tracker.movements,
        stability="Stable",
        time_complexity_best="O(n)",
        time_complexity_avg="O(n²)",
        time_complexity_worst="O(n²)",
        space_complexity="O(1)",
        sorted_data=arr,
        is_compatible=True
    )


# ============================================================================
# 5. QUICK SORT
# ============================================================================

def quick_sort(data: List[Dict[str, Any]], column: str, reverse: bool = False) -> SortResult:
    """
    Quick Sort:
    Selects a pivot using median-of-three to avoid worst-case quadratic behavior on already sorted arrays.
    Partitions the array such that elements smaller than the pivot go to the left and larger to the right.
    Uses an iterative stack approach to eliminate recursion depth limits on large inputs (15,000+).
    
    Time Complexity: Best O(n log n), Average O(n log n), Worst O(n^2)
    Space Complexity: O(log n) auxiliary
    Stability: Unstable (partitioning swaps over long distances)
    """
    arr = [dict(item) for item in data]
    n = len(arr)
    tracker = MetricsTracker()
    start_time = time.perf_counter()

    def _median_of_three(low: int, high: int) -> int:
        mid = (low + high) // 2
        val_low = get_sort_key_value(arr[low], column)
        val_mid = get_sort_key_value(arr[mid], column)
        val_high = get_sort_key_value(arr[high], column)

        # Order low, mid, high
        if is_strictly_smaller(val_mid, val_low, reverse, tracker):
            arr[low], arr[mid] = arr[mid], arr[low]
            tracker.swaps += 1
            val_low, val_mid = val_mid, val_low

        if is_strictly_smaller(val_high, val_low, reverse, tracker):
            arr[low], arr[high] = arr[high], arr[low]
            tracker.swaps += 1
            val_low, val_high = val_high, val_low

        if is_strictly_smaller(val_high, val_mid, reverse, tracker):
            arr[mid], arr[high] = arr[high], arr[mid]
            tracker.swaps += 1
            val_mid, val_high = val_high, val_mid

        return mid

    def _partition(low: int, high: int) -> int:
        pivot_idx = _median_of_three(low, high)
        # Place pivot at high
        arr[pivot_idx], arr[high] = arr[high], arr[pivot_idx]
        tracker.swaps += 1
        pivot_val = get_sort_key_value(arr[high], column)

        i = low - 1
        for j in range(low, high):
            val_j = get_sort_key_value(arr[j], column)
            if is_smaller_or_equal(val_j, pivot_val, reverse, tracker):
                i += 1
                if i != j:
                    arr[i], arr[j] = arr[j], arr[i]
                    tracker.swaps += 1

        arr[i + 1], arr[high] = arr[high], arr[i + 1]
        tracker.swaps += 1
        return i + 1

    # Iterative stack-based quicksort prevents RecursionError
    if n > 1:
        stack = [(0, n - 1)]
        while stack:
            low, high = stack.pop()
            if low < high:
                p = _partition(low, high)
                # Push smaller partition first to optimize stack space
                if p - 1 - low < high - (p + 1):
                    stack.append((p + 1, high))
                    stack.append((low, p - 1))
                else:
                    stack.append((low, p - 1))
                    stack.append((p + 1, high))

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    return SortResult(
        algorithm_name="Quick Sort",
        column=column,
        direction="desc" if reverse else "asc",
        dataset_size=n,
        elapsed_ms=elapsed_ms,
        comparisons=tracker.comparisons,
        swaps=tracker.swaps,
        movements=tracker.movements,
        stability="Unstable",
        time_complexity_best="O(n log n)",
        time_complexity_avg="O(n log n)",
        time_complexity_worst="O(n²)",
        space_complexity="O(log n)",
        sorted_data=arr,
        is_compatible=True
    )


# ============================================================================
# 6. COUNTING SORT
# ============================================================================

def counting_sort(data: List[Dict[str, Any]], column: str, reverse: bool = False) -> SortResult:
    """
    Counting Sort:
    An integer sorting algorithm that operates by counting the number of objects that have each distinct key value,
    and using arithmetic on those counts to determine the positions of each key value in the output sequence.
    
    Handles negative integers by offsetting with the minimum value.
    Extracts None values beforehand and places them at the end.
    
    Time Complexity: O(n + k), where k = max_val - min_val + 1
    Space Complexity: O(n + k) auxiliary
    Stability: Stable (via reverse iteration over input array during placement)
    """
    arr = [dict(item) for item in data]
    n = len(arr)
    tracker = MetricsTracker()
    start_time = time.perf_counter()

    # Separate records with valid integer keys from None/invalid values
    valid_records: List[Tuple[int, Dict[str, Any]]] = []
    null_records: List[Dict[str, Any]] = []

    for item in arr:
        raw_val = item.get(column)
        if raw_val is None or raw_val == "":
            null_records.append(item)
            continue
        try:
            # Support price scaled to cents if sorting by price, otherwise int
            if column == "price":
                int_val = int(round(float(raw_val) * 100))
            elif column == "rating":
                int_val = int(round(float(raw_val) * 10))
            else:
                int_val = int(float(raw_val))
            valid_records.append((int_val, item))
        except (ValueError, TypeError):
            null_records.append(item)

    if not valid_records:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return SortResult(
            algorithm_name="Counting Sort",
            column=column,
            direction="desc" if reverse else "asc",
            dataset_size=n,
            elapsed_ms=elapsed_ms,
            comparisons=0,
            swaps=0,
            movements=0,
            stability="Stable",
            time_complexity_best="O(n + k)",
            time_complexity_avg="O(n + k)",
            time_complexity_worst="O(n + k)",
            space_complexity="O(n + k)",
            sorted_data=null_records,
            is_compatible=True
        )

    # Check key range k
    min_val = min(x[0] for x in valid_records)
    max_val = max(x[0] for x in valid_records)
    range_k = max_val - min_val + 1

    MAX_SAFE_K = 10_000_000  # Avoid allocating absurd memory if input is skewed
    if range_k > MAX_SAFE_K:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return SortResult(
            algorithm_name="Counting Sort",
            column=column,
            direction="desc" if reverse else "asc",
            dataset_size=n,
            elapsed_ms=elapsed_ms,
            comparisons=0,
            swaps=0,
            movements=0,
            stability="Stable",
            time_complexity_best="O(n + k)",
            time_complexity_avg="O(n + k)",
            time_complexity_worst="O(n + k)",
            space_complexity="O(n + k)",
            sorted_data=arr,
            is_compatible=False,
            error_message=f"Key range k={range_k:,} exceeds safe threshold for Counting Sort. Use Quick/Merge/Radix Sort."
        )

    count = [0] * range_k
    for val, _ in valid_records:
        count[val - min_val] += 1
        tracker.movements += 1

    # Cumulative counts for stable placement
    if not reverse:
        for i in range(1, range_k):
            count[i] += count[i - 1]
    else:
        # Descending cumulative counts
        for i in range(range_k - 2, -1, -1):
            count[i] += count[i + 1]

    output = [None] * len(valid_records)
    # Reverse iteration ensures stability
    for i in range(len(valid_records) - 1, -1, -1):
        val, record = valid_records[i]
        idx = val - min_val
        count[idx] -= 1
        output[count[idx]] = record
        tracker.movements += 1

    # Combine valid records and null records
    # By convention, None records are placed at the end
    final_arr = output + null_records

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    return SortResult(
        algorithm_name="Counting Sort",
        column=column,
        direction="desc" if reverse else "asc",
        dataset_size=n,
        elapsed_ms=elapsed_ms,
        comparisons=tracker.comparisons,  # 0 direct element comparisons (non-comparison sort)
        swaps=0,
        movements=tracker.movements,
        stability="Stable",
        time_complexity_best="O(n + k)",
        time_complexity_avg="O(n + k)",
        time_complexity_worst="O(n + k)",
        space_complexity=f"O(n + k) [k={range_k}]",
        sorted_data=final_arr,
        is_compatible=True
    )


# ============================================================================
# 7. BUCKET SORT
# ============================================================================

def bucket_sort(data: List[Dict[str, Any]], column: str, reverse: bool = False, num_buckets: Optional[int] = None) -> SortResult:
    """
    Bucket Sort:
    Distributes elements into a number of buckets. Each bucket is then sorted individually
    using Insertion Sort (which preserves stability), and the buckets are concatenated.
    
    Supports numeric values (rating, price, metacritic_score, rating_count).
    Handles negative numbers, identical values, and empty buckets safely.
    
    Time Complexity: Expected O(n + k), Worst O(n^2) (when all elements fall in one bucket)
    Space Complexity: O(n + k) auxiliary
    Stability: Stable (because internal sorting is Insertion Sort and distribution is sequential)
    """
    arr = [dict(item) for item in data]
    n = len(arr)
    tracker = MetricsTracker()
    start_time = time.perf_counter()

    valid_records: List[Tuple[float, Dict[str, Any]]] = []
    null_records: List[Dict[str, Any]] = []

    for item in arr:
        raw_val = item.get(column)
        if raw_val is None or raw_val == "":
            null_records.append(item)
            continue
        try:
            val = float(raw_val)
            valid_records.append((val, item))
        except (ValueError, TypeError):
            null_records.append(item)

    if not valid_records:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return SortResult(
            algorithm_name="Bucket Sort",
            column=column,
            direction="desc" if reverse else "asc",
            dataset_size=n,
            elapsed_ms=elapsed_ms,
            comparisons=0,
            swaps=0,
            movements=0,
            stability="Stable",
            time_complexity_best="O(n + k)",
            time_complexity_avg="O(n + k)",
            time_complexity_worst="O(n²)",
            space_complexity="O(n + k)",
            sorted_data=null_records,
            is_compatible=True
        )

    min_val = min(x[0] for x in valid_records)
    max_val = max(x[0] for x in valid_records)

    # Number of buckets: default to sqrt(n) or between 10 and 100
    k = num_buckets or max(10, min(100, int(math.isqrt(len(valid_records)))))
    buckets: List[List[Tuple[float, Dict[str, Any]]]] = [[] for _ in range(k)]

    val_range = max_val - min_val
    if val_range == 0.0:
        # All values identical
        for item in valid_records:
            buckets[0].append(item)
            tracker.movements += 1
    else:
        for val, rec in valid_records:
            # Normalize to [0, k-1]
            b_idx = int(((val - min_val) / val_range) * (k - 1))
            b_idx = max(0, min(k - 1, b_idx))
            buckets[b_idx].append((val, rec))
            tracker.movements += 1

    # Sort each bucket using Insertion Sort to guarantee stability
    sorted_valid: List[Dict[str, Any]] = []

    bucket_indices = range(k) if not reverse else range(k - 1, -1, -1)

    for b_idx in bucket_indices:
        b = buckets[b_idx]
        b_len = len(b)
        for i in range(1, b_len):
            key_entry = b[i]
            key_val = key_entry[0]
            j = i - 1
            while j >= 0:
                tracker.comparisons += 1
                condition = (key_val < b[j][0]) if not reverse else (key_val > b[j][0])
                if condition:
                    b[j + 1] = b[j]
                    tracker.movements += 1
                    j -= 1
                else:
                    break
            b[j + 1] = key_entry
            tracker.movements += 1

        for _, rec in b:
            sorted_valid.append(rec)
            tracker.movements += 1

    final_arr = sorted_valid + null_records

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    return SortResult(
        algorithm_name="Bucket Sort",
        column=column,
        direction="desc" if reverse else "asc",
        dataset_size=n,
        elapsed_ms=elapsed_ms,
        comparisons=tracker.comparisons,
        swaps=0,
        movements=tracker.movements,
        stability="Stable",
        time_complexity_best="O(n + k)",
        time_complexity_avg="O(n + k)",
        time_complexity_worst="O(n²)",
        space_complexity=f"O(n + k) [k={k}]",
        sorted_data=final_arr,
        is_compatible=True
    )


# ============================================================================
# 8. RADIX SORT (LSD)
# ============================================================================

def radix_sort(data: List[Dict[str, Any]], column: str, reverse: bool = False) -> SortResult:
    """
    Radix Sort (LSD - Least Significant Digit):
    Non-comparative integer sorting algorithm that sorts keys with digits processed from least
    significant to most significant digit. Uses a stable Counting Sort subroutine for each digit pass.
    
    Handles negative numbers by shifting all values by the absolute minimum offset.
    Supports integer columns, or prices/ratings converted to integer equivalents (e.g. cents).
    
    Time Complexity: O(d * (n + b)), where d is number of digits, b is base (10).
    Space Complexity: O(n + b) auxiliary
    Stability: Stable (due to stable counting passes from LSD to MSD)
    """
    arr = [dict(item) for item in data]
    n = len(arr)
    tracker = MetricsTracker()
    start_time = time.perf_counter()

    valid_records: List[Tuple[int, Dict[str, Any]]] = []
    null_records: List[Dict[str, Any]] = []

    for item in arr:
        raw_val = item.get(column)
        if raw_val is None or raw_val == "":
            null_records.append(item)
            continue
        try:
            if column == "price":
                int_val = int(round(float(raw_val) * 100))
            elif column == "rating":
                int_val = int(round(float(raw_val) * 10))
            else:
                int_val = int(float(raw_val))
            valid_records.append((int_val, item))
        except (ValueError, TypeError):
            null_records.append(item)

    if not valid_records:
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0
        return SortResult(
            algorithm_name="Radix Sort",
            column=column,
            direction="desc" if reverse else "asc",
            dataset_size=n,
            elapsed_ms=elapsed_ms,
            comparisons=0,
            swaps=0,
            movements=0,
            stability="Stable",
            time_complexity_best="O(d * (n + b))",
            time_complexity_avg="O(d * (n + b))",
            time_complexity_worst="O(d * (n + b))",
            space_complexity="O(n + b)",
            sorted_data=null_records,
            is_compatible=True
        )

    # Offset to handle negative integers so all numbers are non-negative
    min_val = min(x[0] for x in valid_records)
    offset = -min_val if min_val < 0 else 0

    shifted_records = [(val + offset, rec) for val, rec in valid_records]
    max_shifted = max(x[0] for x in shifted_records)

    # Base-10 LSD Radix Sort
    exp = 1
    RADIX = 10
    total_digits = 1 if max_shifted == 0 else int(math.log10(max_shifted)) + 1

    current_list = shifted_records
    while max_shifted // exp > 0:
        count = [0] * RADIX
        for val, _ in current_list:
            digit = (val // exp) % RADIX
            count[digit] += 1
            tracker.movements += 1

        for i in range(1, RADIX):
            count[i] += count[i - 1]

        output = [None] * len(current_list)
        for i in range(len(current_list) - 1, -1, -1):
            val, rec = current_list[i]
            digit = (val // exp) % RADIX
            count[digit] -= 1
            output[count[digit]] = (val, rec)
            tracker.movements += 1

        current_list = output
        exp *= RADIX

    # Extract sorted records
    if not reverse:
        sorted_valid = [rec for _, rec in current_list]
    else:
        # Descending: reverse the stable result
        sorted_valid = [current_list[i][1] for i in range(len(current_list) - 1, -1, -1)]

    final_arr = sorted_valid + null_records

    elapsed_ms = (time.perf_counter() - start_time) * 1000.0

    return SortResult(
        algorithm_name="Radix Sort",
        column=column,
        direction="desc" if reverse else "asc",
        dataset_size=n,
        elapsed_ms=elapsed_ms,
        comparisons=0,
        swaps=0,
        movements=tracker.movements,
        stability="Stable",
        time_complexity_best=f"O(d*(n+b)) [d={total_digits}, b=10]",
        time_complexity_avg=f"O(d*(n+b)) [d={total_digits}, b=10]",
        time_complexity_worst=f"O(d*(n+b)) [d={total_digits}, b=10]",
        space_complexity="O(n + b)",
        sorted_data=final_arr,
        is_compatible=True
    )


# ============================================================================
# ALGORITHM REGISTRY & UNIFIED CALL INTERFACE
# ============================================================================

SORTING_ALGORITHMS = {
    "Insertion Sort": insertion_sort,
    "Selection Sort": selection_sort,
    "Merge Sort": merge_sort,
    "Bubble Sort": bubble_sort,
    "Quick Sort": quick_sort,
    "Counting Sort": counting_sort,
    "Bucket Sort": bucket_sort,
    "Radix Sort": radix_sort,
}

# Compatibility map indicating which columns are compatible with specialized algorithms
COLUMN_COMPATIBILITY = {
    "Counting Sort": {"rating", "price", "rating_count", "metacritic_score", "game_id", "multiplayer"},
    "Bucket Sort": {"rating", "price", "rating_count", "metacritic_score", "game_id", "multiplayer"},
    "Radix Sort": {"rating", "price", "rating_count", "metacritic_score", "game_id", "multiplayer"},
}


def is_algorithm_compatible(algorithm_name: str, column: str) -> Tuple[bool, str]:
    """Checks whether an algorithm can run on a given column, explaining reason if not."""
    if algorithm_name in COLUMN_COMPATIBILITY:
        allowed = COLUMN_COMPATIBILITY[algorithm_name]
        if column not in allowed:
            return False, f"{algorithm_name} requires numeric or integer keys. Column '{column}' contains text/dates."
    return True, "Compatible"


def execute_sort(algorithm_name: str, data: List[Dict[str, Any]], column: str, reverse: bool = False) -> SortResult:
    """Unified entry point to execute any of the 8 algorithms."""
    if algorithm_name not in SORTING_ALGORITHMS:
        raise ValueError(f"Unknown sorting algorithm: {algorithm_name}. Supported: {list(SORTING_ALGORITHMS.keys())}")

    compatible, reason = is_algorithm_compatible(algorithm_name, column)
    if not compatible:
        return SortResult(
            algorithm_name=algorithm_name,
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
            sorted_data=list(data),
            is_compatible=False,
            error_message=reason
        )

    algo_func = SORTING_ALGORITHMS[algorithm_name]
    return algo_func(data, column, reverse=reverse)

