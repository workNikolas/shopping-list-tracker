from PySide6.QtWidgets import QApplication
from src.shopping_tracker.gui.ui import MainWindow
from src.shopping_tracker.repository import get_product, get_all_products

url = "https://amazon.com.br/dp/0486223051"

app = QApplication()
window = MainWindow()
window.show()
app.exec()