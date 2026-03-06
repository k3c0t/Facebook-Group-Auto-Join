import sys
import threading
import time

from PySide6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QCheckBox,
    QGroupBox,
    QFormLayout,
    QSpacerItem,
    QSizePolicy,
    QMessageBox,
)
from PySide6.QtCore import Qt

# Asumsi file join.py tetap sama
from join import auto_join_groups, load_cookies

# Anda bisa install library ini untuk tema lebih bagus & konsisten:
# pip install pyqtdarktheme
try:
    import qdarktheme
    DARK_THEME_AVAILABLE = True
except ImportError:
    DARK_THEME_AVAILABLE = False


class JoinGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FB Group Auto Joiner Versi Beta       IG: ncots_id       Telegram: @jlimboo")
        self.setMinimumSize(700, 480)
        self.resize(480, 520)

        self.init_ui()
        self.apply_dark_theme()

    def init_ui(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(24, 20, 24, 24)
        main_layout.setSpacing(16)

        # ── Title ───────────────────────────────────────────────
        title = QLabel("Facebook Group Auto Join")
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("font-size: 20px; font-weight: bold; margin-bottom: 8px;")
        main_layout.addWidget(title)

        # ── Form Group ──────────────────────────────────────────
        form_group = QGroupBox("Pengaturan")
        form_layout = QFormLayout()
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        form_layout.setFormAlignment(Qt.AlignLeft)
        form_layout.setSpacing(12)

        self.keyword = QLineEdit("motor")
        self.keyword.setPlaceholderText("Contoh: kuliner, otomotif, bisnis")
        self.keyword.setMinimumWidth(240)

        self.max_join = QLineEdit("5")
        self.max_join.setPlaceholderText("Maksimal grup yang di-join")
        self.max_join.setFixedWidth(120)

        self.delay = QLineEdit("15")
        self.delay.setPlaceholderText("Detik antar join")
        self.delay.setFixedWidth(120)

        self.headless = QCheckBox("Jalankan dalam mode Headless (tanpa tampilan browser)")
        self.headless.setChecked(True)

        form_layout.addRow("Kata Kunci:", self.keyword)
        form_layout.addRow("Maksimal Join:", self.max_join)
        form_layout.addRow("Delay (detik):", self.delay)
        form_layout.addRow("", self.headless)

        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)

        # ── Status Area ─────────────────────────────────────────
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout()
        status_layout.setSpacing(10)

        self.status = QLabel("🟢 Siap")
        self.status.setAlignment(Qt.AlignCenter)
        self.status.setStyleSheet("font-size: 15px; font-weight: bold; padding: 8px;")

        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(30)

        self.total_lbl   = QLabel("Total Join : 0")
        self.pending_lbl = QLabel("Pending : 0")
        self.success_lbl = QLabel("Sukses : 0")

        for lbl in (self.total_lbl, self.pending_lbl, self.success_lbl):
            lbl.setStyleSheet("font-size: 13px;")

        stats_layout.addWidget(self.total_lbl)
        stats_layout.addWidget(self.pending_lbl)
        stats_layout.addWidget(self.success_lbl)

        status_layout.addWidget(self.status)
        status_layout.addLayout(stats_layout)
        status_group.setLayout(status_layout)

        main_layout.addWidget(status_group)

        # ── Buttons ─────────────────────────────────────────────
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self.start_btn = QPushButton("MULAI")
        self.start_btn.setFixedHeight(48)
        self.start_btn.setMinimumWidth(160)
        self.start_btn.setStyleSheet("""
            QPushButton {
                background-color: #2a9d8f;
                color: white;
                font-weight: bold;
                border-radius: 8px;
                padding: 8px 24px;
            }
            QPushButton:hover {
                background-color: #287b6d;
            }
            QPushButton:pressed {
                background-color: #1f5f54;
            }
            QPushButton:disabled {
                background-color: #555;
                color: #888;
            }
        """)
        self.start_btn.clicked.connect(self.start_bot)

        btn_layout.addWidget(self.start_btn)
        main_layout.addLayout(btn_layout)

        main_layout.addStretch(1)
        self.setLayout(main_layout)

    def apply_dark_theme(self):
        if DARK_THEME_AVAILABLE:
            # Cara paling mudah & konsisten (rekomendasi)
            qdarktheme.setup_theme(
                theme="dark",
                corner_shape="rounded",
                custom_colors={"primary": "#2a9d8f"}  # warna aksen tombol
            )
        else:
            # Fallback stylesheet sederhana jika pyqtdarktheme tidak terinstall
            self.setStyleSheet("""
                QWidget {
                    background-color: #1e1e1e;
                    color: #e0e0e0;
                    font-family: Segoe UI, sans-serif;
                }
                QLineEdit, QComboBox {
                    background-color: #2d2d2d;
                    border: 1px solid #444;
                    border-radius: 6px;
                    padding: 6px;
                    color: #f0f0f0;
                }
                QLineEdit:focus {
                    border: 1px solid #2a9d8f;
                }
                QLabel {
                    color: #d0d0d0;
                }
                QGroupBox {
                    border: 1px solid #444;
                    border-radius: 8px;
                    margin-top: 12px;
                    padding-top: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top left;
                    padding: 0 8px;
                    color: #2a9d8f;
                }
                QCheckBox {
                    spacing: 8px;
                }
                QCheckBox::indicator {
                    width: 18px;
                    height: 18px;
                }
            """)

    def start_bot(self):
        try:
            max_join_val = int(self.max_join.text())
            delay_val = int(self.delay.text())
            if max_join_val < 1 or delay_val < 1:
                raise ValueError("Nilai tidak valid")
        except Exception as e:
            QMessageBox.warning(self, "Input Tidak Valid", str(e))
            return

        self.status.setText("🟡 BERJALAN...")
        self.status.setStyleSheet("color: #f4a261; font-weight: bold;")
        self.start_btn.setEnabled(False)
        self.start_btn.setText("BERJALAN...")

        thread = threading.Thread(target=self.run_selenium, daemon=True)
        thread.start()

    def update_status(self, joined: int, max_join: int):
        success = joined
        pending = max_join - joined

        self.success_lbl.setText(f"Sukses : {success}")
        self.pending_lbl.setText(f"Pending : {pending}")
        self.total_lbl.setText(f"Total Join : {success}")

        # Optional: update warna status
        if success > 0:
            self.status.setStyleSheet("color: #90be6d; font-weight: bold;")

    def run_selenium(self):
        from selenium import webdriver
        from selenium.webdriver.chrome.options import Options
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager

        options = Options()

        if self.headless.isChecked():
            options.add_argument("--headless=new")
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

        options.add_argument("--disable-notifications")
        options.add_argument("--window-size=1280,900")

        driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=options
        )

        try:
            driver.get("https://www.facebook.com/")
            time.sleep(3)

            if not load_cookies(driver):
                self.status.setText("🔴 COOKIES TIDAK VALID / EXPIRED")
                self.status.setStyleSheet("color: #e76f51; font-weight: bold;")
            else:
                driver.get("https://www.facebook.com/")
                time.sleep(4)

                keyword = self.keyword.text().strip()
                max_join = int(self.max_join.text())
                delay = int(self.delay.text())

                auto_join_groups(
                    driver,
                    keyword,
                    max_join,
                    delay,
                    self.update_status
                )

                self.status.setText("✅ SELESAI")
                self.status.setStyleSheet("color: #90be6d; font-weight: bold;")

        except Exception as e:
            self.status.setText(f"🔴 ERROR: {str(e)[:60]}...")
            self.status.setStyleSheet("color: #e76f51; font-weight: bold;")

        finally:
            driver.quit()
            self.start_btn.setEnabled(True)
            self.start_btn.setText("MULAI")


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Cara paling direkomendasikan: gunakan pyqtdarktheme
    if DARK_THEME_AVAILABLE:
        qdarktheme.setup_theme("dark")

    window = JoinGUI()
    window.show()
    sys.exit(app.exec())
