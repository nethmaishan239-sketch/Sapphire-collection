import streamlit as st
import pandas as pd
import os
from datetime import datetime
import barcode
from barcode.writer import ImageWriter
import streamlit.components.v1 as components

# ==================== 1. PAGE CONFIGURATION (පිටු සැකසුම) ====================
st.set_page_config(
    page_title="Sapphire Collection POS",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== 2. FILE PATHS SETUP (ගොනු මාර්ග) ====================
PRODUCT_FILE = "products.csv"
SALES_FILE = "sales.csv"
EXPENSES_FILE = "expenses.csv"
CREDIT_FILE = "credit.csv"
CUSTOMER_FILE = "customers.csv"
SUPPLIER_FILE = "suppliers.csv"
RETURNS_FILE = "returns.csv"

# ==================== 3. FILE INITIALIZATION (ගොනු ආරම්භ කිරීම) ====================
def init_files():
    if not os.path.exists(PRODUCT_FILE) or os.stat(PRODUCT_FILE).st_size == 0:
        df_p = pd.DataFrame(columns=[
            "Code", "Product Name", "Cost Price", "Selling Price", 
            "Total Meter", "Total Yard", "Total Quantity (Pcs)", 
            "Total Kg", "Total Liter", "Min Threshold", "Supplier", "Is_Deleted"
        ])
        df_p.to_csv(PRODUCT_FILE, index=False)

    if not os.stat(SALES_FILE).st_size == 0 if os.path.exists(SALES_FILE) else True:
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

    if not os.path.exists(SUPPLIER_FILE) or os.stat(SUPPLIER_FILE).st_size == 0:
        df_su = pd.DataFrame(columns=["Supplier Name", "Phone", "Company", "Pending Payable", "Is_Deleted"])
        df_su.to_csv(SUPPLIER_FILE, index=False)

    if not os.path.exists(RETURNS_FILE) or os.stat(RETURNS_FILE).st_size == 0:
        df_re = pd.DataFrame(columns=["Date", "Invoice ID", "Product Name", "Code", "Returned Qty", "Refund Amount", "Reason"])
        df_re.to_csv(RETURNS_FILE, index=False)

init_files()

# ==================== 4. HELPER FUNCTIONS (උපකාරක ශ්‍රිත) ====================
def load_data(file_path):
    try:
        df = pd.read_csv(file_path, dtype={"Code": str, "Phone": str})
        if "Is_Deleted" not in df.columns:
            df["Is_Deleted"] = False
        # Missing columns fix for new metrics
        for col in ["Total Kg", "Total Liter"]:
            if col not in df.columns and file_path == PRODUCT_FILE:
                df[col] = 0.0
        return df
    except Exception as e:
        st.error(f"Error loading {file_path}: {e}")
        return pd.DataFrame()

def save_data(df, file_path):
    try:
        df.to_csv(file_path, index=False)
    except Exception as e:
        st.error(f"Error saving to {file_path}: {e}")

# ==================== 5. SESSION STATE (සෙෂන් ස්ටේට්) ====================
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

# ==================== 6. LOGIN PAGE (ඇතුළු වීමේ පිටුව) ====================
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
                st.success("Admin Login Successful! (සාර්ථකව ඇතුළු විය)")
                st.rerun()
            elif "Cashier" in role_selected and pwd_input == "0000":
                st.session_state["logged_in"] = True
                st.session_state["user_role"] = "Cashier"
                st.session_state["current_page"] = "Main Menu"
                st.success("Cashier Login Successful! (සාර්ථකව ඇතුළු විය)")
                st.rerun()
            else:
                st.error("❌ Invalid Password! Please try again. (වැරදි මුරපදයකි!)")

else:
    # ==================== 7. HEADER & NAVIGATION (ඉහළ තීරුව) ====================
    top_col1, top_col2, top_col3 = st.columns([3, 2, 1])
    
    with top_col1:
        if st.session_state["current_page"] != "Main Menu":
            if st.button("⬅️ Back to Main Menu (ප්‍රධාන මෙනුවට)"):
                st.session_state["current_page"] = "Main Menu"
                st.rerun()
        else:
            st.write("📍 **Dashboard Overview (ප්‍රධාන පුවරුව)**")

    with top_col2:
        st.write(f"👤 Current User (පරිශීලක): **{st.session_state['user_role']}**")

    with top_col3:
        if st.button("🔒 Logout System (ඉවත් වන්න)"):
            st.session_state["logged_in"] = False
            st.session_state["user_role"] = None
            st.session_state["current_page"] = "Main Menu"
            st.rerun()

    st.markdown("---")

    # ==================== 🏠 MAIN MENU (ප්‍රධාන මෙනුව) ====================
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
            if st.button("🗑️ Recycle Bin (මකන ලද දත්ත නැවත ලබාගැනීම)", use_container_width=True):
                st.session_state["current_page"] = "Recycle Bin"
                st.rerun()

    # ==================== 🏷️ BARCODE GENERATOR (බාර්කෝඩ් සෑදීම) ====================
    elif st.session_state["current_page"] == "Barcode":
        st.title("🏷️ Barcode Generator Engine (බාර්කෝඩ් නිර්මාණය)")
        st.write("Generate printable Code128 barcodes for inventory tags (භාණ්ඩ සඳහා බාර්කෝඩ් සාදන්න).")

        df_products = load_data(PRODUCT_FILE)
        active_products = df_products[df_products["Is_Deleted"] == False] if not df_products.empty else pd.DataFrame()

        if not active_products.empty:
            sel_p = st.selectbox("Select Product to Generate Barcode (භාණ්ඩය තෝරන්න):", active_products["Code"].astype(str) + " - " + active_products["Product Name"])
            code_to_gen = sel_p.split(" - ")[0]

            col_bc1, col_bc2 = st.columns([1, 2])
            with col_bc1:
                if st.button("Generate Barcode Label (බාර්කෝඩ් එක සාදන්න)"):
                    try:
                        code128 = barcode.get_barcode_class('code128')
                        my_barcode = code128(code_to_gen, writer=ImageWriter())
                        filename = my_barcode.save(f"barcode_{code_to_gen}")
                        
                        st.image(filename, caption=f"Barcode: {code_to_gen}", width=300)
                        
                        with open(filename, "rb") as file:
                            st.download_button(
                                label="📥 Download Image Label (බාගත කරන්න)",
                                data=file,
                                file_name=f"barcode_{code_to_gen}.png",
                                mime="image/png"
                            )
                    except Exception as e:
                        st.error(f"Barcode Generation Failed: {e}")
        else:
            st.warning("No active products available to generate barcodes (භාණ්ඩ නොමැත).")

    # ==================== 📦 PRODUCT MANAGEMENT (භාණ්ඩ කළමනාකරණය) ====================
    elif st.session_state["current_page"] == "Product":
        st.title("📦 Product & Inventory Management (භාණ්ඩ සහ තොග කළමනාකරණය)")
        
        df_products = load_data(PRODUCT_FILE)
        df_sup = load_data(SUPPLIER_FILE)
        
        active_products = df_products[df_products["Is_Deleted"] == False] if not df_products.empty else pd.DataFrame()
        active_sups = df_sup[df_sup["Is_Deleted"] == False]["Supplier Name"].tolist() if not df_sup.empty else ["Default Supplier"]

        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.subheader("➕ Add / Update Product Item (නව භාණ්ඩ ඇතුළත් කිරීම/වෙනස් කිරීම)")
            with st.form("add_product_form", clear_on_submit=True):
                p_code = st.text_input("🏷️ Product Code / Barcode ID (භාණ්ඩ කේතය)").strip()
                p_name = st.text_input("📦 Product Name (භාණ්ඩයේ නම)").strip()
                
                if st.session_state["user_role"] == "Admin":
                    p_cost = st.number_input("Cost Price - ගත් මිල (Rs.)", min_value=0.0, format="%.2f")
                else:
                    p_cost = 0.0

                p_sell = st.number_input("Selling Price - විකුණුම් මිල (Rs.)", min_value=0.0, format="%.2f")
                p_sup = st.selectbox("Supplier (සැපයුම්කරු)", active_sups)

                st.write("---")
                st.write("📐 **Stock Quantities (තොග ප්‍රමාණයන්)**")
                col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns(5)
                with col_p1:
                    p_meter = st.number_input("Meters (මීටර්)", min_value=0.0, step=0.5)
                with col_p2:
                    p_yard = st.number_input("Yards (යාර්ඩ්)", min_value=0.0, step=0.5)
                with col_p3:
                    p_qty = st.number_input("Pcs (කෑලි)", min_value=0.0, step=1.0)
                with col_p4:
                    p_kg = st.number_input("Kg (කිලෝ)", min_value=0.0, step=0.1)
                with col_p5:
                    p_liter = st.number_input("Liters (ලීටර්)", min_value=0.0, step=0.1)

                p_min = st.number_input("⚠️ Minimum Stock Alert Level (අවම තොග සීමාව)", min_value=0.0, value=5.0)

                if st.form_submit_button("Save Product to Database (සුරකින්න)"):
                    if p_code and p_name:
                        new_data = {
                            "Code": p_code,
                            "Product Name": p_name,
                            "Cost Price": p_cost,
                            "Selling Price": p_sell,
                            "Total Meter": p_meter,
                            "Total Yard": p_yard,
                            "Total Quantity (Pcs)": p_qty,
                            "Total Kg": p_kg,
                            "Total Liter": p_liter,
                            "Min Threshold": p_min,
                            "Supplier": p_sup,
                            "Is_Deleted": False
                        }
                        
                        if not df_products.empty and p_code in df_products["Code"].astype(str).values:
                            df_products.loc[df_products["Code"].astype(str) == p_code] = new_data
                            st.success(f"Product '{p_name}' Updated Successfully! (යාවත්කාලීන විය)")
                        else:
                            df_products = pd.concat([df_products, pd.DataFrame([new_data])], ignore_index=True)
                            st.success(f"New Product '{p_name}' Saved Successfully! (සුරකින ලදී)")

                        save_data(df_products, PRODUCT_FILE)
                        st.rerun()
                    else:
                        st.error("Please enter both Product Code and Name. (කේතය සහ නම ඇතුළත් කරන්න)")

        with col_right:
            if st.session_state["user_role"] == "Admin" and not active_products.empty:
                st.subheader("🗑️ Delete Product Item (භාණ්ඩයක් ඉවත් කිරීම)")
                delete_code = st.selectbox("Select Product to Delete (ඉවත් කිරීමට තෝරන්න):", active_products["Code"].astype(str) + " - " + active_products["Product Name"])
                
                if st.button("Move to Recycle Bin (මකන්න)", type="primary"):
                    target_code = delete_code.split(" - ")[0]
                    df_products.loc[df_products["Code"].astype(str) == target_code, "Is_Deleted"] = True
                    save_data(df_products, PRODUCT_FILE)
                    st.success("Item moved to Recycle Bin! (ඉවත් කරන ලදී)")
                    st.rerun()

        st.markdown("---")
        st.subheader("📋 Active Product Catalogue (දැනට ඇති භාණ්ඩ ලැයිස්තුව)")
        if not active_products.empty:
            st.dataframe(
                active_products[["Code", "Product Name", "Cost Price", "Selling Price", "Total Meter", "Total Yard", "Total Quantity (Pcs)", "Total Kg", "Total Liter", "Supplier"]],
                use_container_width=True
            )
        else:
            st.info("No products currently listed in inventory. (භාණ්ඩ නොමැත)")

    # ==================== 🧾 BILL ISSUE & POS (බිල්පත් නිකුත් කිරීම) ====================
    elif st.session_state["current_page"] == "Bill Issue":
        st.title("🧾 Bill Issue & Cashier Terminal (බිල්පත් නිකුත් කිරීමේ ස්ථානය)")

        df_products = load_data(PRODUCT_FILE)
        df_cust = load_data(CUSTOMER_FILE)

        active_products = df_products[df_products["Is_Deleted"] == False] if not df_products.empty else pd.DataFrame()

        if not active_products.empty:
            col_left, col_right = st.columns([1.1, 0.9])

            with col_left:
                st.subheader("🔍 Add Item to Billing Cart (භාණ්ඩ එකතු කිරීම)")
                search_query = st.text_input("Scan Barcode / Search Name or Code (බාර්කෝඩ් එක සකසන්න / නම සොයන්න):").strip()
                
                if search_query:
                    filtered = active_products[
                        active_products["Code"].astype(str).str.contains(search_query, case=False, na=False) |
                        active_products["Product Name"].str.contains(search_query, case=False, na=False)
                    ]
                else:
                    filtered = active_products

                if not filtered.empty:
                    sel_prod = st.selectbox("Choose Product From Search Result (භාණ්ඩය තෝරන්න):", filtered["Code"].astype(str) + " - " + filtered["Product Name"])
                    sel_code = sel_prod.split(" - ")[0]
                    prod_row = filtered[filtered["Code"].astype(str) == sel_code].iloc[0]

                    st.info(f"Unit Selling Price (විකුණුම් මිල): Rs. {float(prod_row['Selling Price']):,.2f}")

                    col_b1, col_b2, col_b3, col_b4, col_b5 = st.columns(5)
                    with col_b1:
                        sell_m = st.number_input("Meter (මීටර්):", min_value=0.0, step=0.1)
                    with col_b2:
                        sell_y = st.number_input("Yard (යාර්ඩ්):", min_value=0.0, step=0.1)
                    with col_b3:
                        sell_q = st.number_input("Pcs (කෑලි):", min_value=0.0, step=1.0)
                    with col_b4:
                        sell_kg = st.number_input("Kg (කිලෝ):", min_value=0.0, step=0.05)
                    with col_b5:
                        sell_l = st.number_input("Liter (ලීටර්):", min_value=0.0, step=0.05)

                    warranty_val = st.selectbox("Warranty Options (වගකීම් කාලය):", ["No Warranty (නැත)", "6 Months (මාස 6)", "1 Year (වසර 1)", "2 Years (වසර 2)", "3 Years (වසර 3)"])

                    unit_qty = sell_m + sell_y + sell_q + sell_kg + sell_l
                    item_total = unit_qty * float(prod_row["Selling Price"])

                    st.write(f"**Item Total Value (එකතුව):** Rs. {item_total:,.2f}")

                    if st.button("🛒 Add Selected Item to Cart (කාට් එකට එකතු කරන්න)", use_container_width=True):
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
                            st.success("Item added to cart! (එකතු විය)")
                            st.rerun()
                        else:
                            st.error("Please enter a valid quantity. (ප්‍රමාණය ඇතුළත් කරන්න)")

            with col_right:
                st.subheader("🛍️ Shopping Cart Items (තෝරාගත් භාණ්ඩ)")
                if len(st.session_state["cart"]) > 0:
                    cart_df = pd.DataFrame(st.session_state["cart"])
                    st.dataframe(cart_df[["Product Name", "Total Qty", "Warranty", "Selling Price", "Total Price"]], use_container_width=True)

                    subtotal = cart_df["Total Price"].sum()
                    st.markdown(f"### 💰 Grand Total (මුළු එකතුව): Rs. {subtotal:,.2f}")

                    if st.button("🗑️ Clear Entire Cart (කාට් එක හිස් කරන්න)"):
                        st.session_state["cart"] = []
                        st.rerun()

                    st.write("---")
                    st.subheader("💳 Checkout & Bill Settlement (මුදල් අය කිරීම)")
                    
                    cust_phone = st.text_input("📱 Customer Phone Number (පාරිභෝගිකයාගේ දුරකථන අංකය):")
                    pay_method = st.selectbox("Select Payment Channel (ගෙවීම් ක්‍රමය):", ["Cash (මුදලින්)", "Card (කාඩ්පතින්)", "Online Transfer / QR", "Credit (ණයට)"])

                    if st.button("✅ Complete Transaction & Finalize Sale (බිල්පත අවසන් කරන්න)", type="primary", use_container_width=True):
                        inv_id = datetime.now().strftime("INV%Y%m%d%H%M%S")
                        now_str = datetime.now().strftime("%Y-%m-%d")
                        df_sales = load_data(SALES_FILE)

                        for item in st.session_state["cart"]:
                            p_code_val = item["Code"]
                            p_row = df_products[df_products["Code"].astype(str) == p_code_val].iloc[0]

                            df_products.loc[df_products["Code"].astype(str) == p_code_val, "Total Meter"] = max(0, float(p_row.get("Total Meter", 0)) - item["Meter Amount"])
                            df_products.loc[df_products["Code"].astype(str) == p_code_val, "Total Yard"] = max(0, float(p_row.get("Total Yard", 0)) - item["Yard Amount"])
                            df_products.loc[df_products["Code"].astype(str) == p_code_val, "Total Quantity (Pcs)"] = max(0, float(p_row.get("Total Quantity (Pcs)", 0)) - item["Quantity (Pcs)"])
                            df_products.loc[df_products["Code"].astype(str) == p_code_val, "Total Kg"] = max(0, float(p_row.get("Total Kg", 0)) - item["Kg Amount"])
                            df_products.loc[df_products["Code"].astype(str) == p_code_val, "Total Liter"] = max(0, float(p_row.get("Total Liter", 0)) - item["Liter Amount"])

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
                            "inv_id": inv_id,
                            "items": st.session_state["cart"],
                            "total": subtotal,
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "phone": cust_phone
                        }
                        st.session_state["cart"] = []
                        st.success("✅ Transaction completed successfully! (සාර්ථකයි)")
                        st.rerun()
                else:
                    st.info("The cart is currently empty. (කාට් එක හිස්ව පවතී)")

        # Thermal Receipt & Normal SMS Section
        if st.session_state["last_invoice"]:
            inv_data = st.session_state["last_invoice"]
            st.markdown("---")
            st.subheader("🖨️ Receipt Terminal & Normal SMS Sharing (බිල්පත සහ SMS යැවීම)")

            if inv_data["phone"]:
                sms_body = f"Sapphire Collection: Invoice {inv_data['inv_id']} Total: Rs.{inv_data['total']:,.2f}. Thank you!"
                sms_url = f"sms:{inv_data['phone']}?body={sms_body.replace(' ', '%20')}"
                st.markdown(f"[📲 Click Here to Send Normal SMS (Message App එකෙන් SMS එක යවන්න)]({sms_url})")

            receipt_html = f"""
            <html>
            <head>
                <style>
                    body {{ font-family: monospace; width: 280px; margin: 0 auto; padding: 10px; }}
                    .center {{ text-align: center; }}
                    table {{ width: 100%; font-size: 12px; border-collapse: collapse; }}
                    th, td {{ text-align: left; padding: 3px 0; }}
                    .line {{ border-bottom: 1px dashed #000; margin: 5px 0; }}
                </style>
            </head>
            <body>
                <div class="center">
                    <h2>SAPPHIRE COLLECTION</h2>
                    <p>No. 123, Main Street, Sri Lanka<br>Tel: 077 123 4567</p>
                </div>
                <div class="line"></div>
                <p>Invoice: {inv_data['inv_id']}<br>Date: {inv_data['date']}</p>
                <div class="line"></div>
                <table>
                    <tr><th>Item</th><th>Qty</th><th>Price</th></tr>
            """
            for itm in inv_data['items']:
                receipt_html += f"<tr><td>{itm['Product Name']}</td><td>{itm['Total Qty']}</td><td>{itm['Total Price']:,.2f}</td></tr>"

            receipt_html += f"""
                </table>
                <div class="line"></div>
                <h3>NET TOTAL: Rs. {inv_data['total']:,.2f}</h3>
                <div class="line"></div>
                <div class="center">
                    <p>Thank You For Shopping With Us!</p>
                    <p>--- Exchange possible within 7 days ---</p>
                </div>
                <button onclick="window.print()" style="width:100%; padding: 10px; background-color: #2196F3; color: white; border: none; font-size: 16px; cursor: pointer; border-radius: 4px;">🖨️ PRINT THERMAL RECEIPT (බිල්පත ප්‍රින්ට් කරන්න)</button>
            </body>
            </html>
            """
            components.html(receipt_html, height=450, scrolling=True)

    # ==================== 🔄 ITEM RETURN & EXCHANGE (ආපසු බාරගැනීම) ====================
    elif st.session_state["current_page"] == "Returns":
        st.title("🔄 Item Return & Exchange System (භාණ්ඩ ආපසු බාරගැනීම)")

        df_sales = load_data(SALES_FILE)
        df_products = load_data(PRODUCT_FILE)
        df_returns = load_data(RETURNS_FILE)

        inv_search = st.text_input("🔍 Enter Invoice ID to Search Sale Record (බිල්පත් අංකය ඇතුළත් කරන්න):")
        
        if inv_search:
            matched_sales = df_sales[(df_sales["Invoice ID"] == inv_search) & (df_sales["Is_Deleted"] == False)]
            if not matched_sales.empty:
                st.subheader("Invoice Sold Items (විකුණන ලද භාණ්ඩ)")
                st.dataframe(matched_sales[["Product Name", "Code", "Total Price", "Total Qty"]], use_container_width=True)

                ret_item = st.selectbox("Select Returned Item (ආපසු භාරගන්නා භාණ්ඩය):", matched_sales["Code"].astype(str) + " - " + matched_sales["Product Name"])
                ret_code = ret_item.split(" - ")[0]
                ret_qty = st.number_input("Enter Returned Quantity (ආපසු ගන්නා ප්‍රමාණය):", min_value=1.0, step=1.0)
                reason = st.text_input("Reason for Item Return (හේතුව):")

                if st.button("✅ Process Return and Restock Inventory (බාරගෙන තොගයට එකතු කරන්න)"):
                    df_products.loc[df_products["Code"].astype(str) == ret_code, "Total Quantity (Pcs)"] += ret_qty
                    save_data(df_products, PRODUCT_FILE)

                    new_ret = {
                        "Date": datetime.now().strftime("%Y-%m-%d"),
                        "Invoice ID": inv_search,
                        "Product Name": ret_item.split(" - ")[1],
                        "Code": ret_code,
                        "Returned Qty": ret_qty,
                        "Refund Amount": 0.0,
                        "Reason": reason
                    }
                    df_returns = pd.concat([df_returns, pd.DataFrame([new_ret])], ignore_index=True)
                    save_data(df_returns, RETURNS_FILE)

                    st.success("Item successfully returned and stock restocked! (සාර්ථකයි)")
                    st.rerun()
            else:
                st.warning("No sales record found matching this Invoice ID. (සොයාගත නොහැකි විය)")

        st.markdown("---")
        st.subheader("📋 Return History Logs (ආපසු ලබාගත් ලැයිස්තුව)")
        if not df_returns.empty:
            st.dataframe(df_returns, use_container_width=True)

    # ==================== 📈 REPORTS & ANALYTICS (විකුණුම් වාර්තා) ====================
    elif st.session_state["current_page"] == "Reports":
        st.title("📈 Reports & Business Analytics (විකුණුම් සහ ලාභ වාර්තා)")

        df_sales = load_data(SALES_FILE)
        df_exp = load_data(EXPENSES_FILE)

        if not df_sales.empty:
            st.subheader("📊 Sales Revenue Trend Chart (දිනපතා විකුණුම් ප්‍රස්ථාරය)")
            daily_sales = df_sales.groupby("Date")["Total Price"].sum()
            st.line_chart(daily_sales)

            m1, m2, m3 = st.columns(3)
            total_rev = df_sales['Total Price'].sum()
            total_prof = df_sales['Profit'].sum()
            total_exp = df_exp['Amount'].sum() if not df_exp.empty else 0.0

            m1.metric("💰 Total Revenue (මුළු ආදායම)", f"Rs. {total_rev:,.2f}")
            m2.metric("📦 Gross Profit (දළ ලාභය)", f"Rs. {total_prof:,.2f}")
            m3.metric("💸 Expenses (වියදම්)", f"Rs. {total_exp:,.2f}")

            st.markdown("---")
            st.subheader("📜 Comprehensive Sales Register (සම්පූර්ණ විකුණුම් ලැයිස්තුව)")
            st.dataframe(
                df_sales[["Invoice ID", "Date", "Time", "Product Name", "Total Price", "Profit", "Payment Method", "Customer"]],
                use_container_width=True
            )
        else:
            st.info("No sales records available to generate analytics. (වාර්තා නොමැත)")

    # ==================== 📖 CREDIT BOOK (ණය පොත) ====================
    elif st.session_state["current_page"] == "Credit Book":
        st.title("📖 Udara Book - Customer Credit Ledger (ණය පොත)")

        df_credit = load_data(CREDIT_FILE)

        with st.form("add_credit_form", clear_on_submit=True):
            st.subheader("➕ Record New Customer Debt (නව ණය මුදලක් ඇතුළත් කිරීම)")
            c_name = st.text_input("Customer Full Name (පාරිභෝගිකයාගේ නම)")
            c_phone = st.text_input("Contact Phone Number (දුරකථන අංකය)")
            c_due = st.number_input("Outstanding Balance - ණය මුදල (Rs.)", min_value=0.0, format="%.2f")

            if st.form_submit_button("Save Ledger Record (සුරකින්න)"):
                if c_name:
                    new_cred = {
                        "Customer Name": c_name,
                        "Phone": c_phone,
                        "Due Balance": c_due,
                        "Last Date": datetime.now().strftime("%Y-%m-%d"),
                        "Is_Deleted": False
                    }
                    df_credit = pd.concat([df_credit, pd.DataFrame([new_cred])], ignore_index=True)
                    save_data(df_credit, CREDIT_FILE)
                    st.success("Credit entry created successfully! (සුරකින ලදී)")
                    st.rerun()

        st.markdown("---")
        st.subheader("📋 Active Outstanding Balances (දැනට ඇති ණය ලැයිස්තුව)")
        if not df_credit.empty:
            st.dataframe(df_credit[df_credit["Is_Deleted"] == False], use_container_width=True)

    # ==================== 👥 CUSTOMER MANAGEMENT (පාරිභෝගිකයින්) ====================
    elif st.session_state["current_page"] == "Customers":
        st.title("👥 Customer & Loyalty Management (පාරිභෝගික කළමනාකරණය)")

        df_cust = load_data(CUSTOMER_FILE)

        with st.form("add_cust_form", clear_on_submit=True):
            st.subheader("➕ Register New Client (නව පාරිභෝගිකයෙකු ඇතුළත් කිරීම)")
            cust_n = st.text_input("Customer Name (නම)")
            cust_p = st.text_input("Mobile Number (දුරකථන අංකය)")

            if st.form_submit_button("Register Customer (ලියාපදිංචි කරන්න)"):
                if cust_n:
                    new_c = {
                        "Customer Name": cust_n,
                        "Phone": cust_p,
                        "Loyalty Points": 0,
                        "Is_Deleted": False
                    }
                    df_cust = pd.concat([df_cust, pd.DataFrame([new_c])], ignore_index=True)
                    save_data(df_cust, CUSTOMER_FILE)
                    st.success("Customer account created! (ලියාපදිංචි විය)")
                    st.rerun()

        st.markdown("---")
        st.subheader("📋 Registered Customer Directory (පාරිභෝගික ලැයිස්තුව)")
        if not df_cust.empty:
            st.dataframe(df_cust[df_cust["Is_Deleted"] == False], use_container_width=True)

    # ==================== 📊 STOCK & REORDER ALERTS (තොග පරීක්ෂාව) ====================
    elif st.session_state["current_page"] == "Stock":
        st.title("📊 Stock Inventory & Reorder Warnings (තොග ප්‍රමාණයන්)")

        df_p = load_data(PRODUCT_FILE)
        active_p = df_p[df_p["Is_Deleted"] == False] if not df_p.empty else pd.DataFrame()

        if not active_p.empty:
            # Check stock levels across all units
            low_stock = active_p[
                (active_p["Total Meter"] <= active_p["Min Threshold"]) &
                (active_p["Total Quantity (Pcs)"] <= active_p["Min Threshold"]) &
                (active_p["Total Kg"] <= active_p["Min Threshold"]) &
                (active_p["Total Liter"] <= active_p["Min Threshold"])
            ]
            if not low_stock.empty:
                st.error("⚠️ Low Stock Alert! The following products need restock urgently (අඩුවෙමින් පවතින තොග):")
                st.dataframe(low_stock[["Code", "Product Name", "Total Meter", "Total Quantity (Pcs)", "Total Kg", "Total Liter", "Min Threshold", "Supplier"]], use_container_width=True)

            st.markdown("---")
            st.subheader("📦 Inventory Master Stock List (සම්පූර්ණ තොග ලැයිස්තුව)")
            st.dataframe(active_p[["Code", "Product Name", "Total Meter", "Total Yard", "Total Quantity (Pcs)", "Total Kg", "Total Liter", "Min Threshold", "Supplier"]], use_container_width=True)

    # ==================== 💸 EXPENSE TRACKER (වියදම් කළමනාකරණය) ====================
    elif st.session_state["current_page"] == "Expenses":
        st.title("💸 Store Expense Tracker (කඩයේ වියදම් සටහන)")

        df_exp = load_data(EXPENSES_FILE)

        with st.form("add_exp_form", clear_on_submit=True):
            st.subheader("➕ Record Shop Expense (නව වියදමක් ඇතුළත් කිරීම)")
            exp_desc = st.text_input("Expense Description - විස්තරය (උදා: කුලිය, විදුලි බිල)")
            exp_amt = st.number_input("Expense Amount - මුදල (Rs.)", min_value=0.0, format="%.2f")

            if st.form_submit_button("Save Expense Record (සුරකින්න)"):
                if exp_desc and exp_amt > 0:
                    new_e = {
                        "Date": datetime.now().strftime("%Y-%m-%d"),
                        "Description": exp_desc,
                        "Amount": exp_amt,
                        "Is_Deleted": False
                    }
                    df_exp = pd.concat([df_exp, pd.DataFrame([new_e])], ignore_index=True)
                    save_data(df_exp, EXPENSES_FILE)
                    st.success("Expense recorded successfully! (සුරකින ලදී)")
                    st.rerun()

        st.markdown("---")
        st.subheader("📋 Store Expense Ledger (වියදම් ලැයිස්තුව)")
        if not df_exp.empty:
            st.dataframe(df_exp[df_exp["Is_Deleted"] == False], use_container_width=True)

    # ==================== 🏭 SUPPLIER MANAGEMENT (සැපයුම්කරුවන්) ====================
    elif st.session_state["current_page"] == "Suppliers":
        st.title("🏭 Supplier & Vendor Management (සැපයුම්කරුවන් කළමනාකරණය)")

        df_sup = load_data(SUPPLIER_FILE)

        with st.form("add_sup_form", clear_on_submit=True):
            st.subheader("➕ Add New Vendor (නව සැපයුම්කරුවෙකු ඇතුළත් කිරීම)")
            sup_n = st.text_input("Supplier Contact Person (නම)")
            sup_p = st.text_input("Phone Number (දුරකථන අංකය)")
            sup_c = st.text_input("Company / Brand Name (ආයතනය / බ්‍රෑන්ඩ් එක)")

            if st.form_submit_button("Save Supplier Profile (සුරකින්න)"):
                if sup_n:
                    new_s = {
                        "Supplier Name": sup_n,
                        "Phone": sup_p,
                        "Company": sup_c,
                        "Pending Payable": 0.0,
                        "Is_Deleted": False
                    }
                    df_sup = pd.concat([df_sup, pd.DataFrame([new_s])], ignore_index=True)
                    save_data(df_sup, SUPPLIER_FILE)
                    st.success("Supplier profile created! (සුරකින ලදී)")
                    st.rerun()

        st.markdown("---")
        st.subheader("📋 Registered Vendors (සැපයුම්කරුවන්ගේ ලැයිස්තුව)")
        if not df_sup.empty:
            st.dataframe(df_sup[df_sup["Is_Deleted"] == False], use_container_width=True)

    # ==================== 🗑️ RECYCLE BIN (මකන ලද දත්ත) ====================
    elif st.session_state["current_page"] == "Recycle Bin":
        st.title("🗑️ Recycle Bin - Trash & Restore System (මකන ලද දත්ත නැවත ලබාගැනීම)")

        df_p = load_data(PRODUCT_FILE)
        deleted_p = df_p[df_p["Is_Deleted"] == True] if not df_p.empty else pd.DataFrame()

        if not deleted_p.empty:
            st.subheader("Deleted Product Items (මකන ලද භාණ්ඩ)")
            st.dataframe(deleted_p[["Code", "Product Name", "Selling Price", "Supplier"]], use_container_width=True)
            
            res_code = st.selectbox("Select Product to Restore (නැවත ලබාගැනීමට තෝරන්න):", deleted_p["Code"].astype(str) + " - " + deleted_p["Product Name"])
            
            if st.button("🔄 Restore Selected Product (නැවත යථා තත්ත්වයට පත් කරන්න)"):
                code_val = res_code.split(" - ")[0]
                df_p.loc[df_p["Code"].astype(str) == code_val, "Is_Deleted"] = False
                save_data(df_p, PRODUCT_FILE)
                st.success("Product successfully restored to Active Inventory! (සාර්ථකයි)")
                st.rerun()
        else:
            st.info("The Recycle Bin is empty. (හිස්ව පවතී)")
