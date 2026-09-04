import streamlit as st
import pandas as pd
import os
from datetime import datetime, date

# Page Configuration
st.set_page_config(page_title="Sapphire Collection POS", layout="wide")

# File Paths for Data Persistence
PRODUCT_FILE = "products.csv"
SALES_FILE = "sales.csv"
EXPENSES_FILE = "expenses.csv"
CREDIT_FILE = "credit.csv"
CUSTOMER_FILE = "customers.csv"
SUPPLIER_FILE = "suppliers.csv"

# Function to initialize CSV files
def init_files():
    if not os.path.exists(PRODUCT_FILE) or os.stat(PRODUCT_FILE).st_size == 0:
        df_p = pd.DataFrame(columns=["Code", "Product Name", "Cost Price", "Selling Price", "Total Meter", "Total Yard", "Total Quantity (Pcs)", "Min Threshold", "Supplier", "Is_Deleted"])
        df_p.to_csv(PRODUCT_FILE, index=False)
    
    if not os.path.exists(SALES_FILE) or os.stat(SALES_FILE).st_size == 0:
        df_s = pd.DataFrame(columns=["Date", "Time", "Product Name", "Code", "Meter Amount", "Yard Amount", "Quantity (Pcs)", "Warranty", "Cost Price", "Selling Price", "Discount", "Points Used", "Total Price", "Profit", "Payment Method", "Customer", "Is_Deleted"])
        df_s.to_csv(SALES_FILE, index=False)

    if not os.path.exists(EXPENSES_FILE) or os.stat(EXPENSES_FILE).st_size == 0:
        df_e = pd.DataFrame(columns=["Date", "Description", "Amount", "Is_Deleted"])
        df_e.to_csv(EXPENSES_FILE, index=False)

    if not os.path.exists(CREDIT_FILE) or os.stat(CREDIT_FILE).st_size == 0:
        df_c = pd.DataFrame(columns=["Customer Name", "Phone", "Due Balance", "Last Date", "Is_Deleted"])
        df_c.to_csv(CREDIT_FILE, index=False)

    if not os.path.exists(CUSTOMER_FILE) or os.stat(CUSTOMER_FILE).st_size == 0:
        df_cust = pd.DataFrame(columns=["Customer Name", "Phone", "Loyalty Points", "Is_Deleted"])
        df_cust.to_csv(CUSTOMER_FILE, index=False)

    if not os.path.exists(SUPPLIER_FILE) or os.stat(SUPPLIER_FILE).st_size == 0:
        df_sup = pd.DataFrame(columns=["Supplier Name", "Phone", "Company", "Pending Payable", "Is_Deleted"])
        df_sup.to_csv(SUPPLIER_FILE, index=False)

init_files()

# Data Helpers
def load_data(file_path):
    try:
        df = pd.read_csv(file_path, dtype={"Code": str, "Phone": str})
        if "Is_Deleted" not in df.columns:
            df["Is_Deleted"] = False
        return df
    except Exception:
        return pd.DataFrame()

def save_data(df, file_path):
    df.to_csv(file_path, index=False)

# Session State Setup
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "user_role" not in st.session_state:
    st.session_state["user_role"] = None
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Main Menu"

# ==================== 🔒 1. LOGIN PAGE ====================
if not st.session_state["logged_in"]:
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>SAPPHIRE COLLECTION POS</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>System Login</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        role_selected = st.selectbox("Login As:", ["Admin", "Cashier"])
        pwd_input = st.text_input("Password:", type="password", key="login_pwd")
        
        if st.button("Login", type="primary", use_container_width=True):
            if role_selected == "Admin" and pwd_input == "1234":
                st.session_state["logged_in"] = True
                st.session_state["user_role"] = "Admin"
                st.session_state["current_page"] = "Main Menu"
                st.rerun()
            elif role_selected == "Cashier" and pwd_input == "0000":
                st.session_state["logged_in"] = True
                st.session_state["user_role"] = "Cashier"
                st.session_state["current_page"] = "Main Menu"
                st.rerun()
            else:
                st.error("වැරදි Password එකක්!")

