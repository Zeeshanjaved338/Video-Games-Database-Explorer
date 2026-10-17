"""
Models for filtering, searching, and sorting operations.
Provides typed definitions for multi-level sorting and composite condition trees.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Any, Dict


@dataclass
class FilterCondition:
    """Represents a single atomic filter condition on a column."""
    column: str
    operator: str  # contains, not_contains, starts_with, ends_with, equals, not_equals, gt, lt, gte, lte, between, before, after
    value: Any
    value2: Optional[Any] = None  # for range/between operations
    is_negated: bool = False  # logical NOT modifier
    case_sensitive: bool = False

    def to_dict(self) -> Dict[str, Any]:
        return {
            "column": self.column,
            "operator": self.operator,
            "value": self.value,
            "value2": self.value2,
            "is_negated": self.is_negated,
            "case_sensitive": self.case_sensitive
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FilterCondition":
        return cls(
            column=data.get("column", "title"),
            operator=data.get("operator", "contains"),
            value=data.get("value", ""),
            value2=data.get("value2"),
            is_negated=data.get("is_negated", False),
            case_sensitive=data.get("case_sensitive", False)
        )


@dataclass
class FilterGroup:
    """Represents a composite group of filter conditions joined by AND / OR."""
    logical_op: str = "AND"  # "AND" or "OR"
    conditions: List[FilterCondition] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "logical_op": self.logical_op,
            "conditions": [c.to_dict() for c in self.conditions]
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "FilterGroup":
        group = cls(logical_op=data.get("logical_op", "AND"))
        group.conditions = [FilterCondition.from_dict(c) for c in data.get("conditions", [])]
        return group


@dataclass
class SortLevel:
    """Represents one level in a multi-level sort specification."""
    column: str
    direction: str = "asc"  # "asc" or "desc"

    def to_dict(self) -> Dict[str, Any]:
        return {"column": self.column, "direction": self.direction}


@dataclass
class SortResult:
    """Complete measurement and execution result of a sorting algorithm run."""
    algorithm_name: str
    column: str
    direction: str
    dataset_size: int
    elapsed_ms: float
    comparisons: int
    swaps: int
    movements: int
    stability: str  # "Stable" or "Unstable"
    time_complexity_best: str
    time_complexity_avg: str
    time_complexity_worst: str
    space_complexity: str
    sorted_data: List[Dict[str, Any]] = field(default_factory=list)
    is_compatible: bool = True
    error_message: Optional[str] = None

    def to_summary_dict(self) -> Dict[str, Any]:
        """Convert to a dictionary suitable for tabular display / CSV export."""
        return {
            "Algorithm": self.algorithm_name,
            "Elapsed Time (ms)": round(self.elapsed_ms, 3),
            "Comparisons": self.comparisons,
            "Swaps": self.swaps,
            "Movements / Shifts": self.movements,
            "Stability": self.stability,
            "Time (Best)": self.time_complexity_best,
            "Time (Avg)": self.time_complexity_avg,
            "Time (Worst)": self.time_complexity_worst,
            "Space Complexity": self.space_complexity,
            "Status": "Success" if self.is_compatible else f"Skipped: {self.error_message}"
        }

