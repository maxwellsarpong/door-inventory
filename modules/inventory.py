"""
Inventory Management Page
This module contains all inventory management functionality
"""
import streamlit as st
import pandas as pd
from database import SessionLocal
from models import Product
from datetime import datetime

def render():
    """Main render function for inventory page"""
    
    # Custom CSS for this page
    st.markdown("""
        <style>
        .section-header {
            background: linear-gradient(135deg, #2E86AB 0%, #1a5f7a 100%);
            padding: 1.5rem;
            border-radius: 12px;
            color: white;
            margin-bottom: 1.5rem;
        }
        .section-header h2 {
            margin: 0;
            font-size: 1.8rem;
            font-weight: 600;
        }
        .section-header p {
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
            font-size: 0.95rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Page header
    st.markdown("""
        <div class="section-header">
            <h2>📦 Inventory Management</h2>
            <p>Manage your door inventory with real-time tracking and comprehensive controls</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize database
    db = SessionLocal()
    
    # Helper functions
    def format_currency(amount):
        return f"₵{amount:,.2f}"
    
    def get_profit_margin(buy_price, sell_price):
        if buy_price == 0:
            return 0
        return ((sell_price - buy_price) / buy_price) * 100
    
    # Get inventory stats
    products = db.query(Product).all()
    total_products = len(products)
    total_quantity = sum(p.quantity for p in products)
    total_value = sum(p.quantity * p.buy_price for p in products)
    low_stock = len([p for p in products if p.quantity < 10])
    
    # Display stats
    st.markdown("### 📊 Inventory Overview")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Products", total_products, help="Total number of unique products")
    with col2:
        st.metric("Total Quantity", f"{total_quantity:,}", help="Total units across all products")
    with col3:
        st.metric("Inventory Value", format_currency(total_value), help="Total value based on buy prices")
    with col4:
        st.metric("Low Stock Items", low_stock, help="Products with quantity less than 10")
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 View Inventory", "➕ Add Product", "🔍 Search & Filter"])
    
    # Tab 1: View Inventory
    with tab1:
        st.markdown("### Current Inventory")
        
        if not products:
            st.info("🔍 No products in inventory yet. Add your first product using the 'Add Product' tab.")
        else:
            df_data = []
            for p in products:
                profit_margin = get_profit_margin(p.buy_price, p.sell_price)
                df_data.append({
                    "ID": p.id,
                    "Name": p.name,
                    "Type": p.type,
                    "Size": p.size,
                    "Buy Price": format_currency(p.buy_price),
                    "Sell Price": format_currency(p.sell_price),
                    "Margin %": f"{profit_margin:.1f}%",
                    "Quantity": p.quantity,
                    "Stock Value": format_currency(p.quantity * p.buy_price)
                })
            
            df = pd.DataFrame(df_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
            
            # Export button
            if st.button("📥 Export to CSV", key="export_inventory"):
                csv = df.to_csv(index=False)
                st.download_button(
                    "💾 Download CSV",
                    csv,
                    f"inventory_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "text/csv"
                )
            
            # Edit/Delete section
            st.markdown("---")
            st.markdown("### ✏️ Edit or Delete Product")
            
            product_options = {f"{p.id} - {p.name} ({p.type}, {p.size})": p.id for p in products}
            selected_product = st.selectbox("Select a product", list(product_options.keys()))
            
            if selected_product:
                product_id = product_options[selected_product]
                product = db.query(Product).filter(Product.id == product_id).first()
                
                if product:
                    with st.expander("📝 Edit Product Details", expanded=False):
                        with st.form(f"edit_product_{product_id}"):
                            col1, col2 = st.columns(2)
                            
                            with col1:
                                edit_name = st.text_input("Door Name", value=product.name)
                                # edit_type = st.text_input("Type", value=product.type)
                                types = ["Metal", "Glass", "Wood"]
                                selected_type = st.selectbox("Type", options=types, index=types.index(product.type) if product.type in types else 0)
                                
                                sizes = ["O/H", "Single", "Double"]
                                selected_size = st.selectbox(
                                                    "Size",
                                                    options=sizes,
                                                    index=sizes.index(product.size) if product.size in sizes else 0
                                                )
                            
                            with col2:
                                edit_buy = st.number_input("Buy Price (₵)", value=float(product.buy_price), min_value=0.0)
                                edit_sell = st.number_input("Sell Price (₵)", value=float(product.sell_price), min_value=0.0)
                                edit_qty = st.number_input("Quantity", value=int(product.quantity), min_value=0)
                            
                            col1, col2 = st.columns(2)
                            with col1:
                                if st.form_submit_button("💾 Save Changes", use_container_width=True):
                                    product.name = edit_name.strip()
                                    product.type = selected_type.strip()
                                    product.size = selected_size.strip()
                                    product.buy_price = edit_buy
                                    product.sell_price = edit_sell
                                    product.quantity = edit_qty
                                    db.commit()
                                    st.success("✅ Product updated successfully!")
                                    st.rerun()
                            
                            with col2:
                                if st.form_submit_button("🗑️ Delete Product", use_container_width=True):
                                    db.delete(product)
                                    db.commit()
                                    st.success("✅ Product deleted successfully!")
                                    st.rerun()
    
    # Tab 2: Add Product
    with tab2:
        st.markdown("### ➕ Add New Product")
        
        with st.form("add_product", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Door Name / Model Number *", placeholder="e.g., Oak Premium Door / 5555")
                dtype = st.text_input("Type *", placeholder="e.g., Glass, Metal, Wood")
                
                # types = ["Metal", "Glass", "Wood"]
                # try:
                #     default_index = types.index(product.type) if product.type in types else 0
                # except (ValueError, AttributeError):
                #     default_index = 0
                # dtype = st.selectbox("Type", options=types, index=default_index)
                
                size = st.text_input("Size *", placeholder="e.g., O/H, Single, Double")
                # sizes = ["O/H", "Single", "Double"]
                # size = st.selectbox(
                #                     "Size",
                #                     options=sizes,
                #                     index=sizes.index(product.size) if product.size in sizes else 0
                #                 )
            
            with col2:
                buy = st.number_input("Buy Price (₵) *", min_value=0.0, step=0.01)
                sell = st.number_input("Sell Price (₵) *", min_value=0.0, step=0.01)
                qty = st.number_input("Quantity *", min_value=0, step=1)
            
            if buy > 0 and sell > 0:
                profit_margin = get_profit_margin(buy, sell)
                st.info(f"💰 Profit Preview: {format_currency(sell - buy)} per unit • {profit_margin:.1f}% margin")
            
            if st.form_submit_button("➕ Add Product", use_container_width=True, type="primary"):
                if name and dtype and size and buy > 0 and sell > 0:
                    new_product = Product(
                        name=name.strip(),
                        type=dtype.strip(),
                        size=size.strip(),
                        buy_price=buy,
                        sell_price=sell,
                        quantity=qty
                    )
                    db.add(new_product)
                    db.commit()
                    st.success(f"✅ Product '{name}' added successfully!")
                    st.balloons()
                else:
                    st.error("❌ Please fill in all required fields")
    
    # Tab 3: Search & Filter
    with tab3:
        st.markdown("### 🔍 Search & Filter Inventory")
        
        if not products:
            st.info("🔍 No products available to search.")
        else:
            col1, col2, col3 = st.columns(3)
            
            with col1:
                search_name = st.text_input("🔎 Search by Name", placeholder="Enter door name...")
            with col2:
                all_types = list(set(p.type for p in products))
                search_type = st.selectbox("Filter by Type", ["All"] + sorted(all_types))
            with col3:
                stock_filter = st.selectbox("Stock Status", ["All", "In Stock (≥10)", "Low Stock (1-9)", "Out of Stock (0)"])
            
            # Apply filters
            filtered = products
            if search_name:
                filtered = [p for p in filtered if search_name.lower() in p.name.lower()]
            if search_type != "All":
                filtered = [p for p in filtered if p.type == search_type]
            if stock_filter == "In Stock (≥10)":
                filtered = [p for p in filtered if p.quantity >= 10]
            elif stock_filter == "Low Stock (1-9)":
                filtered = [p for p in filtered if 0 < p.quantity < 10]
            elif stock_filter == "Out of Stock (0)":
                filtered = [p for p in filtered if p.quantity == 0]
            
            st.markdown(f"### Results ({len(filtered)} products)")
            
            if filtered:
                df_data = []
                for p in filtered:
                    df_data.append({
                        "ID": p.id,
                        "Name": p.name,
                        "Type": p.type,
                        "Size": p.size,
                        "Quantity": p.quantity,
                        "Value": format_currency(p.quantity * p.buy_price)
                    })
                st.dataframe(pd.DataFrame(df_data), use_container_width=True, hide_index=True)
            else:
                st.warning("⚠️ No products match your search criteria.")
    
    # Close database
    db.close()
