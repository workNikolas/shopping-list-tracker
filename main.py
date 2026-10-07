from PySide6.QtWidgets import QApplication
from src.shopping_tracker.database import migrate_add_image_url
from src.shopping_tracker.repository import get_all_products
from src.shopping_tracker.gui.ui import MainWindow
from src.shopping_tracker.amazon import AmazonFetcher, AmazonParser
from src.shopping_tracker.service import track_amazon_product, refresh_product, get_product_history
from src.shopping_tracker.fetch_image import fetch_image

url1 = "https://amazon.com.br/dp/0486223051"
url2 = "https://www.amazon.com.br/Paradise-Lost-John-Milton/dp/0140424393"
url3 = "https://www.amazon.com.br/gp/product/8580700809/ref=ewc_pr_img_3?smid=A1ZZFT5FULY4LN&psc=1"

app = QApplication()
window = MainWindow()
window.show()
app.exec()