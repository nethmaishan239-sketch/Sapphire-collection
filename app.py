import streamlit as st
import pandas as pd
import os
from datetime import datetime, date

# Page Configuration
st.set_page_config(page_title="Sapphire Collection POS", layout="wide")

# Files for Data Persistence
PRODUCT_FILE = "products.csv"
SALES_FILE = "sales.csv"
EXPENSES_FILE = "expenses.csv"
CREDIT_FILE = "credit.csv"

# Function to initialize CSV files
def init_files():
    if not os.path.exists(PRODUCT_FILE) or os.stat(PRODUCT_FILE).st_size == 0:
        df_p = pd.DataFrame(columns=["Code", "Product Name", "Cost Price", "Selling Price", "Total Meter", "Total Yard", "Total Quantity (Pcs)", "Min Threshold"])
        df_p.to_csv(PRODUCT_FILE, index=False)
    
    if not os.path.exists(SALES_FILE) or os.stat(SALES_FILE).st_size == 0:
        df_s = pd.DataFrame(columns=["Date", "Time", "Product Name", "Code", "Meter Amount", "Yard Amount", "Quantity (Pcs)", "Warranty", "Cost Price", "Selling Price", "Discount", "Total Price", "Profit", "Payment Method", "Customer"])
        df_s.to_csv(SALES_FILE, index=False)

    if not os.path.exists(EXPENSES_FILE) or os.stat(EXPENSES_FILE).st_size == 0:
        df_e = pd.DataFrame(columns=["Date", "Description", "Amount"])
        df_e.to_csv(EXPENSES_FILE, index=False)

    if not os.path.exists(CREDIT_FILE) or os.stat(CREDIT_FILE).st_size == 0:
        df_c = pd.DataFrame(columns=["Customer Name", "Phone", "Due Balance", "Last Date"])
        df_c.to_csv(CREDIT_FILE, index=False)

init_files()

# Data Load & Save Helpers
def load_data(file_path):
    try:
        return pd.read_csv(file_path, dtype={"Code": str, "Phone": str})
    except Exception:
        return pd.DataFrame()

def save_data(df, file_path):
    df.to_csv(file_path, index=False)

# Session State Setup
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Main Menu"

