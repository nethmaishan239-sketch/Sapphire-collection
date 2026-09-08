import streamlit as st
import pandas as pd
import os
from datetime import datetime
import barcode
from barcode.writer import ImageWriter

# ==================== 1. PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="Sapphire Collection POS",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== 2. FILE PATHS SETUP ====================
PRODUCT_FILE = "products.csv"
SALES_FILE = "sales.csv"
EXPENSES_FILE = "expenses.csv"
CREDIT_FILE = "credit.csv"
CUSTOMER_FILE = "customers.csv"
SUPPLIER_FILE = "suppliers.csv"
RETURNS_FILE = "returns.csv"

# ==================== 3. FILE INITIALIZATION ====================
def init_files():
    if not os.path.exists(PRODUCT_FILE) or os.stat(PRODUCT_FILE).st_size == 0:
        df_p = pd.DataFrame(columns=[
            "Code", "Product Name", "Cost Price", "Selling Price", 
            "Total Meter", "Total Yard", "Total Quantity (Pcs)", 
            "Total Kg", "Total Liter", "Min Threshold", "Supplier", "Is_Deleted"
        ])
        df_p.to_csv(PRODUCT_FILE, index=False)

    if not os.path.exists(SALES_FILE) or os.stat(SALES_FILE).st_size == 0:
        df_s = pd.DataFrame(columns=[
            "Invoice ID", "Date", "Time", "Product Name", "Code", 
            "Meter Amount", "Yard Amount", "Quantity (Pcs)", "Kg Amount", "Liter Amount", 
            "Warranty", "Cost Price", "Selling Price", "Discount", "Points Used", 
            "Total Price", "Profit", "Payment Method", "Customer", "Is_Deleted"
        ])
        df_s.to_csv(SALES_FILE, index=False)

    if not os.path.exists(EXPENSES_FILE) or os.stat(EXPENSES_FILE).st_size == 0:
        df_e = pd.DataFrame(columns=["Date", "Description", "Amount", "Is_Deleted"])
        df_e.to_csv(EXPENSES_FILE, index=False)

    if not os.path.exists(CREDIT_FILE) or os.stat(CREDIT_FILE).st_size == 0:
        df_cr = pd.DataFrame(columns=["Customer Name", "Phone", "Due Balance", "Last Date", "Is_Deleted"])
        df_cr.to_csv(CREDIT_FILE, index=False)

    if not os.path.exists(CUSTOMER_FILE) or os.stat(CUSTOMER_FILE).st_size == 0:
        df_cu = pd.DataFrame(columns=["Customer Name", "Phone", "Loyalty Points", "Is_Deleted"])
        df_cu.to_csv(CUSTOMER_FILE, index=False)

    if not os.stat(SUPPLIER_FILE).st_size == 0 if os.path.exists(SUPPLIER_FILE) else True:
        df_su = pd.DataFrame(columns=["Supplier Name", "Phone", "Company", "Pending Payable", "Is_Deleted"])
        df_su.to_csv(SUPPLIER_FILE, index=False)

    if not os.path.exists(RETURNS_FILE) or os.stat(RETURNS_FILE).st_size == 0:
        df_re = pd.DataFrame(columns=["Date", "Invoice ID", "Product Name", "Code", "Returned Qty", "Refund Amount", "Reason"])
        df_re.to_csv(RETURNS_FILE, index=False)

init_files()

# ==================== 4. HELPER FUNCTIONS ====================
def load_data(file_path):
    try:
        if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
            return pd.DataFrame()
        
        df = pd.read_csv(file_path, dtype={"Code": str, "Phone": str, "Invoice ID": str})
        if "Is_Deleted" not in df.columns:
            df["Is_Deleted"] = False
            
        return df
    except Exception as e:
        st.error(f"Error loading {file_path}: {e}")
        return pd.DataFrame()

def save_data(df, file_path):
    try:
        df.to_csv(file_path, index=False)
    except Exception as e:
        st.error(f"Error saving to {file_path}: {e}")

# ==================== 5. SESSION STATE MANAGEMENT ====================
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False

if "user_role" not in st.session_state:
    st.session_state["user_role"] = None

if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Main Menu"

if "cart" not in st.session_state:
    st.session_state["cart"] = []

if "last_invoice" not in st.session_state:
    st.session_state["last_invoice"] = None

