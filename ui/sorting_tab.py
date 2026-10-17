"""
Sorting Tab: Single-column sorting and multi-level sorting interface with live complexity
metrics and dataset scope selection (Full Dataset vs Currently Filtered Results).
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QGroupBox, QGridLayout, QFrame, QRadioButton,
    QButtonGroup, QMessageBox, QScrollArea
)
from PyQt5.QtCore import Qt, pyqtSignal
from typing import List, Dict, Any, Optional
from models.filter_sort import SortLevel, SortResult
from algorithms.sorting import SORTING_ALGORITHMS, is_algorithm_compatible
from services.sort_service import SortService


class SortLevelWidget(QWidget):
    removed = pyqtSignal(QWidget)

    COLUMNS = [
        ("rating", "Rating (0 - 100)"),
        ("metacritic_score", "Metacritic Score"),
        ("rating_count", "Reviews Count"),
        ("price", "Price ($)"),
        ("release_date", "Release Date"),
        ("title", "Title (Alphabetical)"),
        ("developer", "Developer"),
        ("publisher", "Publisher"),
        ("source", "Data Source"),
    ]

    def __init__(self, level_num: int, parent=None):
        super().__init__(parent)
        self.level_num = level_num
        self.init_ui()

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(4, 4, 4, 4)
        layout.setSpacing(8)

        self.lbl_level = QLabel(f"Level {self.level_num}:")
        self.lbl_level.setStyleSheet("font-weight: 700; color: #2563eb; min-width: 60px;")
        layout.addWidget(self.lbl_level)

        self.combo_col = QComboBox()
        for col_id, col_name in self.COLUMNS:
            self.combo_col.addItem(col_name, col_id)
        layout.addWidget(self.combo_col, stretch=3)

        self.combo_dir = QComboBox()
        self.combo_dir.addItem("Ascending (Low to High / A-Z)", "asc")
        self.combo_dir.addItem("Descending (High to Low / Z-A)", "desc")
        layout.addWidget(self.combo_dir, stretch=2)

        self.btn_del = QPushButton("✖")
        self.btn_del.setObjectName("dangerBtn")
        self.btn_del.setFixedWidth(28)
        self.btn_del.clicked.connect(lambda: self.removed.emit(self))
        layout.addWidget(self.btn_del)

    def get_sort_level(self) -> SortLevel:
        col = self.combo_col.currentData()
        direction = self.combo_dir.currentData()
        return SortLevel(column=col, direction=direction)


class SortingTab(QWidget):
    data_sorted = pyqtSignal(list, object)  # (sorted_data, SortResult)
    navigate_to_tab = pyqtSignal(int)

    def __init__(self, data_service, parent=None):
        super().__init__(parent)
        self.data_service = data_service
        self.filtered_data: Optional[List[Dict[str, Any]]] = None
        self.level_widgets: List[SortLevelWidget] = []
        self.last_sort_result: Optional[SortResult] = None

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 8, 10, 8)
        main_layout.setSpacing(8)

        # Dataset Scope Selection Box
        scope_group = QGroupBox("Dataset Scope")
        scope_layout = QHBoxLayout(scope_group)
        scope_layout.setContentsMargins(8, 10, 8, 8)
        scope_layout.setSpacing(10)

        self.radio_full = QRadioButton("Full Database (All Unique Records)")
        self.radio_full.setChecked(True)
        self.radio_filtered = QRadioButton("Currently Filtered Results")

        scope_layout.addWidget(self.radio_full)
        scope_layout.addWidget(self.radio_filtered)
        self.lbl_scope_info = QLabel("")
        self.lbl_scope_info.setStyleSheet("color: #64748b; font-size: 11px; margin-left: 10px;")
        scope_layout.addWidget(self.lbl_scope_info)
        scope_layout.addStretch()

        main_layout.addWidget(scope_group)

        # Middle Area: Split into Single Sort (Left) and Multi-Level Sort (Right)
        middle_layout = QHBoxLayout()
        middle_layout.setSpacing(8)

        # Left Box: Single Column Custom Sort
        single_group = QGroupBox("Single-Column Sort")
        s_layout = QVBoxLayout(single_group)
        s_layout.setContentsMargins(8, 10, 8, 8)
        s_layout.setSpacing(6)

        grid_s = QGridLayout()
        grid_s.setHorizontalSpacing(8)
        grid_s.setVerticalSpacing(6)

        lbl_col = QLabel("Target Column:")
        lbl_col.setStyleSheet("color: #475569; font-weight: 600;")
        grid_s.addWidget(lbl_col, 0, 0)
        self.combo_single_col = QComboBox()
        for col_id, col_name in SortLevelWidget.COLUMNS:
            self.combo_single_col.addItem(col_name, col_id)
        self.combo_single_col.currentIndexChanged.connect(self._check_algorithm_compatibility)
        grid_s.addWidget(self.combo_single_col, 0, 1)

        lbl_algo = QLabel("Algorithm:")
        lbl_algo.setStyleSheet("color: #475569; font-weight: 600;")
        grid_s.addWidget(lbl_algo, 1, 0)
        self.combo_algo = QComboBox()
        for name in SORTING_ALGORITHMS.keys():
            self.combo_algo.addItem(name, name)
        self.combo_algo.currentIndexChanged.connect(self._check_algorithm_compatibility)
        grid_s.addWidget(self.combo_algo, 1, 1)

        lbl_dir = QLabel("Direction:")
        lbl_dir.setStyleSheet("color: #475569; font-weight: 600;")
        grid_s.addWidget(lbl_dir, 2, 0)
        self.combo_single_dir = QComboBox()
        self.combo_single_dir.addItem("Ascending (Low to High / A-Z)", "asc")
        self.combo_single_dir.addItem("Descending (High to Low / Z-A)", "desc")
        grid_s.addWidget(self.combo_single_dir, 2, 1)

        s_layout.addLayout(grid_s)

        self.lbl_compat_warning = QLabel("")
        self.lbl_compat_warning.setWordWrap(True)
        self.lbl_compat_warning.setStyleSheet("color: #d97706; font-size: 11px;")
        s_layout.addWidget(self.lbl_compat_warning)

        self.btn_run_single = QPushButton("Execute Sort")
        self.btn_run_single.setObjectName("successBtn")
        self.btn_run_single.clicked.connect(self._run_single_sort)
        s_layout.addWidget(self.btn_run_single)

        s_layout.addStretch()
        middle_layout.addWidget(single_group, stretch=1)

        # Right Box: Multi-Level Sort Builder
        multi_group = QGroupBox("Multi-Level Priority Sort")
        m_layout = QVBoxLayout(multi_group)
        m_layout.setContentsMargins(8, 10, 8, 8)
        m_layout.setSpacing(6)

        m_top = QHBoxLayout()
        m_top.setSpacing(6)
        lbl_pri_algo = QLabel("Primary Algorithm:")
        lbl_pri_algo.setStyleSheet("color: #475569; font-weight: 600;")
        m_top.addWidget(lbl_pri_algo)
        self.combo_multi_algo = QComboBox()
        for name in ["Merge Sort", "Insertion Sort", "Bubble Sort", "Quick Sort", "Selection Sort"]:
            self.combo_multi_algo.addItem(name, name)
        m_top.addWidget(self.combo_multi_algo)
        m_top.addStretch()

        self.btn_add_level = QPushButton("Add Level")
        self.btn_add_level.setObjectName("secondaryBtn")
        self.btn_add_level.clicked.connect(self._add_sort_level)
        m_top.addWidget(self.btn_add_level)
        m_layout.addLayout(m_top)

        # Container for levels
        self.levels_container = QWidget()
        self.levels_layout = QVBoxLayout(self.levels_container)
        self.levels_layout.setContentsMargins(0, 0, 0, 0)
        self.levels_layout.setSpacing(4)
        m_layout.addWidget(self.levels_container)

        self.btn_run_multi = QPushButton("Execute Multi-Level Sort")
        self.btn_run_multi.setObjectName("successBtn")
        self.btn_run_multi.clicked.connect(self._run_multi_sort)
        m_layout.addWidget(self.btn_run_multi)

        m_layout.addStretch()
        middle_layout.addWidget(multi_group, stretch=1)

        main_layout.addLayout(middle_layout)

        # Bottom Section: Live Metrics & Complexity Inspector Card
        metrics_group = QGroupBox("Execution Metrics & Complexity")
        m_grid = QGridLayout(metrics_group)
        m_grid.setContentsMargins(8, 10, 8, 8)
        m_grid.setHorizontalSpacing(8)
        m_grid.setVerticalSpacing(4)

        self.lbl_m_algo = self._make_metric_box(m_grid, "Algorithm", "None", 0, 0, "#0f172a")
        self.lbl_m_time = self._make_metric_box(m_grid, "Elapsed Time", "0.000 ms", 0, 1, "#059669")
        self.lbl_m_comparisons = self._make_metric_box(m_grid, "Comparisons", "0", 0, 2, "#0f172a")
        self.lbl_m_swaps = self._make_metric_box(m_grid, "Swaps", "0", 0, 3, "#0f172a")
        self.lbl_m_movements = self._make_metric_box(m_grid, "Movements", "0", 0, 4, "#0f172a")
        self.lbl_m_stability = self._make_metric_box(m_grid, "Stability", "N/A", 1, 0, "#0f172a")
        self.lbl_m_time_c = self._make_metric_box(m_grid, "Time Complexity", "N/A", 1, 1, "#475569")
        self.lbl_m_space_c = self._make_metric_box(m_grid, "Space Complexity", "N/A", 1, 2, "#475569")
        self.lbl_m_status = self._make_metric_box(m_grid, "Status", "Idle", 1, 3, "#059669")

        # Action button to view in library
        self.btn_view_sorted = QPushButton("View in Library")
        self.btn_view_sorted.setObjectName("secondaryBtn")
        self.btn_view_sorted.setEnabled(False)
        self.btn_view_sorted.clicked.connect(lambda: self.navigate_to_tab.emit(1))
        m_grid.addWidget(self.btn_view_sorted, 1, 4)

        main_layout.addWidget(metrics_group)

        # Setup initial 2 multi-sort levels
        self._add_sort_level()
        self._add_sort_level()
        self._check_algorithm_compatibility()

    def _make_metric_box(self, grid: QGridLayout, title: str, val: str, r: int, c: int, color_hex: str) -> QLabel:
        frame = QFrame()
        frame.setStyleSheet("background-color: #f8fafc; border: 1px solid #e2e8f0; border-radius: 4px; padding: 4px;")
        vbox = QVBoxLayout(frame)
        vbox.setContentsMargins(6, 3, 6, 3)
        vbox.setSpacing(2)

        t_lbl = QLabel(title)
        t_lbl.setObjectName("metricTitle")
        t_lbl.setStyleSheet("color: #64748b; font-size: 10px; font-weight: 700; text-transform: uppercase; letter-spacing: 0.3px;")
        v_lbl = QLabel(val)
        v_lbl.setObjectName("metricValue")
        v_lbl.setStyleSheet(f"color: {color_hex}; font-size: 12px; font-weight: 700;")

        vbox.addWidget(t_lbl)
        vbox.addWidget(v_lbl)
        grid.addWidget(frame, r, c)
        return v_lbl

    def _add_sort_level(self):
        lvl_num = len(self.level_widgets) + 1
        widget = SortLevelWidget(lvl_num, self.levels_container)
        widget.removed.connect(self._remove_sort_level)
        self.level_widgets.append(widget)
        self.levels_layout.addWidget(widget)

    def _remove_sort_level(self, widget: SortLevelWidget):
        if len(self.level_widgets) <= 1:
            QMessageBox.information(self, "Sort Level", "At least one sort level is required.")
            return

        self.levels_layout.removeWidget(widget)
        self.level_widgets.remove(widget)
        widget.deleteLater()

        # Renumber
        for idx, w in enumerate(self.level_widgets):
            w.level_num = idx + 1
            w.lbl_level.setText(f"Level {idx + 1}:")

    def set_filtered_context(self, filtered_games: List[Dict[str, Any]]):
        self.filtered_data = filtered_games
        count = len(filtered_games)
        self.lbl_scope_info.setText(f"(Filtered dataset contains {count:,} games)")

    def _get_input_dataset(self) -> List[Dict[str, Any]]:
        if self.radio_filtered.isChecked() and self.filtered_data is not None:
            return list(self.filtered_data)
        return self.data_service.get_all_games()

    def _check_algorithm_compatibility(self):
        col = self.combo_single_col.currentData()
        algo = self.combo_algo.currentText()
        compat, reason = is_algorithm_compatible(algo, col)
        if not compat:
            self.lbl_compat_warning.setText(f"⚠️ {reason}")
            self.btn_run_single.setEnabled(False)
        else:
            self.lbl_compat_warning.setText("✓ Column and algorithm are fully compatible.")
            self.btn_run_single.setEnabled(True)

    def _run_single_sort(self):
        data = self._get_input_dataset()
        if not data:
            QMessageBox.warning(self, "Sort Notice", "No records found in selected scope to sort.")
            return

        col = self.combo_single_col.currentData()
        algo = self.combo_algo.currentText()
        reverse = (self.combo_single_dir.currentData() == "desc")

        res = SortService.sort_single_column(data, algo, col, reverse=reverse)
        self._update_metrics_card(res)

    def _run_multi_sort(self):
        data = self._get_input_dataset()
        if not data:
            QMessageBox.warning(self, "Sort Notice", "No records found in selected scope to sort.")
            return

        primary_algo = self.combo_multi_algo.currentText()
        levels = [w.get_sort_level() for w in self.level_widgets]

        res = SortService.sort_multi_level(data, primary_algo, levels)
        self._update_metrics_card(res)

    def _update_metrics_card(self, res: SortResult):
        self.last_sort_result = res
        self.lbl_m_algo.setText(res.algorithm_name)
        self.lbl_m_time.setText(f"{res.elapsed_ms:.3f} ms")
        self.lbl_m_comparisons.setText(f"{res.comparisons:,}")
        self.lbl_m_swaps.setText(f"{res.swaps:,}")
        self.lbl_m_movements.setText(f"{res.movements:,}")
        self.lbl_m_stability.setText(res.stability)
        self.lbl_m_time_c.setText(f"Avg: {res.time_complexity_avg} | Worst: {res.time_complexity_worst}")
        self.lbl_m_space_c.setText(res.space_complexity)
        self.lbl_m_status.setText("Success" if res.is_compatible else f"Error: {res.error_message}")

        self.btn_view_sorted.setEnabled(True)
        self.data_sorted.emit(res.sorted_data, res)

