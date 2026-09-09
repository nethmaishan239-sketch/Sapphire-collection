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
    .receipt-container { background: #fff; color: #000; padding: 25px; font-family: 'Courier New', monospace; border: 1px dashed #333; max-width: 400px; margin: auto; }
    .status-badge { padding: 4px 8px; border-radius: 4px; font-size: 12px; font-weight: bold; }
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
# 3. CORE FUNCTIONS (SECURITY, I/O, AUDIT)
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
        except Exception as e:
            st.error(f"DB Load Error [{filepath}]: {e}")
            return pd.DataFrame(columns=default_cols)
    return pd.DataFrame(columns=default_cols)

def save_data(df, filepath):
    try:
        df.to_csv(filepath, index=False)
    except Exception as e:
        st.error(f"DB Write Error [{filepath}]: {e}")

def init_system_files():
    df_u = load_data(USERS_FILE, ["Username", "PasswordHash", "Role", "Is_Deleted"])
    if df_u.empty:
        df_u = pd.DataFrame([{"Username": "admin", "PasswordHash": hash_password("admin123"), "Role": "Admin", "Is_Deleted": False}])
        save_data(df_u, USERS_FILE)
        log_audit("System Init", "Default admin account created")

init_system_files()

# Load Master Tables
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
    st.markdown("<h4 style='text-align: center; color: gray; margin-bottom: 5vh;'>Secure Access Gateway</h4>", unsafe_allow_html=True)
    
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
                    log_audit("Login", f"User logged in successfully", in_user)
                    st.rerun()
                else:
                    st.error("❌ Invalid Username or Password. Please try again.")
                    log_audit("Failed Login", f"Attempted username: {in_user}", "System")
    st.stop()

# ==============================================================================
# 5. SIDEBAR NAVIGATION
# ==============================================================================
st.sidebar.markdown(f"## 👤 {st.session_state.username}")
st.sidebar.caption(f"Role: **{st.session_state.role}** | Status: **Online**")
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

# Active Records DataFrames
active_items = df_items[df_items["Is_Deleted"] == False] if not df_items.empty else pd.DataFrame()
active_cust = df_cust[df_cust["Is_Deleted"] == False] if not df_cust.empty else pd.DataFrame()
active_sup = df_sup[df_sup["Is_Deleted"] == False] if not df_sup.empty else pd.DataFrame()
active_emp = df_emp[df_emp["Is_Deleted"] == False] if not df_emp.empty else pd.DataFrame()

# ==============================================================================
# MODULE 1: POS CHECKOUT
# ==============================================================================
if menu_choice == "🛒 POS Checkout":
    st.title("🛒 Point of Sale Terminal")
    
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
            st.info("No items found or Inventory is empty.")

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
                <small>Sub: {sub_total:,.2f} | Disc: -{calc_disc:,.2f} | Tax: +{tax_amt:,.2f}</small>
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
                elif pay_method == "Store Credit" and sel_cust == "Cash Customer":
                    st.error("Store credit requires a registered Customer.")
                else:
                    dt_now = datetime.now()
                    inv_num = f"INV-{dt_now.strftime('%y%m%d%H%M%S')}"
                    
                    # Update Inventory
                    for ci in st.session_state.cart:
                        i_idx = df_items[df_items["Item Code"] == ci["Item Code"]].index[0]
                        df_items.loc[i_idx, "Stock Quantity"] -= ci["Qty"]
                    save_data(df_items, ITEMS_FILE)

                    # Update Customer
                    if sel_cust != "Cash Customer":
                        c_idx = df_cust[df_cust["Customer Name"] == sel_cust].index[0]
                        if pay_method == "Store Credit":
                            df_cust.loc[c_idx, "Credit_Owed"] += grand_total
                            tendered, balance_due = 0.0, 0.0
                        else:
                            pts_earned = int(grand_total // 100)
                            df_cust.loc[c_idx, "Loyalty Points"] += pts_earned
                            df_cust.loc[c_idx, "Tier"] = calculate_customer_tier(df_cust.loc[c_idx, "Loyalty Points"])
                        save_data(df_cust, CUSTOMER_FILE)

                    # Record Sale
                    new_sale = {
                        "Date": dt_now.strftime("%Y-%m-%d %H:%M:%S"), "Invoice No": inv_num, 
                        "Cashier": st.session_state.username, "Customer": sel_cust, 
                        "SubTotal": sub_total, "Discount": calc_disc, "Tax": tax_amt, 
                        "Total Amount": grand_total, "Paid Amount": tendered, "Balance": balance_due, 
                        "Payment Method": pay_method
                    }
                    global df_sales
                    df_sales = pd.concat([df_sales, pd.DataFrame([new_sale])], ignore_index=True)
                    save_data(df_sales, SALES_FILE)
                    
                    log_audit("Sale Processed", f"Invoice {inv_num} generated for {grand_total}", st.session_state.username)
                    
                    st.session_state.cart = []
                    st.success(f"Transaction Successful! Invoice: {inv_num} | Balance: Rs. {balance_due:,.2f}")
                    st.rerun()

# ==============================================================================
# MODULE 2: RETURNS & REFUNDS
# ==============================================================================
elif menu_choice == "↩️ Returns & Refunds":
    global df_ret, df_exp
    st.title("↩️ Return Merchandise Authorization (RMA)")
    st.write("Process customer returns, update inventory, and issue refunds.")
    
    if df_sales.empty:
        st.warning("No sales history available to process returns.")
    else:
        r1, r2 = st.columns([1, 1])
        with r1:
            st.subheader("Process a Return")
            with st.form("return_form"):
                inv_to_return = st.text_input("Original Invoice Number (e.g., INV-2310...)")
                ret_code = st.text_input("Item Code being returned")
                ret_qty = st.number_input("Quantity to Return", min_value=1)
                ret_reason = st.selectbox("Reason", ["Defective", "Wrong Item", "Customer Changed Mind", "Other"])
                ref_amt = st.number_input("Refund Amount (Rs.)", min_value=0.0)
                
                if st.form_submit_button("Process Refund & Restock"):
                    inv_match = df_sales[df_sales["Invoice No"] == inv_to_return]
                    if inv_match.empty:
                        st.error("Invoice not found in system.")
                    else:
                        item_match = active_items[active_items["Item Code"] == ret_code]
                        if item_match.empty:
                            st.error("Item code not recognized.")
                        else:
                            ret_id = f"RET-{uuid.uuid4().hex[:6].upper()}"
                            i_idx = df_items[df_items["Item Code"] == ret_code].index[0]
                            df_items.loc[i_idx, "Stock Quantity"] += ret_qty
                            save_data(df_items, ITEMS_FILE)
                            
                            new_ret = {
                                "Return_ID": ret_id, "Date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                                "Invoice_No": inv_to_return, "Item_Code": ret_code, "Return_Qty": ret_qty,
                                "Reason": ret_reason, "Refund_Amount": ref_amt, "Processed_By": st.session_state.username
                            }
                            df_ret = pd.concat([df_ret, pd.DataFrame([new_ret])], ignore_index=True)
                            save_data(df_ret, RETURNS_FILE)
                            
                            if ref_amt > 0:
                                exp_row = {"Date": datetime.now().strftime("%Y-%m-%d"), "Category": "Refunds", "Description": f"Refund for {ret_id}", "Amount": ref_amt, "Logged By": st.session_state.username}
                                df_exp = pd.concat([df_exp, pd.DataFrame([exp_row])], ignore_index=True)
                                save_data(df_exp, EXPENSE_FILE)
                            
                            log_audit("Return Processed", f"Return {ret_id} for Inv {inv_to_return}", st.session_state.username)
                            st.success(f"Return processed successfully. Stock updated and Refund logged.")
                            st.rerun()

        with r2:
            st.subheader("Recent Returns Log")
            st.dataframe(df_ret, use_container_width=True)

# ==============================================================================
# MODULE 3: INVENTORY & STOCK
# ==============================================================================
elif menu_choice == "📦 Inventory & Stock":
    global df_items
    st.title("📦 Master Inventory Management")
    
    t_add, t_view, t_alerts = st.tabs(["Add / Edit Items", "Inventory Database", "Low Stock Alerts"])
    
    with t_add:
        st.subheader("Product Registration Form")
        with st.form("inv_form"):
            col1, col2 = st.columns(2)
            i_code = col1.text_input("Item Code / SKU *").strip()
            i_name = col2.text_input("Item Name *").strip()
            i_cat = col1.selectbox("Category", ["Groceries", "Electronics", "Hardware", "Pharmacy", "Clothing", "Other"])
            c_price = col1.number_input("Cost Price (Rs.)", 0.0)
            s_price = col2.number_input("Selling Price (Rs.)", 0.0)
            s_qty = col1.number_input("Current Stock Qty", 0)
            r_lvl = col2.number_input("Reorder Alert Level", 5)
            
            if st.form_submit_button("Save Product"):
                if i_code and i_name:
                    if not df_items.empty and i_code in df_items["Item Code"].astype(str).values:
                        idx = df_items[df_items["Item Code"].astype(str) == i_code].index[0]
                        df_items.loc[idx, ["Item Name", "Category", "Cost Price", "Selling Price", "Stock Quantity", "Reorder_Level"]] = [i_name, i_cat, c_price, s_price, s_qty, r_lvl]
                        log_audit("Item Updated", f"Code: {i_code}", st.session_state.username)
                        st.success("Item updated.")
                    else:
                        new_item = {"Item Code": i_code, "Item Name": i_name, "Category": i_cat, "Cost Price": c_price, "Selling Price": s_price, "Stock Quantity": s_qty, "Reorder_Level": r_lvl, "Is_Deleted": False}
                        df_items = pd.concat([df_items, pd.DataFrame([new_item])], ignore_index=True)
                        log_audit("Item Created", f"Code: {i_code}", st.session_state.username)
                        st.success("Item created.")
                    save_data(df_items, ITEMS_FILE)
                    st.rerun()
                else:
                    st.error("Code and Name are required.")

    with t_view:
        st.subheader("Complete Inventory Directory")
        if not active_items.empty:
            st.dataframe(active_items.drop(columns=["Is_Deleted"]), use_container_width=True)
            
            with st.expander("Remove an Item (Soft Delete)"):
                d_item = st.selectbox("Select item to remove", active_items["Item Code"].astype(str) + " - " + active_items["Item Name"])
                if st.button("Delete Selected"):
                    target_code = d_item.split(" - ")[0]
                    idx = df_items[df_items["Item Code"].astype(str) == target_code].index[0]
                    df_items.loc[idx, "Is_Deleted"] = True
                    save_data(df_items, ITEMS_FILE)
                    log_audit("Item Deleted", f"Code: {target_code}", st.session_state.username)
                    st.success("Item removed from active list.")
                    st.rerun()

    with t_alerts:
        st.subheader("⚠️ Stock Replenishment Alerts")
        if not active_items.empty:
            low_stock = active_items[pd.to_numeric(active_items["Stock Quantity"]) <= pd.to_numeric(active_items["Reorder_Level"])]
            if not low_stock.empty:
                st.error(f"Critical! {len(low_stock)} items need immediate reordering.")
                st.dataframe(low_stock[["Item Code", "Item Name", "Stock Quantity", "Reorder_Level"]], use_container_width=True)
            else:
                st.success("All inventory levels are healthy. No immediate reorders needed.")

# ==============================================================================
# MODULE 4: PURCHASES & PO SYSTEM
# ==============================================================================
elif menu_choice == "🏭 Purchases (PO)":
    global df_sup, df_po
    st.title("🏭 Purchase Orders & Vendors")
    
    t_ven, t_po_tab, t_recv = st.tabs(["Manage Vendors", "Create PO", "Receive Goods & Pay"])
    
    with t_ven:
        v1, v2 = st.columns([1, 1.5])
        with v1:
            st.subheader("Add Vendor")
            with st.form("sup_reg"):
                s_name = st.text_input("Supplier Name *").strip()
                s_comp = st.text_input("Company Name")
                s_phone = st.text_input("Phone Number")
                s_debt = st.number_input("Initial Balance Due (Rs.)", 0.0)
                if st.form_submit_button("Register Vendor"):
                    if s_name:
                        new_sup = {"Supplier Name": s_name, "Phone": s_phone, "Company": s_comp, "Pending Payable": s_debt, "Is_Deleted": False}
                        df_sup = pd.concat([df_sup, pd.DataFrame([new_sup])], ignore_index=True)
                        save_data(df_sup, SUPPLIER_FILE)
                        st.success("Vendor added.")
                        st.rerun()
        with v2:
            st.subheader("Vendor Directory")
            st.dataframe(active_sup, use_container_width=True)

    with t_po_tab:
        st.subheader("Generate Purchase Order")
        if not active_sup.empty and not active_items.empty:
            with st.form("po_form"):
                sel_sup = st.selectbox("Select Supplier", active_sup["Supplier Name"].tolist())
                sel_item = st.selectbox("Select Item to Order", active_items["Item Code"].astype(str) + " - " + active_items["Item Name"])
                ord_qty = st.number_input("Order Quantity", min_value=1)
                cost_est = st.number_input("Estimated Cost Per Unit", 0.0)
                
                if st.form_submit_button("Issue Purchase Order"):
                    po_id = f"PO-{datetime.now().strftime('%Y%m%d%H%M%S')}"
                    t_cost = ord_qty * cost_est
                    i_code = sel_item.split(" - ")[0]
                    
                    new_po = {
                        "PO_ID": po_id, "Date": datetime.now().strftime("%Y-%m-%d"), 
                        "Supplier": sel_sup, "Item_Code": i_code, "Qty": ord_qty, 
                        "Cost_Per_Unit": cost_est, "Total_Cost": t_cost, "Status": "Pending"
                    }
                    df_po = pd.concat([df_po, pd.DataFrame([new_po])], ignore_index=True)
                    save_data(df_po, PO_FILE)
                    log_audit("PO Created", f"PO: {po_id} for {sel_sup}", st.session_state.username)
                    st.success(f"Purchase Order {po_id} generated.")
                    st.rerun()
        else:
            st.warning("Ensure you have at least one vendor and one item registered.")

    with t_recv:
        st.subheader("Receive PO & Settle Accounts")
        pending_pos = df_po[df_po["Status"] == "Pending"] if not df_po.empty else pd.DataFrame()
        
        if not pending_pos.empty:
            st.dataframe(pending_pos, use_container_width=True)
            with st.form("recv_form"):
                po_to_recv = st.selectbox("Select PO to Receive", pending_pos["PO_ID"].tolist())
                pay_now = st.number_input("Amount Paying Now to Vendor (Rs.)", 0.0)
                
                if st.form_submit_button("Mark as Received & Update System"):
                    po_data = pending_pos[pending_pos["PO_ID"] == po_to_recv].iloc[0]
                    
                    po_idx = df_po[df_po["PO_ID"] == po_to_recv].index[0]
                    df_po.loc[po_idx, "Status"] = "Completed"
                    save_data(df_po, PO_FILE)
                    
                    itm_code = po_data["Item_Code"]
                    itm_idx = df_items[df_items["Item Code"].astype(str) == str(itm_code)].index[0]
                    df_items.loc[itm_idx, "Stock Quantity"] = int(df_items.loc[itm_idx, "Stock Quantity"]) + int(po_data["Qty"])
                    df_items.loc[itm_idx, "Cost Price"] = float(po_data["Cost_Per_Unit"])
                    save_data(df_items, ITEMS_FILE)
                    
                    sup_name = po_data["Supplier"]
                    sup_idx = df_sup[df_sup["Supplier Name"] == sup_name].index[0]
                    total_po_cost = float(po_data["Total_Cost"])
                    
                    df_sup.loc[sup_idx, "Pending Payable"] += (total_po_cost - pay_now)
                    save_data(df_sup, SUPPLIER_FILE)
                    
                    if pay_now > 0:
                        exp_row = {"Date": datetime.now().strftime("%Y-%m-%d"), "Category": "Inventory Purchase", "Description": f"Payment for {po_to_recv}", "Amount": pay_now, "Logged By": st.session_state.username}
                        df_exp = pd.concat([df_exp, pd.DataFrame([exp_row])], ignore_index=True)
                        save_data(df_exp, EXPENSE_FILE)
                    
                    log_audit("PO Received", f"PO: {po_to_recv} fulfilled", st.session_state.username)
                    st.success("PO Received! Inventory and Accounts updated automatically.")
                    st.rerun()
        else:
            st.info("No pending Purchase Orders.")

# ==============================================================================
# MODULE 5: CRM & CREDIT
# ==============================================================================
elif menu_choice == "👥 CRM & Credit":
    global df_cust
    st.title("👥 Customer Relations & Credit Control")
    
    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("Register Client")
        with st.form("cust_reg"):
            c_name = st.text_input("Customer Name *").strip()
            c_phone = st.text_input("Phone")
            c_pts = st.number_input("Starting Points", 0)
            if st.form_submit_button("Save Customer"):
                if c_name:
                    tier = calculate_customer_tier(c_pts)
                    new_c = {"Customer Name": c_name, "Phone": c_phone, "Loyalty Points": c_pts, "Tier": tier, "Credit_Owed": 0.0, "Is_Deleted": False}
                    df_cust = pd.concat([df_cust, pd.DataFrame([new_c])], ignore_index=True)
                    save_data(df_cust, CUSTOMER_FILE)
                    st.success("Client registered.")
                    st.rerun()
                    
    with c2:
        st.subheader("Credit Settlement")
        if not active_cust.empty:
            debtors = active_cust[active_cust["Credit_Owed"] > 0]
            if not debtors.empty:
                with st.form("credit_form"):
                    sel_d = st.selectbox("Select Debtor", debtors["Customer Name"].tolist())
                    amt_owed = debtors[debtors["Customer Name"] == sel_d]["Credit_Owed"].iloc[0]
                    st.warning(f"Total Due: Rs. {amt_owed:,.2f}")
                    pay_val = st.number_input("Payment Received", 0.0, float(amt_owed))
                    
                    if st.form_submit_button("Record Settlement"):
                        if pay_val > 0:
                            idx = df_cust[df_cust["Customer Name"] == sel_d].index[0]
                            df_cust.loc[idx, "Credit_Owed"] -= pay_val
                            save_data(df_cust, CUSTOMER_FILE)
                            log_audit("Credit Settled", f"Rs. {pay_val} from {sel_d}", st.session_state.username)
                            st.success(f"Recorded Rs. {pay_val} payment.")
                            st.rerun()
            else:
                st.success("No outstanding store credit! 🥳")

    st.markdown("---")
    st.subheader("Customer Directory & Tiers")
    st.dataframe(active_cust[["Customer Name", "Phone", "Tier", "Loyalty Points", "Credit_Owed"]], use_container_width=True)

# ==============================================================================
# MODULE 6: HR, ATTENDANCE & PAYROLL
# ==============================================================================
elif menu_choice == "💸 HR & Payroll":
    global df_emp, df_att
    st.title("💸 Staff Management & Expense Logger")
    
    t_emp, t_att, t_exp = st.tabs(["Employees", "Attendance & Shifts", "General Expenses"])
    
    with t_emp:
        st.subheader("Employee Records")
        with st.form("emp_reg"):
            col_e1, col_e2 = st.columns(2)
            e_id = col_e1.text_input("Emp ID")
            e_name = col_e2.text_input("Name")
            e_role = col_e1.selectbox("Role", ["Cashier", "Manager", "Store Keeper"])
            e_sal = col_e2.number_input("Basic Salary", 0.0)
            if st.form_submit_button("Add Employee") and e_id:
                df_emp = pd.concat([df_emp, pd.DataFrame([{"Emp ID": e_id, "Name": e_name, "Role": e_role, "Phone": "", "Basic_Salary": e_sal, "Is_Deleted": False}])], ignore_index=True)
                save_data(df_emp, EMPLOYEE_FILE)
                st.success("Employee Added.")
                st.rerun()
        st.dataframe(active_emp, use_container_width=True)
        
        with st.form("payroll"):
            st.write("Run Payroll")
            p_emp = st.selectbox("Employee", active_emp["Name"].tolist() if not active_emp.empty else [])
            p_amt = st.number_input("Amount", 0.0)
            if st.form_submit_button("Issue Salary"):
                exp_row = {"Date": datetime.now().strftime("%Y-%m-%d"), "Category": "Staff Salaries", "Description": f"Salary for {p_emp}", "Amount": p_amt, "Logged By": st.session_state.username}
                df_exp = pd.concat([df_exp, pd.DataFrame([exp_row])], ignore_index=True)
                save_data(df_exp, EXPENSE_FILE)
                st.success("Salary disbursed and logged as expense.")

    with t_att:
        st.subheader("Daily Attendance System")
        if not active_emp.empty:
            c_att1, c_att2 = st.columns(2)
            with c_att1:
                st.markdown("**Check In**")
                sel_emp_in = st.selectbox("Select Employee (In)", active_emp["Name"].tolist(), key="att_in")
                if st.button("Mark Check-In"):
                    emp_id = active_emp[active_emp["Name"]==sel_emp_in]["Emp ID"].iloc[0]
                    dt = datetime.now().strftime("%Y-%m-%d")
                    tm = datetime.now().strftime("%H:%M:%S")
                    new_att = {"Date": dt, "Emp ID": emp_id, "Name": sel_emp_in, "Check_In": tm, "Check_Out": "", "Hours_Worked": 0.0}
                    df_att = pd.concat([df_att, pd.DataFrame([new_att])], ignore_index=True)
                    save_data(df_att, ATTENDANCE_FILE)
                    st.success(f"{sel_emp_in} checked in at {tm}")
                    st.rerun()
            with c_att2:
                st.markdown("**Check Out**")
                today = datetime.now().strftime("%Y-%m-%d")
                if not df_att.empty:
                    open_shifts = df_att[(df_att["Date"] == today) & (df_att["Check_Out"] == "")]
                    if not open_shifts.empty:
                        sel_emp_out = st.selectbox("Select Employee (Out)", open_shifts["Name"].tolist())
                        if st.button("Mark Check-Out"):
                            tm_out = datetime.now().strftime("%H:%M:%S")
                            idx = df_att[(df_att["Date"] == today) & (df_att["Name"] == sel_emp_out) & (df_att["Check_Out"] == "")].index[0]
                            df_att.loc[idx, "Check_Out"] = tm_out
                            
                            fmt = "%H:%M:%S"
                            tdelta = datetime.strptime(tm_out, fmt) - datetime.strptime(df_att.loc[idx, "Check_In"], fmt)
                            df_att.loc[idx, "Hours_Worked"] = round(tdelta.seconds / 3600, 2)
                            
                            save_data(df_att, ATTENDANCE_FILE)
                            st.success(f"{sel_emp_out} checked out. Hours: {df_att.loc[idx, 'Hours_Worked']}")
                            st.rerun()
                    else:
                        st.info("No open shifts for today.")
            
            st.write("Recent Attendance Logs")
            st.dataframe(df_att.tail(10), use_container_width=True)

    with t_exp:
        st.subheader("Log General Expense")
        with st.form("exp_form"):
            cat = st.selectbox("Category", ["Utility Bills", "Rent", "Marketing", "Maintenance", "Transport", "Office Supplies", "Other"])
            desc = st.text_input("Memo")
            amt = st.number_input("Amount (Rs.)", 0.0)
            if st.form_submit_button("Log Expense") and amt > 0:
                df_exp = pd.concat([df_exp, pd.DataFrame([{"Date": datetime.now().strftime("%Y-%m-%d"), "Category": cat, "Description": desc, "Amount": amt, "Logged By": st.session_state.username}])], ignore_index=True)
                save_data(df_exp, EXPENSE_FILE)
                st.success("Expense added.")
                st.rerun()
        st.dataframe(df_exp, use_container_width=True)

# ==============================================================================
# MODULE 7: PROFIT & LOSS REPORTS
# ==============================================================================
elif menu_choice == "📊 Profit & Loss Reports":
    st.title("📊 Financial Intelligence & P&L")
    
    if st.session_state.role != "Admin":
        st.warning("⚠️ Restricted Area: Admin access required for full financial statements.")
    else:
        st.subheader("Enterprise Income Statement (P&L)")
        
        tot_sales = df_sales["Total Amount"].sum() if not df_sales.empty else 0.0
        cogs = df_po[df_po["Status"]=="Completed"]["Total_Cost"].sum() if not df_po.empty else 0.0
        gross_profit = tot_sales - cogs
        
        tot_opex = df_exp["Amount"].sum() if not df_exp.empty else 0.0
        net_profit = gross_profit - tot_opex
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Gross Revenue", f"Rs. {tot_sales:,.2f}")
        col2.metric("Total OPEX", f"Rs. {tot_opex:,.2f}")
        col3.metric("Net Profit", f"Rs. {net_profit:,.2f}", delta="Profit" if net_profit > 0 else "Loss", delta_color="normal" if net_profit > 0 else "inverse")
        
        st.markdown("---")
        
        c1, c2 = st.columns(2)
        with c1:
            st.write("**Revenue Trend**")
            if not df_sales.empty:
                s_trend = df_sales.copy()
                s_trend['Date'] = pd.to_datetime(s_trend['Date']).dt.date
                daily_s = s_trend.groupby('Date')['Total Amount'].sum().reset_index()
                fig_s = px.bar(daily_s, x='Date', y='Total Amount', title="Daily Revenue", template="plotly_white")
                st.plotly_chart(fig_s, use_container_width=True)
                
        with c2:
            st.write("**Expense Breakdown**")
            if not df_exp.empty:
                exp_pie = df_exp.groupby('Category')['Amount'].sum().reset_index()
                fig_e = px.pie(exp_pie, values='Amount', names='Category', hole=0.5, template="plotly_white")
                st.plotly_chart(fig_e, use_container_width=True)

# ==============================================================================
# MODULE 8: SYSTEM ADMIN
# ==============================================================================
elif menu_choice == "⚙️ System Admin":
    global df_users
    if st.session_state.role != "Admin":
        st.error("Access Denied.")
        st.stop()
        
    st.title("⚙️ System Configurations & Audit")
    
    t_usr, t_aud, t_db = st.tabs(["User Management", "Security Audit Logs", "Database & Reset"])
    
    with t_usr:
        st.subheader("Manage User Accounts")
        with st.form("new_user"):
            u1, u2, u3 = st.columns(3)
            nu_name = u1.text_input("Username").strip()
            nu_pass = u2.text_input("Password", type="password")
            nu_role = u3.selectbox("Role", ["Cashier", "Manager", "Admin"])
            if st.form_submit_button("Create Account") and nu_name:
                if not df_users[df_users["Username"]==nu_name].empty:
                    st.error("User exists.")
                else:
                    new_u = {"Username": nu_name, "PasswordHash": hash_password(nu_pass), "Role": nu_role, "Is_Deleted": False}
                    df_users = pd.concat([df_users, pd.DataFrame([new_u])], ignore_index=True)
                    save_data(df_users, USERS_FILE)
                    log_audit("User Created", f"Account {nu_name} created", st.session_state.username)
                    st.success("User added.")
                    st.rerun()
        st.dataframe(df_users[["Username", "Role", "Is_Deleted"]], use_container_width=True)

    with t_aud:
        st.subheader("Security & Action Audit Trail")
        if os.path.exists(AUDIT_FILE):
            df_audit_view = pd.read_csv(AUDIT_FILE)
            st.dataframe(df_audit_view.sort_values(by="Timestamp", ascending=False), use_container_width=True, height=400)
        else:
            st.info("No audit logs found.")

    with t_db:
        st.subheader("Database Maintenance")
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            for root, _, files in os.walk(DB_DIR):
                for file in files:
                    file_path = os.path.join(root, file)
                    zip_file.write(file_path, os.path.basename(file_path))
                    
        st.download_button(
            label="📦 Download System Full Backup (.zip)",
            data=zip_buffer.getvalue(),
            file_name=f"Sapphire_Backup_v2_{datetime.now().strftime('%Y%m%d_%H%M')}.zip",
            mime="application/zip",
            type="primary"
        )
        
        st.markdown("---")
        st.warning("⚠️ **FACTORY RESET**")
        if st.checkbox("Unlock Factory Reset"):
            if st.button("🗑️ Erase All Data", type="primary"):
                st.error("System wipe initiated!")
                log_audit("System Wipe", "Admin triggered data wipe", st.session_state.username)