# ==================== 🔒 1. LOGIN PAGE ====================
if not st.session_state["logged_in"]:
    st.markdown("<h1 style='text-align: center; color: #4CAF50;'>SAPPHIRE COLLECTION POS</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Login</h3>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pwd_input = st.text_input("Password:", type="password", key="login_pwd")
        if st.button("Login", type="primary", use_container_width=True):
            if pwd_input == "1234":
                st.session_state["logged_in"] = True
                st.session_state["current_page"] = "Main Menu"
                st.rerun()
            else:
                st.error("වැරදි Password එකක්!")

# ==================== 🏠 LOGGED IN SYSTEM ====================
else:
    # Header & Logout
    top_col1, top_col2 = st.columns([5, 1])
    with top_col1:
        if st.session_state["current_page"] != "Main Menu":
            if st.button("⬅️ Back to Main Menu"):
                st.session_state["current_page"] = "Main Menu"
                st.rerun()
    with top_col2:
        if st.button("🔒 Logout"):
            st.session_state["logged_in"] = False
            st.session_state["current_page"] = "Main Menu"
            st.rerun()

    # ==================== 2. MAIN MENU ====================
    if st.session_state["current_page"] == "Main Menu":
        st.markdown("<h1 style='text-align: center;'>Sapphire Collection POS</h1>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📦 Product", use_container_width=True):
                st.session_state["current_page"] = "Product"
                st.rerun()
            if st.button("📖 Udara Book (ණය)", use_container_width=True):
                st.session_state["current_page"] = "Credit Book"
                st.rerun()
        with col2:
            if st.button("🧾 Bill Issue", use_container_width=True):
                st.session_state["current_page"] = "Bill Issue"
                st.rerun()
            if st.button("💸 Shop Expenses", use_container_width=True):
                st.session_state["current_page"] = "Expenses"
                st.rerun()
        with col3:
            if st.button("📊 Stock & Alerts", use_container_width=True):
                st.session_state["current_page"] = "Stock"
                st.rerun()
            if st.button("📈 Reports & Net Profit", use_container_width=True):
                st.session_state["current_page"] = "Reports"
                st.rerun()

    # ==================== 3. PRODUCT PAGE ====================
    elif st.session_state["current_page"] == "Product":
        st.title("📦 Product Management")
        df_products = load_data(PRODUCT_FILE)
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("➕ Product එකතු කිරීම / Update කිරීම")
            with st.form("add_product_form", clear_on_submit=True):
                p_name = st.text_input("Product Name").strip()
                p_code = st.text_input("Product Code").strip()
                p_cost = st.number_input("Cost Price (ගන්නා මිල Rs.)", min_value=0.0, step=10.0)
                p_sell = st.number_input("Selling Price (විකුණන මිල Rs.)", min_value=0.0, step=10.0)
                
                col_p1, col_p2, col_p3 = st.columns(3)
                with col_p1:
                    p_meter = st.number_input("Total Meter", min_value=0.0, step=0.5)
                with col_p2:
                    p_yard = st.number_input("Total Yard", min_value=0.0, step=0.5)
                with col_p3:
                    p_qty = st.number_input("Quantity (Pcs)", min_value=0.0, step=1.0)
                
                p_min = st.number_input("⚠️ Low Stock Warning Threshold (අඩුම තොග සීමාව)", min_value=1.0, value=5.0)

                if st.form_submit_button("Save Product"):
                    if not p_code or not p_name:
                        st.error("Code සහ Product Name ඇතුළත් කරන්න.")
                    else:
                        new_data = {
                            "Code": p_code, "Product Name": p_name, "Cost Price": p_cost, 
                            "Selling Price": p_sell, "Total Meter": p_meter, "Total Yard": p_yard, 
                            "Total Quantity (Pcs)": p_qty, "Min Threshold": p_min
                        }
                        if not df_products.empty and p_code in df_products["Code"].astype(str).values:
                            df_products.loc[df_products["Code"].astype(str) == p_code] = new_data
                        else:
                            df_products = pd.concat([df_products, pd.DataFrame([new_data])], ignore_index=True)
                        save_data(df_products, PRODUCT_FILE)
                        st.success("Product එක Save විය!")
                        st.rerun()

        with col2:
            st.subheader("🗑️ Delete Product")
            if not df_products.empty:
                delete_code = st.selectbox("මකා දැමීමට Product එක තෝරන්න:", df_products["Code"].astype(str) + " - " + df_products["Product Name"])
                if st.button("Delete Product", type="primary"):
                    selected_code = delete_code.split(" - ")[0]
                    df_products = df_products[df_products["Code"].astype(str) != selected_code]
                    save_data(df_products, PRODUCT_FILE)
                    st.success("Product එක මකා දමන ලදී!")
                    st.rerun()

    # ==================== 4. BILL ISSUE PAGE ====================
    elif st.session_state["current_page"] == "Bill Issue":
        st.title("🧾 Bill Issue & POS")
        df_products = load_data(PRODUCT_FILE)
        
        if df_products.empty:
            st.warning("පළමුව 'Product' අංශයෙන් භාණ්ඩ ඇතුළත් කරන්න.")
        else:
            search_query = st.text_input("🔍 Search Product Name or Code:", "").strip()
            filtered = df_products if not search_query else df_products[
                df_products["Code"].astype(str).str.contains(search_query, case=False, na=False) |
                df_products["Product Name"].str.contains(search_query, case=False, na=False)
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

                st.info(f"📌 Stock: {curr_m}m | {curr_y}yd | {int(curr_q)} Pcs | Selling Price: Rs. {sell_price:,.2f}")

                col_b1, col_b2, col_b3 = st.columns(3)
                with col_b1: sell_m = st.number_input("Meter Amount:", min_value=0.0, step=0.1)
                with col_b2: sell_y = st.number_input("Yard Amount:", min_value=0.0, step=0.1)
                with col_b3: sell_q = st.number_input("Quantity Pcs:", min_value=0.0, step=1.0)

                col_o1, col_o2 = st.columns(2)
                with col_o1:
                    disc_type = st.radio("Discount Type:", ["Flat Amount (Rs.)", "Percentage (%)"], horizontal=True)
                    disc_val = st.number_input("Discount Value:", min_value=0.0)
                with col_o2:
                    pay_method = st.selectbox("Payment Method:", ["Cash", "Card", "Online Transfer / QR", "Credit (ණය)"])
                    warranty_val = st.selectbox("Warranty:", ["No Warranty", "6 Months", "1 Year", "2 Years", "3 Years"])

                cust_name, cust_phone = "", ""
                if pay_method == "Credit (ණය)":
                    st.subheader("👤 Customer Credit Details")
                    cust_name = st.text_input("Customer Name:")
                    cust_phone = st.text_input("Phone Number:")

                unit_qty = sell_m + sell_y + sell_q
                subtotal = unit_qty * sell_price
                
                discount_rs = disc_val if "Flat" in disc_type else (subtotal * disc_val / 100.0)
                final_total = max(0.0, subtotal - discount_rs)
                net_profit = final_total - (unit_qty * cost_price)

                st.markdown(f"### 💵 Net Total: **Rs. {final_total:,.2f}** (Discount: Rs. {discount_rs:,.2f})")

                if st.button("🛒 Complete Sale & Issue Bill", type="primary"):
                    if unit_qty <= 0:
                        st.error("ප්‍රමාණයක් ඇතුළත් කරන්න.")
                    elif sell_m > curr_m or sell_y > curr_y or sell_q > curr_q:
                        st.error("තොගයේ ප්‍රමාණවත් තරම් බඩු නොමැත!")
                    else:
                        # Stock Update
                        df_products.loc[df_products["Code"].astype(str) == sel_code, "Total Meter"] = curr_m - sell_m
                        df_products.loc[df_products["Code"].astype(str) == sel_code, "Total Yard"] = curr_y - sell_y
                        df_products.loc[df_products["Code"].astype(str) == sel_code, "Total Quantity (Pcs)"] = curr_q - sell_q
                        save_data(df_products, PRODUCT_FILE)

                        # Record Sale
                        now = datetime.now()
                        new_sale = {
                            "Date": now.strftime("%Y-%m-%d"), "Time": now.strftime("%H:%M:%S"),
                            "Product Name": prod_row["Product Name"], "Code": sel_code,
                            "Meter Amount": sell_m, "Yard Amount": sell_y, "Quantity (Pcs)": sell_q,
                            "Warranty": warranty_val, "Cost Price": cost_price, "Selling Price": sell_price,
                            "Discount": discount_rs, "Total Price": final_total, "Profit": net_profit,
                            "Payment Method": pay_method, "Customer": cust_name
                        }
                        df_sales = load_data(SALES_FILE)
                        df_sales = pd.concat([df_sales, pd.DataFrame([new_sale])], ignore_index=True)
                        save_data(df_sales, SALES_FILE)

                        # Record Credit if applicable
                        if pay_method == "Credit (ණය)" and cust_name:
                            df_cred = load_data(CREDIT_FILE)
                            cred_row = {"Customer Name": cust_name, "Phone": cust_phone, "Due Balance": final_total, "Last Date": now.strftime("%Y-%m-%d")}
                            df_cred = pd.concat([df_cred, pd.DataFrame([cred_row])], ignore_index=True)
                            save_data(df_cred, CREDIT_FILE)

                        st.success("✅ බිල්පත සාර්ථකව නිකුත් කරන ලදී!")

                        # Thermal POS Layout Display
                        st.markdown("---")
                        st.subheader("🖨️ POS Receipt Preview (80mm Thermal)")
                        receipt_html = f"""
                        <div style="width: 280px; background: white; color: black; padding: 10px; font-family: monospace; font-size: 12px; border: 1px solid #ccc;">
                            <h3 style="text-align:center; margin:0;">SAPPHIRE COLLECTION</h3>
                            <p style="text-align:center; margin:0;">Electronics & Textiles</p>
                            <p>--------------------------------</p>
                            <p>Date: {now.strftime("%Y-%m-%d %H:%M")}<br>Pay: {pay_method}</p>
                            <p>--------------------------------</p>
                            <p>Item: {prod_row['Product Name']}<br>Qty: {unit_qty}<br>Price: Rs. {sell_price}</p>
                            <p>Discount: Rs. {discount_rs:,.2f}</p>
                            <h4>TOTAL: Rs. {final_total:,.2f}</h4>
                            <p>--------------------------------</p>
                            <p style="text-align:center;">Thank You! Come Again.</p>
                        </div>
                        """
                        st.markdown(receipt_html, unsafe_allow_html=True)

    # ==================== 5. STOCK & ALERTS ====================
    elif st.session_state["current_page"] == "Stock":
        st.title("📊 Stock & Low Stock Warnings")
        df_products = load_data(PRODUCT_FILE)

        if not df_products.empty:
            st.subheader("⚠️ Low Stock Alerts (තොග අඩුවී ඇති භාණ්ඩ)")
            
            # නිවැරදි කරන ලද Low Stock Logic එක
            low_stock = df_products[
                ((df_products["Total Meter"] > 0) & (df_products["Total Meter"] <= df_products["Min Threshold"])) |
                ((df_products["Total Quantity (Pcs)"] > 0) & (df_products["Total Quantity (Pcs)"] <= df_products["Min Threshold"])) |
                ((df_products["Total Meter"] == 0) & (df_products["Total Quantity (Pcs)"] == 0))
            ]
            
            if not low_stock.empty:
                st.dataframe(low_stock[["Product Name", "Code", "Total Meter", "Total Quantity (Pcs)", "Min Threshold"]], use_container_width=True)
            else:
                st.success("සියලුම භාණ්ඩ ප්‍රමාණවත් ලෙස තොගයේ ඇත.")

            st.subheader("📋 Complete Stock")
            st.dataframe(df_products, use_container_width=True)

            # Export to CSV
            csv_data = df_products.to_csv(index=False).encode('utf-8')
            st.download_button("📊 Download Stock Report (CSV/Excel)", data=csv_data, file_name="Stock_Report.csv", mime="text/csv")

    # ==================== 6. REPORTS & NET PROFIT ====================
    elif st.session_state["current_page"] == "Reports":
        st.title("📈 Sales Reports & Net Profit")
        df_sales = load_data(SALES_FILE)
        df_expenses = load_data(EXPENSES_FILE)

        col_d1, col_d2 = st.columns(2)
        with col_d1: start_d = st.date_input("Start Date", value=date.today())
        with col_d2: end_d = st.date_input("End Date", value=date.today())

        if not df_sales.empty:
            df_sales["Date_dt"] = pd.to_datetime(df_sales["Date"]).dt.date
            mask = (df_sales["Date_dt"] >= start_d) & (df_sales["Date_dt"] <= end_d)
            filtered_s = df_sales.loc[mask]

            total_rev = filtered_s["Total Price"].sum() if not filtered_s.empty else 0
            gross_profit = filtered_s["Profit"].sum() if not filtered_s.empty else 0

            # Expenses in range
            total_exp = 0
            if not df_expenses.empty:
                df_expenses["Date_dt"] = pd.to_datetime(df_expenses["Date"]).dt.date
                filtered_e = df_expenses.loc[(df_expenses["Date_dt"] >= start_d) & (df_expenses["Date_dt"] <= end_d)]
                total_exp = filtered_e["Amount"].sum()

            net_profit = gross_profit - total_exp

            m1, m2, m3, m4 = st.columns(4)
            m1.metric("💰 මුළු ආදායම (Revenue)", f"Rs. {total_rev:,.2f}")
            m2.metric("📦 දළ ලාභය (Gross Profit)", f"Rs. {gross_profit:,.2f}")
            m3.metric("💸 මුළු වියදම් (Expenses)", f"Rs. {total_exp:,.2f}")
            m4.metric("🔥 නියම ශුද්ධ ලාභය (Net Profit)", f"Rs. {net_profit:,.2f}")

            st.dataframe(filtered_s, use_container_width=True)

            csv_sales = filtered_s.to_csv(index=False).encode('utf-8')
            st.download_button("📊 Download Sales Report (CSV)", data=csv_sales, file_name="Sales_Report.csv", mime="text/csv")

    # ==================== 7. SHOP EXPENSES ====================
    elif st.session_state["current_page"] == "Expenses":
        st.title("💸 Daily Shop Expenses Tracker")
        df_exp = load_data(EXPENSES_FILE)

        with st.form("add_exp"):
            exp_desc = st.text_input("Expense Description (උදා: ලයිට් බිල, ප්‍රවාහන වියදම්)")
            exp_amt = st.number_input("Amount (Rs.)", min_value=0.0)
            if st.form_submit_button("Add Expense"):
                if exp_desc and exp_amt > 0:
                    new_exp = {"Date": datetime.now().strftime("%Y-%m-%d"), "Description": exp_desc, "Amount": exp_amt}
                    df_exp = pd.concat([df_exp, pd.DataFrame([new_exp])], ignore_index=True)
                    save_data(df_exp, EXPENSES_FILE)
                    st.success("වියදම ඇතුළත් විය!")
                    st.rerun()

        st.subheader("📋 Expenses Log")
        st.dataframe(df_exp, use_container_width=True)

    # ==================== 8. CREDIT BOOK (UDARA BOOK) ====================
    elif st.session_state["current_page"] == "Credit Book":
        st.title("📖 Customer Credit Book (ණය පොත)")
        df_cred = load_data(CREDIT_FILE)

        if not df_cred.empty:
            st.dataframe(df_cred, use_container_width=True)
            sel_cust = st.selectbox("Settle Debt for Customer:", df_cred["Customer Name"].unique())
            if st.button("Settle / Clear Credit"):
                df_cred = df_cred[df_cred["Customer Name"] != sel_cust]
                save_data(df_cred, CREDIT_FILE)
                st.success("ණය ගෙවා අවසන් ලෙස සටහන් විය!")
                st.rerun()
        else:
            st.info("ණය හිඟ මුදල් නොමැත.")
