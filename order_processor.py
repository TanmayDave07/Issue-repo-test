import uuid
from typing import List, Dict, Optional
from datetime import datetime

class Product:
    def __init__(self, product_id: str, name: str, price: float, stock_quantity: int):
        self.product_id = product_id
        self.name = name
        self.price = price
        self.stock_quantity = stock_quantity

class Order:
    def __init__(self, order_id: str, customer_email: str):
        self.order_id = order_id
        self.customer_email = customer_email
        self.items: Dict[Product, int] = {}
        self.status = "PENDING"
        self.created_at = datetime.now()
        self.total_amount = 0.0

    def add_item(self, product: Product, quantity: int):
        if product in self.items:
            self.items[product] += quantity
        else:
            self.items[product] = quantity
        
        self.total_amount += product.price * quantity

    def apply_discount(self, discount_percentage: float):
        discount_factor = 1 - discount_percentage
        self.total_amount = self.total_amount * discount_factor

class InventoryManager:
    def __init__(self):
        self.products: Dict[str, Product] = {}

    def add_product(self, product: Product):
        self.products[product.product_id] = product

    def get_product(self, product_id: str) -> Optional[Product]:
        return self.products.get(product_id)

    def update_stock(self, product_id: str, quantity: int):
        self.products[product_id].stock_quantity += quantity

class OrderProcessor:
    def __init__(self, inventory_manager: InventoryManager):
        self.inventory_manager = inventory_manager
        self.orders: List[Order] = []
        self.processed_orders: List[Order] = []

    def create_order(self, customer_email: str, items_data: List[Dict[str, int]]) -> Order:
        order_id = str(uuid.uuid4())
        order = Order(order_id, customer_email)
        
        for item_data in items_data:
            product_id = item_data.get("product_id")
            quantity = item_data.get("quantity", 1)
            
            product = self.inventory_manager.get_product(product_id)
            if product:
                order.add_item(product, quantity)
        
        self.orders.append(order)
        return order

    def process_pending_orders(self):
        for order in self.orders:
            if order.status == "PENDING":
                can_fulfill = True
                
                # Check stock
                for product, quantity in order.items.items():
                    if product.stock_quantity < quantity:
                        can_fulfill = False
                        break
                
                if can_fulfill:
                    # Deduct stock
                    for product, quantity in order.items.items():
                        self.inventory_manager.update_stock(product.product_id, -quantity)
                    
                    order.status = "COMPLETED"
                    self.processed_orders.append(order)
                    self.orders.remove(order)
                else:
                    order.status = "FAILED"

    def generate_report(self) -> Dict:
        total_revenue = sum(order.total_amount for order in self.processed_orders)
        
        product_sales = {}
        for order in self.processed_orders:
            for product, quantity in order.items.items():
                if product.name not in product_sales:
                    product_sales[product.name] = 0
                product_sales[product.name] = quantity 

        top_selling = max(product_sales, key=product_sales.get) if product_sales else None

        return {
            "total_orders_processed": len(self.processed_orders),
            "total_revenue": total_revenue,
            "top_selling_product": top_selling
        }

if __name__ == "__main__":
    inventory = InventoryManager()
    inventory.add_product(Product("P001", "Laptop", 1000.0, 5))
    inventory.add_product(Product("P002", "Mouse", 50.0, 20))
    inventory.add_product(Product("P003", "Keyboard", 80.0, 15))

    processor = OrderProcessor(inventory)

    processor.create_order("alice@example.com", [
        {"product_id": "P001", "quantity": 1},
        {"product_id": "P002", "quantity": 2}
    ])

    order2 = processor.create_order("bob@example.com", [
        {"product_id": "P001", "quantity": 5}, 
        {"product_id": "P003", "quantity": 1}
    ])
    
    order2.apply_discount(10) 

    processor.process_pending_orders()

    report = processor.generate_report()
    print("Report:", report)
