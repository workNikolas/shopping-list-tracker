from src.shopping_tracker.service import (
    track_amazon_product, 
    get_product_details, 
    list_tracked_products, 
    refresh_product,
    remove_product,
)
from src.shopping_tracker.models import Product, ProductSnapshot
from src.shopping_tracker.fetch_image import fetch_image
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMessageBox
)
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from matplotlib.figure import Figure
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from datetime import timedelta
import matplotlib.dates as mdates

BG = "#EDEAD0"

class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()

        self.setup_window()
        #self.setup_style()
        self.setup_widgets()
        self.create_layouts()
        self.bind_events()
        self.load_db()


    def setup_window(self): 
        self.setWindowTitle("Shopping Tracker")
        self.resize(1000, 650)


    def setup_style(self):
        pass


    def setup_widgets(self):
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("Paste Amazon Product URL")

        self.add_button = QPushButton("Add")

        self.left_panel = QWidget()
        self.product_title = QLabel("TRACKED PRODUCTS")
        self.product_list = QListWidget()

        # Details 
        self.right_panel = QWidget()
        self.details_title = QLabel("PRODUCT DETAILS")
        self.details_placeholder = QLabel("Select a product to view its details.")

        self.product_name_label = QLabel()
        self.provider_label = QLabel()
        self.rating_label = QLabel()

        self.current_price_title = QLabel("Current price")
        self.current_price_label = QLabel()

        self.last_checked_label = QLabel()

        self.product_image_label = QLabel()

        self.refresh_button = QPushButton("Refresh")
        self.remove_button = QPushButton("Remove")

        self.price_figure = Figure() # É tipo o QWidget, que define onde vai os elementos
        self.price_axes = self.price_figure.add_subplot(111) # Região do gráfico 111 stand for 1 line 1 col and graph n1
        self.price_canvas = FigureCanvas(self.price_figure)


    def create_layouts(self):
        # Central widget
        self.central = QWidget()
        self.setCentralWidget(self.central)

        self.main_layout = QVBoxLayout(self.central)

        # -------------------------
        # Input area
        # -------------------------
        self.input_layout = QHBoxLayout()
        self.input_layout.addWidget(self.url_input)
        self.input_layout.addWidget(self.add_button)

        # -------------------------
        # Left panel
        # -------------------------
        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.addWidget(self.product_title)
        self.left_layout.addWidget(self.product_list)

        # -------------------------
        # Right panel
        # -------------------------
        self.right_layout = QVBoxLayout(self.right_panel)

        self.right_layout.addWidget(self.details_title)
        self.right_layout.addWidget(self.details_placeholder)
        self.right_layout.addWidget(self.refresh_button)
        self.right_layout.addWidget(self.remove_button)

        # Product header:
        #
        # [ IMAGE ] [ name     ]
        #           [ provider ]
        #           [ rating   ]
        #           [ price    ]
        #
        self.product_header_layout = QHBoxLayout()
        self.product_info_layout = QVBoxLayout()

        self.product_header_layout.addWidget(
            self.product_image_label,
            0,
            Qt.AlignmentFlag.AlignTop,
        )

        self.product_info_layout.addWidget(self.product_name_label)
        self.product_info_layout.addWidget(self.provider_label)
        self.product_info_layout.addWidget(self.rating_label)
        self.product_info_layout.addWidget(self.current_price_title)
        self.product_info_layout.addWidget(self.current_price_label)
        self.product_info_layout.addStretch()

        self.product_header_layout.addLayout(
            self.product_info_layout,
            1,
        )

        # This was missing in your version
        self.right_layout.addLayout(self.product_header_layout)

        # Price history
        self.right_layout.addWidget(self.price_canvas)

        # Footer
        self.right_layout.addWidget(self.last_checked_label)

        # -------------------------
        # Main content
        # -------------------------
        self.content_layout = QHBoxLayout()

        self.content_layout.addWidget(self.left_panel, 1)
        self.content_layout.addWidget(self.right_panel, 2)

        # -------------------------
        # Assemble main window
        # -------------------------
        self.main_layout.addLayout(self.input_layout)
        self.main_layout.addLayout(self.content_layout)


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
        # Returns product_id, product and snapshot
        self.upsert_product_to_list(
            product_id=result.product_id, product=result.product, snapshot=result.snapshot
            )


    def show_product_details(self, item):
        product_id = item.data(Qt.ItemDataRole.UserRole)
        product_details = get_product_details(product_id)
        if product_details is None:
            return
        product = product_details.product
        history = product_details.history

        self.update_chart_price(history)

        latest_snapshot = product_details.latest_snapshot

        self.details_placeholder.hide()

        image_url = product_details.product.image_url
        if image_url is not None:
            image_bytes = fetch_image(image_url)
            pixmap = QPixmap()
            pixmap.loadFromData(image_bytes)
            scaled_pixmap = pixmap.scaled(180, 260, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
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
            return None

        product_id = item.data(Qt.ItemDataRole.UserRole)
        result = refresh_product(product_id)

        self.upsert_product_to_list(product_id, result.product, result.snapshot)
        self.show_product_details(item)


    def remove_selected_product(self):
        item = self.product_list.currentItem()
        product_id = item.data(Qt.ItemDataRole.UserRole)

        details = get_product_details(product_id)
        if details is None:
            return
    
        if item is None:
            return None

        answer = QMessageBox.question(
            self,
            "Remove product",
            f"Remove '{details.product.name}' and its price history?",
            QMessageBox.StandardButton.Yes
            | QMessageBox.StandardButton.No,
        )

        if answer != QMessageBox.StandardButton.Yes:
            return
        remove_product(product_id)

        row = self.product_list.row(item)
        self.product_list.takeItem(row)

        self.clear_product_details()

    def load_db(self):
        products = list_tracked_products()

        for product_id, product in products:
            details = get_product_details(product_id)
            if details is None:
                continue

            self.upsert_product_to_list(
                product_id=product_id, product=product, snapshot=details.latest_snapshot 
                )


    def upsert_product_to_list(self, product_id: int, product: Product, snapshot: ProductSnapshot):

        text = f"{product.name} - R${snapshot.price}"

        for row in range(self.product_list.count()):
            item = self.product_list.item(row)

            stored_product_id = item.data(Qt.ItemDataRole.UserRole)
            if product_id == stored_product_id:
                return
        
        item = QListWidgetItem(
            f"{product.name} - R${snapshot.price}"
        )
        item.setData(Qt.ItemDataRole.UserRole, product_id)
        self.product_list.addItem(item)


    def update_chart_price(self, history: list[ProductSnapshot]):
        self.price_axes.clear()

        dates = []
        prices = []

        for snapshot in history:
            if snapshot.price is None:
                continue

            dates.append(snapshot.observed_at)
            prices.append(float(snapshot.price))

        if not dates:
            self.price_axes.set_title("No price history available")
            self.price_canvas.draw()
            return

        self.price_axes.plot(
            dates,
            prices,
            marker="o",
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

        self.price_axes.clear()
        self.price_canvas.draw()