# ==================== 6. LOGIN PAGE UI ====================
if not st.session_state["logged_in"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #1E88E5;'>SAPPHIRE COLLECTION POS</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #555;'>Advanced Retail & Apparel Management System (වෙළඳසැල් කළමනාකරණ පද්ධතිය)</h4>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.subheader("🔐 User Authentication (පද්ධතියට ඇතුළු වීම)")
        role_selected = st.selectbox("Select Account Role (ගිණුම් වර්ගය):", ["Admin (පරිපාලක)", "Cashier (කැෂියර්)"])
        pwd_input = st.text_input("Enter Password (මුරපදය ඇතුළත් කරන්න):", type="password", key="login_pwd")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Login to System (ඇතුළු වන්න)", type="primary", use_container_width=True):
            if "Admin" in role_selected and pwd_input == "1234":
                st.session_state["logged_in"] = True
                st.session_state["user_role"] = "Admin"
                st.session_state["current_page"] = "Main Menu"
                st.success("Admin Login Successful!")
                st.rerun()
            elif "Cashier" in role_selected and pwd_input == "0000":
                st.session_state["logged_in"] = True
                st.session_state["user_role"] = "Cashier"
                st.session_state["current_page"] = "Main Menu"
                st.success("Cashier Login Successful!")
                st.rerun()
            else:
                st.error("❌ Invalid Password! Please try again.")

else:
    # ==================== 7. SYSTEM HEADER & NAVIGATION ====================
    top_col1, top_col2, top_col3 = st.columns([3, 2, 1])
    
    with top_col1:
        if st.session_state["current_page"] != "Main Menu":
            if st.button("⬅️ Back to Main Menu (ප්‍රධාන මෙනුවට)"):
                st.session_state["current_page"] = "Main Menu"
                st.rerun()
        else:
            st.write("📍 **Dashboard Overview (ප්‍රධාන පුවරුව)**")

    with top_col2:
        st.write(f"👤 Current User: **{st.session_state['user_role']}**")

    with top_col3:
        if st.button("🔒 Logout System"):
            st.session_state["logged_in"] = False
            st.session_state["user_role"] = None
            st.session_state["current_page"] = "Main Menu"
            st.rerun()

    st.markdown("---")

    # ==================== 8. MAIN MENU DASHBOARD ====================
    if st.session_state["current_page"] == "Main Menu":
        st.markdown("<h1 style='text-align: center; color: #333;'>💎 Sapphire Collection POS System</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Select a module below to proceed (අවශ්‍ය අංශය තෝරන්න)</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("📦 Inventory & Products (තොග සහ භාණ්ඩ)")
            if st.button("📦 Product Management (භාණ්ඩ කළමනාකරණය)", use_container_width=True):
                st.session_state["current_page"] = "Product"
                st.rerun()
            
            if st.button("📖 Udara Book - Credit Records (ණය පොත)", use_container_width=True):
                st.session_state["current_page"] = "Credit Book"
                st.rerun()

            if st.button("👥 Customer & Loyalty (පාරිභෝගිකයින්)", use_container_width=True):
                st.session_state["current_page"] = "Customers"
                st.rerun()

            if st.button("🏷️ Barcode Generator (බාර්කෝඩ් සෑදීම)", use_container_width=True):
                st.session_state["current_page"] = "Barcode"
                st.rerun()

        with col2:
            st.subheader("🧾 Sales & Billing (විකුණුම් සහ බිල්පත්)")
            if st.button("🧾 Bill Issue & Cashier Terminal (බිල්පත් නිකුත් කිරීම)", use_container_width=True):
                st.session_state["current_page"] = "Bill Issue"
                st.rerun()

            if st.button("🔄 Item Return System (භාණ්ඩ ආපසු බාරගැනීම)", use_container_width=True):
                st.session_state["current_page"] = "Returns"
                st.rerun()

            if st.session_state["user_role"] == "Admin":
                if st.button("💸 Shop Expense Tracker (වියදම් සටහන)", use_container_width=True):
                    st.session_state["current_page"] = "Expenses"
                    st.rerun()

        with col3:
            st.subheader("📊 Analytics & Admin (වාර්තා සහ පරිපාලනය)")
            if st.button("📊 Stock Levels & Reorder Alerts (තොග ප්‍රමාණයන්)", use_container_width=True):
                st.session_state["current_page"] = "Stock"
                st.rerun()

            if st.session_state["user_role"] == "Admin":
                if st.button("📈 Sales Reports & Profit Analytics (විකුණුම් වාර්තා)", use_container_width=True):
                    st.session_state["current_page"] = "Reports"
                    st.rerun()

                if st.button("🏭 Supplier Management (සැපයුම්කරුවන්)", use_container_width=True):
                    st.session_state["current_page"] = "Suppliers"
                    st.rerun()

        if st.session_state["user_role"] == "Admin":
            st.markdown("<br><hr>", unsafe_allow_html=True)
            if st.button("🗑️ Recycle Bin (මකන ලද දත්ත නැවත ලබාගැනීම / සම්පූර්ණයෙන්ම ඉවත් කිරීම)", use_container_width=True):
                st.session_state["current_page"] = "Recycle Bin"
                st.rerun()

    # ==================== 9. BARCODE GENERATOR MODULE ====================
    elif st.session_state["current_page"] == "Barcode":
        st.title("🏷️ Barcode Generator Engine")
        df_products = load_data(PRODUCT_FILE)
        active_products = df_products[df_products["Is_Deleted"] == False] if not df_products.empty else pd.DataFrame()

        if not active_products.empty:
            sel_p = st.selectbox("Select Product for Barcode:", active_products["Code"].astype(str) + " - " + active_products["Product Name"])
            code_to_gen = sel_p.split(" - ")[0]

            if st.button("Generate & Print Barcode Label"):
                try:
                    code128 = barcode.get_barcode_class('code128')
                    my_barcode = code128(code_to_gen, writer=ImageWriter())
                    filename = my_barcode.save(f"barcode_{code_to_gen}")
                    st.image(filename, caption=f"Generated Barcode ID: {code_to_gen}", width=300)
                except Exception as e:
                    st.error(f"Barcode Generation Failed: {e}")
        else:
            st.info("No active products available to generate barcodes.")

    # ==================== 10. PRODUCT MANAGEMENT MODULE ====================
    elif st.session_state["current_page"] == "Product":
        st.title("📦 Product & Inventory Management (භාණ්ඩ කළමනාකරණය)")
        df_products = load_data(PRODUCT_FILE)
        df_sup = load_data(SUPPLIER_FILE)
        
        active_products = df_products[df_products["Is_Deleted"] == False] if not df_products.empty else pd.DataFrame()
        active_sups = df_sup[df_sup["Is_Deleted"] == False]["Supplier Name"].tolist() if not df_sup.empty else ["Default Supplier"]

        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.subheader("➕ Add / Update Product Details")
            with st.form("add_product_form", clear_on_submit=True):
                p_code = st.text_input("🏷️ Product Code / Barcode ID").strip()
                p_name = st.text_input("📦 Product Name").strip()
                
                if st.session_state["user_role"] == "Admin":
                    p_cost = st.number_input("Cost Price (ගැනුම් මිල) (Rs.)", min_value=0.0, format="%.2f")
                else:
                    p_cost = 0.0

                p_sell = st.number_input("Selling Price (විකුණුම් මිල) (Rs.)", min_value=0.0, format="%.2f")
                p_sup = st.selectbox("Supplier (සැපයුම්කරු)", active_sups)

                st.markdown("---")
                st.write("**Stock Quantities across Measurement Units:**")
                col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns(5)
                p_meter = col_p1.number_input("Meters", min_value=0.0, step=0.5)
                p_yard = col_p2.number_input("Yards", min_value=0.0, step=0.5)
                p_qty = col_p3.number_input("Pcs", min_value=0.0, step=1.0)
                p_kg = col_p4.number_input("Kg", min_value=0.0, step=0.1)
                p_liter = col_p5.number_input("Liters", min_value=0.0, step=0.1)

                p_min = st.number_input("⚠️ Min Stock Reorder Alert Level", min_value=0.0, value=5.0)

                if st.form_submit_button("Save Product Record"):
                    if p_code and p_name:
                        new_row = pd.DataFrame([{
                            "Code": str(p_code), 
                            "Product Name": str(p_name), 
                            "Cost Price": float(p_cost),
                            "Selling Price": float(p_sell), 
                            "Total Meter": float(p_meter), 
                            "Total Yard": float(p_yard),
                            "Total Quantity (Pcs)": float(p_qty), 
                            "Total Kg": float(p_kg), 
                            "Total Liter": float(p_liter),
                            "Min Threshold": float(p_min), 
                            "Supplier": str(p_sup), 
                            "Is_Deleted": False
                        }])

                        if not df_products.empty and str(p_code) in df_products["Code"].astype(str).values:
                            df_products = df_products[df_products["Code"].astype(str) != str(p_code)]

                        df_products = pd.concat([df_products, new_row], ignore_index=True)

                        save_data(df_products, PRODUCT_FILE)
                        st.success("Product Saved Successfully!")
                        st.rerun()
                    else:
                        st.error("Please fill in both Code and Name fields!")

        with col_right:
            st.subheader("🗑️ Soft Delete Product")
            if not active_products.empty:
                del_p_sel = st.selectbox("Select Product to Move to Trash:", active_products["Code"].astype(str) + " - " + active_products["Product Name"])
                if st.button("🗑️ Move to Trash / Delete"):
                    code_to_del = del_p_sel.split(" - ")[0]
                    df_products.loc[df_products["Code"].astype(str) == code_to_del, "Is_Deleted"] = True
                    save_data(df_products, PRODUCT_FILE)
                    st.warning("Product moved to Recycle Bin!")
                    st.rerun()

        st.markdown("---")
        st.subheader("📋 Active Product Catalogue")
        if not active_products.empty:
            st.dataframe(
                active_products[["Code", "Product Name", "Cost Price", "Selling Price", "Total Meter", "Total Yard", "Total Quantity (Pcs)", "Total Kg", "Total Liter", "Supplier"]], 
                use_container_width=True
            )
        else:
            st.info("No active products available in system.")

    # ==================== 11. BILL ISSUE & CASHIER TERMINAL ====================
    elif st.session_state["current_page"] == "Bill Issue":
        st.title("🧾 Bill Issue & Cashier Terminal (බිල්පත් නිකුත් කිරීම)")
        df_products = load_data(PRODUCT_FILE)
        active_products = df_products[df_products["Is_Deleted"] == False] if not df_products.empty else pd.DataFrame()

        if not active_products.empty:
            col_left, col_right = st.columns([1.1, 0.9])

            with col_left:
                st.subheader("🔍 Select & Add Items")
                search_query = st.text_input("Scan Barcode or Type Product Name/Code:").strip()
                
                if search_query:
                    filtered = active_products[
                        active_products["Code"].astype(str).str.contains(search_query, case=False, na=False) |
                        active_products["Product Name"].str.contains(search_query, case=False, na=False)
                    ]
                else:
                    filtered = active_products

                if not filtered.empty:
                    sel_prod = st.selectbox("Select Product Item:", filtered["Code"].astype(str) + " - " + filtered["Product Name"])
                    sel_code = sel_prod.split(" - ")[0]
                    prod_row = filtered[filtered["Code"].astype(str) == sel_code].iloc[0]

                    st.success(f"Selling Price: **Rs. {float(prod_row['Selling Price']):,.2f}**")

                    st.write("Enter Quantities to Add:")
                    col_b1, col_b2, col_b3, col_b4, col_b5 = st.columns(5)
                    sell_m = col_b1.number_input("Meter:", min_value=0.0, step=0.1)
                    sell_y = col_b2.number_input("Yard:", min_value=0.0, step=0.1)
                    sell_q = col_b3.number_input("Pcs:", min_value=0.0, step=1.0)
                    sell_kg = col_b4.number_input("Kg:", min_value=0.0, step=0.05)
                    sell_l = col_b5.number_input("Liter:", min_value=0.0, step=0.05)

                    warranty_val = st.selectbox("Warranty Period:", ["No Warranty", "6 Months", "1 Year", "2 Years", "3 Years"])
                    unit_qty = sell_m + sell_y + sell_q + sell_kg + sell_l
                    item_total = unit_qty * float(prod_row["Selling Price"])

                    st.markdown(f"#### Calculated Item Total: **Rs. {item_total:,.2f}**")

                    if st.button("🛒 Add Item to Cart", use_container_width=True):
                        if unit_qty > 0:
                            st.session_state["cart"].append({
                                "Code": sel_code,
                                "Product Name": prod_row["Product Name"],
                                "Cost Price": float(prod_row["Cost Price"]),
                                "Selling Price": float(prod_row["Selling Price"]),
                                "Meter Amount": sell_m,
                                "Yard Amount": sell_y,
                                "Quantity (Pcs)": sell_q,
                                "Kg Amount": sell_kg,
                                "Liter Amount": sell_l,
                                "Total Qty": unit_qty,
                                "Warranty": warranty_val,
                                "Total Price": item_total,
                                "Profit": item_total - (unit_qty * float(prod_row["Cost Price"]))
                            })
                            st.success("Item added to cart!")
                            st.rerun()
                        else:
                            st.warning("Please specify quantity before adding to cart!")

            with col_right:
                st.subheader("🛍️ Customer Shopping Cart")
                if len(st.session_state["cart"]) > 0:
                    subtotal = 0.0
                    
                    c_h1, c_h2, c_h3, c_h4 = st.columns([2.5, 1, 1.5, 0.8])
                    c_h1.write("**Product Name**")
                    c_h2.write("**Qty**")
                    c_h3.write("**Total (Rs.)**")
                    c_h4.write("**Remove**")
                    st.markdown("---")

                    for idx, item in enumerate(st.session_state["cart"]):
                        c1, c2, c3, c4 = st.columns([2.5, 1, 1.5, 0.8])
                        c1.write(item["Product Name"])
                        c2.write(f"{item['Total Qty']}")
                        c3.write(f"{item['Total Price']:,.2f}")
                        
                        if c4.button("🗑️", key=f"del_cart_{idx}"):
                            st.session_state["cart"].pop(idx)
                            st.rerun()

                        subtotal += item["Total Price"]

                    st.markdown("---")
                    st.markdown(f"### 💰 Bill Grand Total: Rs. {subtotal:,.2f}")

                    if st.button("🗑️ Clear Entire Cart", type="secondary"):
                        st.session_state["cart"] = []
                        st.rerun()

                    st.markdown("---")
                    cust_phone = st.text_input("📱 Customer Phone Number (Optional):")
                    pay_method = st.selectbox("Payment Method:", ["Cash", "Card", "Online Transfer", "Credit"])

                    if st.button("✅ Checkout & Print Receipt", type="primary", use_container_width=True):
                        inv_id = datetime.now().strftime("INV%Y%m%d%H%M%S")
                        now_str = datetime.now().strftime("%Y-%m-%d")
                        
                        df_sales = load_data(SALES_FILE)

                        for item in st.session_state["cart"]:
                            p_code_val = item["Code"]
                            
                            if p_code_val in df_products["Code"].astype(str).values:
                                p_idx = df_products[df_products["Code"].astype(str) == p_code_val].index[0]
                                df_products.loc[p_idx, "Total Meter"] = max(0.0, float(df_products.loc[p_idx, "Total Meter"]) - item["Meter Amount"])
                                df_products.loc[p_idx, "Total Yard"] = max(0.0, float(df_products.loc[p_idx, "Total Yard"]) - item["Yard Amount"])
                                df_products.loc[p_idx, "Total Quantity (Pcs)"] = max(0.0, float(df_products.loc[p_idx, "Total Quantity (Pcs)"]) - item["Quantity (Pcs)"])
                                df_products.loc[p_idx, "Total Kg"] = max(0.0, float(df_products.loc[p_idx, "Total Kg"]) - item["Kg Amount"])
                                df_products.loc[p_idx, "Total Liter"] = max(0.0, float(df_products.loc[p_idx, "Total Liter"]) - item["Liter Amount"])

                            new_sale = item.copy()
                            new_sale.update({
                                "Invoice ID": inv_id,
                                "Date": now_str,
                                "Time": datetime.now().strftime("%H:%M:%S"),
                                "Discount": 0,
                                "Points Used": 0,
                                "Payment Method": pay_method,
                                "Customer": cust_phone if cust_phone else "Guest",
                                "Is_Deleted": False
                            })
                            df_sales = pd.concat([df_sales, pd.DataFrame([new_sale])], ignore_index=True)

                        save_data(df_products, PRODUCT_FILE)
                        save_data(df_sales, SALES_FILE)

                        st.session_state["last_invoice"] = {
                            "id": inv_id,
                            "date": now_str,
                            "items": st.session_state["cart"],
                            "total": subtotal,
                            "payment": pay_method
                        }

                        st.session_state["cart"] = []
                        st.success("✅ Sale Processed Successfully!")
                        st.rerun()
                else:
                    st.info("Cart is currently empty.")

        if st.session_state.get("last_invoice"):
            st.markdown("---")
            st.subheader("🖨️ Printable Thermal Receipt")
            inv = st.session_state["last_invoice"]
            
            receipt_html = f"""
            <div style="width: 300px; padding: 15px; border: 1px dashed #333; font-family: monospace; background: #fff; color: #000;">
                <h3 style="text-align: center; margin: 0;">SAPPHIRE COLLECTION</h3>
                <p style="text-align: center; margin: 0;">No. 123, Main Street, City</p>
                <p style="text-align: center; margin: 0;">Tel: 077-1234567</p>
                <hr style="border-top: 1px dashed #000;">
                <p><b>Invoice:</b> {inv['id']}<br><b>Date:</b> {inv['date']}</p>
                <hr style="border-top: 1px dashed #000;">
            """
            for it in inv['items']:
                receipt_html += f"<div>{it['Product Name']} x {it['Total Qty']}<span style='float:right;'>Rs.{it['Total Price']:,.2f}</span></div>"
            
            receipt_html += f"""
                <hr style="border-top: 1px dashed #000;">
                <h4><b>TOTAL: <span style="float:right;">Rs.{inv['total']:,.2f}</span></b></h4>
                <p>Payment: {inv['payment']}</p>
                <hr style="border-top: 1px dashed #000;">
                <p style="text-align: center;">Thank You Come Again!</p>
            </div>
            """
            st.components.v1.html(receipt_html, height=400)

    # ==================== 12. REPORTS & FINANCIAL ANALYTICS ====================
    elif st.session_state["current_page"] == "Reports":
        st.title("📈 Sales Reports & Business Analytics (විකුණුම් වාර්තා)")

        df_sales = load_data(SALES_FILE)
        df_exp = load_data(EXPENSES_FILE)

        active_sales = df_sales[df_sales["Is_Deleted"] == False] if not df_sales.empty and "Is_Deleted" in df_sales.columns else df_sales

        if not active_sales.empty:
            st.subheader("📊 Revenue Analytics Trend")
            daily_sales = active_sales.groupby("Date")["Total Price"].sum()
            st.line_chart(daily_sales)

            m1, m2, m3, m4 = st.columns(4)
            total_rev = active_sales['Total Price'].sum()
            total_prof = active_sales['Profit'].sum()
            total_exp = df_exp['Amount'].sum() if not df_exp.empty else 0.0
            net_profit = total_prof - total_exp

            m1.metric("💰 Gross Revenue", f"Rs. {total_rev:,.2f}")
            m2.metric("📦 Gross Profit", f"Rs. {total_prof:,.2f}")
            m3.metric("💸 Shop Expenses", f"Rs. {total_exp:,.2f}")
            m4.metric("💵 Net Profit", f"Rs. {net_profit:,.2f}")

            st.markdown("---")
            st.subheader("📜 Detailed Sales Transaction History")
            st.dataframe(
                active_sales[["Invoice ID", "Date", "Time", "Product Name", "Total Price", "Profit", "Payment Method", "Customer"]],
                use_container_width=True
            )
        else:
            st.info("No sales records available to generate analytics.")

    # ==================== 13. STOCK LEVELS & REORDER ALERTS ====================
    elif st.session_state["current_page"] == "Stock":
        st.title("📊 Stock Inventory & Reorder Warnings")
        df_p = load_data(PRODUCT_FILE)
        active_p = df_p[df_p["Is_Deleted"] == False] if not df_p.empty else pd.DataFrame()

        if not active_p.empty:
            low_stock = active_p[
                (active_p["Total Meter"] <= active_p["Min Threshold"]) &
                (active_p["Total Quantity (Pcs)"] <= active_p["Min Threshold"]) &
                (active_p["Total Kg"] <= active_p["Min Threshold"]) &
                (active_p["Total Liter"] <= active_p["Min Threshold"])
            ]
            if not low_stock.empty:
                st.error("⚠️ Low Stock Alert (ප්‍රමාණය අඩු වී ඇති භාණ්ඩ):")
                st.dataframe(
                    low_stock[["Code", "Product Name", "Total Meter", "Total Quantity (Pcs)", "Total Kg", "Total Liter", "Min Threshold", "Supplier"]], 
                    use_container_width=True
                )

            st.markdown("---")
            st.subheader("📦 Complete Inventory Stock Table")
            st.dataframe(
                active_p[["Code", "Product Name", "Total Meter", "Total Yard", "Total Quantity (Pcs)", "Total Kg", "Total Liter", "Min Threshold", "Supplier"]], 
                use_container_width=True
            )
        else:
            st.info("No stock data available.")

    # ==================== 14. EXPENSE TRACKER ====================
    elif st.session_state["current_page"] == "Expenses":
        st.title("💸 Shop Expense Tracker (වියදම් සටහන)")
        df_exp = load_data(EXPENSES_FILE)

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("➕ Record New Expense")
            with st.form("add_exp_form", clear_on_submit=True):
                exp_desc = st.text_input("Expense Description (විස්තරය)")
                exp_amt = st.number_input("Amount (වටිනාකම Rs.)", min_value=0.0, format="%.2f")

                if st.form_submit_button("Save Expense Entry"):
                    if exp_desc and exp_amt > 0:
                        new_e = {"Date": datetime.now().strftime("%Y-%m-%d"), "Description": exp_desc, "Amount": exp_amt, "Is_Deleted": False}
                        df_exp = pd.concat([df_exp, pd.DataFrame([new_e])], ignore_index=True)
                        save_data(df_exp, EXPENSES_FILE)
                        st.success("Expense Entry Saved!")
                        st.rerun()

        with col2:
            st.subheader("📜 Expense Log")
            if not df_exp.empty:
                st.dataframe(df_exp[df_exp["Is_Deleted"] == False][["Date", "Description", "Amount"]], use_container_width=True)

    # ==================== 15. SUPPLIER MANAGEMENT ====================
    elif st.session_state["current_page"] == "Suppliers":
        st.title("🏭 Supplier Management System")
        df_sup = load_data(SUPPLIER_FILE)

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("➕ Register New Supplier")
            with st.form("add_sup_form", clear_on_submit=True):
                sup_n = st.text_input("Supplier Name")
                sup_p = st.text_input("Contact Phone Number")
                sup_c = st.text_input("Company / Brand Name")

                if st.form_submit_button("Register Supplier"):
                    if sup_n:
                        new_s = {"Supplier Name": sup_n, "Phone": sup_p, "Company": sup_c, "Pending Payable": 0.0, "Is_Deleted": False}
                        df_sup = pd.concat([df_sup, pd.DataFrame([new_s])], ignore_index=True)
                        save_data(df_sup, SUPPLIER_FILE)
                        st.success("Supplier Registered!")
                        st.rerun()

        with col2:
            st.subheader("📋 Registered Suppliers Directory")
            if not df_sup.empty:
                st.dataframe(df_sup[df_sup["Is_Deleted"] == False][["Supplier Name", "Phone", "Company"]], use_container_width=True)

    # ==================== 16. UDARA BOOK (CREDIT LEDGER) FIXED ====================
    elif st.session_state["current_page"] == "Credit Book":
        st.title("📖 Udara Book - Customer Credit Ledger (ණය පොත)")
        df_credit = load_data(CREDIT_FILE)
        active_credit = df_credit[df_credit["Is_Deleted"] == False] if not df_credit.empty else pd.DataFrame()

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("➕ Record New Credit / Add Due")
            with st.form("add_credit_form", clear_on_submit=True):
                c_name = st.text_input("Customer Name (පාරිභෝගික නම)").strip()
                c_phone = st.text_input("Phone Number (දුරකථන අංකය)").strip()
                c_due = st.number_input("Credit Amount to Add (ණය මුදල Rs.)", min_value=0.0, format="%.2f")

                if st.form_submit_button("Save Ledger Entry"):
                    if c_name and c_due > 0:
                        # Case-insensitive Name Matching
                        existing_match = df_credit[
                            (df_credit["Customer Name"].str.lower() == c_name.lower()) & 
                            (df_credit["Is_Deleted"] == False)
                        ]
                        
                        if not existing_match.empty:
                            idx = existing_match.index[0]
                            df_credit.loc[idx, "Due Balance"] = float(df_credit.loc[idx, "Due Balance"]) + float(c_due)
                            df_credit.loc[idx, "Last Date"] = datetime.now().strftime("%Y-%m-%d")
                        else:
                            new_cred = {
                                "Customer Name": str(c_name), 
                                "Phone": str(c_phone), 
                                "Due Balance": float(c_due), 
                                "Last Date": datetime.now().strftime("%Y-%m-%d"), 
                                "Is_Deleted": False
                            }
                            df_credit = pd.concat([df_credit, pd.DataFrame([new_cred])], ignore_index=True)
                        
                        save_data(df_credit, CREDIT_FILE)
                        st.success("Credit Entry Saved Successfully!")
                        st.rerun()

        with col2:
            st.subheader("💵 Settle / Pay Due Balance (ණය ගෙවීම)")
            # ණය මුදලක් (Due Balance > 0) ඇති අය පමණක් තේරීම
            pending_credits = active_credit[active_credit["Due Balance"] > 0] if not active_credit.empty else pd.DataFrame()
            
            if not pending_credits.empty:
                with st.form("settle_credit_form", clear_on_submit=True):
                    cust_options = pending_credits["Customer Name"].tolist()
                    sel_cust = st.selectbox("Select Customer to Settle:", cust_options)
                    
                    curr_due = float(pending_credits[pending_credits["Customer Name"] == sel_cust]["Due Balance"].iloc[0])
                    st.info(f"Current Balance Due for **{sel_cust}**: **Rs. {curr_due:,.2f}**")
                    
                    pay_amt = st.number_input("Paid Amount by Customer (ගෙවන ලද මුදල Rs.)", min_value=0.0, max_value=curr_due, format="%.2f")

                    if st.form_submit_button("✅ Deduct Paid Amount (ණය මුදලින් අඩු කරන්න)"):
                        if pay_amt > 0:
                            idx = df_credit[(df_credit["Customer Name"] == sel_cust) & (df_credit["Is_Deleted"] == False)].index[0]
                            new_bal = curr_due - pay_amt
                            df_credit.loc[idx, "Due Balance"] = new_bal
                            df_credit.loc[idx, "Last Date"] = datetime.now().strftime("%Y-%m-%d")
                            
                            save_data(df_credit, CREDIT_FILE)
                            st.success(f"Payment Recorded! Remaining Balance: Rs. {new_bal:,.2f}")
                            st.rerun()
            else:
                st.info("🎉 No pending customer credits to settle! (සියලු ණය ගෙවා අවසන්)")

        st.markdown("---")
        st.subheader("📋 Active Customer Credit Records Log")
        if not active_credit.empty:
            st.dataframe(active_credit[["Customer Name", "Phone", "Due Balance", "Last Date"]], use_container_width=True)

    # ==================== 17. CUSTOMER & LOYALTY ====================
    elif st.session_state["current_page"] == "Customers":
        st.title("👥 Customer Loyalty & Directory")
        df_cust = load_data(CUSTOMER_FILE)

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("➕ Register Customer Profile")
            with st.form("add_cust_form", clear_on_submit=True):
                cust_n = st.text_input("Customer Full Name")
                cust_p = st.text_input("Mobile Number")

                if st.form_submit_button("Register Customer"):
                    if cust_n:
                        new_c = {"Customer Name": cust_n, "Phone": cust_p, "Loyalty Points": 0, "Is_Deleted": False}
                        df_cust = pd.concat([df_cust, pd.DataFrame([new_c])], ignore_index=True)
                        save_data(df_cust, CUSTOMER_FILE)
                        st.success("Customer Profile Created!")
                        st.rerun()

        with col2:
            st.subheader("📋 Registered Customer Directory")
            if not df_cust.empty:
                st.dataframe(df_cust[df_cust["Is_Deleted"] == False][["Customer Name", "Phone", "Loyalty Points"]], use_container_width=True)

    # ==================== 18. ITEM RETURNS SYSTEM (FIXED & FULLY WORKING) ====================
    elif st.session_state["current_page"] == "Returns":
        st.title("🔄 Item Return & Refund Processing")
        df_sales = load_data(SALES_FILE)
        df_products = load_data(PRODUCT_FILE)
        df_returns = load_data(RETURNS_FILE)

        inv_search = st.text_input("Enter Invoice ID to Search Transaction:").strip()
        if inv_search:
            matched = df_sales[df_sales["Invoice ID"] == inv_search] if not df_sales.empty else pd.DataFrame()
            if not matched.empty:
                st.subheader("Invoice Items Found:")
                st.dataframe(matched[["Product Name", "Code", "Selling Price", "Meter Amount", "Yard Amount", "Quantity (Pcs)", "Kg Amount", "Liter Amount", "Total Price"]], use_container_width=True)

                with st.form("process_return_form"):
                    ret_p = st.selectbox("Select Item to Return:", matched["Code"].astype(str) + " - " + matched["Product Name"])
                    sel_code = ret_p.split(" - ")[0]
                    item_matched = matched[matched["Code"].astype(str) == sel_code].iloc[0]

                    st.write("**Specify Units to Return / Restock:**")
                    col_r1, col_r2, col_r3, col_r4, col_r5 = st.columns(5)
                    ret_m = col_r1.number_input("Meter:", min_value=0.0, max_value=float(item_matched.get("Meter Amount", 0)), step=0.1)
                    ret_y = col_r2.number_input("Yard:", min_value=0.0, max_value=float(item_matched.get("Yard Amount", 0)), step=0.1)
                    ret_q = col_r3.number_input("Pcs:", min_value=0.0, max_value=float(item_matched.get("Quantity (Pcs)", 0)), step=1.0)
                    ret_kg = col_r4.number_input("Kg:", min_value=0.0, max_value=float(item_matched.get("Kg Amount", 0)), step=0.05)
                    ret_l = col_r5.number_input("Liter:", min_value=0.0, max_value=float(item_matched.get("Liter Amount", 0)), step=0.05)

                    ret_qty_total = ret_m + ret_y + ret_q + ret_kg + ret_l
                    refund_amt = ret_qty_total * float(item_matched["Selling Price"])
                    
                    st.info(f"Calculated Refund Amount: **Rs. {refund_amt:,.2f}**")
                    ret_reason = st.text_area("Reason for Return / Refund:")

                    if st.form_submit_button("✅ Process Return & Restock Product"):
                        if ret_qty_total > 0:
                            # 1. Update Product Stock (Restock)
                            if sel_code in df_products["Code"].astype(str).values:
                                p_idx = df_products[df_products["Code"].astype(str) == sel_code].index[0]
                                df_products.loc[p_idx, "Total Meter"] = float(df_products.loc[p_idx, "Total Meter"]) + ret_m
                                df_products.loc[p_idx, "Total Yard"] = float(df_products.loc[p_idx, "Total Yard"]) + ret_y
                                df_products.loc[p_idx, "Total Quantity (Pcs)"] = float(df_products.loc[p_idx, "Total Quantity (Pcs)"]) + ret_q
                                df_products.loc[p_idx, "Total Kg"] = float(df_products.loc[p_idx, "Total Kg"]) + ret_kg
                                df_products.loc[p_idx, "Total Liter"] = float(df_products.loc[p_idx, "Total Liter"]) + ret_l
                                save_data(df_products, PRODUCT_FILE)

                            # 2. Add Entry to returns.csv
                            new_return = {
                                "Date": datetime.now().strftime("%Y-%m-%d"),
                                "Invoice ID": inv_search,
                                "Product Name": item_matched["Product Name"],
                                "Code": sel_code,
                                "Returned Qty": ret_qty_total,
                                "Refund Amount": refund_amt,
                                "Reason": ret_reason
                            }
                            df_returns = pd.concat([df_returns, pd.DataFrame([new_return])], ignore_index=True)
                            save_data(df_returns, RETURNS_FILE)

                            st.success(f"Return Processed! Product Restocked and Rs. {refund_amt:,.2f} Refunded.")
                            st.rerun()
                        else:
                            st.warning("Please specify return quantity greater than zero.")
            else:
                st.error("No invoice records found for the given ID.")

        st.markdown("---")
        st.subheader("📜 Return History Log")
        if not df_returns.empty:
            st.dataframe(df_returns, use_container_width=True)

    # ==================== 19. RECYCLE BIN (FIXED RESTORE & DELETE) ====================
    elif st.session_state["current_page"] == "Recycle Bin":
        st.title("🗑️ System Recycle Bin & Data Management")
        df_p = load_data(PRODUCT_FILE)
        deleted_p = df_p[df_p["Is_Deleted"] == True] if not df_p.empty else pd.DataFrame()

        if not deleted_p.empty:
            st.subheader("Deleted Product Records:")
            st.dataframe(deleted_p[["Code", "Product Name", "Selling Price", "Supplier"]], use_container_width=True)
            
            res_code = st.selectbox("Select Product:", deleted_p["Code"].astype(str) + " - " + deleted_p["Product Name"])
            code_val = res_code.split(" - ")[0]

            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("🔄 Restore Selected Product", use_container_width=True):
                    df_p.loc[df_p["Code"].astype(str) == code_val, "Is_Deleted"] = False
                    save_data(df_p, PRODUCT_FILE)
                    st.success("Product successfully restored to active catalogue!")
                    st.rerun()

            with col_btn2:
                if st.button("❌ Permanently Delete Product", type="primary", use_container_width=True):
                    df_p = df_p[df_p["Code"].astype(str) != code_val]
                    save_data(df_p, PRODUCT_FILE)
                    st.warning("Product permanently deleted from database!")
                    st.rerun()
        else:
            st.info("Recycle bin is completely empty.")
