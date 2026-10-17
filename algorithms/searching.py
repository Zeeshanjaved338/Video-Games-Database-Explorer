"""
Searching and Composite Filtering Engine for Video Game Database Explorer.

Implements Requirement 2 (Column-based Search) and Requirement 3 (Composite Filters).
Supports:
- Text operators: contains, not_contains, starts_with, ends_with, equals, not_equals
- Numeric operators: equals, not_equals, gt, lt, gte, lte, between
- Date operators: before, after, between, exact
- Logical operators: AND, OR, and condition-level NOT inversion
- Consistent missing/null value handling
"""

import datetime
from typing import List, Dict, Any, Optional
from models.filter_sort import FilterCondition, FilterGroup


def evaluate_text_operator(val_str: str, op: str, target_val: str, case_sensitive: bool = False) -> bool:
    """Evaluates text match against an operator."""
    s = val_str if case_sensitive else val_str.lower()
    t = target_val if case_sensitive else target_val.lower()

    if op == "contains":
        return t in s
    elif op == "not_contains":
        return t not in s
    elif op == "starts_with":
        return s.startswith(t)
    elif op == "ends_with":
        return s.endswith(t)
    elif op == "equals":
        return s == t
    elif op == "not_equals":
        return s != t
    return False


def evaluate_numeric_operator(val_num: float, op: str, target_num: float, target_num2: Optional[float] = None) -> bool:
    """Evaluates numeric comparison against an operator."""
    if op == "equals":
        return abs(val_num - target_num) < 1e-6
    elif op == "not_equals":
        return abs(val_num - target_num) >= 1e-6
    elif op == "gt":
        return val_num > target_num
    elif op == "lt":
        return val_num < target_num
    elif op == "gte":
        return val_num >= target_num
    elif op == "lte":
        return val_num <= target_num
    elif op == "between":
        low = min(target_num, target_num2 if target_num2 is not None else target_num)
        high = max(target_num, target_num2 if target_num2 is not None else target_num)
        return low <= val_num <= high
    return False


def parse_date_str(d_str: Any) -> Optional[datetime.date]:
    """Tries to parse various date strings into datetime.date."""
    if not d_str:
        return None
    s = str(d_str).strip()
    # Try ISO YYYY-MM-DD
    for fmt in ("%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%b %d, %Y", "%d %b %Y", "%Y"):
        try:
            return datetime.datetime.strptime(s[:10] if len(s) >= 10 else s, fmt).date()
        except ValueError:
            continue
    return None


def evaluate_date_operator(val_date: datetime.date, op: str, target_d1: datetime.date, target_d2: Optional[datetime.date] = None) -> bool:
    """Evaluates date comparisons."""
    if op in ("exact", "equals"):
        return val_date == target_d1
    elif op == "before":
        return val_date < target_d1
    elif op == "after":
        return val_date > target_d1
    elif op == "between":
        d_low = min(target_d1, target_d2 if target_d2 else target_d1)
        d_high = max(target_d1, target_d2 if target_d2 else target_d1)
        return d_low <= val_date <= d_high
    return False


def evaluate_condition(record: Dict[str, Any], cond: FilterCondition) -> bool:
    """
    Evaluates a single filter condition on a record.
    Returns True if the record satisfies the condition (respecting is_negated).
    """
    raw_val = record.get(cond.column)

    # Missing value handling
    if raw_val is None or raw_val == "":
        # For not_equals or not_contains, missing value might pass if looking for something specific
        matched = False
        if cond.operator in ("not_equals", "not_contains"):
            matched = True
        return not matched if cond.is_negated else matched

    col = cond.column
    op = cond.operator

    matched = False

    # 1. Numeric columns
    if col in ("rating", "rating_count", "price", "metacritic_score", "game_id"):
        try:
            val_num = float(raw_val)
            t1 = float(cond.value)
            t2 = float(cond.value2) if cond.value2 is not None and str(cond.value2).strip() != "" else None
            matched = evaluate_numeric_operator(val_num, op, t1, t2)
        except (ValueError, TypeError):
            matched = False

    # 2. Date columns
    elif col == "release_date":
        val_d = parse_date_str(raw_val)
        target_d1 = parse_date_str(cond.value)
        target_d2 = parse_date_str(cond.value2) if cond.value2 else None
        if val_d and target_d1:
            matched = evaluate_date_operator(val_d, op, target_d1, target_d2)
        else:
            # Fallback to string matching if date parsing fails
            matched = evaluate_text_operator(str(raw_val), "contains" if op == "contains" else "equals", str(cond.value))

    # 3. Multiplayer boolean column
    elif col == "multiplayer":
        s_val = str(raw_val).lower() in ("1", "true", "yes")
        s_target = str(cond.value).lower() in ("1", "true", "yes", "multiplayer")
        matched = (s_val == s_target) if op == "equals" else (s_val != s_target)

    # 4. Text columns (title, developer, publisher, genres, platforms, source, description)
    else:
        val_str = str(raw_val)
        target_str = str(cond.value)
        matched = evaluate_text_operator(val_str, op, target_str, cond.case_sensitive)

    # Invert result if NOT is applied
    return not matched if cond.is_negated else matched


def apply_composite_filters(records: List[Dict[str, Any]], filter_group: FilterGroup) -> List[Dict[str, Any]]:
    """
    Filters records according to a FilterGroup.
    Joins conditions via AND or OR logic.
    """
    if not filter_group.conditions:
        return list(records)

    results: List[Dict[str, Any]] = []
    is_and = filter_group.logical_op.upper() == "AND"

    for rec in records:
        if is_and:
            # All conditions must be True
            matches = True
            for cond in filter_group.conditions:
                if not evaluate_condition(rec, cond):
                    matches = False
                    break
            if matches:
                results.append(rec)
        else:
            # At least one condition must be True
            matches = False
            for cond in filter_group.conditions:
                if evaluate_condition(rec, cond):
                    matches = True
                    break
            if matches:
                results.append(rec)

    return results


# Built-in Filter Presets for quick selection by users
BUILTIN_PRESETS: Dict[str, FilterGroup] = {
    "Top Rated Games (Rating >= 85)": FilterGroup(
        logical_op="AND",
        conditions=[
            FilterCondition(column="rating", operator="gte", value=85.0)
        ]
    ),
    "Metacritic Acclaimed (Score >= 90)": FilterGroup(
        logical_op="AND",
        conditions=[
            FilterCondition(column="metacritic_score", operator="gte", value=90)
        ]
    ),
    "Budget Games (Price <= $10)": FilterGroup(
        logical_op="AND",
        conditions=[
            FilterCondition(column="price", operator="lte", value=10.0),
            FilterCondition(column="price", operator="gt", value=0.0)
        ]
    ),
    "Free to Play Games": FilterGroup(
        logical_op="AND",
        conditions=[
            FilterCondition(column="price", operator="equals", value=0.0)
        ]
    ),
    "Multiplayer Action Games": FilterGroup(
        logical_op="AND",
        conditions=[
            FilterCondition(column="multiplayer", operator="equals", value=True),
            FilterCondition(column="genres", operator="contains", value="Action")
        ]
    ),
}

