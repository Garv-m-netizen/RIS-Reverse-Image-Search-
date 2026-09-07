"""
PyQt5 Desktop Application Entry Point for Face Verification Pipeline.
Provides a modern dark theme interface with drag-and-drop, live status logging,
asynchronous worker management, and clickable Etherscan verification details.
"""

import sys
import os
import webbrowser
from pathlib import Path

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTextEdit, QFrame, QFileDialog, QLineEdit,
    QProgressBar, QStatusBar, QGraphicsDropShadowEffect, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QIcon, QFont, QColor, QDragEnterEvent, QDropEvent
from PyQt5.QtCore import Qt, QSize, QUrl

import config
from pipeline import PipelineWorker

DARK_STYLESHEET = """
QMainWindow {
    background-color: #1e1e2e;
}
QWidget {
    font-family: 'Segoe UI', Arial, sans-serif;
    color: #cdd6f4;
}
QFrame#card {
    background-color: #313244;
    border-radius: 12px;
    border: 1px solid #45475a;
}
QFrame#dropZone {
    background-color: #181825;
    border: 2px dashed #89b4fa;
    border-radius: 12px;
}
QFrame#dropZone:hover {
    background-color: #1e1e2e;
    border-color: #b4befe;
}
QLabel#titleLabel {
    font-size: 20px;
    font-weight: bold;
    color: #89b4fa;
}
QLabel#sectionTitle {
    font-size: 13px;
    font-weight: bold;
    color: #a6adc8;
    text-transform: uppercase;
    letter-spacing: 1px;
}
QPushButton#primaryBtn {
    background-color: #89b4fa;
    color: #11111b;
    font-size: 15px;
    font-weight: bold;
    border-radius: 8px;
    padding: 12px 24px;
    border: none;
}
QPushButton#primaryBtn:hover {
    background-color: #b4befe;
}
QPushButton#primaryBtn:disabled {
    background-color: #45475a;
    color: #7f849c;
}
QPushButton#secondaryBtn {
    background-color: #45475a;
    color: #cdd6f4;
    font-size: 13px;
    font-weight: bold;
    border-radius: 6px;
    padding: 8px 16px;
    border: 1px solid #585b70;
}
QPushButton#secondaryBtn:hover {
    background-color: #585b70;
}
QTextEdit#logConsole {
    background-color: #11111b;
    color: #a6e3a1;
    font-family: 'Consolas', 'Courier New', monospace;
    font-size: 12px;
    border: 1px solid #313244;
    border-radius: 8px;
    padding: 8px;
}
QProgressBar {
    border: 1px solid #45475a;
    border-radius: 6px;
    text-align: center;
    background-color: #181825;
    color: #cdd6f4;
    font-weight: bold;
}
QProgressBar::chunk {
    background-color: #89b4fa;
    border-radius: 5px;
}
QStatusBar {
    background-color: #181825;
    color: #a6adc8;
    border-top: 1px solid #313244;
}
"""


class DropZoneWidget(QFrame):
    """Custom Drag & Drop area accepting image files."""
    def __init__(self, parent_app):
        super().__init__()
        self.parent_app = parent_app
        self.setObjectName("dropZone")
        self.setAcceptDrops(True)
        self.setMinimumHeight(170)

        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        self.icon_label = QLabel("📁")
        self.icon_label.setStyleSheet("font-size: 36px; background: transparent;")
        self.icon_label.setAlignment(Qt.AlignCenter)

        self.text_label = QLabel("Drag & Drop Face Image Here\nor Click to Browse")
        self.text_label.setStyleSheet("font-size: 14px; color: #a6adc8; font-weight: bold; background: transparent;")
        self.text_label.setAlignment(Qt.AlignCenter)

        layout.addWidget(self.icon_label)
        layout.addWidget(self.text_label)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.parent_app.browse_file()

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            urls = event.mimeData().urls()
            if len(urls) > 0 and urls[0].toLocalFile().lower().endswith(('.jpg', '.jpeg', '.png')):
                event.acceptProposedAction()
                self.setStyleSheet("QFrame#dropZone { background-color: #313244; border: 2px dashed #a6e3a1; }")

    def dragLeaveEvent(self, event):
        self.setStyleSheet("")

    def dropEvent(self, event: QDropEvent):
        self.setStyleSheet("")
        urls = event.mimeData().urls()
        if urls:
            file_path = urls[0].toLocalFile()
            self.parent_app.set_image_file(file_path)


class FaceVerificationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.current_image_path = None
        self.worker = None
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("🏆 Face Verification Pipeline — AI & Sepolia Blockchain")
        self.resize(880, 840)
        self.setMinimumSize(780, 750)
        self.setStyleSheet(DARK_STYLESHEET)

        # Main Central Widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(24, 20, 24, 20)
        main_layout.setSpacing(16)

        # 1. Header Bar
        header_card = QFrame()
        header_card.setObjectName("card")
        header_layout = QHBoxLayout(header_card)
        header_layout.setContentsMargins(16, 12, 16, 12)

        title = QLabel("🔍 FACE VERIFICATION PIPELINE")
        title.setObjectName("titleLabel")

        subtitle = QLabel("AI InsightFace • Bright Data Web Search • Ethereum Sepolia Testnet")
        subtitle.setStyleSheet("color: #a6adc8; font-size: 12px; font-weight: 500;")

        header_info = QVBoxLayout()
        header_info.addWidget(title)
        header_info.addWidget(subtitle)

        header_layout.addLayout(header_info)
        header_layout.addStretch()

        status_badge = QLabel("NETWORK: SEPOLIA")
        status_badge.setStyleSheet(
            "background-color: #45475a; color: #a6e3a1; font-weight: bold; "
            "padding: 6px 12px; border-radius: 6px; font-size: 11px;"
        )
        header_layout.addWidget(status_badge)

        main_layout.addWidget(header_card)

        # 2. Top Split: Image Upload & Preview Card
        upload_card = QFrame()
        upload_card.setObjectName("card")
        upload_layout = QVBoxLayout(upload_card)
        upload_layout.setContentsMargins(16, 14, 16, 14)

        sec1_title = QLabel("1. IMAGE UPLOAD & AI SCAN")
        sec1_title.setObjectName("sectionTitle")
        upload_layout.addWidget(sec1_title)

        upload_content_layout = QHBoxLayout()
        upload_content_layout.setSpacing(16)

        # Drop Zone
        self.drop_zone = DropZoneWidget(self)
        upload_content_layout.addWidget(self.drop_zone, stretch=2)

        # Image Preview Panel
        preview_frame = QFrame()
        preview_frame.setStyleSheet("background-color: #181825; border-radius: 8px; border: 1px solid #45475a;")
        preview_layout = QVBoxLayout(preview_frame)
        preview_layout.setAlignment(Qt.AlignCenter)

        self.preview_label = QLabel("No Image Loaded")
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setStyleSheet("color: #7f849c; font-size: 12px;")
        self.preview_label.setFixedSize(140, 140)

        preview_layout.addWidget(self.preview_label)
        upload_content_layout.addWidget(preview_frame, stretch=1)

        upload_layout.addLayout(upload_content_layout)

        # File Status Label & Browse Button
        file_bar = QHBoxLayout()
        self.file_status_label = QLabel("📁 Status: Please select or drop a face image file")
        self.file_status_label.setStyleSheet("color: #a6adc8; font-size: 12px;")

        self.browse_btn = QPushButton("Browse File...")
        self.browse_btn.setObjectName("secondaryBtn")
        self.browse_btn.clicked.connect(self.browse_file)

        file_bar.addWidget(self.file_status_label)
        file_bar.addStretch()
        file_bar.addWidget(self.browse_btn)

        upload_layout.addLayout(file_bar)

        # Target URL Optional Input Field
        self.target_url_input = QLineEdit()
        self.target_url_input.setPlaceholderText("🔗 Target Social Media / Profile URL (Optional - e.g. https://linkedin.com/in/... or leave blank to search)")
        self.target_url_input.setStyleSheet("background-color: #181825; border: 1px solid #45475a; border-radius: 6px; padding: 8px 12px; color: #cdd6f4; font-size: 13px;")
        upload_layout.addWidget(self.target_url_input)

        main_layout.addWidget(upload_card)

        # 3. Control Action Card
        ctrl_card = QFrame()
        ctrl_card.setObjectName("card")
        ctrl_layout = QHBoxLayout(ctrl_card)
        ctrl_layout.setContentsMargins(16, 12, 16, 12)

        self.start_btn = QPushButton("▶ START PIPELINE")
        self.start_btn.setObjectName("primaryBtn")
        self.start_btn.setEnabled(False)
        self.start_btn.clicked.connect(self.start_pipeline)

        ctrl_layout.addWidget(self.start_btn)
        main_layout.addWidget(ctrl_card)

        # 4. Live Status Log Card
        log_card = QFrame()
        log_card.setObjectName("card")
        log_layout = QVBoxLayout(log_card)
        log_layout.setContentsMargins(16, 14, 16, 14)

        sec3_title = QLabel("2. LIVE EXECUTION LOG")
        sec3_title.setObjectName("sectionTitle")
        log_layout.addWidget(sec3_title)

        self.log_console = QTextEdit()
        self.log_console.setObjectName("logConsole")
        self.log_console.setReadOnly(True)
        self.log_console.setMinimumHeight(140)
        self.log_console.append("> Ready. Load a face image to begin verification pipeline.\n")

        log_layout.addWidget(self.log_console)
        main_layout.addWidget(log_card)

        # 5. Results & Blockchain Verification Card
        results_card = QFrame()
        results_card.setObjectName("card")
        results_layout = QVBoxLayout(results_card)
        results_layout.setContentsMargins(16, 14, 16, 14)

        sec4_title = QLabel("3. VERIFICATION RESULTS & BLOCKCHAIN PROOF")
        sec4_title.setObjectName("sectionTitle")
        results_layout.addWidget(sec4_title)

        results_grid = QVBoxLayout()
        results_grid.setSpacing(8)

        self.res_url_label = QLabel("Found Post: -")
        self.res_url_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #89b4fa;")
        self.res_url_label.setOpenExternalLinks(True)

        self.res_source_label = QLabel("Source Platform: -")
        self.res_source_label.setStyleSheet("font-size: 12px; color: #cdd6f4;")

        self.res_blockchain_label = QLabel("Blockchain Status: Waiting for execution")
        self.res_blockchain_label.setStyleSheet("font-size: 12px; color: #f9e2af;")

        self.res_tx_label = QLabel("Tx Hash: -")
        self.res_tx_label.setStyleSheet("font-size: 12px; font-family: monospace; color: #a6e3a1;")

        results_grid.addWidget(self.res_url_label)
        results_grid.addWidget(self.res_source_label)
        results_grid.addWidget(self.res_blockchain_label)
        results_grid.addWidget(self.res_tx_label)

        action_bar = QHBoxLayout()
        self.etherscan_btn = QPushButton("🔗 View on Etherscan")
        self.etherscan_btn.setObjectName("secondaryBtn")
        self.etherscan_btn.setEnabled(False)
        self.etherscan_btn.clicked.connect(self.open_etherscan)

        action_bar.addWidget(self.etherscan_btn)
        action_bar.addStretch()

        results_layout.addLayout(results_grid)
        results_layout.addLayout(action_bar)

        main_layout.addWidget(results_card)

        # 6. Progress Bar & Status Bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(14)
        main_layout.addWidget(self.progress_bar)

        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Status: Ready | Pipeline: Idle | Time: 0.0s")

        self.last_etherscan_url = None

    def browse_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Face Image", "", "Image Files (*.jpg *.jpeg *.png)"
        )
        if file_path:
            self.set_image_file(file_path)

    def set_image_file(self, file_path: str):
        if not os.path.exists(file_path):
            return

        self.current_image_path = file_path
        size_kb = round(os.path.getsize(file_path) / 1024, 1)
        file_name = Path(file_path).name

        self.file_status_label.setText(f"✅ Loaded: {file_name} ({size_kb} KB)")
        self.file_status_label.setStyleSheet("color: #a6e3a1; font-weight: bold;")

        # Load pixmap into preview label
        pixmap = QPixmap(file_path)
        if not pixmap.isNull():
            scaled = pixmap.scaled(130, 130, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.preview_label.setPixmap(scaled)

        self.start_btn.setEnabled(True)
        self.append_log(f"> Loaded image file: '{file_name}' ({size_kb} KB). Ready to start pipeline.", "info")

    def append_log(self, text: str, level: str = "info"):
        color = "#a6e3a1" if level == "success" else "#89b4fa" if level == "info" else "#f38ba8" if level == "error" else "#f9e2af"
        html_msg = f"<span style='color: {color};'>{text}</span>"
        self.log_console.append(html_msg)
        self.log_console.verticalScrollBar().setValue(self.log_console.verticalScrollBar().maximum())

    def start_pipeline(self):
        if not self.current_image_path:
            return

        self.start_btn.setEnabled(False)
        self.browse_btn.setEnabled(False)
        self.etherscan_btn.setEnabled(False)
        self.progress_bar.setValue(0)
        self.log_console.clear()
        
        self.res_url_label.setText("Found Post: Searching...")
        self.res_source_label.setText("Source Platform: Searching...")
        self.res_blockchain_label.setText("Blockchain Status: Processing...")
        self.res_blockchain_label.setStyleSheet("font-size: 12px; color: #f9e2af;")
        self.res_tx_label.setText("Tx Hash: Waiting for transaction...")

        self.append_log("🚀 Starting Face Verification Pipeline...", "info")
        self.status_bar.showMessage("Status: Running Pipeline... | Pipeline: Active | Time: 0.0s")

        # Launch QThread worker
        target_url = self.target_url_input.text().strip()
        self.worker = PipelineWorker(self.current_image_path, target_url=target_url)
        self.worker.log_signal.connect(self.append_log)
        self.worker.progress_signal.connect(self.progress_bar.setValue)
        self.worker.finished_signal.connect(self.on_pipeline_finished)
        self.worker.error_signal.connect(self.on_pipeline_error)
        self.worker.start()

    def on_pipeline_finished(self, data: dict):
        self.start_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)

        search = data["search"]
        post_url = search["url"]
        platform = search["platform"]
        bc = data["blockchain"]
        tx_hash = bc["tx_hash"]
        self.last_etherscan_url = data["etherscan_url"]

        self.res_url_label.setText(f"Found Post: <a style='color: #89b4fa;' href='{post_url}'>{post_url}</a>")
        self.res_source_label.setText(f"Source Platform: {platform} (Relevance: {int(search.get('relevance', 0.95)*100)}%)")
        
        if bc.get("success") or data.get("verification", {}).get("verified"):
            self.res_blockchain_label.setText("Blockchain: ✅ Verified on Ethereum Sepolia Testnet")
            self.res_blockchain_label.setStyleSheet("font-size: 12px; color: #a6e3a1; font-weight: bold;")
        else:
            self.res_blockchain_label.setText("Blockchain: ⚠️ Transaction Pending / Warning")
            self.res_blockchain_label.setStyleSheet("font-size: 12px; color: #f9e2af;")

        self.res_tx_label.setText(f"Tx Hash: {tx_hash}")
        self.etherscan_btn.setEnabled(True)

        elapsed = data["elapsed"]
        self.status_bar.showMessage(f"Status: Ready | Pipeline: Complete ✅ | Time: {elapsed}s")

    def on_pipeline_error(self, err_msg: str):
        self.start_btn.setEnabled(True)
        self.browse_btn.setEnabled(True)
        self.res_blockchain_label.setText(f"Blockchain Status: ❌ Error: {err_msg}")
        self.res_blockchain_label.setStyleSheet("font-size: 12px; color: #f38ba8;")
        self.status_bar.showMessage("Status: Error encountered | Pipeline: Failed | Time: -")

    def open_etherscan(self):
        if self.last_etherscan_url:
            webbrowser.open(self.last_etherscan_url)


def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Face Verification Pipeline")
    
    # Run configuration diagnostics
    config.print_config_status()

    window = FaceVerificationApp()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
