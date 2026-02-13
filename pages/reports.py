"""
Sales Reports Page
This module contains sales analytics and reporting
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from database import SessionLocal
from models import Sale, SaleItem, Product, User
from datetime import datetime, timedelta
from sqlalchemy import func

def render():
    """Main render function for reports page"""
    
    def format_currency(amount):
        return f"₵{amount:,.2f}"
    
    # Page header
    st.markdown("""
        <div style="background: linear-gradient(135deg, #A23B72 0%, #7c2d5a 100%); padding: 1.5rem; border-radius: 12px; color: white; margin-bottom: 1.5rem;">
            <h2 style="margin: 0;">📊 Sales Reports & Analytics</h2>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Comprehensive sales insights and performance metrics</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize database
    db = SessionLocal()
    
    # Get sales data
    sales = db.query(Sale).order_by(Sale.created_at.desc()).all()
    
    if not sales:
        st.info("📊 No sales data available yet.")
        db.close()
        return
    
    # Date filter
    date_filter = st.selectbox("📅 Time Period", ["All Time", "Today", "Last 7 Days", "Last 30 Days", "Last 90 Days"])
    
    # Apply filter
    filtered_sales = sales
    if date_filter == "Today":
        today = datetime.utcnow().date()
        filtered_sales = [s for s in sales if s.created_at.date() == today]
    elif date_filter == "Last 7 Days":
        cutoff = datetime.utcnow() - timedelta(days=7)
        filtered_sales = [s for s in sales if s.created_at >= cutoff]
    elif date_filter == "Last 30 Days":
        cutoff = datetime.utcnow() - timedelta(days=30)
        filtered_sales = [s for s in sales if s.created_at >= cutoff]
    elif date_filter == "Last 90 Days":
        cutoff = datetime.utcnow() - timedelta(days=90)
        filtered_sales = [s for s in sales if s.created_at >= cutoff]
    
    # Calculate metrics
    total_sales = sum(s.total for s in filtered_sales)
    total_transactions = len(filtered_sales)
    avg_transaction = total_sales / total_transactions if total_transactions > 0 else 0
    
    st.markdown("---")
    st.markdown("### 💰 Key Performance Indicators")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Revenue", format_currency(total_sales))
    with col2:
        st.metric("Total Transactions", f"{total_transactions:,}")
    with col3:
        st.metric("Average Transaction", format_currency(avg_transaction))
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📈 Charts", "📋 Transactions", "🏆 Top Products"])
    
    # Tab 1: Charts
    with tab1:
        st.markdown("### 📈 Sales Trends")
        
        # Group by date
        sales_by_date = {}
        for sale in filtered_sales:
            date = sale.created_at.date()
            if date not in sales_by_date:
                sales_by_date[date] = {"count": 0, "total": 0}
            sales_by_date[date]["count"] += 1
            sales_by_date[date]["total"] += sale.total
        
        if sales_by_date:
            df_timeline = pd.DataFrame([
                {"Date": date, "Revenue": data["total"], "Transactions": data["count"]}
                for date, data in sorted(sales_by_date.items())
            ])
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.line(df_timeline, x="Date", y="Revenue", title="Revenue Over Time", markers=True)
                fig.update_traces(line_color='#A23B72')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(df_timeline, x="Date", y="Transactions", title="Daily Transactions")
                fig.update_traces(marker_color='#2E86AB')
                st.plotly_chart(fig, use_container_width=True)
    
    # Tab 2: Transactions
    with tab2:
        st.markdown("### 📋 Sales Transactions")
        
        df_data = []
        for s in filtered_sales:
            items = db.query(SaleItem).filter(SaleItem.sale_id == s.id).all()
            items_count = sum(item.quantity for item in items)
            
            df_data.append({
                "ID": s.id,
                "Date": s.created_at.strftime("%Y-%m-%d %H:%M"),
                "Staff": s.user.username if s.user else "Unknown",
                "Items": items_count,
                "Payment": s.payment_method,
                "Total": format_currency(s.total)
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Export
        if st.button("📥 Export to CSV"):
            csv = df.to_csv(index=False)
            st.download_button(
                "💾 Download CSV",
                csv,
                f"sales_report_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv",
                "text/csv"
            )
    
    # Tab 3: Top Products
    with tab3:
        st.markdown("### 🏆 Top Selling Products")
        
        top_products = (
            db.query(
                Product.name,
                func.sum(SaleItem.quantity).label('total_quantity'),
                func.sum(SaleItem.quantity * SaleItem.price).label('total_revenue')
            )
            .join(SaleItem, Product.id == SaleItem.product_id)
            .group_by(Product.id, Product.name)
            .order_by(func.sum(SaleItem.quantity).desc())
            .limit(10)
            .all()
        )
        
        if top_products:
            df_top = pd.DataFrame([
                {"Product": p[0], "Units Sold": int(p[1]), "Revenue": float(p[2])}
                for p in top_products
            ])
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(df_top, x="Units Sold", y="Product", orientation='h', title="Top Products by Units")
                fig.update_traces(marker_color='#2E86AB')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(df_top, x="Revenue", y="Product", orientation='h', title="Top Products by Revenue")
                fig.update_traces(marker_color='#A23B72')
                st.plotly_chart(fig, use_container_width=True)
            
            # Table
            df_display = df_top.copy()
            df_display["Revenue"] = df_display["Revenue"].apply(format_currency)
            st.dataframe(df_display, use_container_width=True, hide_index=True)
        else:
            st.info("No product sales data available.")
    
    db.close()
