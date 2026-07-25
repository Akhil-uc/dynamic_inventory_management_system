from product import Product
from inventory import InventoryManager


def menu():
    print("\n" + "=" * 50)
    print("DYNAMIC INVENTORY MANAGEMENT SYSTEM")
    print("=" * 50)
    print("1. Add Product")
    print("2. Search Product")
    print("3. Update Product")
    print("4. Delete Product")
    print("5. Display Inventory")
    print("6. Place Customer Order")
    print("7. Process Next Order")
    print("8. Display Low Stock Products")
    print("9. Exit")
    print("=" * 50)

def main():
    inventory = InventoryManager()
    while True:
        menu()
        choice = input("Enter your choice: ")
        if choice == "1":
            try:
                pid = int(input("Product ID: "))
                name = input("Product Name: ")
                category = input("Category: ")
                quantity = int(input("Quantity: "))
                price = float(input("Price: "))
                product = Product(
                    pid,
                    name,
                    category,
                    quantity,
                    price
                )
                inventory.add_product(product)
            except ValueError:
                print("Invalid input.")
        elif choice == "2":
            pid = int(input("Enter Product ID: "))
            inventory.search_product(pid)
        elif choice == "3":
            pid = int(input("Product ID: "))
            quantity = int(input("New Quantity: "))
            price = float(input("New Price: "))
            inventory.update_product(
                pid,
                quantity,
                price
            )
        elif choice == "4":
            pid = int(input("Product ID: "))
            inventory.delete_product(pid)
        elif choice == "5":
            inventory.display_inventory()
        elif choice == "6":
            pid = int(input("Product ID: "))
            qty = int(input("Quantity: "))
            inventory.place_order(
                pid,
                qty
            )
        elif choice == "7":
            inventory.process_order()
        elif choice == "8":
            threshold = int(
                input("Low Stock Threshold: ")
            )
            inventory.display_low_stock(threshold)
        elif choice == "9":
            print("\nThank you for using the system.")
            break
        else:
            print("Invalid option.")

if __name__ == "__main__":
    main()