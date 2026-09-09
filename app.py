import streamlit as st
import pandas as pd
import os
from datetime import datetime

# ==============================================================================
# 1. PAGE CONFIGURATION & THEMING
# ==============================================================================
st.set_page_config(
    page_title="Sapphire Collection POS",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==============================================================================
# 2. FILE PATHS & DATA MANAGEMENT
# ==============================================================================
DB_DIR = "sapphire_retail_db"
if not os.path.exists(DB_DIR): os.makedirs(DB_DIR)

PRODUCTS_FILE = os.path.join(DB_DIR, "products.csv")
CREDIT_FILE = os.path.join(DB_DIR, "credit_records.csv")
CUSTOMER_FILE = os.path.join(DB_DIR, "customers.csv")
SALES_FILE = os.path.join(DB_DIR, "sales.csv")

def load_data(filepath, default_cols):
    if os.path.exists(filepath):
        try:
            df = pd.read_csv(filepath)
            for col in default_cols:
                if col not in df.columns:
                    if col in ["Price", "Cost", "Amount", "Paid", "Balance"]: df[col] = 0.0
                    elif col in ["Stock", "Points", "Qty"]: df[col] = 0
                    else: df[col] = ""
            return df
        except:
            return pd.DataFrame(columns=default_cols)
    return pd.DataFrame(columns=default_cols)

def save_data(df, filepath):
    try:
        df.to_csv(filepath, index=False)
    except: pass

df_products = load_data(PRODUCTS_FILE, ["Item Code", "Product Name", "Category", "Cost", "Price", "Stock"])
df_credit = load_data(CREDIT_FILE, ["Record ID", "Customer Name", "Phone", "Description", "Amount", "Date", "Status"])
df_customers = load_data(CUSTOMER_FILE, ["Customer Name", "Phone", "Points", "Tier"])
df_sales = load_data(SALES_FILE, ["Invoice No", "Date", "Cashier", "Customer", "Total", "Payment Method"])

# ==============================================================================
REGION_ROLES = {
    "Admin": "admin123",
    "Cashier": "cashier123",
    "Store Manager": "mgr123"
}

# ==============================================================================
# 3. AUTHENTICATION GATEWAY
# ==============================================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.role = ""

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; color: #1f77b4; margin-top: 2rem;'>SAPPHIRE COLLECTION POS</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: gray; margin-bottom: 2rem;'>Advanced Retail & Apparel Management System</h4>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("### 🔐 User Authentication")
        with st.form("auth_form"):
            sel_role = st.selectbox("Select Account Role:", list(REGION_ROLES.keys()))
            entered_pass = st.text_input("Enter Password:", type="password")
            
            submit_login = st.form_submit_button("🚀 Login to System", use_container_width=True)
            if submit_login:
                if entered_pass == REGION_ROLES.get(sel_role):
                    st.session_state.logged_in = True
                    st.session_state.role = sel_role
                    st.success("Login Successful!")
                    st.rerun()
                else:
                    st.error("❌ Incorrect Password for selected role.")
    st.stop()

# ==============================================================================
# 4. DASHBOARD & MODULE NAVIGATION
# ==============================================================================
st.sidebar.markdown(f"### 👤 Current User: **{st.session_state.role}**")
if st.sidebar.button("🔒 Logout System", use_container_width=True):
    st.session_state.logged_in = False
    st.session_state.role = ""
    st.rerun()

st.sidebar.markdown("---")
st.sidebar.markdown("### 📌 Navigation")
app_mode = st.sidebar.radio("Select Module:", [
    "🏠 Dashboard Overview", 
    "🛒 POS Billing Counter", 
    "📦 Product Management", 
    "📖 Udara Book (Credit Records)", 
    "👥 Customer & Loyalty Program", 
    "🏷️ Barcode Generator",
    "📊 Sales Reports"
])

st.markdown("<h2 style='text-align: center; color: #1f77b4;'>Sapphire Collection POS System</h2>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>Select a module below to proceed</p>", unsafe_allow_html=True)
st.markdown("---")

# ==============================================================================
# MODULE 0: DASHBOARD OVERVIEW
# ==============================================================================
if app_mode == "🏠 Dashboard Overview":
    st.subheader("📍 Dashboard Overview")
    
    col1, col2, col3 = st.columns(3)
    total_prod = len(df_products) if not df_products.empty else 0
    total_sales_amt = df_sales["Total"].sum() if not df_sales.empty else 0.0
    total_credit = df_credit[df_credit["Status"] == "Pending"]["Amount"].sum() if not df_credit.empty else 0.0
    
    col1.metric("Total Products", total_prod)
    col2.metric("Total Sales Revenue", f"Rs. {total_sales_amt:,.2f}")
    col3.metric("Pending Credit (Udara Book)", f"Rs. {total_credit:,.2f}")
    
    st.info("💡 Use the sidebar menu to navigate through Product Management, Billing, Credit Records, and Barcode generation features seamlessly.")

# ==============================================================================
# MODULE 1: POS BILLING COUNTER
# ==============================================================================
elif app_mode == "🛒 POS Billing Counter":
    st.subheader("🛒 POS Billing Counter")
    if "cart" not in st.session_state: st.session_state.cart = []
    
    c1, c2 = st.columns([1.5, 1])
    with c1:
        search_term = st.text_input("🔍 Search Products by Code or Name").strip()
        display_prod = df_products.copy()
        if search_term and not display_prod.empty:
            display_prod = display_prod[
                display_prod['Product Name'].str.contains(search_term, case=False, na=False) |
                display_prod['Item Code'].astype(str).str.contains(search_term, case=False, na=False)
            ]
        st.dataframe(display_prod, use_container_width=True, height=250)
        
        if not df_products.empty:
            with st.form("add_to_cart_form"):
                item_code_sel = st.selectbox("Select Item Code", df_products["Item Code"].tolist())
                qty_sel = st.number_input("Quantity", min_value=1, value=1)
                if st.form_submit_button("Add to Cart"):
                    row = df_products[df_products["Item Code"] == item_code_sel].iloc[0]
                    st.session_state.cart.append({
                        "Code": row["Item Code"], "Name": row["Product Name"],
                        "Price": float(row["Price"]), "Qty": int(qty_sel),
                        "Total": float(row["Price"] * qty_sel)
                    })
                    st.success("Added to cart!")
                    st.rerun()

    with c2:
        st.subheader("🧾 Shopping Cart")
        if st.session_state.cart:
            cart_df = pd.DataFrame(st.session_state.cart)
            st.dataframe(cart_df[["Name", "Price", "Qty", "Total"]], use_container_width=True, height=200)
            
            grand_total = cart_df["Total"].sum()
            st.markdown(f"### Total: Rs. {grand_total:,.2f}")
            
            pay_method = st.selectbox("Payment Method", ["Cash", "Card", "Credit"])
            cust_name = st.text_input("Customer Name", value="Walk-in Customer")
            
            if st.button("Complete Transaction", type="primary", use_container_width=True):
                inv_no = f"INV-{datetime.now().strftime('%y%m%d%H%M%S')}"
                new_sale = {
                    "Invoice No": inv_no, "Date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "Cashier": st.session_state.role, "Customer": cust_name,
                    "Total": grand_total, "Payment Method": pay_method
                }
                df_sales_up = pd.concat([df_sales, pd.DataFrame([new_sale])], ignore_index=True)
                save_data(df_sales_up, SALES_FILE)
                st.session_state.cart = []
                st.success(f"Sale Completed! Invoice: {inv_no}")
                st.rerun()
            
            if st.button("Clear Cart"):
                st.session_state.cart = []
                st.rerun()
        else:
            st.info("Cart is empty.")

# ==============================================================================
# MODULE 2: PRODUCT MANAGEMENT
# ==============================================================================
elif app_mode == "📦 Product Management":
    st.subheader("📦 Product Management")
    with st.form("prod_form"):
        col1, col2 = st.columns(2)
        p_code = col1.text_input("Item Code / Barcode")
        p_name = col2.text_input("Product Name")
        p_cat = col1.selectbox("Category", ["Apparel", "Footwear", "Accessories", "General"])
        p_cost = col2.number_input("Cost Price", 0.0)
        p_price = col1.number_input("Selling Price", 0.0)
        p_stock = col2.number_input("Initial Stock Quantity", 0)
        
        if st.form_submit_button("Save Product"):
            new_p = {"Item Code": p_code, "Product Name": p_name, "Category": p_cat, "Cost": p_cost, "Price": p_price, "Stock": p_stock}
            df_prod_up = pd.concat([df_products, pd.DataFrame([new_p])], ignore_index=True)
            save_data(df_prod_up, PRODUCTS_FILE)
            st.success("Product saved successfully!")
            st.rerun()
            
    st.markdown("### Existing Inventory")
    st.dataframe(df_products, use_container_width=True)

# ==============================================================================
# MODULE 3: UDARA BOOK (CREDIT RECORDS)
# ==============================================================================
elif app_mode == "📖 Udara Book (Credit Records)":
    st.subheader("📖 Udara Book (Credit & Customer Ledger)")
    with st.form("credit_form"):
        c_name = st.text_input("Customer Name")
        c_phone = st.text_input("Phone Number")
        c_desc = st.text_input("Description / Items Bought on Credit")
        c_amt = st.number_input("Credit Amount (Rs.)", 0.0)
        
        if st.form_submit_button("Record Credit"):
            rec_id = f"CR-{datetime.now().strftime('%H%M%S')}"
            new_cr = {"Record ID": rec_id, "Customer Name": c_name, "Phone": c_phone, "Description": c_desc, "Amount": c_amt, "Date": datetime.now().strftime("%Y-%m-%d"), "Status": "Pending"}
            df_cr_up = pd.concat([df_credit, pd.DataFrame([new_cr])], ignore_index=True)
            save_data(df_cr_up, CREDIT_FILE)
            st.success("Credit record added successfully.")
            st.rerun()
            
    st.dataframe(df_credit, use_container_width=True)

# ==============================================================================
# MODULE 4: CUSTOMER & LOYALTY PROGRAM
# ==============================================================================
elif app_mode == "👥 Customer & Loyalty Program":
    st.subheader("👥 Customer & Loyalty Program")
    with st.form("cust_form"):
        name = st.text_input("Customer Full Name")
        phone = st.text_input("Mobile Number")
        if st.form_submit_button("Register Customer"):
            new_c = {"Customer Name": name, "Phone": phone, "Points": 0, "Tier": "Bronze 🥉"}
            df_cust_up = pd.concat([df_customers, pd.DataFrame([new_c])], ignore_index=True)
            save_data(df_cust_up, CUSTOMER_FILE)
            st.success("Customer registered!")
            st.rerun()
    st.dataframe(df_customers, use_container_width=True)

# ==============================================================================
# MODULE 5: BARCODE GENERATOR
# ==============================================================================
elif app_mode == "🏷️ Barcode Generator":
    st.subheader("🏷️ Barcode Generator & Printing")
    bc_input = st.text_input("Enter Text or Item Code for Barcode", "SAPPHIRE-001")
    if bc_input:
        st.code(f"| |||| ||||| || ||| | -> {bc_input}")
        st.success("Ready for label printing simulation.")

# ==============================================================================
# MODULE 6: SALES REPORTS
# ==============================================================================
elif app_mode == "📊 Sales Reports":
    st.subheader("📊 Sales History & Reports")
    if not df_sales.empty:
        st.dataframe(df_sales, use_container_width=True)
        tot_rev = df_sales["Total"].sum()
        st.metric("Total Gross Revenue", f"Rs. {tot_rev:,.2f}")
    else:
        st.info("No sales recorded yet.")
