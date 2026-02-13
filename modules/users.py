"""
User Management Page
This module contains user administration functionality
"""
import streamlit as st
import pandas as pd
from database import SessionLocal
from models import User, Sale
from auth import hash_password
from datetime import datetime
from sqlalchemy import func

def render():
    """Main render function for user management page"""
    
    # Check admin access
    if st.session_state.user['role'] != 'admin':
        st.error("⛔ Access Denied: Admin privileges required")
        return
    
    def format_currency(amount):
        return f"${amount:,.2f}"
    
    # Page header
    st.markdown("""
        <div style="background: linear-gradient(135deg, #6C63FF 0%, #4834DF 100%); padding: 1.5rem; border-radius: 12px; color: white; margin-bottom: 1.5rem;">
            <h2 style="margin: 0;">👥 User Management</h2>
            <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Manage user accounts, roles, and permissions</p>
        </div>
    """, unsafe_allow_html=True)
    
    # Initialize database
    db = SessionLocal()
    
    # Get users
    users = db.query(User).all()
    
    # Stats
    st.markdown("### 📊 User Overview")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Users", len(users))
    with col2:
        admin_count = len([u for u in users if u.role == "admin"])
        st.metric("Administrators", admin_count)
    with col3:
        staff_count = len([u for u in users if u.role == "staff"])
        st.metric("Staff Members", staff_count)
    
    st.markdown("---")
    
    # Tabs
    tab1, tab2, tab3 = st.tabs(["📋 User List", "➕ Add User", "✏️ Edit User"])
    
    # Tab 1: User List
    with tab1:
        st.markdown("### 👥 All Users")
        
        df_data = []
        for u in users:
            sales_count = db.query(func.count(Sale.id)).filter(Sale.user_id == u.id).scalar() or 0
            total_revenue = db.query(func.sum(Sale.total)).filter(Sale.user_id == u.id).scalar() or 0
            
            df_data.append({
                "ID": u.id,
                "Username": u.username,
                "Role": u.role.title(),
                "Created": u.created_at.strftime("%Y-%m-%d"),
                "Sales": sales_count,
                "Revenue": format_currency(float(total_revenue))
            })
        
        df = pd.DataFrame(df_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
    
    # Tab 2: Add User
    with tab2:
        st.markdown("### ➕ Create New User")
        
        with st.form("add_user", clear_on_submit=True):
            col1, col2 = st.columns(2)
            
            with col1:
                new_username = st.text_input("Username *", placeholder="Enter username")
                new_password = st.text_input("Password *", type="password", placeholder="Min 6 characters")
                new_password_confirm = st.text_input("Confirm Password *", type="password")
            
            with col2:
                new_role = st.selectbox("Role *", ["staff", "admin"], format_func=lambda x: "Administrator" if x == "admin" else "Staff Member")
                
                if new_role == "admin":
                    st.warning("⚠️ Admin users have full system access")
                else:
                    st.info("ℹ️ Staff users can process sales")
            
            if st.form_submit_button("➕ Create User", type="primary"):
                errors = []
                
                if not new_username or len(new_username) < 3:
                    errors.append("Username must be at least 3 characters")
                elif db.query(User).filter(User.username == new_username).first():
                    errors.append("Username already exists")
                
                if not new_password or len(new_password) < 6:
                    errors.append("Password must be at least 6 characters")
                
                if new_password != new_password_confirm:
                    errors.append("Passwords do not match")
                
                if errors:
                    for error in errors:
                        st.error(f"❌ {error}")
                else:
                    new_user = User(
                        username=new_username.strip(),
                        password_hash=hash_password(new_password),
                        role=new_role,
                        created_at=datetime.utcnow()
                    )
                    db.add(new_user)
                    db.commit()
                    st.success(f"✅ User '{new_username}' created successfully!")
                    st.balloons()
    
    # Tab 3: Edit User
    with tab3:
        st.markdown("### ✏️ Edit User")
        
        if not users:
            st.info("No users available to edit.")
        else:
            user_options = {f"{u.username} ({u.role})": u.id for u in users}
            selected = st.selectbox("Select user to edit", list(user_options.keys()))
            
            if selected:
                user_id = user_options[selected]
                edit_user = db.query(User).filter(User.id == user_id).first()
                
                if edit_user:
                    is_self = edit_user.id == st.session_state.user["id"]
                    
                    with st.form(f"edit_user_{user_id}"):
                        edit_username = st.text_input("Username", value=edit_user.username, disabled=is_self)
                        edit_role = st.selectbox("Role", ["staff", "admin"], 
                                                index=0 if edit_user.role == "staff" else 1,
                                                disabled=is_self)
                        
                        st.markdown("#### Change Password (Optional)")
                        new_password = st.text_input("New Password", type="password", placeholder="Leave blank to keep current")
                        
                        if new_password:
                            new_password_confirm = st.text_input("Confirm New Password", type="password")
                        
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.form_submit_button("💾 Save Changes", type="primary"):
                                errors = []
                                
                                if new_password and len(new_password) < 6:
                                    errors.append("Password must be at least 6 characters")
                                if new_password and new_password != new_password_confirm:
                                    errors.append("Passwords do not match")
                                
                                if errors:
                                    for error in errors:
                                        st.error(f"❌ {error}")
                                else:
                                    if not is_self:
                                        edit_user.username = edit_username.strip()
                                        edit_user.role = edit_role
                                    
                                    if new_password:
                                        edit_user.password_hash = hash_password(new_password)
                                    
                                    db.commit()
                                    st.success("✅ User updated successfully!")
                                    st.rerun()
                        
                        with col2:
                            if not is_self:
                                if st.form_submit_button("🗑️ Delete User"):
                                    has_sales = db.query(Sale).filter(Sale.user_id == user_id).first()
                                    if has_sales:
                                        st.error("❌ Cannot delete user with sales records")
                                    else:
                                        db.delete(edit_user)
                                        db.commit()
                                        st.success("✅ User deleted!")
                                        st.rerun()
    
    db.close()
