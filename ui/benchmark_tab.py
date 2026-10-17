"""
Benchmark Tab: Executes all eight sorting algorithms across identical inputs,
displays results in a comparison table, renders Matplotlib performance charts,
and exports benchmark reports to CSV. Uses background QThread so UI never freezes.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QPushButton, QGroupBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QProgressBar, QMessageBox, QFileDialog, QSplitter
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from typing import List, Dict, Any, Optional
from models.filter_sort import SortResult
from services.benchmark_service import BenchmarkService
from services.export_service import ExportService
from algorithms.sorting import SORTING_ALGORITHMS

import matplotlib
matplotlib.use("Qt5Agg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure


class BenchmarkWorker(QThread):
    progress_updated = pyqtSignal(str, int, int)  # algo_name, step, total
    benchmark_complete = pyqtSignal(list)         # List[SortResult]

    def __init__(self, data: List[Dict[str, Any]], column: str, reverse: bool = False, parent=None):
        super().__init__(parent)
        self.data = data
        self.column = column
        self.reverse = reverse
        self._is_cancelled = False

    def cancel(self):
        self._is_cancelled = True

    def run(self):
        def _should_cancel() -> bool:
            return self._is_cancelled

        def _progress(algo_name: str, step: int, total: int):
            self.progress_updated.emit(algo_name, step, total)

        results = BenchmarkService.run_benchmark(
            data=self.data,
            column=self.column,
            reverse=self.reverse,
            progress_callback=_progress,
            should_cancel=_should_cancel
        )
        self.benchmark_complete.emit(results)


class BenchmarkTab(QWidget):
    def __init__(self, data_service, parent=None):
        super().__init__(parent)
        self.data_service = data_service
        self.filtered_data: Optional[List[Dict[str, Any]]] = None
        self.worker: Optional[BenchmarkWorker] = None
        self.current_results: List[SortResult] = []

        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(10, 8, 10, 8)
        main_layout.setSpacing(8)

        # Control Panel
        control_group = QGroupBox("Benchmark Configuration & Controls")
        c_layout = QHBoxLayout(control_group)

        c_layout.addWidget(QLabel("Target Column:"))
        self.combo_col = QComboBox()
        columns = [
            ("rating", "Rating (Numeric)"),
            ("price", "Price (Numeric)"),
            ("metacritic_score", "Metacritic (Integer)"),
            ("rating_count", "Reviews Count (Integer)"),
            ("release_date", "Release Date (Comparable)"),
            ("title", "Title (Alphabetical)"),
        ]
        for col_id, col_name in columns:
            self.combo_col.addItem(col_name, col_id)
        c_layout.addWidget(self.combo_col)

        c_layout.addWidget(QLabel("Order:"))
        self.combo_dir = QComboBox()
        self.combo_dir.addItem("Ascending (Low to High)", False)
        self.combo_dir.addItem("Descending (High to Low)", True)
        c_layout.addWidget(self.combo_dir)

        c_layout.addWidget(QLabel("Scope / Dataset Size:"))
        self.combo_scope = QComboBox()
        self.combo_scope.addItem("Fast Viva Demo (1,000 records)", 1000)
        self.combo_scope.addItem("Standard Benchmark (3,000 records)", 3000)
        self.combo_scope.addItem("Large Benchmark (5,000 records)", 5000)
        self.combo_scope.addItem("Full Database (All ~15,000+ records)", "all")
        self.combo_scope.addItem("Currently Filtered Results", "filtered")
        c_layout.addWidget(self.combo_scope)

        self.btn_run = QPushButton("Run Benchmark")
        self.btn_run.setObjectName("successBtn")
        self.btn_run.clicked.connect(self._start_benchmark)
        c_layout.addWidget(self.btn_run)

        self.btn_cancel = QPushButton("Cancel")
        self.btn_cancel.setObjectName("dangerBtn")
        self.btn_cancel.setEnabled(False)
        self.btn_cancel.clicked.connect(self._cancel_benchmark)
        c_layout.addWidget(self.btn_cancel)

        self.btn_export = QPushButton("Export CSV Report")
        self.btn_export.setObjectName("secondaryBtn")
        self.btn_export.setEnabled(False)
        self.btn_export.clicked.connect(self._export_report)
        c_layout.addWidget(self.btn_export)

        c_layout.addStretch()
        main_layout.addWidget(control_group)

        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 8)
        self.progress_bar.setValue(0)
        self.lbl_progress = QLabel("Select benchmark settings and click 'Run Benchmark'.")
        self.lbl_progress.setStyleSheet("color: #64748b; font-size: 11px;")

        p_box = QHBoxLayout()
        p_box.addWidget(self.lbl_progress)
        p_box.addStretch()
        p_box.addWidget(self.progress_bar)
        main_layout.addLayout(p_box)

        # Splitter: Table (Top) + Matplotlib Charts (Bottom)
        splitter = QSplitter(Qt.Vertical)

        # Results Table
        table_group = QGroupBox("Benchmark Comparative Metrics")
        t_layout = QVBoxLayout(table_group)

        self.table = QTableWidget()
        headers = [
            "Algorithm", "Time (ms)", "Comparisons", "Swaps",
            "Movements / Shifts", "Stability", "Time (Best)",
            "Time (Avg)", "Time (Worst)", "Space Complexity", "Status"
        ]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.verticalHeader().setVisible(False)
        t_layout.addWidget(self.table)
        splitter.addWidget(table_group)

        # Matplotlib Canvas Container
        chart_group = QGroupBox("Graphical Performance Comparison")
        chart_layout = QVBoxLayout(chart_group)

        self.figure = Figure(facecolor="#ffffff", figsize=(8, 3.5))
        self.canvas = FigureCanvas(self.figure)
        chart_layout.addWidget(self.canvas)
        splitter.addWidget(chart_group)

        splitter.setStretchFactor(0, 2)
        splitter.setStretchFactor(1, 3)
        main_layout.addWidget(splitter)

        self._draw_empty_chart()

    def set_filtered_context(self, filtered_games: List[Dict[str, Any]]):
        self.filtered_data = filtered_games

    def _start_benchmark(self):
        col = self.combo_col.currentData()
        reverse = self.combo_dir.currentData()
        scope_choice = self.combo_scope.currentData()

        # Select data slice
        if scope_choice == "filtered":
            if not self.filtered_data:
                QMessageBox.warning(self, "Scope Notice", "No active filtered results. Apply filters first in Tab 3.")
                return
            benchmark_data = list(self.filtered_data)
        elif scope_choice == "all":
            benchmark_data = self.data_service.get_all_games()
        else:
            all_games = self.data_service.get_all_games()
            sample_size = int(scope_choice)
            benchmark_data = all_games[:sample_size]

        if not benchmark_data:
            QMessageBox.warning(self, "Benchmark Notice", "No records found to benchmark.")
            return

        self.btn_run.setEnabled(False)
        self.btn_cancel.setEnabled(True)
        self.btn_export.setEnabled(False)
        self.progress_bar.setValue(0)
        self.lbl_progress.setText(f"Starting benchmark on {len(benchmark_data):,} records for column '{col}'...")

        self.worker = BenchmarkWorker(benchmark_data, col, reverse=reverse, parent=self)
        self.worker.progress_updated.connect(self._on_worker_progress)
        self.worker.benchmark_complete.connect(self._on_worker_complete)
        self.worker.start()

    def _cancel_benchmark(self):
        if self.worker:
            self.worker.cancel()
            self.lbl_progress.setText("Cancelling benchmark...")
            self.btn_cancel.setEnabled(False)

    def _on_worker_progress(self, algo_name: str, step: int, total: int):
        self.progress_bar.setValue(step)
        self.lbl_progress.setText(f"Running algorithm {step} of {total}: {algo_name}...")

    def _on_worker_complete(self, results: List[SortResult]):
        self.current_results = results
        self.btn_run.setEnabled(True)
        self.btn_cancel.setEnabled(False)
        self.btn_export.setEnabled(True)
        self.lbl_progress.setText("✓ Benchmark completed successfully for all algorithms!")

        self._populate_table(results)
        self._plot_charts(results)

    def _populate_table(self, results: List[SortResult]):
        self.table.setRowCount(len(results))
        for row_idx, res in enumerate(results):
            vals = [
                res.algorithm_name,
                f"{res.elapsed_ms:.2f}" if res.is_compatible else "—",
                f"{res.comparisons:,}" if res.is_compatible else "—",
                f"{res.swaps:,}" if res.is_compatible else "—",
                f"{res.movements:,}" if res.is_compatible else "—",
                res.stability if res.is_compatible else "—",
                res.time_complexity_best if res.is_compatible else "—",
                res.time_complexity_avg if res.is_compatible else "—",
                res.time_complexity_worst if res.is_compatible else "—",
                res.space_complexity if res.is_compatible else "—",
                "Success (Verified)" if res.is_compatible else f"Skipped: {res.error_message}"
            ]

            for col_idx, val in enumerate(vals):
                item = QTableWidgetItem(val)
                if col_idx in (1, 2, 3, 4):
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                else:
                    item.setTextAlignment(Qt.AlignLeft | Qt.AlignVCenter)

                if not res.is_compatible:
                    item.setForeground(Qt.darkRed)
                self.table.setItem(row_idx, col_idx, item)

    def _draw_empty_chart(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor("#f8fafc")
        ax.text(0.5, 0.5, "Performance charts will appear here after running benchmark.",
                color="#64748b", ha="center", va="center", fontsize=10)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_color("#e2e8f0")
        self.canvas.draw()

    def _plot_charts(self, results: List[SortResult]):
        self.figure.clear()

        # Filter compatible results
        valid = [r for r in results if r.is_compatible]
        if not valid:
            self._draw_empty_chart()
            return

        names = [r.algorithm_name.replace(" Sort", "") for r in valid]
        times = [r.elapsed_ms for r in valid]
        comparisons = [r.comparisons for r in valid]

        # 2 Subplots side by side
        ax1 = self.figure.add_subplot(121)
        ax2 = self.figure.add_subplot(122)

        for ax in (ax1, ax2):
            ax.set_facecolor("#ffffff")
            ax.tick_params(colors="#334155", labelsize=8)
            for spine in ax.spines.values():
                spine.set_color("#cbd5e1")

        # Plot 1: Execution Time (ms)
        bars1 = ax1.bar(names, times, color="#2563eb", edgecolor="#1d4ed8", width=0.6)
        ax1.set_title("Execution Time (milliseconds)", color="#0f172a", fontsize=9, fontweight="bold", pad=8)
        ax1.set_ylabel("Elapsed ms", color="#475569", fontsize=8)
        ax1.tick_params(axis='x', rotation=30)
        ax1.grid(axis='y', linestyle='--', alpha=0.3, color='#94a3b8')

        # Add values on top of bars
        for bar in bars1:
            h = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width() / 2.0, h, f"{h:.1f}", ha='center', va='bottom', color='#0f172a', fontsize=7.5)

        # Plot 2: Operations Count (Comparisons)
        bars2 = ax2.bar(names, comparisons, color="#059669", edgecolor="#047857", width=0.6)
        ax2.set_title("Key Comparisons Count", color="#0f172a", fontsize=9, fontweight="bold", pad=8)
        ax2.set_ylabel("Comparisons", color="#475569", fontsize=8)
        ax2.tick_params(axis='x', rotation=30)
        ax2.grid(axis='y', linestyle='--', alpha=0.3, color='#94a3b8')

        self.figure.tight_layout(pad=1.5)
        self.canvas.draw()

    def _export_report(self):
        if not self.current_results:
            return

        path, _ = QFileDialog.getSaveFileName(self, "Export Benchmark Report", "benchmark_report.csv", "CSV Files (*.csv)")
        if path:
            success = ExportService.export_benchmark_to_csv(self.current_results, path)
            if success:
                QMessageBox.information(self, "Export Complete", f"Benchmark metrics report saved to:\n{path}")
            else:
                QMessageBox.critical(self, "Export Failed", "Could not export benchmark report.")

