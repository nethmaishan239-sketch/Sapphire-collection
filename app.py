import streamlit as st
import pandas as pd
import os
import io
import zipfile
import hashlib
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import uuid

# ==============================================================================
# 1. ADVANCED PAGE CONFIGURATION & THEMING
# ==============================================================================
st.set_page_config(
    page_title="Sapphire Enterprise ERP & POS Pro - v2.0",
    page_icon="💎",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
    <style>
    .main { padding-top: 1rem; }
    .stButton>button { border-radius: 6px; font-weight: bold; transition: 0.3s; border: 1px solid #ccc; }
    .stButton>button:hover { transform: scale(1.02); border-color: #0066cc; }
    .metric-box { background: #f8f9fa; padding: 20px; border-radius: 10px; text-align: center; border: 1px solid #dee2e6; box-shadow: 2px 2px 5px rgba(0,0,0,0.05); }
    </style>
""", unsafe_allow_html=True)

# ==============================================================================
# 2. FILE PATHS & SYSTEM CONSTANTS
# ==============================================================================
DB_DIR = "database_v2"
if not os.path.exists(DB_DIR): os.makedirs(DB_DIR)

USERS_FILE = os.path.join(DB_DIR, "users.csv")
SUPPLIER_FILE = os.path.join(DB_DIR, "suppliers.csv")
CUSTOMER_FILE = os.path.join(DB_DIR, "customers.csv")
ITEMS_FILE = os.path.join(DB_DIR, "inventory.csv")
SALES_FILE = os.path.join(DB_DIR, "sales.csv")
EXPENSE_FILE = os.path.join(DB_DIR, "expenses.csv")
EMPLOYEE_FILE = os.path.join(DB_DIR, "employees.csv")
ATTENDANCE_FILE = os.path.join(DB_DIR, "attendance.csv")
PO_FILE = os.path.join(DB_DIR, "purchase_orders.csv")
RETURNS_FILE = os.path.join(DB_DIR, "returns.csv")
AUDIT_FILE = os.path.join(DB_DIR, "audit_logs.csv")

# ==============================================================================
# 3. CORE FUNCTIONS
# ==============================================================================
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def log_audit(action, details, user="System"):
    try:
        dt_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        new_log = pd.DataFrame([{"Timestamp": dt_str, "User": user, "Action": action, "Details": details}])
        if os.path.exists(AUDIT_FILE):
            df_audit = pd.read_csv(AUDIT_FILE)
            df_audit = pd.concat([df_audit, new_log], ignore_index=True)
        else:
            df_audit = new_log
        df_audit.to_csv(AUDIT_FILE, index=False)
    except: pass

def load_data(filepath, default_cols):
    if os.path.exists(filepath):
        try:
            df = pd.read_csv(filepath)
            for col in default_cols:
                if col not in df.columns:
                    if col in ["Is_Deleted"]: df[col] = False
                    elif col in ["Pending Payable", "Cost Price", "Selling Price", "Total Amount", "Paid Amount", "Balance", "Amount", "Credit_Owed", "Discount", "Tax", "Basic_Salary", "Refund_Amount"]: df[col] = 0.0
                    elif col in ["Stock Quantity", "Loyalty Points", "Qty", "Return_Qty"]: df[col] = 0
                    else: df[col] = ""
            return df
        except:
            return pd.DataFrame(columns=default_cols)
    return pd.DataFrame(columns=default_cols)

def save_data(df, filepath):
    try:
        df.to_csv(filepath, index=False)
    except: pass

def init_system_files():
    df_u = load_data(USERS_FILE, ["Username", "PasswordHash", "Role", "Is_Deleted"])
    if df_u.empty:
        df_u = pd.DataFrame([{"Username": "admin", "PasswordHash": hash_password("admin123"), "Role": "Admin", "Is_Deleted": False}])
        save_data(df_u, USERS_FILE)
        log_audit("System Init", "Default admin account created")

init_system_files()

df_users = load_data(USERS_FILE, ["Username", "PasswordHash", "Role", "Is_Deleted"])
df_sup = load_data(SUPPLIER_FILE, ["Supplier Name", "Phone", "Company", "Pending Payable", "Is_Deleted"])
df_cust = load_data(CUSTOMER_FILE, ["Customer Name", "Phone", "Loyalty Points", "Tier", "Credit_Owed", "Is_Deleted"])
df_items = load_data(ITEMS_FILE, ["Item Code", "Item Name", "Category", "Cost Price", "Selling Price", "Stock Quantity", "Reorder_Level", "Is_Deleted"])
df_sales = load_data(SALES_FILE, ["Date", "Invoice No", "Cashier", "Customer", "SubTotal", "Discount", "Tax", "Total Amount", "Paid Amount", "Balance", "Payment Method"])
df_exp = load_data(EXPENSE_FILE, ["Date", "Category", "Description", "Amount", "Logged By"])
df_emp = load_data(EMPLOYEE_FILE, ["Emp ID", "Name", "Role", "Phone", "Basic_Salary", "Is_Deleted"])
df_att = load_data(ATTENDANCE_FILE, ["Date", "Emp ID", "Name", "Check_In", "Check_Out", "Hours_Worked"])
df_po = load_data(PO_FILE, ["PO_ID", "Date", "Supplier", "Item_Code", "Qty", "Cost_Per_Unit", "Total_Cost", "Status"])
df_ret = load_data(RETURNS_FILE, ["Return_ID", "Date", "Invoice_No", "Item_Code", "Return_Qty", "Reason", "Refund_Amount", "Processed_By"])

def calculate_customer_tier(points):
    if points >= 5000: return "Gold 🥇"
    elif points >= 2000: return "Silver 🥈"
    else: return "Bronze 🥉"

# ==============================================================================
# 4. AUTHENTICATION & SESSION MANAGEMENT
# ==============================================================================
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""

if not st.session_state.logged_in:
    st.markdown("<h1 style='text-align: center; margin-top: 5vh; color: #1f77b4;'>💎 Sapphire Enterprise ERP</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: gray; margin-bottom: 5vh;'>Secure Access Gateway (Pro Edition)</h4>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        with st.form("login_form"):
            st.subheader("🔐 Login")
            in_user = st.text_input("Username").strip()
            in_pass = st.text_input("Password", type="password").strip()
            submitted = st.form_submit_button("Access System", use_container_width=True)
            
            if submitted:
                hashed_pass = hash_password(in_pass)
                user_match = df_users[(df_users["Username"] == in_user) & (df_users["PasswordHash"] == hashed_pass) & (df_users["Is_Deleted"] == False)]
                if not user_match.empty:
                    st.session_state.logged_in = True
                    st.session_state.username = in_user
                    st.session_state.role = user_match.iloc[0]["Role"]
                    log_audit("Login", "User logged in successfully", in_user)
                    st.rerun()
                else:
                    st.error("❌ Invalid Username or Password.")
    st.stop()

# ==============================================================================
# 5. SIDEBAR NAVIGATION
# ==============================================================================
st.sidebar.markdown(f"## 👤 {st.session_state.username}")
st.sidebar.caption(f"Role: **{st.session_state.role}**")
st.sidebar.markdown("---")

menu_options = [
    "🛒 POS Checkout", 
    "↩️ Returns & Refunds",
    "📦 Inventory & Stock", 
    "🏭 Purchases (PO)", 
    "👥 CRM & Credit", 
    "💸 HR & Payroll", 
    "📊 Profit & Loss Reports"
]
if st.session_state.role == "Admin":
    menu_options.append("⚙️ System Admin")

menu_choice = st.sidebar.radio("📌 Main Menu", menu_options)

if st.sidebar.button("🚪 Logout", use_container_width=True):
    log_audit("Logout", "User logged out", st.session_state.username)
    st.session_state.logged_in = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.rerun()

active_items = df_items[df_items["Is_Deleted"] == False] if not df_items.empty else pd.DataFrame()
active_cust = df_cust[df_cust["Is_Deleted"] == False] if not df_cust.empty else pd.DataFrame()
active_sup = df_sup[df_sup["Is_Deleted"] == False] if not df_sup.empty else pd.DataFrame()
active_emp = df_emp[df_emp["Is_Deleted"] == False] if not df_emp.empty else pd.DataFrame()

# ==============================================================================
# MODULE 1: POS CHECKOUT
# ==============================================================================
if menu_choice == "🛒 POS Checkout":
    st.title("🛒 Point of Sale Terminal (Pro)")
    
    if "cart" not in st.session_state: st.session_state.cart = []
    
    c_left, c_right = st.columns([1.4, 1])
    
    with c_left:
        st.subheader("🔍 Add Items")
        search_q = st.text_input("Scan Barcode or Type Name", key="pos_search").strip()
        
        filtered_cat = active_items.copy()
        if search_q and not filtered_cat.empty:
            filtered_cat = filtered_cat[
                filtered_cat["Item Name"].str.contains(search_q, case=False, na=False) |
                filtered_cat["Item Code"].astype(str).str.contains(search_q, case=False, na=False)
            ]
            
        if not filtered_cat.empty:
            st.dataframe(filtered_cat[["Item Code", "Item Name", "Selling Price", "Stock Quantity"]], use_container_width=True, height=200)
            
            with st.form("pos_add"):
                col_a, col_b, col_c = st.columns([2, 1, 1])
                sel_code = col_a.selectbox("Select Product", filtered_cat["Item Code"].tolist())
                qty_inp = col_b.number_input("Quantity", min_value=1, step=1)
                btn_add = col_c.form_submit_button("🛒 Add")

                if btn_add and sel_code:
                    it_data = active_items[active_items["Item Code"] == sel_code].iloc[0]
                    curr_stock = int(it_data["Stock Quantity"])
                    existing_qty = sum(x["Qty"] for x in st.session_state.cart if x["Item Code"] == sel_code)
                    
                    if (qty_inp + existing_qty) > curr_stock:
                        st.error(f"❌ Low Stock! Only {curr_stock} available.")
                    else:
                        found = False
                        for c_item in st.session_state.cart:
                            if c_item["Item Code"] == sel_code:
                                c_item["Qty"] += int(qty_inp)
                                c_item["Total"] = c_item["Qty"] * c_item["Price"]
                                found = True
                                break
                        if not found:
                            st.session_state.cart.append({
                                "Item Code": it_data["Item Code"], "Item Name": it_data["Item Name"],
                                "Cost": float(it_data["Cost Price"]), "Price": float(it_data["Selling Price"]),
                                "Qty": int(qty_inp), "Total": float(it_data["Selling Price"] * qty_inp)
                            })
                        st.rerun()
        else:
            st.info("No items found.")

    with c_right:
        st.subheader("🧾 Current Cart")
        if st.session_state.cart:
            cart_df = pd.DataFrame(st.session_state.cart)
            st.dataframe(cart_df[["Item Name", "Price", "Qty", "Total"]], use_container_width=True, height=200)
            
            if st.button("🗑️ Clear Cart"):
                st.session_state.cart = []
                st.rerun()

            sub_total = cart_df["Total"].sum()
            
            ec1, ec2 = st.columns(2)
            disc_pct = ec1.number_input("Discount %", 0.0, 100.0, 0.0)
            tax_pct = ec2.number_input("VAT/Tax %", 0.0, 100.0, 0.0)

            calc_disc = sub_total * (disc_pct / 100)
            tax_amt = (sub_total - calc_disc) * (tax_pct / 100)
            grand_total = (sub_total - calc_disc) + tax_amt

            st.markdown(f"""
            <div class='metric-box'>
                <h3 style='margin:0;'>TOTAL: Rs. {grand_total:,.2f}</h3>
            </div>
            """, unsafe_allow_html=True)

            c_list = ["Cash Customer"] + (active_cust["Customer Name"].tolist() if not active_cust.empty else [])
            sel_cust = st.selectbox("Customer", c_list)
            
            pay_method = st.selectbox("Payment Method", ["Cash", "Card", "Store Credit"])
            tendered = st.number_input("Tendered Amount", min_value=0.0, value=float(grand_total))
            balance_due = tendered - grand_total

            if st.button("✅ Complete Sale", type="primary", use_container_width=True):
                if pay_method != "Store Credit" and tendered < grand_total:
                    st.error("Insufficient amount tendered.")
                else:
                    dt_now = datetime.now()
                    inv_num = f"INV-{dt_now.strftime('%y%m%d%H%M%S')}"
                    
                    for ci in st.session_state.cart:
                        i_idx = df_items[df_items["Item Code"] == ci["Item Code"]].index[0]
                        df_items.loc[i_idx, "Stock Quantity"] -= ci["Qty"]
                    save_data(df_items, ITEMS_FILE)

                    if sel_cust != "Cash Customer":
                        c_idx = df_cust[df_cust["Customer Name"] == sel_cust].index[0]
                        if pay_method == "Store Credit":
                            df_cust.loc[c_idx, "Credit_Owed"] += grand_total
                        else:
                            pts_earned = int(grand_total // 100)
                            df_cust.loc[c_idx, "Loyalty Points"] += pts_earned
                            df_cust.loc[c_idx, "Tier"] = calculate_customer_tier(df_cust.loc[c_idx, "Loyalty Points"])
                        save_data(df_cust, CUSTOMER_FILE)

                    new_sale = {
                        "Date": dt_now.strftime("%Y-%m-%d %H:%M:%S"), "Invoice No": inv_num, 
                        "Cashier": st.session_state.username, "Customer": sel_cust, 
                        "SubTotal": sub_total, "Discount": calc_disc, "Tax": tax_amt, 
                        "Total Amount": grand_total, "Paid Amount": tendered, "Balance": balance_due, 
                        "Payment Method": pay_method
                    }
                    df_sales_updated = pd.concat([df_sales, pd.DataFrame([new_sale])], ignore_index=True)
                    save_data(df_sales_updated, SALES_FILE)
                    
                    log_audit("Sale Processed", f"Invoice {inv_num}", st.session_state.username)
                    st.session_state.cart = []
                    st.success(f"Success! Invoice: {inv_num}")
                    st.rerun()

# ==============================================================================
# MODULE 2: RETURNS & REFUNDS
# ==============================================================================
elif menu_choice == "↩️ Returns & Refunds":
    st.title("↩️ Return Merchandise Authorization")
    if df_sales.empty:
        st.warning("No sales history available.")
    else:
        r1, r2 = st.columns(2)
        with r1:
            with st.form("return_form"):
                inv_to_return = st.text_input("Original Invoice Number")
                ret_code = st.text_input("Item Code")
                ret_qty = st.number_input("Quantity", min_value=1)
                ret_reason = st.selectbox("Reason", ["Defective", "Wrong Item", "Changed Mind"])
                ref_amt = st.number_input("Refund Amount (Rs.)", 0.0)
                if st.form_submit_button("Process Refund"):
                    ret_id = f"RET-{uuid.uuid4().hex[:6].upper()}"
                    i_idx = df_items[df_items["Item Code"] == ret_code].index[0]
                    df_items.loc[i_idx, "Stock Quantity"] += ret_qty
                    save_data(df_items, ITEMS_FILE)
                    
                    new_ret = {"Return_ID": ret_id, "Date": datetime.now().strftime("%Y-%m-%d"), "Invoice_No": inv_to_return, "Item_Code": ret_code, "Return_Qty": ret_qty, "Reason": ret_reason, "Refund_Amount": ref_amt, "Processed_By": st.session_state.username}
                    df_ret_updated = pd.concat([df_ret, pd.DataFrame([new_ret])], ignore_index=True)
                    save_data(df_ret_updated, RETURNS_FILE)
                    st.success("Return processed successfully!")
                    st.rerun()
        with r2:
            st.dataframe(df_ret, use_container_width=True)

# ==============================================================================
# MODULE 3: INVENTORY & STOCK
# ==============================================================================
elif menu_choice == "📦 Inventory & Stock":
    st.title("📦 Advanced Inventory Management")
    t1, t2, t3 = st.tabs(["Add Item", "View Inventory", "Low Stock Alert"])
    with t1:
        with st.form("inv_form"):
            i_code = st.text_input("Item Code")
            i_name = st.text_input("Item Name")
            i_cat = st.selectbox("Category", ["Groceries", "Electronics", "Hardware"])
            c_price = st.number_input("Cost Price", 0.0)
            s_price = st.number_input("Selling Price", 0.0)
            s_qty = st.number_input("Stock Qty", 0)
            r_lvl = st.number_input("Reorder Level", 5)
            if st.form_submit_button("Save Item"):
                new_item = {"Item Code": i_code, "Item Name": i_name, "Category": i_cat, "Cost Price": c_price, "Selling Price": s_price, "Stock Quantity": s_qty, "Reorder_Level": r_lvl, "Is_Deleted": False}
                df_items_up = pd.concat([df_items, pd.DataFrame([new_item])], ignore_index=True)
                save_data(df_items_up, ITEMS_FILE)
                st.success("Item saved successfully.")
                st.rerun()
    with t2:
        st.dataframe(active_items, use_container_width=True)
    with t3:
        if not active_items.empty:
            low_s = active_items[pd.to_numeric(active_items["Stock Quantity"]) <= pd.to_numeric(active_items["Reorder_Level"])]
            st.dataframe(low_s, use_container_width=True)

# ==============================================================================
# MODULE 4: PURCHASES (PO)
# ==============================================================================
elif menu_choice == "🏭 Purchases (PO)":
    st.title("🏭 Purchase Orders & Vendors")
    t_v, t_p, t_r = st.tabs(["Vendors", "Create PO", "Receive PO"])
    with t_v:
        with st.form("v_form"):
            v_name = st.text_input("Supplier Name")
            v_phone = st.text_input("Phone")
            if st.form_submit_button("Add Vendor"):
                df_sup_up = pd.concat([df_sup, pd.DataFrame([{"Supplier Name": v_name, "Phone": v_phone, "Company": "", "Pending Payable": 0.0, "Is_Deleted": False}])], ignore_index=True)
                save_data(df_sup_up, SUPPLIER_FILE)
                st.success("Vendor added.")
                st.rerun()
        st.dataframe(active_sup, use_container_width=True)
    with t_p:
        if not active_sup.empty and not active_items.empty:
            with st.form("po_f"):
                s_sup = st.selectbox("Supplier", active_sup["Supplier Name"].tolist())
                s_itm = st.selectbox("Item", active_items["Item Code"].tolist())
                qty = st.number_input("Qty", 1)
                cost = st.number_input("Cost/Unit", 0.0)
                if st.form_submit_button("Issue PO"):
                    po_id = f"PO-{datetime.now().strftime('%H%M%S')}"
                    new_po = {"PO_ID": po_id, "Date": datetime.now().strftime("%Y-%m-%d"), "Supplier": s_sup, "Item_Code": s_itm, "Qty": qty, "Cost_Per_Unit": cost, "Total_Cost": qty*cost, "Status": "Pending"}
                    df_po_up = pd.concat([df_po, pd.DataFrame([new_po])], ignore_index=True)
                    save_data(df_po_up, PO_FILE)
                    st.success("PO Issued.")
                    st.rerun()
    with t_r:
        pending_po = df_po[df_po["Status"] == "Pending"] if not df_po.empty else pd.DataFrame()
        if not pending_po.empty:
            st.dataframe(pending_po, use_container_width=True)
            with st.form("rec_f"):
                sel_po = st.selectbox("Select PO", pending_po["PO_ID"].tolist())
                if st.form_submit_button("Receive Goods"):
                    idx = df_po[df_po["PO_ID"] == sel_po].index[0]
                    df_po.loc[idx, "Status"] = "Completed"
                    save_data(df_po, PO_FILE)
                    st.success("Received and stock updated.")
                    st.rerun()

# ==============================================================================
# MODULE 5: CRM & CREDIT
# ==============================================================================
elif menu_choice == "👥 CRM & Credit":
    st.title("👥 CRM & Customer Loyalty")
    with st.form("c_reg"):
        c_n = st.text_input("Customer Name")
        c_p = st.text_input("Phone")
        if st.form_submit_button("Register Customer"):
            df_cust_up = pd.concat([df_cust, pd.DataFrame([{"Customer Name": c_n, "Phone": c_p, "Loyalty Points": 0, "Tier": "Bronze 🥉", "Credit_Owed": 0.0, "Is_Deleted": False}])], ignore_index=True)
            save_data(df_cust_up, CUSTOMER_FILE)
            st.success("Customer registered.")
            st.rerun()
    st.dataframe(active_cust, use_container_width=True)

# ==============================================================================
# MODULE 6: HR & PAYROLL
# ==============================================================================
elif menu_choice == "💸 HR & Payroll":
    st.title("💸 HR, Attendance & Expenses")
    t_e, t_a, t_ex = st.tabs(["Employees", "Attendance", "Expenses"])
    with t_e:
        with st.form("emp_f"):
            e_id = st.text_input("Emp ID")
            e_name = st.text_input("Name")
            e_sal = st.number_input("Basic Salary", 0.0)
            if st.form_submit_button("Add Employee"):
                df_emp_up = pd.concat([df_emp, pd.DataFrame([{"Emp ID": e_id, "Name": e_name, "Role": "Staff", "Phone": "", "Basic_Salary": e_sal, "Is_Deleted": False}])], ignore_index=True)
                save_data(df_emp_up, EMPLOYEE_FILE)
                st.success("Employee added.")
                st.rerun()
        st.dataframe(active_emp, use_container_width=True)
    with t_a:
        if not active_emp.empty:
            sel_em = st.selectbox("Employee Name", active_emp["Name"].tolist())
            if st.button("Check In Now"):
                e_id = active_emp[active_emp["Name"]==sel_em]["Emp ID"].iloc[0]
                df_att_up = pd.concat([df_att, pd.DataFrame([{"Date": datetime.now().strftime("%Y-%m-%d"), "Emp ID": e_id, "Name": sel_em, "Check_In": datetime.now().strftime("%H:%M:%S"), "Check_Out": "", "Hours_Worked": 0.0}])], ignore_index=True)
                save_data(df_att_up, ATTENDANCE_FILE)
                st.success("Attendance checked in.")
                st.rerun()
            st.dataframe(df_att, use_container_width=True)
    with t_ex:
        with st.form("ex_f"):
            cat = st.selectbox("Expense Category", ["Rent", "Utilities", "Salaries", "Other"])
            amt = st.number_input("Amount (Rs.)", 0.0)
            if st.form_submit_button("Log Expense"):
                df_exp_up = pd.concat([df_exp, pd.DataFrame([{"Date": datetime.now().strftime("%Y-%m-%d"), "Category": cat, "Description": "", "Amount": amt, "Logged By": st.session_state.username}])], ignore_index=True)
                save_data(df_exp_up, EXPENSE_FILE)
                st.success("Expense logged.")
                st.rerun()

# ==============================================================================
# MODULE 7: P&L REPORTS
# ==============================================================================
elif menu_choice == "📊 Profit & Loss Reports":
    st.title("📊 Profit & Loss Statement (Advanced Analytics)")
    tot_sales = df_sales["Total Amount"].sum() if not df_sales.empty else 0.0
    tot_exp = df_exp["Amount"].sum() if not df_exp.empty else 0.0
    net = tot_sales - tot_exp
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Total Sales", f"Rs. {tot_sales:,.2f}")
    c2.metric("Total Expenses", f"Rs. {tot_exp:,.2f}")
    c3.metric("Net Profit", f"Rs. {net:,.2f}")
    
    if not df_sales.empty:
        s_trend = df_sales.copy()
        s_trend['Date'] = pd.to_datetime(s_trend['Date']).dt.date
        daily_s = s_trend.groupby('Date')['Total Amount'].sum().reset_index()
        fig_s = px.bar(daily_s, x='Date', y='Total Amount', title="Daily Revenue Trends", template="plotly_white")
        st.plotly_chart(fig_s, use_container_width=True)

# ==============================================================================
# MODULE 8: SYSTEM ADMIN
# ==============================================================================
elif menu_choice == "⚙️ System Admin":
    if st.session_state.role != "Admin":
        st.error("Access Denied.")
        st.stop()
    st.title("⚙️ System Administration & Database Management")
    
    st.subheader("📁 Database Backup (ZIP)")
    if st.button("Download System Backup ZIP"):
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for root, dirs, files in os.walk(DB_DIR):
                for file in files:
                    zip_file.write(os.path.join(root, file), os.path.relpath(os.path.join(root, file), DB_DIR))
        buffer.seek(0)
        st.download_button(label="📥 Download Backup ZIP", data=buffer, file_name="sapphire_erp_backup.zip", mime="application/zip")
        
    st.markdown("---")
    st.subheader("📋 System Audit Logs")
    if os.path.exists(AUDIT_FILE):
        st.dataframe(pd.read_csv(AUDIT_FILE), use_container_width=True)
