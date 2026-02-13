"""
Sales/POS Page
This module contains the point of sale system
"""
import streamlit as st
import pandas as pd
from database import SessionLocal
from models import Product, Sale, SaleItem
from datetime import datetime

# Initialize cart in session state
if "cart" not in st.session_state:
    st.session_state.cart = []
if "last_sale" not in st.session_state:
    st.session_state.last_sale = None

def render():
    """Main render function for sales page"""
    
    # Helper functions
    def format_currency(amount):
        return f"₵{amount:,.2f}"
    
    def add_to_cart(product, quantity):
        for item in st.session_state.cart:
            if item["product_id"] == product.id:
                item["quantity"] += quantity
                return True
        st.session_state.cart.append({
            "product_id": product.id,
            "name": product.name,
            "type": product.type,
            "size": product.size,
            "price": product.sell_price,
            "quantity": quantity,
            "available_stock": product.quantity
        })
        return True
    
    def get_cart_total():
        return sum(item["price"] * item["quantity"] for item in st.session_state.cart)
    
    def get_cart_items_count():
        return sum(item["quantity"] for item in st.session_state.cart)
    
    def clear_cart():
        st.session_state.cart = []
    
    def process_sale(db, payment_method, user_id):
        try:
            total = get_cart_total()
            sale = Sale(
                user_id=user_id,
                total=total,
                payment_method=payment_method,
                created_at=datetime.utcnow()
            )
            db.add(sale)
            db.flush()
            
            for item in st.session_state.cart:
                product = db.query(Product).filter(Product.id == item["product_id"]).first()
                product.quantity -= item["quantity"]
                
                sale_item = SaleItem(
                    sale_id=sale.id,
                    product_id=product.id,
                    quantity=item["quantity"],
                    price=item["price"]
                )
                db.add(sale_item)
            
            db.commit()
            
            st.session_state.last_sale = {
                "id": sale.id,
                "total": total,
                "payment_method": payment_method,
                "items": st.session_state.cart.copy(),
                "timestamp": sale.created_at
            }
            
            clear_cart()
            return True, sale.id
        except Exception as e:
            db.rollback()
            return False, str(e)
    
    # Page header
    st.markdown("""
        <div style="background: linear-gradient(135deg, #2E86AB 0%, #1a5f7a 100%); padding: 1.5rem; border-radius: 12px; color: white; margin-bottom: 1.5rem;">
            <h2 style="margin: 0;">💰 Point of Sale System</h2>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Process sales transactions and manage your checkout</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize database
    db = SessionLocal()
    
    # Get products
    products = db.query(Product).filter(Product.quantity > 0).all()
    
    # Main layout
    col_left, col_right = st.columns([2, 1])
    
    # Left: Products
    with col_left:
        st.markdown("### 🛍️ Products")
        
        col1, col2 = st.columns([2, 1])
        with col1:
            search = st.text_input("🔍 Search products", placeholder="Enter product name...")
        with col2:
            all_types = list(set(p.type for p in products)) if products else []
            type_filter = st.selectbox("Filter by Type", ["All"] + sorted(all_types))
        
        # Filter products
        filtered = products
        if search:
            filtered = [p for p in filtered if search.lower() in p.name.lower()]
        if type_filter != "All":
            filtered = [p for p in filtered if p.type == type_filter]
        
        if not filtered:
            st.info("🔍 No products found.")
        else:
            for i in range(0, len(filtered), 2):
                cols = st.columns(2)
                for idx, col in enumerate(cols):
                    if i + idx < len(filtered):
                        product = filtered[i + idx]
                        with col:
                            st.markdown(f"**{product.name}**")
                            st.caption(f"{product.type} • {product.size}")
                            st.write(f"**{format_currency(product.sell_price)}**")
                            st.caption(f"Stock: {product.quantity}")
                            
                            col_qty, col_btn = st.columns([1, 2])
                            with col_qty:
                                qty = st.number_input("Qty", 1, product.quantity, 1, key=f"qty_{product.id}", label_visibility="collapsed")
                            with col_btn:
                                if st.button("🛒 Add", key=f"add_{product.id}", use_container_width=True):
                                    add_to_cart(product, qty)
                                    st.success(f"Added {qty}x {product.name}")
                                    st.rerun()
                            st.markdown("---")
    
    # Right: Cart
    with col_right:
        st.markdown("### 🛒 Shopping Cart")
        
        cart_items = get_cart_items_count()
        cart_total = get_cart_total()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Items", cart_items)
        with col2:
            st.metric("Total", format_currency(cart_total))
        
        st.markdown("---")
        
        if not st.session_state.cart:
            st.info("🛒 Cart is empty")
        else:
            for idx, item in enumerate(st.session_state.cart):
                st.markdown(f"**{item['name']}**")
                st.caption(f"{item['type']} • {item['size']}")
                col1, col2 = st.columns([1, 1])
                with col1:
                    st.write(f"Qty: {item['quantity']}")
                with col2:
                    st.write(f"**{format_currency(item['price'] * item['quantity'])}**")
                if st.button("🗑️ Remove", key=f"remove_{idx}"):
                    st.session_state.cart.pop(idx)
                    st.rerun()
                st.markdown("---")
            
            st.markdown(f"### Total: {format_currency(cart_total)}")
            
            payment_method = st.selectbox("Payment Method", ["Cash", "Credit Card", "Debit Card", "Mobile Payment"])
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Complete Sale", use_container_width=True, type="primary"):
                    success, result = process_sale(db, payment_method, st.session_state.user["id"])
                    if success:
                        st.success(f"✅ Sale #{result} completed!")
                        st.balloons()
                        st.rerun()
                    else:
                        st.error(f"❌ Error: {result}")
            with col2:
                if st.button("🗑️ Clear Cart", use_container_width=True):
                    clear_cart()
                    st.rerun()
    
    # Last sale receipt
    if st.session_state.last_sale:
        st.markdown("---")
        st.markdown("### 🧾 Last Transaction Receipt")
        
        sale = st.session_state.last_sale
        with st.expander("📄 View Receipt", expanded=True):
            st.markdown(f"""
                **Manuel Ventures**  
                **SALES RECEIPT**  
                Transaction #{sale['id']}  
                {sale['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
                
                ---
            """)
            
            for item in sale['items']:
                st.write(f"**{item['name']}** ({item['type']}, {item['size']})")
                st.write(f"{item['quantity']} x {format_currency(item['price'])} = {format_currency(item['quantity'] * item['price'])}")
            
            st.markdown("---")
            st.markdown(f"**TOTAL: {format_currency(sale['total'])}**")
            st.write(f"Payment Method: {sale['payment_method']}")
            st.caption(f"Served by: {st.session_state.user['username']}")
            
            if st.button("🆕 New Sale", use_container_width=True):
                st.session_state.last_sale = None
                st.rerun()
    
    db.close()
