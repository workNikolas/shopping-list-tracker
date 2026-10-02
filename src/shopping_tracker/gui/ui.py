from datetime import timedelta
from pathlib import Path

import matplotlib.dates as mdates
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from src.shopping_tracker.fetch_image import fetch_image
from src.shopping_tracker.models import Product, ProductSnapshot
from src.shopping_tracker.service import (
    get_product_details,
    list_tracked_products,
    refresh_product,
    remove_product,
    track_amazon_product,
)


BG = "#EDEAD0"
BORDER = "#071013"
GREEN = "#537A5A"
RED = "#6B0504"
MAUVE = "#86615C"
WHITE = "#FFFFFF"


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setup_window()
        self.setup_widgets()
        self.create_layouts()
        self.bind_events()
        self.apply_styles()
        self.load_db()

    # ------------------------------------------------------------------
    # Window and widgets
    # ------------------------------------------------------------------

    def setup_window(self):
        self.setWindowTitle("Shopping Tracker")
        self.resize(1100, 760)

    def setup_widgets(self):
        self.app_subtitle = QLabel("Track Amazon product prices over time")
        self.app_subtitle.setObjectName("appSubtitle")

        self.url_input = QLineEdit()
        self.url_input.setObjectName("urlInput")
        self.url_input.setPlaceholderText("Paste Amazon Product URL")

        self.add_button = QPushButton("Add")
        self.add_button.setObjectName("primaryButton")

        self.left_panel = QWidget()
        self.left_panel.setObjectName("panel")

        self.product_title = QLabel("TRACKED PRODUCTS")
        self.product_title.setObjectName("panelTitle")

        self.product_list = QListWidget()
        self.product_list.setObjectName("productList")

        self.right_panel = QWidget()
        self.right_panel.setObjectName("panel")

        self.details_header = QWidget()
        self.details_header.setObjectName("panelHeader")

        self.details_title = QLabel("PRODUCT DETAILS")
        self.details_title.setObjectName("panelTitle")

        self.refresh_button = QPushButton("Refresh")
        self.refresh_button.setObjectName("secondaryButton")

        self.remove_button = QPushButton("Remove")
        self.remove_button.setObjectName("dangerButton")

        self.product_details_content = QWidget()
        self.product_details_content.setObjectName("detailsContent")
        self.product_details_content.setMinimumHeight(280)

        self.details_placeholder = QLabel("Select a product to view its details")
        self.details_placeholder.setObjectName("detailsPlaceholder")
        self.details_placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.product_image_label = QLabel()
        self.product_image_label.setObjectName("productImage")
        self.product_image_label.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignHCenter
        )

        self.product_name_label = QLabel()
        self.product_name_label.setObjectName("productName")
        self.product_name_label.setWordWrap(True)

        self.provider_label = QLabel()
        self.provider_label.setObjectName("secondaryText")

        self.rating_label = QLabel()
        self.rating_label.setObjectName("rating")

        self.current_price_title = QLabel("Current price")
        self.current_price_title.setObjectName("secondaryText")

        self.current_price_label = QLabel()
        self.current_price_label.setObjectName("currentPrice")

        self.price_history_title = QLabel("PRICE HISTORY")
        self.price_history_title.setObjectName("sectionTitle")

        self.price_figure = Figure()
        self.price_figure.set_facecolor(WHITE)
        self.price_axes = self.price_figure.add_subplot(111)
        self.price_canvas = FigureCanvas(self.price_figure)
        self.price_canvas.setObjectName("priceCanvas")
        self._style_price_axes()

        self.last_checked_label = QLabel()
        self.last_checked_label.setObjectName("lastChecked")

    # ------------------------------------------------------------------
    # Layout
    # ------------------------------------------------------------------

    def create_layouts(self):
        self.central = QWidget()
        self.central.setObjectName("centralWidget")
        self.setCentralWidget(self.central)

        self.main_layout = QVBoxLayout(self.central)
        self.main_layout.setContentsMargins(16, 14, 16, 14)
        self.main_layout.setSpacing(10)
        self.main_layout.addWidget(self.app_subtitle)

        self.input_layout = QHBoxLayout()
        self.input_layout.setSpacing(8)
        self.input_layout.addWidget(self.url_input, 1)
        self.input_layout.addWidget(self.add_button)
        self.main_layout.addLayout(self.input_layout)

        self.content_layout = QHBoxLayout()
        self.content_layout.setSpacing(14)
        self.content_layout.addWidget(self.left_panel, 1)
        self.content_layout.addWidget(self.right_panel, 2)
        self.main_layout.addLayout(self.content_layout, 1)

        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.setContentsMargins(0, 0, 0, 0)
        self.left_layout.setSpacing(0)
        self.left_layout.addWidget(self.product_title)
        self.left_layout.addWidget(self.product_list, 1)

        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.setContentsMargins(0, 0, 0, 0)
        self.right_layout.setSpacing(0)

        self.details_header_layout = QHBoxLayout(self.details_header)
        self.details_header_layout.setContentsMargins(10, 4, 4, 4)
        self.details_header_layout.setSpacing(8)
        self.details_header_layout.addWidget(self.details_title)
        self.details_header_layout.addStretch()
        self.details_header_layout.addWidget(self.refresh_button)
        self.details_header_layout.addWidget(self.remove_button)
        self.right_layout.addWidget(self.details_header)

        self.product_details_content_layout = QVBoxLayout(
            self.product_details_content
        )
        self.product_details_content_layout.setContentsMargins(12, 12, 12, 12)
        self.product_details_content_layout.setSpacing(8)

        self.product_header_layout = QHBoxLayout()
        self.product_header_layout.setSpacing(16)
        self.product_header_layout.addWidget(
            self.product_image_label,
            0,
            Qt.AlignmentFlag.AlignTop,
        )

        self.product_info_layout = QVBoxLayout()
        self.product_info_layout.setSpacing(5)
        self.product_info_layout.addWidget(self.product_name_label)
        self.product_info_layout.addWidget(self.provider_label)
        self.product_info_layout.addWidget(self.rating_label)
        self.product_info_layout.addSpacing(6)
        self.product_info_layout.addWidget(self.current_price_title)
        self.product_info_layout.addWidget(self.current_price_label)
        self.product_info_layout.addStretch()
        self.product_header_layout.addLayout(self.product_info_layout, 1)

        self.product_details_content_layout.addWidget(self.details_placeholder, 1)
        self.product_details_content_layout.addLayout(self.product_header_layout)
        self.right_layout.addWidget(self.product_details_content)

        self.right_layout.addWidget(self.price_history_title)
        self.right_layout.addWidget(self.price_canvas, 1)
        self.right_layout.addWidget(self.last_checked_label)

    # ------------------------------------------------------------------
    # Events and service calls
    # ------------------------------------------------------------------

    def bind_events(self):
        self.add_button.clicked.connect(self.add_product)
        self.product_list.itemClicked.connect(self.show_product_details)
        self.remove_button.clicked.connect(self.remove_selected_product)
        self.refresh_button.clicked.connect(self.refresh_selected_product)

    def add_product(self):
        url = self.url_input.text().strip()
        if not url:
            return

        result = track_amazon_product(url)
        self.upsert_product_to_list(
            product_id=result.product_id,
            product=result.product,
            snapshot=result.snapshot,
        )

    def show_product_details(self, item):
        product_id = item.data(Qt.ItemDataRole.UserRole)
        product_details = get_product_details(product_id)
        if product_details is None:
            return

        product = product_details.product
        latest_snapshot = product_details.latest_snapshot

        self.update_chart_price(product_details.history)
        self.details_placeholder.hide()

        if product.image_url is not None:
            image_bytes = fetch_image(product.image_url)
            pixmap = QPixmap()
            pixmap.loadFromData(image_bytes)
            scaled_pixmap = pixmap.scaled(
                180,
                260,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation,
            )
            self.product_image_label.clear()
            self.product_image_label.setPixmap(scaled_pixmap)
        else:
            self.product_image_label.clear()
            self.product_image_label.setText("Unable to load image")

        self.product_name_label.setText(product.name)
        self.provider_label.setText(product.provider.title())

        if latest_snapshot.avg_rating is None:
            self.rating_label.setText("Average rating is unavailable")
        else:
            self.rating_label.setText(f"★ {latest_snapshot.avg_rating}")

        if latest_snapshot.price is None:
            self.current_price_label.setText("Unavailable")
        else:
            self.current_price_label.setText(f"R$ {latest_snapshot.price}")

        self.last_checked_label.setText(
            f"Last checked: {latest_snapshot.observed_at:%d, %b, %H:%M}"
        )

    def refresh_selected_product(self):
        item = self.product_list.currentItem()
        if item is None:
            return

        product_id = item.data(Qt.ItemDataRole.UserRole)
        result = refresh_product(product_id)

        self.upsert_product_to_list(
            product_id,
            result.product,
            result.snapshot,
        )
        self.show_product_details(item)

    def remove_selected_product(self):
        item = self.product_list.currentItem()
        if item is None:
            return

        product_id = item.data(Qt.ItemDataRole.UserRole)
        details = get_product_details(product_id)
        if details is None:
            return

        answer = QMessageBox.question(
            self,
            "Remove product",
            f"Remove '{details.product.name}' and its price history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return

        remove_product(product_id)
        row = self.product_list.row(item)
        self.product_list.takeItem(row)
        self.clear_product_details()

    # ------------------------------------------------------------------
    # UI state
    # ------------------------------------------------------------------

    def load_db(self):
        products = list_tracked_products()

        for product_id, product in products:
            details = get_product_details(product_id)
            if details is None:
                continue

            self.upsert_product_to_list(
                product_id=product_id,
                product=product,
                snapshot=details.latest_snapshot,
            )

    def upsert_product_to_list(
        self,
        product_id: int,
        product: Product,
        snapshot: ProductSnapshot,
    ):
        price = "Unavailable" if snapshot.price is None else f"R${snapshot.price}"
        text = f"{product.name} - {price}"

        for row in range(self.product_list.count()):
            item = self.product_list.item(row)
            stored_product_id = item.data(Qt.ItemDataRole.UserRole)
            if product_id == stored_product_id:
                item.setText(text)
                return

        item = QListWidgetItem(text)
        item.setData(Qt.ItemDataRole.UserRole, product_id)
        self.product_list.addItem(item)

    def update_chart_price(self, history: list[ProductSnapshot]):
        self.price_axes.clear()
        self._style_price_axes()

        dates = []
        prices = []

        for snapshot in history:
            if snapshot.price is None:
                continue

            dates.append(snapshot.observed_at)
            prices.append(float(snapshot.price))

        if not dates:
            self.price_axes.set_title("No price history available")
            self.price_figure.tight_layout()
            self.price_canvas.draw()
            return

        self.price_axes.plot(
            dates,
            prices,
            marker="o",
            color=GREEN,
        )
        self.price_axes.set_title("Price History")
        self.price_axes.set_ylabel("Price (R$)")

        locator = mdates.AutoDateLocator()
        formatter = mdates.ConciseDateFormatter(locator)
        self.price_axes.xaxis.set_major_locator(locator)
        self.price_axes.xaxis.set_major_formatter(formatter)

        if len(dates) == 1:
            self.price_axes.set_xlim(
                dates[0] - timedelta(hours=12),
                dates[0] + timedelta(hours=12),
            )

        self.price_figure.tight_layout()
        self.price_canvas.draw()

    def clear_product_details(self):
        self.product_image_label.clear()
        self.product_name_label.clear()
        self.provider_label.clear()
        self.rating_label.clear()
        self.current_price_label.clear()
        self.last_checked_label.clear()
        self.details_placeholder.show()

        self.price_axes.clear()
        self._style_price_axes()
        self.price_canvas.draw()

    def _style_price_axes(self):
        self.price_axes.set_facecolor(WHITE)
        self.price_axes.tick_params(colors=BORDER)
        self.price_axes.xaxis.label.set_color(BORDER)
        self.price_axes.yaxis.label.set_color(BORDER)
        self.price_axes.title.set_color(BORDER)

        for spine in self.price_axes.spines.values():
            spine.set_color(BORDER)

    def apply_styles(self):
        stylesheet_path = Path(__file__).with_name("styles.qss")
        self.setStyleSheet(stylesheet_path.read_text(encoding="utf-8"))
