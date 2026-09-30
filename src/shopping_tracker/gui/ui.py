from src.shopping_tracker.service import track_amazon_product, get_product_details, list_tracked_products
from src.shopping_tracker.models import Product, ProductSnapshot
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
)
from PySide6.QtCore import Qt

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


    def create_layouts(self):
        self.central = QWidget()
        self.setCentralWidget(self.central)

        self.main_layout = QVBoxLayout(self.central)

        self.input_layout = QHBoxLayout()
        self.input_layout.addWidget(self.url_input)
        self.input_layout.addWidget(self.add_button)

        self.left_layout = QVBoxLayout(self.left_panel)
        self.left_layout.addWidget(self.product_title)
        self.left_layout.addWidget(self.product_list)

        self.right_layout = QVBoxLayout(self.right_panel)
        self.right_layout.addWidget(self.details_title)
        self.right_layout.addWidget(self.details_placeholder)
        

        self.right_layout.addWidget(self.product_name_label)
        self.right_layout.addWidget(self.provider_label)
        self.right_layout.addWidget(self.rating_label)

        self.right_layout.addWidget(self.current_price_title)
        self.right_layout.addWidget(self.current_price_label)

        self.right_layout.addWidget(self.last_checked_label)
        self.right_layout.addStretch()

        self.content_layout = QHBoxLayout()
        self.content_layout.addWidget(self.left_panel, 1)
        self.content_layout.addWidget(self.right_panel, 2)

        self.main_layout.addLayout(self.input_layout)
        self.main_layout.addLayout(self.content_layout)


    def bind_events(self):
        self.add_button.clicked.connect(self.add_product)
        self.product_list.itemClicked.connect(self.show_product_details)


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
        #history = product_details.history
        latest_snapshot = product_details.latest_snapshot

        self.details_placeholder.hide()

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