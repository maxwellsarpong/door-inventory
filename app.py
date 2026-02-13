import streamlit as st
from auth import authenticate, create_admin_if_not_exists

# Page configuration with custom theme
st.set_page_config(
    page_title="Manuel Inventory System",
    page_icon="🚪",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for modern styling
st.markdown("""
    <style>
    /* Main theme colors */
    :root {
        --primary-color: #2E86AB;
        --secondary-color: #A23B72;
        --background-color: #F8F9FA;
        --card-background: #FFFFFF;
    }
    
    /* Hide default Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Custom login card */
    .login-container {
        max-width: 450px;
        margin: 0 auto;
        padding: 3rem 2rem;
        background: white;
        border-radius: 16px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.07), 0 8px 20px rgba(0, 0, 0, 0.06);
    }
    
    /* Login page specific */
    .login-header {
        text-align: center;
        margin-bottom: 2.5rem;
    }
    
    .login-header h1 {
        color: #2E86AB;
        font-size: 2rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
    }
    
    .login-header p {
        color: #6c757d;
        font-size: 0.95rem;
    }
    
    .login-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
    }
    
    /* Input field styling */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 1.5px solid #e0e0e0;
        padding: 0.75rem 1rem;
        font-size: 1rem;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #2E86AB;
        box-shadow: 0 0 0 3px rgba(46, 134, 171, 0.1);
    }
    
    /* Button styling */
    .stButton > button {
        width: 100%;
        background: linear-gradient(135deg, #2E86AB 0%, #1a5f7a 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-size: 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
        margin-top: 1rem;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(46, 134, 171, 0.3);
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #f8f9fa 0%, #ffffff 100%);
    }
    
    /* User info card */
    .user-info {
        background: linear-gradient(135deg, #2E86AB 0%, #1a5f7a 100%);
        padding: 1.5rem;
        border-radius: 12px;
        color: white;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 12px rgba(46, 134, 171, 0.2);
    }
    
    .user-info h3 {
        margin: 0;
        font-size: 0.9rem;
        font-weight: 600;
        opacity: 0.9;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .user-info p {
        margin: 0;
        font-size: 1.3rem;
        font-weight: 700;
    }
    
    .user-info .role-badge {
        display: inline-block;
        background: rgba(255, 255, 255, 0.2);
        padding: 0.25rem 0.75rem;
        border-radius: 12px;
        font-size: 0.75rem;
        margin-top: 0.5rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    /* Navigation section */
    .nav-section-title {
        font-size: 0.75rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: #6c757d;
        margin-bottom: 0.75rem;
        padding-left: 0.5rem;
    }
    
    /* Navigation buttons */
    .stButton > button[kind="secondary"] {
        background: white;
        color: #2E86AB;
        border: 1px solid #e0e0e0;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: #f8f9fa;
        border-color: #2E86AB;
    }
    
    /* Welcome card */
    .welcome-card {
        background: linear-gradient(135deg, #2E86AB 0%, #1a5f7a 100%);
        padding: 3rem 2rem;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 8px 24px rgba(46, 134, 171, 0.2);
    }
    
    .welcome-card h1 {
        font-size: 2.5rem;
        margin-bottom: 1rem;
        font-weight: 700;
    }
    
    .welcome-card p {
        font-size: 1.2rem;
        opacity: 0.95;
    }
    
    /* Feature cards */
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
        transition: all 0.3s ease;
        border: 1px solid #f0f0f0;
    }
    
    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
        border-color: #2E86AB;
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 1rem;
    }
    
    .feature-card h3 {
        color: #1a1a1a;
        margin-bottom: 0.5rem;
        font-size: 1.3rem;
    }
    
    .feature-card p {
        color: #6c757d;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* Quick stats */
    .quick-stats {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1rem;
        border: 1px solid #e0e0e0;
    }
    
    .quick-stats h4 {
        margin: 0 0 0.75rem 0;
        font-size: 0.85rem;
        color: #6c757d;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .stat-item {
        display: flex;
        justify-content: space-between;
        padding: 0.5rem 0;
        border-bottom: 1px solid #f0f0f0;
    }
    
    .stat-item:last-child {
        border-bottom: none;
    }
    
    .stat-label {
        color: #6c757d;
        font-size: 0.9rem;
    }
    
    .stat-value {
        color: #2E86AB;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    /* Spacing utilities */
    .spacer {
        height: 2rem;
    }
    
    .spacer-small {
        height: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize admin user
create_admin_if_not_exists()

# Initialize session state
if "user" not in st.session_state:
    st.session_state.user = None

if "current_page" not in st.session_state:
    st.session_state.current_page = "Home"

def login():
    """Modern login page with card layout"""
    st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
            <div class="login-container">
                <div class="login-header">
                    <div class="login-icon">🚪</div>
                    <h1>Manuel Inventory System</h1>
                    <p>German Doors Management Portal</p>
                    <style>
                        div[data-testid="InputInstructions"] {
                            visibility: hidden;
                        }
                    </style>
                </div>
        """, unsafe_allow_html=True)
        
        with st.form("login_form", clear_on_submit=False):
            username = st.text_input(
                "Username",
                placeholder="Enter your username",
                key="username_input"
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter your password",
                key="password_input"
            )
            
            submit = st.form_submit_button("Sign In", use_container_width=True)
            
            if submit:
                if username and password:
                    user = authenticate(username, password)
                    if user:
                        st.session_state.user = user
                        st.session_state.current_page = "Home"
                        st.success("✓ Login successful! Redirecting...")
                        st.rerun()
                    else:
                        st.error("✗ Invalid credentials. Please try again.")
                else:
                    st.warning("⚠ Please enter both username and password.")
        
        st.markdown("</div>", unsafe_allow_html=True)

def logout():
    """Handle user logout"""
    st.session_state.user = None
    st.session_state.current_page = "Home"
    st.rerun()

def navigate_to(page):
    """Navigate to a specific page"""
    st.session_state.current_page = page
    st.rerun()

def render_sidebar():
    """Render enhanced sidebar with navigation"""
    with st.sidebar:
        # User info card
        st.markdown(f"""
            <div class="user-info">
                <h3>Logged in as</h3>
                <p>👤 {st.session_state.user['username']}</p>
                <span class="role-badge">{st.session_state.user['role'].upper()}</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Main Navigation
        
        if st.button("🏠 Home", use_container_width=True, type="primary" if st.session_state.current_page == "Home" else "secondary"):
            navigate_to("Home")
        
        if st.button("📦 Inventory", use_container_width=True, type="primary" if st.session_state.current_page == "Inventory" else "secondary"):
            navigate_to("Inventory")
        
        if st.button("₵🏷️ Sales", use_container_width=True, type="primary" if st.session_state.current_page == "Sales" else "secondary"):
            navigate_to("Sales")
        
        
        # Reports & Analytics
        
        if st.button("📈 Sales Reports", use_container_width=True, type="primary" if st.session_state.current_page == "Reports" else "secondary"):
            navigate_to("Reports")
        
        
        # Admin Section (only for admins)
        if st.session_state.user['role'] == 'admin':
            #st.markdown('<div class="nav-section-title">⚙️ ADMINISTRATION</div>', unsafe_allow_html=True)
            
            if st.button("👥 User Management", use_container_width=True, type="primary" if st.session_state.current_page == "Users" else "secondary"):
                navigate_to("Users")
            
        
        # Quick Stats (only on non-Home pages)
        if st.session_state.current_page != "Home":
            from database import SessionLocal
            from models import Product, Sale
            from sqlalchemy import func
            from datetime import datetime
            
            db = SessionLocal()
            try:
                total_products = db.query(func.count(Product.id)).scalar() or 0
                low_stock = db.query(func.count(Product.id)).filter(Product.quantity < 10).scalar() or 0
                total_sales_today = db.query(func.count(Sale.id)).filter(
                    func.date(Sale.created_at) == datetime.utcnow().date()
                ).scalar() or 0
                
                st.markdown(f"""
                    <div class="quick-stats">
                        <h4>📊 Quick Stats</h4>
                        <div class="stat-item">
                            <span class="stat-label">Products</span>
                            <span class="stat-value">{total_products}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Low Stock</span>
                            <span class="stat-value">{low_stock}</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-label">Sales Today</span>
                            <span class="stat-value">{total_sales_today}</span>
                        </div>
                    </div>
                """, unsafe_allow_html=True)
            except:
                pass
            finally:
                db.close()
        
        st.markdown("---")
        
        # Account section
        st.markdown('<div class="nav-section-title">👤 ACCOUNT</div>', unsafe_allow_html=True)
        
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            logout()
        
        st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
        
        # Footer
        st.caption("Manuel Inventory System v1.0")
        st.caption(f"© {get_current_year()} All rights reserved")

def get_current_year():
    """Utility function to get current year"""
    from datetime import datetime
    return datetime.utcnow().year

def render_home_page():
    """Render home page"""
    st.markdown("""
        <div class="welcome-card">
            <h1>🚪 Welcome to Manuel System</h1>
            <p>Your comprehensive inventory management solution for German doors</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("### Quick Access")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Go to Inventory", key="nav_inventory", use_container_width=True):
            navigate_to("Inventory")
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📦</div>
                <h3>Inventory</h3>
                <p>Manage your door inventory with real-time tracking and updates</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        if st.button("Go to Sales", key="nav_sales", use_container_width=True):
            navigate_to("Sales")
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">₵🏷️</div>
                <h3>Sales</h3>
                <p>Process sales orders and track revenue performance</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        if st.button("Go to Reports", key="nav_reports", use_container_width=True):
            navigate_to("Reports")
        st.markdown("""
            <div class="feature-card">
                <div class="feature-icon">📊</div>
                <h3>Reports</h3>
                <p>Generate detailed analytics and business insights</p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        if st.session_state.user['role'] == 'admin':
            if st.button("Go to Users", key="nav_users", use_container_width=True):
                navigate_to("Users")
            st.markdown("""
                <div class="feature-card">
                    <div class="feature-icon">👥</div>
                    <h3>Users</h3>
                    <p>Manage user accounts and access permissions</p>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div class="feature-card" style="opacity: 0.5;">
                    <div class="feature-icon">👥</div>
                    <h3>Users</h3>
                    <p>Admin access required</p>
                </div>
            """, unsafe_allow_html=True)
    
    st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 🎯 Getting Started")
        st.markdown("""
            - Use the **sidebar** to navigate between different sections
            - Check **Inventory** to view current stock levels
            - Review **Sales** for recent transactions
            - Generate **Reports** for business analytics
        """)
    
    with col2:
        st.markdown("#### 💡 Quick Tips")
        st.markdown("""
            - All changes are saved automatically
            - Use filters to find specific items quickly
            - Export reports to CSV for external analysis
            - Contact support for any assistance needed
        """)
    
    # System status
    st.markdown("---")
    st.markdown("### 🔔 System Status")
    
    from database import SessionLocal
    from models import Product
    
    db = SessionLocal()
    try:
        low_stock_items = db.query(Product).filter(Product.quantity < 10).all()
        all_products = db.query(Product).filter(Product.quantity == 10).all()
        
        if low_stock_items:
            st.warning(f"⚠️ {len(low_stock_items)} product(s) are running low on stock. Check the Inventory page.")
            
            with st.expander("View Low Stock Items"):
                for item in low_stock_items[:5]:
                    st.write(f"• {item.name} ({item.type}, {item.size}) - Only {item.quantity} left")
                if len(low_stock_items) > 5:
                    st.caption(f"... and {len(low_stock_items) - 5} more")
        elif all_products == 0:
            st.error("🚨 No products in inventory! Please add products to get started.")
        else:
            st.success("✅ All inventory levels are healthy!")
    finally:
        db.close()

def render_page_content():
    """Render content based on current page"""
    if st.session_state.current_page == "Home":
        render_home_page()
    
    elif st.session_state.current_page == "Inventory":
        # Import and render inventory page
        import pages.inventory as inventory
        inventory.render()
    
    elif st.session_state.current_page == "Sales":
        # Import and render sales page
        import pages.sales as sales
        sales.render()
    
    elif st.session_state.current_page == "Reports":
        # Import and render reports page
        import pages.reports as reports
        reports.render()
    
    elif st.session_state.current_page == "Users":
        if st.session_state.user['role'] == 'admin':
            # Import and render user management page
            import pages.users as users
            users.render()
        else:
            st.error("⛔ Access Denied: Admin privileges required")

# Main application logic


if st.session_state.user is None:
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {display: none;}
            [data-testid="collapsedControl"] {display: none;}
        </style>
    """, unsafe_allow_html=True)

    login()
else:
    render_sidebar()
    render_page_content()