# ==================== 🏠 LOGGED IN SYSTEM ====================
else:
    # Header Bar
    top_col1, top_col2, top_col3 = st.columns([4, 2, 1])
    with top_col1:
        if st.session_state["current_page"] != "Main Menu":
            if st.button("⬅️ Back to Main Menu"):
                st.session_state["current_page"] = "Main Menu"
                st.rerun()
    with top_col2:
        st.write(f"👤 Logged in as: **{st.session_state['user_role']}**")
    with top_col3:
        if st.button("🔒 Logout"):
            st.session_state["logged_in"] = False
            st.session_state["user_role"] = None
            st.session_state["current_page"] = "Main Menu"
            st.rerun()

    # ==================== 2. MAIN MENU ====================
    if st.session_state["current_page"] == "Main Menu":
        st.markdown("<h1 style='text-align: center;'>Sapphire Collection POS</h1>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📦 Product Management", use_container_width=True):
                st.session_state["current_page"] = "Product"
                st.rerun()
            if st.button("📖 Udara Book (ණය)", use_container_width=True):
                st.session_state["current_page"] = "Credit Book"
                st.rerun()
            if st.button("👥 Customer & Loyalty", use_container_width=True):
                st.session_state["current_page"] = "Customers"
                st.rerun()

        with col2:
            if st.button("🧾 Bill Issue & POS", use_container_width=True):
                st.session_state["current_page"] = "Bill Issue"
                st.rerun()
            if st.session_state["user_role"] == "Admin":
                if st.button("💸 Shop Expenses", use_container_width=True):
                    st.session_state["current_page"] = "Expenses"
                    st.rerun()
            if st.session_state["user_role"] == "Admin":
                if st.button("🏭 Supplier Management", use_container_width=True):
                    st.session_state["current_page"] = "Suppliers"
                    st.rerun()

        with col3:
            if st.button("📊 Stock & Alerts", use_container_width=True):
                st.session_state["current_page"] = "Stock"
                st.rerun()
            if st.session_state["user_role"] == "Admin":
                if st.button("📈 Reports & Net Profit", use_container_width=True):
                    st.session_state["current_page"] = "Reports"
                    st.rerun()

        if st.session_state["user_role"] == "Admin":
            st.markdown("<br>", unsafe_allow_html=True)
            col_bin, _ = st.columns([1, 2])
            with col_bin:
                if st.button("🗑️ Recycle Bin (Trash)", use_container_width=True):
                    st.session_state["current_page"] = "Recycle Bin"
                    st.rerun()

    # ==================== 3. PRODUCT PAGE ====================
    elif st.session_state["current_page"] == "Product":
        st.title("📦 Product Management")
        df_products = load_data(PRODUCT_FILE)
        df_sup = load_data(SUPPLIER_FILE)
        active_products = df_products[df_products["Is_Deleted"] == False] if not df_products.empty else pd.DataFrame()
        active_sups = df_sup[df_sup["Is_Deleted"] == False]["Supplier Name"].tolist() if not df_sup.empty else ["Default"]

        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("➕ Product එකතු කිරීම / Update කිරීම")
            with st.form("add_product_form", clear_on_submit=True):
                p_code = st.text_input("🏷️ Barcode / Product Code (Scan or Type)").strip()
                p_name = st.text_input("Product Name").strip()
                
                if st.session_state["user_role"] == "Admin":
                    p_cost = st.number_input("Cost Price (ගන්නා මිල Rs.)", min_value=0.0, step=10.0)
                else:
                    p_cost = 0.0
                    
                p_sell = st.number_input("Selling Price (විකුණන මිල Rs.)", min_value=0.0, step=10.0)
                p_sup = st.selectbox("Supplier", active_sups)

                col_p1, col_p2, col_p3 = st.columns(3)
                with col_p1: p_meter = st.number_input("Total Meter", min_value=0.0, step=0.5)
                with col_p2: p_yard = st.number_input("Total Yard", min_value=0.0, step=0.5)
                with col_p3: p_qty = st.number_input("Quantity (Pcs)", min_value=0.0, step=1.0)
                
                p_min = st.number_input("⚠️ Low Stock Warning Threshold", min_value=1.0, value=5.0)

                if st.form_submit_button("Save Product"):
                    if not p_code or not p_name:
                        st.error("Code සහ Product Name ඇතුළත් කරන්න.")
                    else:
                        new_data = {
                            "Code": p_code, "Product Name": p_name, "Cost Price": p_cost, 
                            "Selling Price": p_sell, "Total Meter": p_meter, "Total Yard": p_yard, 
                            "Total Quantity (Pcs)": p_qty, "Min Threshold": p_min, "Supplier": p_sup, "Is_Deleted": False
                        }
                        if not df_products.empty and p_code in df_products["Code"].astype(str).values:
                            df_products.loc[df_products["Code"].astype(str) == p_code] = new_data
                        else:
                            df_products = pd.concat([df_products, pd.DataFrame([new_data])], ignore_index=True)
                        save_data(df_products, PRODUCT_FILE)
                        st.success("Product එක Save විය!")
                        st.rerun()

        with col2:
            if st.session_state["user_role"] == "Admin":
                st.subheader("🗑️ Delete Product (Move to Trash)")
                if not active_products.empty:
                    delete_code = st.selectbox("මකා දැමීමට Product එක තෝරන්න:", active_products["Code"].astype(str) + " - " + active_products["Product Name"])
                    if st.button("Move to Recycle Bin", type="primary"):
                        selected_code = delete_code.split(" - ")[0]
                        df_products.loc[df_products["Code"].astype(str) == selected_code, "Is_Deleted"] = True
                        save_data(df_products, PRODUCT_FILE)
                        st.success("Product එක Recycle Bin එකට යවන ලදී!")
                        st.rerun()

    # ==================== 4. BILL ISSUE PAGE ====================
    elif st.session_state["current_page"] == "Bill Issue":
        st.title("🧾 Bill Issue & POS")
        df_products = load_data(PRODUCT_FILE)
        df_cust = load_data(CUSTOMER_FILE)
        active_products = df_products[df_products["Is_Deleted"] == False] if not df_products.empty else pd.DataFrame()
        active_cust = df_cust[df_cust["Is_Deleted"] == False] if not df_cust.empty else pd.DataFrame()

        if active_products.empty:
            st.warning("පළමුව 'Product Management' අංශයෙන් භාණ්ඩ ඇතුළත් කරන්න.")
        else:
            search_query = st.text_input("🔍 Scan Barcode or Type Product Name/Code:", "").strip()
            filtered = active_products if not search_query else active_products[
                active_products["Code"].astype(str).str.contains(search_query, case=False, na=False) |
                active_products["Product Name"].str.contains(search_query, case=False, na=False)
            ]

            if not filtered.empty:
                prod_opts = filtered["Code"].astype(str) + " - " + filtered["Product Name"]
                sel_prod = st.selectbox("Product එක තෝරන්න:", prod_opts)
                sel_code = sel_prod.split(" - ")[0]
                prod_row = filtered[filtered["Code"].astype(str) == sel_code].iloc[0]

                cost_price = float(prod_row.get("Cost Price", 0))
                sell_price = float(prod_row.get("Selling Price", 0))
                curr_m = float(prod_row.get("Total Meter", 0))
                curr_y = float(prod_row.get("Total Yard", 0))
                curr_q = float(prod_row.get("Total Quantity (Pcs)", 0))

                st.info(f"📌 Stock: {curr_m}m | {curr_y}yd | {int(curr_q)} Pcs | Price: Rs. {sell_price:,.2f}")

                col_b1, col_b2, col_b3 = st.columns(3)
                with col_b1: sell_m = st.number_input("Meter Amount:", min_value=0.0, step=0.1)
                with col_b2: sell_y = st.number_input("Yard Amount:", min_value=0.0, step=0.1)
                with col_b3: sell_q = st.number_input("Quantity Pcs:", min_value=0.0, step=1.0)

                # Customer & Loyalty Points
                st.subheader("👤 Customer & Loyalty Points")
                cust_names = ["Guest Customer"] + active_cust["Customer Name"].tolist() if not active_cust.empty else ["Guest Customer"]
                sel_cust_name = st.selectbox("Select Customer:", cust_names)
                
                avail_points = 0
                points_to_use = 0
                if sel_cust_name != "Guest Customer" and not active_cust.empty:
                    cust_row = active_cust[active_cust["Customer Name"] == sel_cust_name].iloc[0]
                    avail_points = float(cust_row.get("Loyalty Points", 0))
                    st.write(f"🌟 Available Loyalty Points: **{avail_points:.0f} Points** (1 Point = Rs. 1)")
                    use_points = st.checkbox("Redeem Loyalty Points as Discount")
                    if use_points:
                        points_to_use = st.number_input("Points to Redeem:", min_value=0.0, max_value=avail_points, step=1.0)

                col_o1, col_o2 = st.columns(2)
                with col_o1:
                    disc_type = st.radio("Discount Type:", ["Flat Amount (Rs.)", "Percentage (%)"], horizontal=True)
                    disc_val = st.number_input("Discount Value:", min_value=0.0)
                with col_o2:
                    pay_method = st.selectbox("Payment Method:", ["Cash", "Card", "Online Transfer / QR", "Credit (ණය)"])
                    warranty_val = st.selectbox("Warranty:", ["No Warranty", "6 Months", "1 Year", "2 Years", "3 Years"])

                cust_phone = ""
                if pay_method == "Credit (ණය)":
                    cust_phone = st.text_input("Customer Phone Number:")

                unit_qty = sell_m + sell_y + sell_q
                subtotal = unit_qty * sell_price
                
                discount_rs = disc_val if "Flat" in disc_type else (subtotal * disc_val / 100.0)
                discount_rs += points_to_use # Adding points discount
                final_total = max(0.0, subtotal - discount_rs)
                net_profit = final_total - (unit_qty * cost_price)

                # Earned points (1 point per Rs. 100 spent)
                earned_points = int(final_total // 100)

                st.markdown(f"### 💵 Net Total: **Rs. {final_total:,.2f}** (Total Discount: Rs. {discount_rs:,.2f})")

                if st.button("🛒 Complete Sale & Issue Bill", type="primary"):
                    if unit_qty <= 0:
                        st.error("ප්‍රමාණයක් ඇතුළත් කරන්න.")
                    elif sell_m > curr_m or sell_y > curr_y or sell_q > curr_q:
                        st.error("තොගයේ ප්‍රමාණවත් තරම් බඩු නොමැත!")
                    else:
                        # Update Stock
                        df_products.loc[df_products["Code"].astype(str) == sel_code, "Total Meter"] = curr_m - sell_m
                        df_products.loc[df_products["Code"].astype(str) == sel_code, "Total Yard"] = curr_y - sell_y
                        df_products.loc[df_products["Code"].astype(str) == sel_code, "Total Quantity (Pcs)"] = curr_q - sell_q
                        save_data(df_products, PRODUCT_FILE)

                        # Update Customer Loyalty Points
                        if sel_cust_name != "Guest Customer" and not active_cust.empty:
                            new_points = avail_points - points_to_use + earned_points
                            df_cust.loc[df_cust["Customer Name"] == sel_cust_name, "Loyalty Points"] = new_points
                            save_data(df_cust, CUSTOMER_FILE)

                        # Record Sale
                        now = datetime.now()
                        new_sale = {
                            "Date": now.strftime("%Y-%m-%d"), "Time": now.strftime("%H:%M:%S"),
                            "Product Name": prod_row["Product Name"], "Code": sel_code,
                            "Meter Amount": sell_m, "Yard Amount": sell_y, "Quantity (Pcs)": sell_q,
                            "Warranty": warranty_val, "Cost Price": cost_price, "Selling Price": sell_price,
                            "Discount": discount_rs, "Points Used": points_to_use, "Total Price": final_total, 
                            "Profit": net_profit, "Payment Method": pay_method, "Customer": sel_cust_name, "Is_Deleted": False
                        }
                        df_sales = load_data(SALES_FILE)
                        df_sales = pd.concat([df_sales, pd.DataFrame([new_sale])], ignore_index=True)
                        save_data(df_sales, SALES_FILE)

                        if pay_method == "Credit (ණය)" and sel_cust_name:
                            df_cred = load_data(CREDIT_FILE)
                            if not df_cred.empty and sel_cust_name in df_cred[df_cred["Is_Deleted"] == False]["Customer Name"].values:
                                existing_due = df_cred.loc[(df_cred["Customer Name"] == sel_cust_name) & (df_cred["Is_Deleted"] == False), "Due Balance"].values[0]
                                df_cred.loc[(df_cred["Customer Name"] == sel_cust_name) & (df_cred["Is_Deleted"] == False), "Due Balance"] = float(existing_due) + final_total
                                df_cred.loc[(df_cred["Customer Name"] == sel_cust_name) & (df_cred["Is_Deleted"] == False), "Last Date"] = now.strftime("%Y-%m-%d")
                            else:
                                cred_row = {"Customer Name": sel_cust_name, "Phone": cust_phone, "Due Balance": final_total, "Last Date": now.strftime("%Y-%m-%d"), "Is_Deleted": False}
                                df_cred = pd.concat([df_cred, pd.DataFrame([cred_row])], ignore_index=True)
                            save_data(df_cred, CREDIT_FILE)

                        st.success("✅ බිල්පත සාර්ථකව නිකුත් කරන ලදී!")

                        # 🖨️ Thermal POS Receipt Display & Direct Print Button
                        st.markdown("---")
                        st.subheader("🖨️ Receipt Preview")
                        receipt_html = f"""
                        <div id="printableArea" style="width: 280px; background: white; color: black; padding: 12px; font-family: monospace; font-size: 12px; border: 1px solid #ccc; border-radius: 5px; margin: auto;">
                            <h3 style="text-align:center; margin:0;">SAPPHIRE COLLECTION</h3>
                            <p style="text-align:center; margin:2px 0;">Electronics & Textiles</p>
                            <p style="text-align:center; margin:0;">--------------------------------</p>
                            <p style="margin: 4px 0;"><b>Date:</b> {now.strftime("%Y-%m-%d %H:%M")}<br><b>Customer:</b> {sel_cust_name}<br><b>Pay Method:</b> {pay_method}</p>
                            <p style="text-align:center; margin:0;">--------------------------------</p>
                            <p style="margin: 4px 0;"><b>Item:</b> {prod_row['Product Name']}<br><b>Qty:</b> {unit_qty}<br><b>Price:</b> Rs. {sell_price:,.2f}</p>
                            <p style="margin: 4px 0;"><b>Discount:</b> Rs. {discount_rs:,.2f}</p>
                            <h4 style="margin: 6px 0;">TOTAL: Rs. {final_total:,.2f}</h4>
                            <p style="text-align:center; margin:0;">--------------------------------</p>
                            <p style="text-align:center; margin:2px 0;">Points Earned: {earned_points}</p>
                            <p style="text-align:center; margin:4px 0;">Thank You! Come Again.</p>
                        </div>
                        <br>
                        <div style="text-align: center;">
                            <button onclick="window.print()" style="padding: 8px 16px; background-color: #4CAF50; color: white; border: none; border-radius: 4px; cursor: pointer;">🖨️ Print Receipt</button>
                        </div>
                        """
                        st.components.v1.html(receipt_html, height=350)

    # ==================== 5. CUSTOMER & LOYALTY ====================
    elif st.session_state["current_page"] == "Customers":
        st.title("👥 Customer Management & Loyalty Points")
        df_cust = load_data(CUSTOMER_FILE)
        active_cust = df_cust[df_cust["Is_Deleted"] == False] if not df_cust.empty else pd.DataFrame()

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("➕ Add New Customer")
            with st.form("add_cust_form", clear_on_submit=True):
                c_name = st.text_input("Customer Name").strip()
                c_phone = st.text_input("Phone Number").strip()
                if st.form_submit_button("Save Customer"):
                    if c_name:
                        new_c = {"Customer Name": c_name, "Phone": c_phone, "Loyalty Points": 0, "Is_Deleted": False}
                        df_cust = pd.concat([df_cust, pd.DataFrame([new_c])], ignore_index=True)
                        save_data(df_cust, CUSTOMER_FILE)
                        st.success("Customer සාර්ථකව එකතු විය!")
                        st.rerun()

        with col2:
            st.subheader("📋 Registered Customers")
            if not active_cust.empty:
                st.dataframe(active_cust.drop(columns=["Is_Deleted"], errors="ignore"), use_container_width=True)

    # ==================== 6. SUPPLIER MANAGEMENT ====================
    elif st.session_state["current_page"] == "Suppliers":
        st.title("🏭 Supplier Management")
        df_sup = load_data(SUPPLIER_FILE)
        active_sup = df_sup[df_sup["Is_Deleted"] == False] if not df_sup.empty else pd.DataFrame()

        col1, col2 = st.columns(2)
        with col1:
            st.subheader("➕ Add Supplier")
            with st.form("add_sup_form", clear_on_submit=True):
                s_name = st.text_input("Supplier / Contact Name").strip()
                s_company = st.text_input("Company Name").strip()
                s_phone = st.text_input("Phone Number").strip()
                s_payable = st.number_input("Pending Payable Amount (ණය මුදල Rs.)", min_value=0.0)
                if st.form_submit_button("Save Supplier"):
                    if s_name:
                        new_s = {"Supplier Name": s_name, "Company": s_company, "Phone": s_phone, "Pending Payable": s_payable, "Is_Deleted": False}
                        df_sup = pd.concat([df_sup, pd.DataFrame([new_s])], ignore_index=True)
                        save_data(df_sup, SUPPLIER_FILE)
                        st.success("Supplier එකතු විය!")
                        st.rerun()

        with col2:
            st.subheader("📋 Supplier List")
            if not active_sup.empty:
                st.dataframe(active_sup.drop(columns=["Is_Deleted"], errors="ignore"), use_container_width=True)

    # ==================== 7. STOCK & ALERTS ====================
    elif st.session_state["current_page"] == "Stock":
        st.title("📊 Stock & Low Stock Warnings")
        df_products = load_data(PRODUCT_FILE)
        active_products = df_products[df_products["Is_Deleted"] == False] if not df_products.empty else pd.DataFrame()

        if not active_products.empty:
            st.subheader("⚠️ Low Stock Alerts")
            low_stock = active_products[
                ((active_products["Total Meter"] > 0) & (active_products["Total Meter"] <= active_products["Min Threshold"])) |
                ((active_products["Total Quantity (Pcs)"] > 0) & (active_products["Total Quantity (Pcs)"] <= active_products["Min Threshold"])) |
                ((active_products["Total Meter"] == 0) & (active_products["Total Quantity (Pcs)"] == 0))
            ]
            if not low_stock.empty:
                st.dataframe(low_stock[["Product Name", "Code", "Total Meter", "Total Quantity (Pcs)", "Min Threshold"]], use_container_width=True)
            else:
                st.success("සියලුම භාණ්ඩ ප්‍රමාණවත් ලෙස තොගයේ ඇත.")

            st.subheader("📋 Complete Stock")
            if st.session_state["user_role"] == "Cashier":
                st.dataframe(active_products.drop(columns=["Is_Deleted", "Cost Price"], errors="ignore"), use_container_width=True)
            else:
                st.dataframe(active_products.drop(columns=["Is_Deleted"], errors="ignore"), use_container_width=True)

    # ==================== 8. REPORTS & NET PROFIT ====================
    elif st.session_state["current_page"] == "Reports":
        st.title("📈 Sales Reports & Net Profit")
        df_sales = load_data(SALES_FILE)
        df_expenses = load_data(EXPENSES_FILE)

        active_sales = df_sales[df_sales["Is_Deleted"] == False] if not df_sales.empty else pd.DataFrame()
        active_exp = df_expenses[df_expenses["Is_Deleted"] == False] if not df_expenses.empty else pd.DataFrame()

        col_d1, col_d2 = st.columns(2)
        with col_d1: start_d = st.date_input("Start Date", value=date.today())
        with col_d2: end_d = st.date_input("End Date", value=date.today())

        if not active_sales.empty:
            active_sales["Date_dt"] = pd.to_datetime(active_sales["Date"]).dt.date
            mask = (active_sales["Date_dt"] >= start_d) & (active_sales["Date_dt"] <= end_d)
            filtered_s = active_sales.loc[mask]

            total_rev = filtered_s["Total Price"].sum() if not filtered_s.empty else 0
            gross_profit = filtered_s["Profit"].sum() if not filtered_s.empty else 0

            total_exp = 0
            if not active_exp.empty:
                active_exp["Date_dt"] = pd.to_datetime(active_exp["Date"]).dt.date
                filtered_e = active_exp.loc[(active_exp["Date_dt"] >= start_d) & (active_exp["Date_dt"] <= end_d)]
                total_exp = filtered_e["Amount"].sum()

            net_profit = gross_profit - total_exp

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("💰 මුළු ආදායම", f"Rs. {total_rev:,.2f}")
            m2.metric("📦 දළ ලාභය", f"Rs. {gross_profit:,.2f}")
            m3.metric("💸 මුළු වියදම්", f"Rs. {total_exp:,.2f}")
            m4.metric("🔥 නියම ශුද්ධ ලාභය", f"Rs. {net_profit:,.2f}")

            st.dataframe(filtered_s.drop(columns=["Is_Deleted", "Date_dt"], errors="ignore"), use_container_width=True)

            col_del, _ = st.columns([1, 2])
            with col_del:
                sale_idx = st.selectbox("Move Sale Record to Trash:", filtered_s.index)
                if st.button("Delete Sale Record"):
                    df_sales.loc[sale_idx, "Is_Deleted"] = True
                    save_data(df_sales, SALES_FILE)
                    st.success("Sales record එක Recycle Bin එකට යවන ලදී!")
                    st.rerun()

    # ==================== 9. SHOP EXPENSES ====================
    elif st.session_state["current_page"] == "Expenses":
        st.title("💸 Daily Shop Expenses Tracker")
        df_exp = load_data(EXPENSES_FILE)
        active_exp = df_exp[df_exp["Is_Deleted"] == False] if not df_exp.empty else pd.DataFrame()

        with st.form("add_exp"):
            exp_desc = st.text_input("Expense Description")
            exp_amt = st.number_input("Amount (Rs.)", min_value=0.0)
            if st.form_submit_button("Add Expense"):
                if exp_desc and exp_amt > 0:
                    new_exp = {"Date": datetime.now().strftime("%Y-%m-%d"), "Description": exp_desc, "Amount": exp_amt, "Is_Deleted": False}
                    df_exp = pd.concat([df_exp, pd.DataFrame([new_exp])], ignore_index=True)
                    save_data(df_exp, EXPENSES_FILE)
                    st.success("වියදම ඇතුළත් විය!")
                    st.rerun()

        st.subheader("📋 Expenses Log")
        if not active_exp.empty:
            st.dataframe(active_exp.drop(columns=["Is_Deleted"], errors="ignore"), use_container_width=True)
            exp_del_idx = st.selectbox("Move Expense to Trash:", active_exp.index)
            if st.button("Delete Expense"):
                df_exp.loc[exp_del_idx, "Is_Deleted"] = True
                save_data(df_exp, EXPENSES_FILE)
                st.success("Expense එක Recycle Bin එකට යවන ලදී!")
                st.rerun()

    # ==================== 10. CREDIT BOOK (UDARA BOOK) ====================
    elif st.session_state["current_page"] == "Credit Book":
        st.title("📖 Customer Credit Book (ණය පොත)")
        df_cred = load_data(CREDIT_FILE)
        active_cred = df_cred[df_cred["Is_Deleted"] == False] if not df_cred.empty else pd.DataFrame()

        if not active_cred.empty:
            st.dataframe(active_cred.drop(columns=["Is_Deleted"], errors="ignore"), use_container_width=True)
            
            st.markdown("---")
            st.subheader("💵 Debt Payment / Settle (ණය මුදල් ලබාගැනීම)")
            
            sel_cust = st.selectbox("Customer තෝරන්න:", active_cred["Customer Name"].unique())
            cust_row = active_cred[active_cred["Customer Name"] == sel_cust].iloc[0]
            current_due = float(cust_row["Due Balance"])
            
            st.info(f"👤 Customer: **{sel_cust}** | 💳 Current Due Balance: **Rs. {current_due:,.2f}**")
            
            col_pay1, col_pay2 = st.columns(2)
            with col_pay1:
                pay_amount = st.number_input("ලබාදුන් මුදල (Rs.):", min_value=0.0, max_value=current_due, step=100.0)
            with col_pay2:
                settle_option = st.radio("ගෙවීම් වර්ගය:", ["Partial Payment (කොටසක් ගෙවීම)", "Full Settle (සම්පූර්ණයෙන්ම පියවීම)"])

            if st.button("✅ Record Payment / Settle", type="primary"):
                now_str = datetime.now().strftime("%Y-%m-%d")
                
                if "Full Settle" in settle_option or pay_amount >= current_due:
                    df_cred.loc[df_cred["Customer Name"] == sel_cust, "Is_Deleted"] = True
                    save_data(df_cred, CREDIT_FILE)
                    st.success(f"🎉 {sel_cust} ගේ ණය මුදල සම්පූර්ණයෙන්ම ගෙවා අවසන් කර Recycle Bin එකට යවන ලදී!")
                    st.rerun()
                else:
                    if pay_amount > 0:
                        new_balance = current_due - pay_amount
                        df_cred.loc[df_cred["Customer Name"] == sel_cust, "Due Balance"] = new_balance
                        df_cred.loc[df_cred["Customer Name"] == sel_cust, "Last Date"] = now_str
                        save_data(df_cred, CREDIT_FILE)
                        st.success(f"✅ Rs. {pay_amount:,.2f} ක ගෙවීම සටහන් විය. ඉතිරි ණය මුදල: Rs. {new_balance:,.2f}")
                        st.rerun()
                    else:
                        st.error("කරුණාකර ගෙවූ මුදල ඇතුළත් කරන්න.")
        else:
            st.info("ණය හිඟ මුදල් නොමැත.")

    # ==================== 11. RECYCLE BIN (TRASH & RESTORE) ====================
    elif st.session_state["current_page"] == "Recycle Bin":
        st.title("🗑️ Recycle Bin (Trash System)")
        st.info("මෙතැනින් වැරදීමකින් මැකූ හෝ පියවූ ඕනෑම දත්තයක් නැවත පද්ධතියට Restore කරගත හැක.")

        tab1, tab2, tab3, tab4 = st.tabs(["📦 Products Trash", "🧾 Sales Trash", "💸 Expenses Trash", "📖 Credit Trash"])

        # Tab 1: Products
        with tab1:
            df_p = load_data(PRODUCT_FILE)
            deleted_p = df_p[df_p["Is_Deleted"] == True] if not df_p.empty else pd.DataFrame()
            if not deleted_p.empty:
                st.dataframe(deleted_p.drop(columns=["Is_Deleted"], errors="ignore"), use_container_width=True)
                rest_code = st.selectbox("Restore කිරීමට Product එක තෝරන්න:", deleted_p["Code"].astype(str) + " - " + deleted_p["Product Name"])
                if st.button("🔄 Restore Product"):
                    code_val = rest_code.split(" - ")[0]
                    df_p.loc[df_p["Code"].astype(str) == code_val, "Is_Deleted"] = False
                    save_data(df_p, PRODUCT_FILE)
                    st.success("Product එක නැවත පද්ධතියට Restore කරන ලදී!")
                    st.rerun()
            else:
                st.write("මකා දමන ලද Products නොමැත.")

        # Tab 2: Sales
        with tab2:
            df_s = load_data(SALES_FILE)
            deleted_s = df_s[df_s["Is_Deleted"] == True] if not df_s.empty else pd.DataFrame()
            if not deleted_s.empty:
                st.dataframe(deleted_s.drop(columns=["Is_Deleted"], errors="ignore"), use_container_width=True)
                rest_s_idx = st.selectbox("Restore කිරීමට Sales Record එක තෝරන්න:", deleted_s.index)
                if st.button("🔄 Restore Sale Record"):
                    df_s.loc[rest_s_idx, "Is_Deleted"] = False
                    save_data(df_s, SALES_FILE)
                    st.success("Sales record එක නැවත Restore කරන ලදී!")
                    st.rerun()
            else:
                st.write("මකා දමන ලද Sales records නොමැත.")

        # Tab 3: Expenses
        with tab3:
            df_e = load_data(EXPENSES_FILE)
            deleted_e = df_e[df_e["Is_Deleted"] == True] if not df_e.empty else pd.DataFrame()
            if not deleted_e.empty:
                st.dataframe(deleted_e.drop(columns=["Is_Deleted"], errors="ignore"), use_container_width=True)
                rest_e_idx = st.selectbox("Restore කිරීමට Expense එක තෝරන්න:", deleted_e.index)
                if st.button("🔄 Restore Expense"):
                    df_e.loc[rest_e_idx, "Is_Deleted"] = False
                    save_data(df_e, EXPENSES_FILE)
                    st.success("Expense එක නැවත Restore කරන ලදී!")
                    st.rerun()
            else:
                st.write("මකා දමන ලද Expenses නොමැත.")

        # Tab 4: Credit Book
        with tab4:
            df_c = load_data(CREDIT_FILE)
            deleted_c = df_c[df_c["Is_Deleted"] == True] if not df_c.empty else pd.DataFrame()
            if not deleted_c.empty:
                st.dataframe(deleted_c.drop(columns=["Is_Deleted"], errors="ignore"), use_container_width=True)
                rest_c_cust = st.selectbox("Restore කිරීමට Customer තෝරන්න:", deleted_c["Customer Name"].unique())
                if st.button("🔄 Restore Credit Record"):
                    df_c.loc[df_c["Customer Name"] == rest_c_cust, "Is_Deleted"] = False
                    save_data(df_c, CREDIT_FILE)
                    st.success("ණය සටහන නැවත Udara Book එකට Restore කරන ලදී!")
                    st.rerun()
            else:
                st.write("මකා දමන ලද හෝ පියවූ ණය සටහන් නොමැත.")
