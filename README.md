# -API-Group-3_Restaurant-Order-Management
# Restaurant Order Management API

## Group Members
| Name                   | Student ID |
|------------------------|------------|
| Kowthar Ahmed          | 166069     |
| Dee Emmanuel Achiek    | 138547     |
| Mathews Zimba          | 169282     |
| Stephen Wanjogu Ngatara| 168653     |
| Brian Mutuma           | 153113     |
| Allan Tom              | 133106     |
| Abraham Ajuong Kuol    | 169085     |

---

## Project Description
This project is a **Django REST Framework (DRF) API** for managing restaurant operations, including customers, menu items, orders, tables, and order items.  
The system supports:
- Adding and managing menu items.
- Placing and tracking customer orders.
- Assigning tables.
- Recording order details.

The API follows RESTful principles and supports **CRUD operations** for all major resources.  
Permissions ensure that only staff can manage menu items and orders, while customers can view the menu.

---

## Models and Relationships
We implemented **5 models**:

1. **Customer**
   - `name` (CharField)
   - `phone` (CharField)
   - `email` (EmailField)
   
2. **MenuItem**
   - `name` (CharField)
   - `description` (TextField)
   - `price` (DecimalField)
   - `is_available` (BooleanField)
   
3. **Table**
   - `table_number` (IntegerField)
   - `capacity` (IntegerField)
   - `is_reserved` (BooleanField)

4. **Order**
   - `customer` (ForeignKey → Customer)
   - `table` (ForeignKey → Table)
   - `status` (ChoiceField: Pending, In Progress, Completed)
   - `created_at` (DateTimeField)

5. **OrderItem**
   - `order` (ForeignKey → Order)
   - `menu_item` (ForeignKey → MenuItem)
   - `quantity` (IntegerField)
   - `price` (DecimalField – price at the time of order)

**Relationships:**
- One **Customer** can have many **Orders**.
- One **Order** can have many **OrderItems**.
- One **OrderItem** belongs to one **MenuItem**.
- One **Order** belongs to one **Table**.

---

## Serializers
Each model has a corresponding serializer to handle JSON ↔ Python data conversion:

- **CustomerSerializer** – Validates unique email.
- **MenuItemSerializer** – Ensures price is positive.
- **TableSerializer** – Prevents duplicate table numbers.
- **OrderSerializer** – Nested serializer for order items.
- **OrderItemSerializer** – Validates positive quantity.

---

## Views/Viewsets
We used **ModelViewSet** for all models:
- `CustomerViewSet`
- `MenuItemViewSet`
- `TableViewSet`
- `OrderViewSet` (supports nested creation of order items)
- `OrderItemViewSet`

**Permissions:**
- Only authenticated staff can create/update/delete menu items or orders.
- Customers can only read menu items and their orders.

---

## URL Patterns
We used DRF’s `DefaultRouter` for clean and RESTful routes:

