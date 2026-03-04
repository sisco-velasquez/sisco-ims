from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, desc
from database import get_session
from models import Product, Sale
from schemas import ProductCreate, ProductUpdate
from datetime import datetime
router = APIRouter(prefix="/inventory", tags=["Inventory Management"])

@router.post("/add")
async def add_product(item: ProductCreate, session: Session = Depends(get_session)):
    existing_item = session.exec(select(Product).where(Product.name == item.name)).first()
    if existing_item:
        raise HTTPException(status_code=400, detail="Product already exists in inventory")
    
   
    new_product = Product.from_orm(item)
    session.add(new_product)
    session.commit()
    session.refresh(new_product)
    return new_product

@router.get("/")
async def get_all_inventory(session: Session = Depends(get_session)):
    
    items = session.exec(select(Product)).all()
    return items
@router.patch("/update/{product_id}")
async def update_product(product_id: int, item: dict, session: Session = Depends(get_session)):
    db_product = session.get(Product, product_id)
    if not db_product:
        raise HTTPException(status_code=404, detail="Product not found")

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
            timestamp=datetime.utcnow()
        )
        session.add(new_transaction)

    session.commit()
    session.refresh(db_product)
    return db_product

@router.get("/transactions")
async def get_recent_transactions(session: Session = Depends(get_session)):
    # Fetch the 10 most recent transactions, joining with Product to get the name
    statement = select(Sale, Product).join(Product, Sale.product_id == Product.id).order_by(desc(Sale.timestamp)).limit(10)
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