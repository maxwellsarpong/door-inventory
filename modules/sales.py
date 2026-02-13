"""
Sales/POS Page
This module contains the point of sale system
"""
import streamlit as st
import pandas as pd
from database import SessionLocal
from models import Product, Sale, SaleItem
from datetime import datetime

# -------------------------
# SAFE SESSION INITIALIZATION
# -------------------------
if "cart" not in st.session_state:
    st.session_state.cart = []

if "last_sale" not in st.session_state:
    st.session_state.last_sale = None

# Prevent crash if user not set
if "user" not in st.session_state:
    st.session_state.user = {"id": 1, "username": "Admin"}

if "sale_success_message" not in st.session_state:
    st.session_state.sale_success_message = None



def render():
    """Main render function for sales page"""

    # -------------------------
    # Helper functions
    # -------------------------

    def format_currency(amount):
        return f"₵{amount:,.2f}"

    def add_to_cart(product, quantity):

        cart = st.session_state.get("cart", [])

        if quantity <= 0:
            return False

        if quantity > product.quantity:
            return False

        for item in cart:
            if item["product_id"] == product.id:
                new_quantity = item["quantity"] + quantity

                if new_quantity > product.quantity:
                    return False

                item["quantity"] = new_quantity
                st.session_state.cart = cart
                return True

        cart.append({
            "product_id": product.id,
            "name": product.name,
            "type": product.type,
            "size": product.size,
            "price": product.sell_price,
            "quantity": quantity,
            "available_stock": product.quantity
        })

        st.session_state.cart = cart
        return True

    def get_cart_total():
        cart = st.session_state.get("cart", [])
        return sum(item.get("price", 0) * item.get("quantity", 0) for item in cart)

    def get_cart_items_count():
        cart = st.session_state.get("cart", [])
        return sum(item.get("quantity", 0) for item in cart)

    def clear_cart():
        st.session_state.cart = []

    def process_sale(db, payment_method, user_id):
        try:
            cart = st.session_state.get("cart", [])
            total = get_cart_total()

            if not cart or total <= 0:
                return False, "Cart is empty."

            sale = Sale(
                user_id=user_id,
                total=total,
                payment_method=payment_method,
                created_at=datetime.utcnow()
            )

            db.add(sale)
            db.flush()

            for item in cart:
                product = (
                    db.query(Product)
                    .filter(Product.id == item["product_id"])
                    .with_for_update()
                    .first()
                )

                if not product:
                    db.rollback()
                    return False, "Product no longer exists."

                if product.quantity < item["quantity"]:
                    db.rollback()
                    return False, f"Insufficient stock for {product.name}"

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
                "items": cart.copy(),
                "timestamp": sale.created_at
            }

            clear_cart()
            return True, sale.id

        except Exception as e:
            db.rollback()
            return False, str(e)

    # -------------------------
    # PAGE UI (UNCHANGED)
    # -------------------------

    st.markdown("""
        <div style="background: linear-gradient(135deg, #2E86AB 0%, #1a5f7a 100%); padding: 1.5rem; border-radius: 12px; color: white; margin-bottom: 1.5rem;">
            <h2 style="margin: 0;">💰 Point of Sale System</h2>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Process sales transactions and manage your checkout</p>
        </div>
    """, unsafe_allow_html=True)

    # SHOW SUCCESS MESSAGE 
    message = st.session_state.get("sale_success_message")
    if message:
        st.success(message)
        st.session_state.sale_success_message = None

    db = SessionLocal()

    try:
        products = db.query(Product).filter(Product.quantity > 0).all()

        col_left, col_right = st.columns([2, 1])

        # -------------------------
        # LEFT SIDE (Products)
        # -------------------------
        with col_left:
            st.markdown("### 🛍️ Products")

            col1, col2 = st.columns([2, 1])
            with col1:
                search = st.text_input("🔍 Search products", placeholder="Enter product name...")
            with col2:
                all_types = list(set(p.type for p in products)) if products else []
                type_filter = st.selectbox("Filter by Type", ["All"] + sorted(all_types))

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
                                    qty = st.number_input(
                                        "Qty",
                                        1,
                                        product.quantity,
                                        1,
                                        key=f"qty_{product.id}",
                                        label_visibility="collapsed"
                                    )

                                with col_btn:
                                    if st.button("🛒 Add", key=f"add_{product.id}", use_container_width=True):
                                        success = add_to_cart(product, qty)
                                        if success:
                                            st.success(f"Added {qty}x {product.name}")
                                        else:
                                            st.error("Not enough stock available.")
                                        st.rerun()

                                st.markdown("---")

        # -------------------------
        # RIGHT SIDE (Cart)
        # -------------------------
        with col_right:
            st.markdown("### 🛒 Shopping Cart")

            cart = st.session_state.get("cart", [])
            cart_items = get_cart_items_count()
            cart_total = get_cart_total()

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Items", cart_items)
            with col2:
                st.metric("Total", format_currency(cart_total))

            st.markdown("---")

            if not cart:
                st.info("🛒 Cart is empty")
            else:
                for idx, item in enumerate(cart):
                    st.markdown(f"**{item['name']}**")
                    st.caption(f"{item['type']} • {item['size']}")

                    col1, col2 = st.columns([1, 1])
                    with col1:
                        st.write(f"Qty: {item['quantity']}")
                    with col2:
                        st.write(f"**{format_currency(item['price'] * item['quantity'])}**")

                    if st.button("🗑️ Remove", key=f"remove_{idx}"):
                        cart.pop(idx)
                        st.session_state.cart = cart
                        st.rerun()

                    st.markdown("---")

                st.markdown(f"### Total: {format_currency(cart_total)}")

                payment_method = st.selectbox(
                    "Payment Method",
                    ["Cash", "Credit Card", "Debit Card", "Mobile Payment"]
                )

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Complete Sale", use_container_width=True, type="primary"):
                        success, result = process_sale(
                            db,
                            payment_method,
                            st.session_state.user.get("id")
                        )
                        if success:
                            st.session_state.sale_success_message = f"✅ Sale #{result} completed successfully!"
                            st.balloons()
                            st.rerun()
                        else:
                            st.error(f"❌ Error: {result}")

                with col2:
                    if st.button("🗑️ Clear Cart", use_container_width=True):
                        clear_cart()
                        st.rerun()

    finally:
        db.close()
