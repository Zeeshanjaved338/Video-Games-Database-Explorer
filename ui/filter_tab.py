"""
Filter Tab: Visual Composite Filter Builder supporting AND, OR, condition-level NOT inversion,
dynamic condition rows, built-in presets, and filtered result counts.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QComboBox, QCheckBox, QGroupBox, QScrollArea,
    QFrame, QMessageBox
)
from PyQt5.QtCore import Qt, pyqtSignal
from typing import List, Dict, Any
from models.filter_sort import FilterCondition, FilterGroup
from algorithms.searching import BUILTIN_PRESETS


class ConditionRowWidget(QWidget):
    removed = pyqtSignal(QWidget)

    COLUMNS = [
        ("title", "Title (Text)"),
        ("developer", "Developer (Text)"),
        ("publisher", "Publisher (Text)"),
        ("genres", "Genres (Text)"),
        ("platforms", "Platforms (Text)"),
        ("rating", "Rating (Numeric 0-100)"),
        ("rating_count", "Reviews Count (Integer)"),
        ("price", "Price USD (Numeric)"),
        ("metacritic_score", "Metacritic Score (Integer)"),
        ("release_date", "Release Date (YYYY-MM-DD)"),
        ("multiplayer", "Multiplayer (Boolean)"),
        ("source", "Data Source (Text)"),
        ("description", "Description (Text)"),
    ]

    OPERATORS_TEXT = [
        ("contains", "contains"),
        ("not_contains", "does not contain"),
        ("starts_with", "starts with"),
        ("ends_with", "ends with"),
        ("equals", "equals"),
        ("not_equals", "does not equal"),
    ]

    OPERATORS_NUMERIC = [
        ("gte", ">= (Greater than or equal)"),
        ("lte", "<= (Less than or equal)"),
        ("gt", "> (Strictly greater than)"),
        ("lt", "< (Strictly less than)"),
        ("equals", "= (Exactly equals)"),
        ("not_equals", "!= (Not equals)"),
        ("between", "between [Value 1 and Value 2]"),
    ]

    OPERATORS_DATE = [
        ("after", "after (Date >)"),
        ("before", "before (Date <)"),
        ("between", "between [Date 1 and Date 2]"),
        ("exact", "exact date =="),
    ]

    OPERATORS_BOOL = [
        ("equals", "is true / enabled"),
        ("not_equals", "is false / disabled"),
    ]

    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)

        # NOT checkbox
        self.chk_not = QCheckBox("NOT")
        self.chk_not.setToolTip("Invert this condition")
        self.chk_not.setStyleSheet("color: #b91c1c; font-weight: 600; font-size: 11px;")
        layout.addWidget(self.chk_not)

        # Column Selector
        self.combo_col = QComboBox()
        for col_id, col_name in self.COLUMNS:
            self.combo_col.addItem(col_name, col_id)
        self.combo_col.currentIndexChanged.connect(self._on_column_changed)
        layout.addWidget(self.combo_col, stretch=2)

        # Operator Selector
        self.combo_op = QComboBox()
        layout.addWidget(self.combo_op, stretch=2)
        self.combo_op.currentIndexChanged.connect(self._on_operator_changed)

        # Value Input 1
        self.input_val1 = QLineEdit()
        self.input_val1.setPlaceholderText("Condition value...")
        layout.addWidget(self.input_val1, stretch=3)

        # Value Input 2 (for between)
        self.input_val2 = QLineEdit()
        self.input_val2.setPlaceholderText("End value...")
        self.input_val2.setVisible(False)
        layout.addWidget(self.input_val2, stretch=2)

        # Remove Button
        self.btn_del = QPushButton("✕")
        self.btn_del.setObjectName("dangerBtn")
        self.btn_del.setFixedWidth(28)
        self.btn_del.setToolTip("Remove condition")
        self.btn_del.clicked.connect(lambda: self.removed.emit(self))
        layout.addWidget(self.btn_del)

        self._on_column_changed(0)

    def _on_column_changed(self, idx):
        col_id = self.combo_col.currentData()
        self.combo_op.clear()

        if col_id in ("rating", "rating_count", "price", "metacritic_score"):
            for op_id, op_name in self.OPERATORS_NUMERIC:
                self.combo_op.addItem(op_name, op_id)
        elif col_id == "release_date":
            for op_id, op_name in self.OPERATORS_DATE:
                self.combo_op.addItem(op_name, op_id)
        elif col_id == "multiplayer":
            for op_id, op_name in self.OPERATORS_BOOL:
                self.combo_op.addItem(op_name, op_id)
        else:
            for op_id, op_name in self.OPERATORS_TEXT:
                self.combo_op.addItem(op_name, op_id)

    def _on_operator_changed(self, idx):
        op_id = self.combo_op.currentData()
        self.input_val2.setVisible(op_id == "between")

    def get_condition(self) -> Optional[FilterCondition]:
        col_id = self.combo_col.currentData()
        op_id = self.combo_op.currentData()
        val1 = self.input_val1.text().strip()
        val2 = self.input_val2.text().strip() if self.input_val2.isVisible() else None
        is_neg = self.chk_not.isChecked()

        if not val1 and col_id != "multiplayer":
            return None

        if col_id == "multiplayer":
            val1 = True

        return FilterCondition(
            column=col_id,
            operator=op_id,
            value=val1,
            value2=val2,
            is_negated=is_neg
        )

    def set_condition(self, cond: FilterCondition):
        # Find column
        for i in range(self.combo_col.count()):
            if self.combo_col.itemData(i) == cond.column:
                self.combo_col.setCurrentIndex(i)
                break

        # Find operator
        for i in range(self.combo_op.count()):
            if self.combo_op.itemData(i) == cond.operator:
                self.combo_op.setCurrentIndex(i)
                break

        self.input_val1.setText(str(cond.value))
        if cond.value2 is not None:
            self.input_val2.setText(str(cond.value2))
        self.chk_not.setChecked(cond.is_negated)


class FilterTab(QWidget):
    filters_applied = pyqtSignal(list, object)  # (filtered_records, FilterGroup)
    navigate_to_tab = pyqtSignal(int)

    def __init__(self, data_service, parent=None):
        super().__init__(parent)
        self.data_service = data_service
        self.row_widgets: List[ConditionRowWidget] = []
        self.last_filtered_results: List[Dict[str, Any]] = []

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 8, 10, 8)
        main_layout.setSpacing(8)

        # Title & Presets Bar
        top_box = QHBoxLayout()
        top_box.setSpacing(6)
        lbl_title = QLabel("Composite Filter Builder")
        lbl_title.setStyleSheet("font-size: 14px; font-weight: 700; color: #0f172a;")
        top_box.addWidget(lbl_title)
        top_box.addStretch()

        lbl_presets = QLabel("Filter Presets:")
        lbl_presets.setStyleSheet("font-size: 11px; color: #64748b; font-weight: 600;")
        top_box.addWidget(lbl_presets)
        self.combo_presets = QComboBox()
        self.combo_presets.addItem("— Select Preset —", None)
        for name in BUILTIN_PRESETS.keys():
            self.combo_presets.addItem(name, name)
        self.combo_presets.currentIndexChanged.connect(self._on_preset_selected)
        top_box.addWidget(self.combo_presets)

        main_layout.addLayout(top_box)

        # Filter Group Container
        filter_group_box = QGroupBox("Query Conditions")
        self.fg_layout = QVBoxLayout(filter_group_box)
        self.fg_layout.setContentsMargins(8, 10, 8, 8)
        self.fg_layout.setSpacing(6)

        # Logical Mode Row (AND / OR)
        logic_row = QHBoxLayout()
        logic_row.setSpacing(6)
        lbl_mode = QLabel("Join Mode:")
        lbl_mode.setStyleSheet("font-size: 11px; color: #334155; font-weight: 600;")
        logic_row.addWidget(lbl_mode)

        self.combo_logic = QComboBox()
        self.combo_logic.addItem("AND (All conditions must match)", "AND")
        self.combo_logic.addItem("OR (Any condition can match)", "OR")
        logic_row.addWidget(self.combo_logic)

        logic_row.addStretch()

        self.btn_add_row = QPushButton("Add Condition")
        self.btn_add_row.setObjectName("secondaryBtn")
        self.btn_add_row.clicked.connect(self.add_condition_row)
        logic_row.addWidget(self.btn_add_row)

        self.fg_layout.addLayout(logic_row)

        # Scrollable area for condition rows
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)

        self.rows_container = QWidget()
        self.rows_layout = QVBoxLayout(self.rows_container)
        self.rows_layout.setContentsMargins(0, 0, 0, 0)
        self.rows_layout.setSpacing(4)
        scroll.setWidget(self.rows_container)
        self.fg_layout.addWidget(scroll)

        main_layout.addWidget(filter_group_box)

        # Bottom Actions Bar
        action_bar = QHBoxLayout()
        action_bar.setSpacing(6)

        self.btn_apply = QPushButton("Apply Filters")
        self.btn_apply.setObjectName("successBtn")
        self.btn_apply.clicked.connect(self.apply_filters)
        action_bar.addWidget(self.btn_apply)

        self.btn_reset = QPushButton("Reset")
        self.btn_reset.setObjectName("secondaryBtn")
        self.btn_reset.clicked.connect(self.reset_filters)
        action_bar.addWidget(self.btn_reset)

        self.lbl_match_count = QLabel("Showing all records.")
        self.lbl_match_count.setStyleSheet("color: #0f172a; font-weight: 600; font-size: 11px; margin-left: 10px;")
        action_bar.addWidget(self.lbl_match_count)

        action_bar.addStretch()

        self.btn_view_lib = QPushButton("View in Library")
        self.btn_view_lib.setObjectName("secondaryBtn")
        self.btn_view_lib.clicked.connect(lambda: self.navigate_to_tab.emit(1))
        action_bar.addWidget(self.btn_view_lib)

        self.btn_sort_filtered = QPushButton("Sort Filtered Results")
        self.btn_sort_filtered.setObjectName("secondaryBtn")
        self.btn_sort_filtered.clicked.connect(lambda: self.navigate_to_tab.emit(4))
        action_bar.addWidget(self.btn_sort_filtered)

        main_layout.addLayout(action_bar)

        # Add initial default row
        self.add_condition_row()

    def add_condition_row(self) -> ConditionRowWidget:
        row = ConditionRowWidget(self.rows_container)
        row.removed.connect(self._remove_condition_row)
        self.row_widgets.append(row)
        self.rows_layout.addWidget(row)
        return row

    def _remove_condition_row(self, row_widget: ConditionRowWidget):
        if len(self.row_widgets) <= 1:
            QMessageBox.information(self, "Filter Notice", "At least one condition row must remain.")
            return

        self.rows_layout.removeWidget(row_widget)
        self.row_widgets.remove(row_widget)
        row_widget.deleteLater()

    def _on_preset_selected(self, idx):
        preset_name = self.combo_presets.currentData()
        if not preset_name or preset_name not in BUILTIN_PRESETS:
            return

        preset = BUILTIN_PRESETS[preset_name]

        # Clear existing rows
        for row in list(self.row_widgets):
            self.rows_layout.removeWidget(row)
            row.deleteLater()
        self.row_widgets.clear()

        # Set logic
        idx_logic = 0 if preset.logical_op == "AND" else 1
        self.combo_logic.setCurrentIndex(idx_logic)

        # Populate rows
        for cond in preset.conditions:
            row = self.add_condition_row()
            row.set_condition(cond)

        self.apply_filters()

    def get_filter_group(self) -> FilterGroup:
        logical_op = self.combo_logic.currentData()
        conditions = []
        for row in self.row_widgets:
            cond = row.get_condition()
            if cond:
                conditions.append(cond)
        return FilterGroup(logical_op=logical_op, conditions=conditions)

    def apply_filters(self):
        filter_group = self.get_filter_group()
        total_in_db = self.data_service.get_total_count()

        if not filter_group.conditions:
            self.last_filtered_results = self.data_service.get_all_games()
            self.lbl_match_count.setText(f"Showing all {total_in_db:,} records (empty filter).")
        else:
            self.last_filtered_results = self.data_service.filter_games(filter_group)
            matched = len(self.last_filtered_results)
            pct = (matched / total_in_db * 100.0) if total_in_db > 0 else 0
            self.lbl_match_count.setText(f"Matched {matched:,} of {total_in_db:,} records ({pct:.1f}%).")

        self.filters_applied.emit(self.last_filtered_results, filter_group)

    def reset_filters(self):
        for row in list(self.row_widgets):
            self.rows_layout.removeWidget(row)
            row.deleteLater()
        self.row_widgets.clear()

        self.combo_presets.setCurrentIndex(0)
        self.combo_logic.setCurrentIndex(0)
        self.add_condition_row()

        self.last_filtered_results = self.data_service.get_all_games()
        total_in_db = len(self.last_filtered_results)
        self.lbl_match_count.setText(f"Reset: Showing all {total_in_db:,} records.")
        self.filters_applied.emit(self.last_filtered_results, FilterGroup("AND", []))

