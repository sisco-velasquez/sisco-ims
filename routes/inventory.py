from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, desc
from database import get_session
from models import Product, Sale, User
from routes.auth import get_current_user
from schemas import ProductCreate, ProductUpdate
from datetime import datetime

router = APIRouter(prefix="/inventory", tags=["Inventory Management"])
# In routes/inventory.py

@router.post("/add")
async def add_product(item: ProductCreate, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    # Check if THIS specific user already has a product with this name
    existing_item = session.exec(
        select(Product).where(Product.name == item.name, Product.user_id == current_user.id)
    ).first()
    
    if existing_item:
        raise HTTPException(status_code=400, detail="Product already exists in your inventory")
    
    new_product = Product(
        name=item.name,
        category=item.category,
        quantity=item.quantity,
        price=item.price,
        user_id=current_user.id  
    )
    if hasattr(item, "description"):
         new_product.description = item.description
    
    session.add(new_product)
    session.commit()
    session.refresh(new_product)
    return new_product

@router.get("/")
async def get_all_inventory(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    # Fetch ONLY the products belonging to the logged-in user
    items = session.exec(select(Product).where(Product.user_id == current_user.id)).all()
    return items

@router.patch("/update/{product_id}")
async def update_product(product_id: int, item: dict, session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    # Add a WHERE clause to ensure they don't update someone else's product
    statement = select(Product).where(Product.id == product_id, Product.user_id == current_user.id)
    db_product = session.exec(statement).first()
    
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found or unauthorized")

    new_quantity = item.get("quantity")
    if new_quantity is None:
        raise HTTPException(status_code=400, detail="Quantity not provided")

    # Calculate the difference to know if it was a Sale or a Restock
    quantity_diff = new_quantity - db_product.quantity
    
    # Update actual inventory
    db_product.quantity = new_quantity
    session.add(db_product)

    # Automatically record the transaction in the ledger
    if quantity_diff != 0:
        new_transaction = Sale(
            product_id=db_product.id,
            quantity_sold=quantity_diff, # Negative = Sale, Positive = Restock
            timestamp=datetime.utcnow(),
            user_id=current_user.id # Secure the transaction record
        )
        session.add(new_transaction)

    session.commit()
    session.refresh(db_product)
    return db_product

@router.get("/transactions")
async def get_recent_transactions(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    # Fetch ONLY the 10 most recent transactions belonging to the logged-in user
    statement = (
        select(Sale, Product)
        .join(Product, Sale.product_id == Product.id)
        .where(Sale.user_id == current_user.id) # Filter by user
        .order_by(desc(Sale.timestamp))
        .limit(10)
    )
    results = session.exec(statement).all()
    
    transactions = []
    for sale, product in results:
        # If the difference was negative, it means stock went down (a sale)
        is_sale = sale.quantity_sold < 0
        actual_qty = abs(sale.quantity_sold)
        
        transactions.append({
            "id": sale.id,
            "product_name": product.name,
            "type": "Sale" if is_sale else "Restock",
            "quantity": actual_qty,
            "amount": actual_qty * product.price,
            "timestamp": sale.timestamp.strftime("%Y-%m-%d %H:%M")
        })
        
    return transactions