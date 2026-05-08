class Product:
    def __init__(self, pid, name, price, stock):
        self.pid = pid
        self.name = name
        self.price = price
        self.stock = stock

    def __str__(self):
        return f"Product ID: {self.pid}, Name: {self.name}, Price: {self.price}, Stock: {self.stock}"
    
class Customer:
    def __init__(self, cid, name):
        self.cid = cid
        self.name = name

    def __str__(self):        
        return f"Customer ID: {self.cid}, Name: {self.name}"
    
class Order:
    def __init__(self, customer):
        self.customer = customer
        self.items = []

    def add_items(self, product, quantity):
        if product.stock >= quantity:
            self.items.append((product, quantity))
            product.stock -= quantity
        else:
            print("Not enough stock")

    def total_price(self):
        total = 0
        for product, qty in self.items:
            total += product.price * qty
        return total
    
    def __str__(self):
        details = f"Order for {self.customer.name}:\n"
        for product, qty in self.items:
            details += f"{product.name} x {qty}\n"
        details += f"Total Price: {self.total_price()}"
        return details
    
p1 = Product(1, "Laptop", 1000, 10)
p2 = Product(2, "Phone", 500, 20)   

c1 = Customer(1, "Prachi")

order = Order(c1)
order.add_items(p1, 2)
order.add_items(p2, 3)  

print(order)