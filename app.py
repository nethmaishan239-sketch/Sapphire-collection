import streamlit as st
import pandas as pd
import os
from datetime import datetime
import barcode
from barcode.writer import ImageWriter
import urllib.parse

# ==================== 1. PAGE CONFIGURATION (පිටු වින්‍යාසය) ====================
st.set_page_config(
    page_title="Sapphire Collection POS",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== 2. FILE PATHS SETUP (ගොනු මාර්ග සැකසීම) ====================
PRODUCT_FILE = "products.csv"
SALES_FILE = "sales.csv"
EXPENSES_FILE = "expenses.csv"
CREDIT_FILE = "credit.csv"
CUSTOMER_FILE = "customers.csv"
SUPPLIER_FILE = "suppliers.csv"
RETURNS_FILE = "returns.csv"

# ==================== 3. FILE INITIALIZATION (ගොනු ආරම්භය) ====================
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

    if not os.path.exists(SUPPLIER_FILE) or os.stat(SUPPLIER_FILE).st_size == 0:
        df_su = pd.DataFrame(columns=["Supplier Name", "Phone", "Company", "Pending Payable", "Is_Deleted"])
        df_su.to_csv(SUPPLIER_FILE, index=False)

    if not os.path.exists(RETURNS_FILE) or os.stat(RETURNS_FILE).st_size == 0:
        df_re = pd.DataFrame(columns=["Date", "Invoice ID", "Product Name", "Code", "Returned Qty", "Refund Amount", "Reason", "Is_Deleted"])
        df_re.to_csv(RETURNS_FILE, index=False)

init_files()

# ==================== 4. HELPER FUNCTIONS (උපකාරක ක්‍රියාකාරකම්) ====================
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

if "last_credit_receipt" not in st.session_state:
    st.session_state["last_credit_receipt"] = None

for key in ["form_meter", "form_yard", "form_pcs", "form_kg", "form_liter"]:
    if key not in st.session_state:
        st.session_state[key] = 0.0

for key in ["inp_meter", "inp_yard", "inp_pcs", "inp_kg", "inp_liter"]:
    if key not in st.session_state:
        st.session_state[key] = 0.0

# ==================== 6. LOGIN PAGE UI (ප්‍රවේශ වීම) ====================
if not st.session_state["logged_in"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #1E88E5;'>SAPPHIRE COLLECTION POS</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #555;'>Advanced Retail & Apparel Management System (ව්‍යාපාර කළමනාකරණ පද්ධතිය)</h4>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.subheader("🔐 User Authentication (පරිශීලක තහවුරු කිරීම)")
        role_selected = st.selectbox("Select Account Role (භූමිකාව තෝරන්න):", ["Admin (පරිපාලක)", "Cashier (කැෂියර්)"])
        pwd_input = st.text_input("Enter Password (මුරපදය ඇතුළත් කරන්න):", type="password", key="login_pwd")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 Login to System (පද්ධතියට පිවිසෙන්න)", type="primary", use_container_width=True):
            if "Admin" in role_selected and pwd_input == "1234":
                st.session_state["logged_in"] = True
                st.session_state["user_role"] = "Admin"
                st.session_state["current_page"] = "Main Menu"
                st.success("Admin Login Successful! (පරිපාලක පිවිසීම සාර්ථකයි!)")
                st.rerun()
            elif "Cashier" in role_selected and pwd_input == "0000":
                st.session_state["logged_in"] = True
                st.session_state["user_role"] = "Cashier"
                st.session_state["current_page"] = "Main Menu"
                st.success("Cashier Login Successful! (කැෂියර් පිවිසීම සාර්ථකයි!)")
                st.rerun()
            else:
                st.error("❌ Invalid Password! Please try again. (වැරදි මුරපදයකි!)")

else:
    # ==================== 7. SYSTEM HEADER & NAVIGATION ====================
    top_col1, top_col2, top_col3 = st.columns([3, 2, 1])
    
    with top_col1:
        if st.session_state["current_page"] != "Main Menu":
            if st.button("⬅️ Back to Main Menu (ප්‍රධාන මෙනුවට යන්න)"):
                st.session_state["current_page"] = "Main Menu"
                st.rerun()
        else:
            st.write("📍 **Dashboard Overview (මුල් පිටුව)**")

    with top_col2:
        st.write(f"👤 Current User (වත්මන් පරිශීලක): **{st.session_state['user_role']}**")

    with top_col3:
        if st.button("🔒 Logout System (පද්ධතියෙන් ඉවත් වන්න)"):
            st.session_state["logged_in"] = False
            st.session_state["user_role"] = None
            st.session_state["current_page"] = "Main Menu"
            st.rerun()

    st.markdown("---")

    # ==================== 8. MAIN MENU DASHBOARD (ප්‍රධාන මෙනුව) ====================
    if st.session_state["current_page"] == "Main Menu":
        st.markdown("<h1 style='text-align: center; color: #333;'>💎 Sapphire Collection POS System</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>Select a module below to proceed (කැමති අංශයක් තෝරන්න)</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("📦 Inventory (භාණ්ඩ)")
            if st.button("📦 Product Management (භාණ්ඩ කළමනාකරණය)", use_container_width=True):
                st.session_state["current_page"] = "Product"
                st.rerun()
            
            if st.button("📖 Udara Book - Credit Records (ණය පොත)", use_container_width=True):
                st.session_state["current_page"] = "Credit Book"
                st.rerun()

            if st.button("👥 Customer & Loyalty (ගනුදෙනුකරුවන්)", use_container_width=True):
                st.session_state["current_page"] = "Customers"
                st.rerun()

            if st.button("🏷️ Barcode Generator (බාර්කෝඩ් සාදනය)", use_container_width=True):
                st.session_state["current_page"] = "Barcode"
                st.rerun()

        with col2:
            st.subheader("🧾 Sales (විකුණුම්)")
            if st.button("🧾 Bill Issue & Cashier Terminal (බිල්පත් නිකුත් කිරීම)", use_container_width=True):
                st.session_state["current_page"] = "Bill Issue"
                st.rerun()

            if st.button("🔄 Item Return System (භාණ්ඩ ආපසු භාරගැනීම)", use_container_width=True):
                st.session_state["current_page"] = "Returns"
                st.rerun()

            if st.session_state["user_role"] == "Admin":
                if st.button("💸 Shop Expense Tracker (වියදම් ලුහුබැඳීම)", use_container_width=True):
                    st.session_state["current_page"] = "Expenses"
                    st.rerun()

        with col3:
            st.subheader("📊 Analytics (විශ්ලේෂණ)")
            if st.button("📊 Stock Levels & Reorder Alerts (තොග මට්ටම්)", use_container_width=True):
                st.session_state["current_page"] = "Stock"
                st.rerun()

            if st.session_state["user_role"] == "Admin":
                if st.button("📈 Sales Reports & Profit (විකුණුම් වාර්තා)", use_container_width=True):
                    st.session_state["current_page"] = "Reports"
                    st.rerun()

                if st.button("🏭 Supplier Management (සපයන්නන්)", use_container_width=True):
                    st.session_state["current_page"] = "Suppliers"
                    st.rerun()

        if st.session_state["user_role"] == "Admin":
            st.markdown("<br><hr>", unsafe_allow_html=True)
            if st.button("🗑️ Recycle Bin (ඉවත දැමූ දත්ත බඳුන)", use_container_width=True):
                st.session_state["current_page"] = "Recycle Bin"
                st.rerun()

    # ==================== 9. BARCODE GENERATOR MODULE ====================
    elif st.session_state["current_page"] == "Barcode":
        st.title("🏷️ Barcode Generator Engine (බාර්කෝඩ් සාදනය)")
        df_products = load_data(PRODUCT_FILE)
        active_products = df_products[df_products["Is_Deleted"] == False] if not df_products.empty else pd.DataFrame()

        if not active_products.empty:
            sel_p = st.selectbox("Select Product for Barcode (භාණ්ඩය තෝරන්න):", active_products["Code"].astype(str) + " - " + active_products["Product Name"])
            code_to_gen = sel_p.split(" - ")[0]

            if st.button("Generate & Print Barcode Label (බාර්කෝඩ් සාදන්න)"):
                try:
                    code128 = barcode.get_barcode_class('code128')
                    my_barcode = code128(code_to_gen, writer=ImageWriter())
                    filename = my_barcode.save(f"barcode_{code_to_gen}")
                    st.image(filename, caption=f"Generated Barcode ID: {code_to_gen}", width=300)
                except Exception as e:
                    st.error(f"Barcode Generation Failed: {e}")
        else:
            st.info("No active products available to generate barcodes. (භාණ්ඩ හමුවී නැත)")

    # ==================== 10. PRODUCT MANAGEMENT MODULE ====================
    elif st.session_state["current_page"] == "Product":
        st.title("📦 Product & Inventory Management (භාණ්ඩ කළමනාකරණය)")
        df_products = load_data(PRODUCT_FILE)
        df_sup = load_data(SUPPLIER_FILE)
        
        active_products = df_products[df_products["Is_Deleted"] == False] if not df_products.empty else pd.DataFrame()
        active_sups = df_sup[df_sup["Is_Deleted"] == False]["Supplier Name"].tolist() if not df_sup.empty else ["Default Supplier"]

        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.subheader("➕ Add / Update Product Details (නව භාණ්ඩයක් එක් කරන්න)")
            with st.form("add_product_form", clear_on_submit=True):
                p_code = st.text_input("🏷️ Product Code / Barcode ID (භාණ්ඩ කේතය)").strip()
                p_name = st.text_input("📦 Product Name (භාණ්ඩයේ නම)").strip()
                
                if st.session_state["user_role"] == "Admin":
                    p_cost = st.number_input("Cost Price (Rs.) (මිදීගත් මිල)", min_value=0.0, format="%.2f")
                else:
                    p_cost = 0.0

                p_sell = st.number_input("Selling Price (Rs.) (විකුණුම් මිල)", min_value=0.0, format="%.2f")
                p_sup = st.selectbox("Supplier (සපයන්නා)", active_sups)

                st.markdown("---")
                st.write("**Stock Quantities across Measurement Units (මිනුම් ඒකක අනුව තොග ප්‍රමාණය):**")
                col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns(5)
                p_meter = col_p1.number_input("Meters (මීටර්)", min_value=0.0, step=0.5)
                p_yard = col_p2.number_input("Yards (යට්)", min_value=0.0, step=0.5)
                p_qty = col_p3.number_input("Pcs (කෑලි)", min_value=0.0, step=1.0)
                p_kg = col_p4.number_input("Kg (කිලෝග්‍රෑම්)", min_value=0.0, step=0.1)
                p_liter = col_p5.number_input("Liters (ලීටර්)", min_value=0.0, step=0.1)

                p_min = st.number_input("⚠️ Min Stock Reorder Alert Level (අවම තොග සීමාව)", min_value=0.0, value=5.0)

                if st.form_submit_button("Save Product Record (භාණ්ඩය සුරකින්න)"):
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
                        st.success("Product Saved Successfully! (භාණ්ඩය සාර්ථකව සුරකින ලදී!)")
                        st.rerun()
                    else:
                        st.error("Please fill in both Code and Name fields! (කේතය සහ නම ඇතුළත් කරන්න!)")

        with col_right:
            st.subheader("🗑️ Soft Delete Product (භාණ්ඩ ඉවත් කිරීම)")
            if not active_products.empty:
                del_p_sel = st.selectbox("Select Product to Move to Trash (ඉවත් කිරීමට භාණ්ඩයක් තෝරන්න):", active_products["Code"].astype(str) + " - " + active_products["Product Name"])
                if st.button("🗑️ Move to Trash / Delete (ඉවත දැමූ බඳුනට යවන්න)"):
                    code_to_del = del_p_sel.split(" - ")[0]
                    df_products.loc[df_products["Code"].astype(str) == code_to_del, "Is_Deleted"] = True
                    save_data(df_products, PRODUCT_FILE)
                    st.warning("Product moved to Recycle Bin! (භාණ්ඩය ඉවත දැමූ බඳුනට යවන ලදී!)")
                    st.rerun()

        st.markdown("---")
        st.subheader("📋 Active Product Catalogue (භාණ්ඩ ලැයිස්තු වගුව)")
        if not active_products.empty:
            table_data = []
            for idx, row in active_products.iterrows():
                table_data.append({
                    "Index": idx,
                    "Code": row["Code"],
                    "Product Name": row["Product Name"],
                    "Sell Price (Rs.)": row["Selling Price"],
                    "Meters": row["Total Meter"],
                    "Pcs": row["Total Quantity (Pcs)"],
                    "Supplier": row["Supplier"]
                })
            
            df_table = pd.DataFrame(table_data)
            
            for i, r in df_table.iterrows():
                cols = st.columns([0.5, 1.2, 2, 1.2, 1, 1, 1.2])
                orig_idx = r["Index"]
                
                if cols[0].button("🗑️", key=f"del_prod_tbl_{orig_idx}"):
                    df_products.loc[orig_idx, "Is_Deleted"] = True
                    save_data(df_products, PRODUCT_FILE)
                    st.rerun()
                
                cols[1].write(str(r["Code"]))
                cols[2].write(str(r["Product Name"]))
                cols[3].write(str(r["Sell Price (Rs.)"]))
                cols[4].write(str(r["Meters"]))
                cols[5].write(str(r["Pcs"]))
                cols[6].write(str(r["Supplier"]))
        else:
            st.info("No active products available in system. (සක්‍රීය භාණ්ඩ නොමැත)")

    # ==================== 11. BILL ISSUE & CASHIER TERMINAL ====================
    elif st.session_state["current_page"] == "Bill Issue":
        st.title("🧾 Bill Issue & Cashier Terminal (බිල්පත් නිකුත් කිරීම)")
        df_products = load_data(PRODUCT_FILE)
        active_products = df_products[df_products["Is_Deleted"] == False] if not df_products.empty else pd.DataFrame()

        if not active_products.empty:
            col_left, col_right = st.columns([1.1, 0.9])

            with col_left:
                st.subheader("🔍 Select & Add Items (භාණ්ඩ තෝරා එකතු කරන්න)")
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

                    st.success(f"Selling Price (විකුණුම් මිල): **Rs. {float(prod_row['Selling Price']):,.2f}**")

                    st.write("Enter Quantities to Add (ප්‍රමාණයන් ඇතුළත් කරන්න):")
                    col_b1, col_b2, col_b3, col_b4, col_b5 = st.columns(5)
                    
                    sell_m = col_b1.number_input("Meter:", min_value=0.0, step=0.1, key="inp_meter")
                    sell_y = col_b2.number_input("Yard:", min_value=0.0, step=0.1, key="inp_yard")
                    sell_q = col_b3.number_input("Pcs:", min_value=0.0, step=1.0, key="inp_pcs")
                    sell_kg = col_b4.number_input("Kg:", min_value=0.0, step=0.05, key="inp_kg")
                    sell_l = col_b5.number_input("Liter:", min_value=0.0, step=0.05, key="inp_liter")

                    warranty_val = st.selectbox("Warranty Period (වගකීම් කාලය):", ["No Warranty", "6 Months", "1 Year", "2 Years", "3 Years"])
                    unit_qty = sell_m + sell_y + sell_q + sell_kg + sell_l
                    item_total = unit_qty * float(prod_row["Selling Price"])

                    st.markdown(f"#### Calculated Item Total (එකතුව): **Rs. {item_total:,.2f}**")

                    if st.button("🛒 Add Item to Cart ( කරත්තයට එකතු කරන්න)", use_container_width=True):
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
                            
                            # Reset input values in session state so meter, yard, pcs, kg, liter clear to 0 automatically
                            st.session_state["inp_meter"] = 0.0
                            st.session_state["inp_yard"] = 0.0
                            st.session_state["inp_pcs"] = 0.0
                            st.session_state["inp_kg"] = 0.0
                            st.session_state["inp_liter"] = 0.0
                            st.session_state["form_meter"] = 0.0
                            st.session_state["form_yard"] = 0.0
                            st.session_state["form_pcs"] = 0.0
                            st.session_state["form_kg"] = 0.0
                            st.session_state["form_liter"] = 0.0
                            
                            st.success("Item added to cart! (කරත්තයට එකතු කරන ලදී!)")
                            st.rerun()
                        else:
                            st.warning("Please specify quantity! (ප්‍රමාණය සඳහන් කරන්න!)")

            with col_right:
                st.subheader("🛍️ Customer Shopping Cart (මිලදී ගැනීමේ කරත්තය)")
                if len(st.session_state["cart"]) > 0:
                    subtotal = 0.0
                    
                    c_h1, c_h2, c_h3, c_h4 = st.columns([0.8, 2.2, 1, 1.5])
                    c_h1.write("**Action**")
                    c_h2.write("**Product Name**")
                    c_h3.write("**Qty**")
                    c_h4.write("**Total (Rs.)**")
                    st.markdown("---")

                    for idx, item in enumerate(st.session_state["cart"]):
                        c1, c2, c3, c4 = st.columns([0.8, 2.2, 1, 1.5])
                        
                        if c1.button("🗑️", key=f"del_cart_{idx}"):
                            st.session_state["cart"].pop(idx)
                            st.rerun()
                            
                        c2.write(item["Product Name"])
                        c3.write(f"{item['Total Qty']}")
                        c4.write(f"{item['Total Price']:,.2f}")

                        subtotal += item["Total Price"]

                    st.markdown("---")
                    st.markdown(f"### 💰 Bill Grand Total (මුළු එකතුව): Rs. {subtotal:,.2f}")

                    if st.button("🗑️ Clear Entire Cart (කරත්තය හිස් කරන්න)", type="secondary"):
                        st.session_state["cart"] = []
                        st.rerun()

                    st.markdown("---")
                    cust_phone = st.text_input("📱 Customer Phone Number (දුරකථන අංකය):").strip()
                    pay_method = st.selectbox("Payment Method (ගෙවීමේ ක්‍රමය):", ["Cash (මුදල්)", "Card (කාඩ්)", "Online Transfer (ඔන්ලයින්)", "Credit (ණය)"])

                    if st.button("✅ Checkout & Print Receipt (බිල්පත මුද්‍රණය කරන්න)", type="primary", use_container_width=True):
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
                            "payment": pay_method,
                            "phone": cust_phone if cust_phone else ""
                        }

                        st.session_state["cart"] = []
                        st.success("✅ Sale Processed Successfully! (විකුණුම සාර්ථකයි!)")
                        st.rerun()
                else:
                    st.info("Cart is currently empty. (කරත්තය හිස්ය)")

        if st.session_state.get("last_invoice"):
            st.markdown("---")
            st.subheader("🖨️ Printable Thermal Receipt (බිල්පත් මුද්‍රණය)")
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
            st.components.v1.html(receipt_html, height=380)

            if st.button("🔄 නව බිල්පතක් සකසන්න (New Bill)", type="primary", use_container_width=True):
                st.session_state["last_invoice"] = None
                st.rerun()

            cust_phone_val = inv.get("phone", "").strip()
            if cust_phone_val:
                if cust_phone_val.startswith("0"):
                    formatted_phone = "+94" + cust_phone_val[1:]
                elif not cust_phone_val.startswith("+"):
                    formatted_phone = "+94" + cust_phone_val
                else:
                    formatted_phone = cust_phone_val

                sms_msg = f"Thank you for shopping at Sapphire Collection! Invoice: {inv['id']}, Total: Rs.{inv['total']:,.2f}. Thank You!"
                encoded_msg = urllib.parse.quote(sms_msg)
                sms_intent_url = f"sms:{formatted_phone}?body={encoded_msg}"

                st.markdown(
                    f"""
                    <a href="{sms_intent_url}" target="_blank" style="text-decoration: none;">
                        <button style="
                            background-color: #25D366; 
                            color: white; 
                            padding: 12px 20px; 
                            font-size: 16px; 
                            font-weight: bold; 
                            border: none; 
                            border-radius: 8px; 
                            cursor: pointer; 
                            width: 100%;
                            box-shadow: 0px 4px 6px rgba(0,0,0,0.1);">
                            📱 Send Bill SMS to Customer via Phone App ({formatted_phone})
                        </button>
                    </a>
                    """, 
                    unsafe_allow_html=True
                )

    # ==================== 12. REPORTS & FINANCIAL ANALYTICS ====================
    elif st.session_state["current_page"] == "Reports":
        st.title("📈 Sales Reports & Business Analytics (විකුණුම් වාර්තා)")

        df_sales = load_data(SALES_FILE)
        df_exp = load_data(EXPENSES_FILE)

        active_sales = df_sales[df_sales["Is_Deleted"] == False] if not df_sales.empty and "Is_Deleted" in df_sales.columns else df_sales

        if not active_sales.empty:
            st.subheader("📊 Revenue Analytics Trend (ආදායම් ප්‍රවණතාව)")
            daily_sales = active_sales.groupby("Date")["Total Price"].sum()
            st.line_chart(daily_sales)

            m1, m2, m3, m4 = st.columns(4)
            total_rev = active_sales['Total Price'].sum()
            total_prof = active_sales['Profit'].sum()
            total_exp = df_exp[df_exp["Is_Deleted"] == False]['Amount'].sum() if not df_exp.empty else 0.0
            net_profit = total_prof - total_exp

            m1.metric("💰 Gross Revenue (මුළු ආදායම)", f"Rs. {total_rev:,.2f}")
            m2.metric("📦 Gross Profit ( දළ ලාභය)", f"Rs. {total_prof:,.2f}")
            m3.metric("💸 Shop Expenses (වියදම්)", f"Rs. {total_exp:,.2f}")
            m4.metric("💵 Net Profit (ශුද්ධ ලාභය)", f"Rs. {net_profit:,.2f}")

            st.markdown("---")
            st.subheader("📜 Detailed Sales Transaction History (විකුණුම් ඉතිහාස වගුව)")
            for idx, row in active_sales.iterrows():
                cols = st.columns([0.8, 1.5, 1.2, 2, 1.5, 1.2, 1.2])
                if cols[0].button("🗑️", key=f"del_sale_{idx}"):
                    df_sales.loc[idx, "Is_Deleted"] = True
                    save_data(df_sales, SALES_FILE)
                    st.rerun()
                cols[1].write(str(row['Invoice ID']))
                cols[2].write(str(row['Date']))
                cols[3].write(str(row['Product Name']))
                cols[4].write(f"Rs. {row['Total Price']:,.2f}")
                cols[5].write(str(row['Payment Method']))
                cols[6].write(str(row['Customer']))
        else:
            st.info("No sales records available. (විකුණුම් වාර්තා නොමැත)")

    # ==================== 13. STOCK LEVELS & REORDER ALERTS ====================
    elif st.session_state["current_page"] == "Stock":
        st.title("📊 Stock Inventory & Reorder Warnings (තොග මට්ටම්)")
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
                st.error("⚠️ Low Stock Alert (අවම තොග අනතුරු ඇඟවීම):")
                for idx, row in low_stock.iterrows():
                    cols = st.columns([0.8, 1.5, 2.5, 1.5, 1.5])
                    if cols[0].button("🗑️", key=f"del_low_{idx}"):
                        df_p.loc[df_p["Code"].astype(str) == str(row['Code']), "Is_Deleted"] = True
                        save_data(df_p, PRODUCT_FILE)
                        st.rerun()
                    cols[1].write(str(row['Code']))
                    cols[2].write(str(row['Product Name']))
                    cols[3].write(f"Pcs: {row['Total Quantity (Pcs)']}")
                    cols[4].write(str(row['Supplier']))

            st.markdown("---")
            st.subheader("📦 Complete Inventory Stock Table (තොග වගුව)")
            for idx, row in active_p.iterrows():
                cols = st.columns([0.8, 1.5, 2.5, 1.2, 1.2, 1.2, 1.5])
                if cols[0].button("🗑️", key=f"del_stock_{idx}"):
                    df_p.loc[idx, "Is_Deleted"] = True
                    save_data(df_p, PRODUCT_FILE)
                    st.rerun()
                cols[1].write(str(row['Code']))
                cols[2].write(str(row['Product Name']))
                cols[3].write(f"M: {row['Total Meter']}")
                cols[4].write(f"Pcs: {row['Total Quantity (Pcs']}")
                cols[5].write(f"Kg: {row['Total Kg']}")
                cols[6].write(str(row['Supplier']))
        else:
            st.info("No stock data available. (තොග දත්ත නොමැත)")

    # ==================== 14. EXPENSE TRACKER ====================
    elif st.session_state["current_page"] == "Expenses":
        st.title("💸 Shop Expense Tracker (වියදම් ලුහුබැඳීම)")
        df_exp = load_data(EXPENSES_FILE)

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("➕ Record New Expense (නව වියදමක් ඇතුළත් කරන්න)")
            with st.form("add_exp_form", clear_on_submit=True):
                exp_desc = st.text_input("Expense Description (විස්තරය)")
                exp_amt = st.number_input("Amount (Rs.) (මුදල)", min_value=0.0, format="%.2f")

                if st.form_submit_button("Save Expense Entry (වියදම සුරකින්න)"):
                    if exp_desc and exp_amt > 0:
                        new_e = {"Date": datetime.now().strftime("%Y-%m-%d"), "Description": exp_desc, "Amount": exp_amt, "Is_Deleted": False}
                        df_exp = pd.concat([df_exp, pd.DataFrame([new_e])], ignore_index=True)
                        save_data(df_exp, EXPENSES_FILE)
                        st.success("Expense Entry Saved! (වියදම සුරකින ලදී!)")
                        st.rerun()

        with col2:
            st.subheader("📜 Expense Log (වියදම් වගුව)")
            active_exp = df_exp[df_exp["Is_Deleted"] == False] if not df_exp.empty else pd.DataFrame()
            if not active_exp.empty:
                for idx, row in active_exp.iterrows():
                    cols = st.columns([0.8, 1.5, 2.5, 1.5])
                    if cols[0].button("🗑️", key=f"del_exp_{idx}"):
                        df_exp.loc[idx, "Is_Deleted"] = True
                        save_data(df_exp, EXPENSES_FILE)
                        st.rerun()
                    cols[1].write(str(row['Date']))
                    cols[2].write(str(row['Description']))
                    cols[3].write(f"Rs. {row['Amount']:,.2f}")
            else:
                st.info("No expense records found. (වියදම් වාර්තා නොමැත)")

    # ==================== 15. SUPPLIER MANAGEMENT ====================
    elif st.session_state["current_page"] == "Suppliers":
        st.title("🏭 Supplier Management System (සපයන්නන් කළමනාකරණය)")
        df_sup = load_data(SUPPLIER_FILE)

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("➕ Register New Supplier (නව සපයන්නකු ලියාපදිංචි කරන්න)")
            with st.form("add_sup_form", clear_on_submit=True):
                sup_n = st.text_input("Supplier Name (නම)")
                sup_p = st.text_input("Contact Phone Number (දුරකථන අංකය)")
                sup_c = st.text_input("Company / Brand Name (සමාගම)")

                if st.form_submit_button("Register Supplier (ලියාපදිංචි කරන්න)"):
                    if sup_n:
                        new_s = {"Supplier Name": sup_n, "Phone": sup_p, "Company": sup_c, "Pending Payable": 0.0, "Is_Deleted": False}
                        df_sup = pd.concat([df_sup, pd.DataFrame([new_s])], ignore_index=True)
                        save_data(df_sup, SUPPLIER_FILE)
                        st.success("Supplier Registered! (සාර්ථකව ලියාපදිංචි කරන ලදී!)")
                        st.rerun()

        with col2:
            st.subheader("📋 Registered Suppliers Directory (සපයන්නන්ගේ වගුව)")
            active_sup = df_sup[df_sup["Is_Deleted"] == False] if not df_sup.empty else pd.DataFrame()
            if not active_sup.empty:
                for idx, row in active_sup.iterrows():
                    cols = st.columns([0.8, 2, 1.5, 1.5])
                    if cols[0].button("🗑️", key=f"del_sup_{idx}"):
                        df_sup.loc[idx, "Is_Deleted"] = True
                        save_data(df_sup, SUPPLIER_FILE)
                        st.rerun()
                    cols[1].write(str(row['Supplier Name']))
                    cols[2].write(str(row['Phone']))
                    cols[3].write(str(row['Company']))
            else:
                st.info("No supplier records found. (සපයන්නන් නොමැත)")

    # ==================== 16. UDARA BOOK (CREDIT LEDGER) ====================
    elif st.session_state["current_page"] == "Credit Book":
        st.title("📖 Udara Book - Customer Credit Ledger (ණය පොත)")
        df_credit = load_data(CREDIT_FILE)
        active_credit = df_credit[df_credit["Is_Deleted"] == False] if not df_credit.empty else pd.DataFrame()

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("➕ Record New Credit / Add Due (නව ණය මුදලක් ඇතුළත් කරන්න)")
            with st.form("add_credit_form", clear_on_submit=True):
                c_name = st.text_input("Customer Name (ගනුදෙනුකරුගේ නම)").strip()
                c_phone = st.text_input("Phone Number (දුරකථන අංකය)").strip()
                c_due = st.number_input("Credit Amount to Add (Rs.) (ණය මුදල)", min_value=0.0, format="%.2f")

                if st.form_submit_button("Save Ledger Entry (ණය සුරකින්න)"):
                    if c_name and c_due > 0:
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
                        st.success("Credit Entry Saved Successfully! (ණය සටහන සුරකින ලදී!)")
                        st.rerun()

        with col2:
            st.subheader("💵 Settle / Pay Due Balance (ණය පියවීම)")
            pending_credits = active_credit[active_credit["Due Balance"] > 0] if not active_credit.empty else pd.DataFrame()
            
            if not pending_credits.empty:
                cust_options = pending_credits["Customer Name"].tolist()
                sel_cust = st.selectbox("Select Customer to Settle (ගනුදෙනුකරු තෝරන්න):", cust_options)
                
                curr_due = float(pending_credits[pending_credits["Customer Name"] == sel_cust]["Due Balance"].iloc[0])
                st.info(f"Current Balance Due for **{sel_cust}**: **Rs. {curr_due:,.2f}**")

                with st.form("settle_credit_form", clear_on_submit=True):
                    pay_amt = st.number_input("Paid Amount by Customer (Rs.) (ගෙවන ලද මුදල)", min_value=0.0, max_value=curr_due, format="%.2f")

                    if st.form_submit_button("✅ Deduct Paid Amount (ණය අඩු කරන්න)"):
                        if pay_amt > 0:
                            idx = df_credit[(df_credit["Customer Name"] == sel_cust) & (df_credit["Is_Deleted"] == False)].index[0]
                            cust_phone_rec = str(df_credit.loc[idx, "Phone"]) if "Phone" in df_credit.columns else ""
                            new_bal = curr_due - pay_amt
                            df_credit.loc[idx, "Due Balance"] = new_bal
                            df_credit.loc[idx, "Last Date"] = datetime.now().strftime("%Y-%m-%d")
                            
                            save_data(df_credit, CREDIT_FILE)

                            st.session_state["last_credit_receipt"] = {
                                "receipt_id": datetime.now().strftime("CR%Y%m%d%H%M%S"),
                                "customer": sel_cust,
                                "phone": cust_phone_rec,
                                "previous_due": curr_due,
                                "paid_amount": pay_amt,
                                "remaining_due": new_bal,
                                "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            }

                            st.success(f"Payment Recorded! Remaining Balance: Rs. {new_bal:,.2f}")
                            st.rerun()
            else:
                st.info("🎉 No pending customer credits to settle! (පියවිය යුතු ණය නොමැත)")

        if st.session_state.get("last_credit_receipt"):
            st.markdown("---")
            st.subheader("🖨️ Printable Payment Receipt (ණය ගෙවීමේ ලදුපත)")
            c_rec = st.session_state["last_credit_receipt"]
            
            c_receipt_html = f"""
            <div style="width: 300px; padding: 15px; border: 1px dashed #333; font-family: monospace; background: #fff; color: #000;">
                <h3 style="text-align: center; margin: 0;">SAPPHIRE COLLECTION</h3>
                <p style="text-align: center; margin: 0;">Credit Payment Receipt</p>
                <p style="text-align: center; margin: 0;">Tel: 077-1234567</p>
                <hr style="border-top: 1px dashed #000;">
                <p><b>Receipt No:</b> {c_rec['receipt_id']}<br>
                <b>Date:</b> {c_rec['date']}<br>
                <b>Customer:</b> {c_rec['customer']}</p>
                <hr style="border-top: 1px dashed #000;">
                <p>Previous Balance: <span style="float:right;">Rs.{c_rec['previous_due']:,.2f}</span></p>
                <p><b>Paid Amount: <span style="float:right;">Rs.{c_rec['paid_amount']:,.2f}</span></b></p>
                <hr style="border-top: 1px dashed #000;">
                <h4><b>Remaining Due: <span style="float:right;">Rs.{c_rec['remaining_due']:,.2f}</span></b></h4>
                <hr style="border-top: 1px dashed #000;">
                <p style="text-align: center;">Thank You!</p>
            </div>
            """
            st.components.v1.html(c_receipt_html, height=350)

            if st.button("❌ Close Receipt (ලදුපත වසන්න)", type="secondary"):
                st.session_state["last_credit_receipt"] = None
                st.rerun()

        st.markdown("---")
        st.subheader("📋 Active Customer Credit Records Log (ණය ලැයිස්තු වගුව)")
        if not active_credit.empty:
            for idx, row in active_credit.iterrows():
                cols = st.columns([0.8, 2, 1.5, 1.5, 1.5])
                if cols[0].button("🗑️", key=f"del_cred_{idx}"):
                    df_credit.loc[idx, "Is_Deleted"] = True
                    save_data(df_credit, CREDIT_FILE)
                    st.rerun()
                cols[1].write(str(row['Customer Name']))
                cols[2].write(str(row['Phone']))
                cols[3].write(f"Due: Rs. {row['Due Balance']:,.2f}")
                cols[4].write(str(row['Last Date']))
        else:
            st.info("No credit records found. (ණය වාර්තා නොමැත)")

    # ==================== 17. CUSTOMER & LOYALTY ====================
    elif st.session_state["current_page"] == "Customers":
        st.title("👥 Customer Loyalty & Directory (ගනුදෙනුකරුවන්)")
        df_cust = load_data(CUSTOMER_FILE)

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("➕ Register Customer Profile (ගනුදෙනුකරු ලියාපදිංචි කරන්න)")
            with st.form("add_cust_form", clear_on_submit=True):
                cust_n = st.text_input("Customer Full Name (සම්පූර්ණ නම)")
                cust_p = st.text_input("Mobile Number (ජංගම දුරකථන අංකය)")

                if st.form_submit_button("Register Customer (ලියාපදිංචි කරන්න)"):
                    if cust_n:
                        new_c = {"Customer Name": cust_n, "Phone": cust_p, "Loyalty Points": 0, "Is_Deleted": False}
                        df_cust = pd.concat([df_cust, pd.DataFrame([new_c])], ignore_index=True)
                        save_data(df_cust, CUSTOMER_FILE)
                        st.success("Customer Profile Created! (සාර්ථකයි!)")
                        st.rerun()

        with col2:
            st.subheader("📋 Registered Customer Directory (ගනුදෙනුකරුවන්ගේ වගුව)")
            active_cust = df_cust[df_cust["Is_Deleted"] == False] if not df_cust.empty else pd.DataFrame()
            if not active_cust.empty:
                for idx, row in active_cust.iterrows():
                    cols = st.columns([0.8, 2, 1.5, 1.2])
                    if cols[0].button("🗑️", key=f"del_cust_{idx}"):
                        df_cust.loc[idx, "Is_Deleted"] = True
                        save_data(df_cust, CUSTOMER_FILE)
                        st.rerun()
                    cols[1].write(str(row['Customer Name']))
                    cols[2].write(str(row['Phone']))
                    cols[3].write(f"Pts: {row['Loyalty Points']}")
            else:
                st.info("No customer profiles found. (ගනුදෙනුකරුවන් නොමැත)")

    # ==================== 18. ITEM RETURNS SYSTEM ====================
    elif st.session_state["current_page"] == "Returns":
        st.title("🔄 Item Return & Refund Processing (භාණ්ඩ ආපසු භාරගැනීම)")
        df_sales = load_data(SALES_FILE)
        df_products = load_data(PRODUCT_FILE)
        df_returns = load_data(RETURNS_FILE)

        inv_search = st.text_input("Enter Invoice ID to Search Transaction (බිල්පත් අංකය ඇතුළත් කරන්න):").strip()
        if inv_search:
            matched = df_sales[df_sales["Invoice ID"] == inv_search] if not df_sales.empty else pd.DataFrame()
            if not matched.empty:
                st.subheader("Invoice Items Found (හමුවූ භාණ්ඩ):")
                st.dataframe(matched[["Product Name", "Code", "Selling Price", "Meter Amount", "Yard Amount", "Quantity (Pcs)", "Kg Amount", "Liter Amount", "Total Price"]], use_container_width=True)

                with st.form("process_return_form"):
                    ret_p = st.selectbox("Select Item to Return (ආපසු දීමට භාණ්ඩය තෝරන්න):", matched["Code"].astype(str) + " - " + matched["Product Name"])
                    sel_code = ret_p.split(" - ")[0]
                    item_matched = matched[matched["Code"].astype(str) == sel_code].iloc[0]

                    st.write("**Specify Units to Return / Restock (ආපසු දෙන ප්‍රමාණය):**")
                    col_r1, col_r2, col_r3, col_r4, col_r5 = st.columns(5)
                    ret_m = col_r1.number_input("Meter:", min_value=0.0, max_value=float(item_matched.get("Meter Amount", 0)), step=0.1)
                    ret_y = col_r2.number_input("Yard:", min_value=0.0, max_value=float(item_matched.get("Yard Amount", 0)), step=0.1)
                    ret_q = col_r3.number_input("Pcs:", min_value=0.0, max_value=float(item_matched.get("Quantity (Pcs)", 0)), step=1.0)
                    ret_kg = col_r4.number_input("Kg:", min_value=0.0, max_value=float(item_matched.get("Kg Amount", 0)), step=0.05)
                    ret_l = col_r5.number_input("Liter:", min_value=0.0, max_value=float(item_matched.get("Liter Amount", 0)), step=0.05)

                    ret_qty_total = ret_m + ret_y + ret_q + ret_kg + ret_l
                    refund_amt = ret_qty_total * float(item_matched["Selling Price"])
                    
                    st.info(f"Calculated Refund Amount (මුදල් ආපසු ගෙවීම): **Rs. {refund_amt:,.2f}**")
                    ret_reason = st.text_area("Reason for Return / Refund (හේතුව):")

                    if st.form_submit_button("✅ Process Return & Restock Product (ආපසු භාරගන්න)"):
                        if ret_qty_total > 0:
                            if sel_code in df_products["Code"].astype(str).values:
                                p_idx = df_products[df_products["Code"].astype(str) == sel_code].index[0]
                                df_products.loc[p_idx, "Total Meter"] = float(df_products.loc[p_idx, "Total Meter"]) + ret_m
                                df_products.loc[p_idx, "Total Yard"] = float(df_products.loc[p_idx, "Total Yard"]) + ret_y
                                df_products.loc[p_idx, "Total Quantity (Pcs)"] = float(df_products.loc[p_idx, "Total Quantity (Pcs)"]) + ret_q
                                df_products.loc[p_idx, "Total Kg"] = float(df_products.loc[p_idx, "Total Kg"]) + ret_kg
                                df_products.loc[p_idx, "Total Liter"] = float(df_products.loc[p_idx, "Total Liter"]) + ret_l
                                save_data(df_products, PRODUCT_FILE)

                            new_return = {
                                "Date": datetime.now().strftime("%Y-%m-%d"),
                                "Invoice ID": inv_search,
                                "Product Name": item_matched["Product Name"],
                                "Code": sel_code,
                                "Returned Qty": ret_qty_total,
                                "Refund Amount": refund_amt,
                                "Reason": ret_reason,
                                "Is_Deleted": False
                            }
                            df_returns = pd.concat([df_returns, pd.DataFrame([new_return])], ignore_index=True)
                            save_data(df_returns, RETURNS_FILE)

                            st.success(f"Return Processed! Product Restocked and Rs. {refund_amt:,.2f} Refunded.")
                            st.rerun()
                        else:
                            st.warning("Please specify return quantity! (ප්‍රමාණය සඳහන් කරන්න)")
            else:
                st.error("No invoice records found for the given ID. (බිල්පත් අංකය හමුවී නැත)")

        st.markdown("---")
        st.subheader("📜 Return History Log (ආපසු භාරගත් භාණ්ඩ වගුව)")
        active_returns = df_returns[df_returns["Is_Deleted"] == False] if not df_returns.empty and "Is_Deleted" in df_returns.columns else df_returns
        if not active_returns.empty:
            for idx, row in active_returns.iterrows():
                cols = st.columns([0.8, 1.5, 1.5, 2.5, 1.5])
                if cols[0].button("🗑️", key=f"del_ret_{idx}"):
                    df_returns.loc[idx, "Is_Deleted"] = True
                    save_data(df_returns, RETURNS_FILE)
                    st.rerun()
                cols[1].write(str(row['Date']))
                cols[2].write(str(row['Invoice ID']))
                cols[3].write(str(row['Product Name']))
                cols[4].write(f"Rs. {row['Refund Amount']:,.2f}")
        else:
            st.info("No return history found. (වාර්තා නොමැත)")

    # ==================== 19. RECYCLE BIN & DATA MANAGEMENT ====================
    elif st.session_state["current_page"] == "Recycle Bin":
        st.title("🗑️ System Recycle Bin & Data Management (ඉවත දැමූ දත්ත බඳුන)")
        st.write("මෙහි මකා දැමූ සියලු දත්ත අංශ අනුව පවතින අතර, නැවත ලබාගැනීමට (Restore) හෝ සදහටම පද්ධතියෙන්ම මකා දැමීමට (Permanent Delete) හැක.")
        st.markdown("---")

        tab_p, tab_s, tab_e, tab_c, tab_cu, tab_sup, tab_r = st.tabs([
            "📦 Products", "🧾 Sales", "💸 Expenses", "📖 Credit Book", "👥 Customers", "🏭 Suppliers", "🔄 Returns"
        ])

        # 1. Products
        with tab_p:
            st.subheader("📦 Deleted Products (මකා දැමූ භාණ්ඩ)")
            df_p = load_data(PRODUCT_FILE)
            if not df_p.empty and "Is_Deleted" in df_p.columns:
                del_p = df_p[df_p["Is_Deleted"] == True]
                if not del_p.empty:
                    for idx, row in del_p.iterrows():
                        cols = st.columns([1, 1.2, 1.5, 2.5, 1.5])
                        if cols[0].button("🔄 Restore", key=f"res_p_{idx}"):
                            df_p.loc[idx, "Is_Deleted"] = False
                            save_data(df_p, PRODUCT_FILE)
                            st.success("Product Restored!")
                            st.rerun()
                        if cols[1].button("❌ Perm Delete", key=f"perm_p_{idx}"):
                            df_p = df_p.drop(idx)
                            save_data(df_p, PRODUCT_FILE)
                            st.warning("Product Permanently Deleted!")
                            st.rerun()
                        cols[2].write(str(row['Code']))
                        cols[3].write(str(row['Product Name']))
                        cols[4].write(str(row['Supplier']))
                else:
                    st.info("No deleted products in Recycle Bin. (මකා දැමූ භාණ්ඩ නොමැත)")
            else:
                st.info("No deleted products in Recycle Bin. (මකා දැමූ භාණ්ඩ නොමැත)")

        # 2. Sales
        with tab_s:
            st.subheader("🧾 Deleted Sales Transactions (මකා දැමූ විකුණුම්)")
            df_s = load_data(SALES_FILE)
            if not df_s.empty and "Is_Deleted" in df_s.columns:
                del_s = df_s[df_s["Is_Deleted"] == True]
                if not del_s.empty:
                    for idx, row in del_s.iterrows():
                        cols = st.columns([1, 1.2, 1.5, 2, 1.5, 1.5])
                        if cols[0].button("🔄 Restore", key=f"res_s_{idx}"):
                            df_s.loc[idx, "Is_Deleted"] = False
                            save_data(df_s, SALES_FILE)
                            st.success("Sales Record Restored!")
                            st.rerun()
                        if cols[1].button("❌ Perm Delete", key=f"perm_s_{idx}"):
                            df_s = df_s.drop(idx)
                            save_data(df_s, SALES_FILE)
                            st.warning("Sales Record Permanently Deleted!")
                            st.rerun()
                        cols[2].write(str(row['Invoice ID']))
                        cols[3].write(str(row['Product Name']))
                        cols[4].write(f"Rs. {row['Total Price']:,.2f}")
                        cols[5].write(str(row['Date']))
                else:
                    st.info("No deleted sales records in Recycle Bin. (මකා දැමූ විකුණුම් වාර්තා නොමැත)")
            else:
                st.info("No deleted sales records in Recycle Bin. (මකා දැමූ විකුණුම් වාර්තා නොමැත)")

        # 3. Expenses
        with tab_e:
            st.subheader("💸 Deleted Expenses (මකා දැමූ වියදම්)")
            df_e = load_data(EXPENSES_FILE)
            if not df_e.empty and "Is_Deleted" in df_e.columns:
                del_e = df_e[df_e["Is_Deleted"] == True]
                if not del_e.empty:
                    for idx, row in del_e.iterrows():
                        cols = st.columns([1, 1.2, 1.5, 2.5, 1.5])
                        if cols[0].button("🔄 Restore", key=f"res_e_{idx}"):
                            df_e.loc[idx, "Is_Deleted"] = False
                            save_data(df_e, EXPENSES_FILE)
                            st.success("Expense Entry Restored!")
                            st.rerun()
                        if cols[1].button("❌ Perm Delete", key=f"perm_e_{idx}"):
                            df_e = df_e.drop(idx)
                            save_data(df_e, EXPENSES_FILE)
                            st.warning("Expense Entry Permanently Deleted!")
                            st.rerun()
                        cols[2].write(str(row['Date']))
                        cols[3].write(str(row['Description']))
                        cols[4].write(f"Rs. {row['Amount']:,.2f}")
                else:
                    st.info("No deleted expenses in Recycle Bin. (මකා දැමූ වියදම් නොමැත)")
            else:
                st.info("No deleted expenses in Recycle Bin. (මකා දැමූ වියදම් නොමැත)")

        # 4. Credit Book
        with tab_c:
            st.subheader("📖 Deleted Credit Records (මකා දැමූ ණය සටහන්)")
            df_cr = load_data(CREDIT_FILE)
            if not df_cr.empty and "Is_Deleted" in df_cr.columns:
                del_cr = df_cr[df_cr["Is_Deleted"] == True]
                if not del_cr.empty:
                    for idx, row in del_cr.iterrows():
                        cols = st.columns([1, 1.2, 2, 1.5, 1.5])
                        if cols[0].button("🔄 Restore", key=f"res_cr_{idx}"):
                            df_cr.loc[idx, "Is_Deleted"] = False
                            save_data(df_cr, CREDIT_FILE)
                            st.success("Credit Record Restored!")
                            st.rerun()
                        if cols[1].button("❌ Perm Delete", key=f"perm_cr_{idx}"):
                            df_cr = df_cr.drop(idx)
                            save_data(df_cr, CREDIT_FILE)
                            st.warning("Credit Record Permanently Deleted!")
                            st.rerun()
                        cols[2].write(str(row['Customer Name']))
                        cols[3].write(str(row['Phone']))
                        cols[4].write(f"Rs. {row['Due Balance']:,.2f}")
                else:
                    st.info("No deleted credit records in Recycle Bin. (මකා දැමූ ණය සටහන් නොමැත)")
            else:
                st.info("No deleted credit records in Recycle Bin. (මකා දැමූ ණය සටහන් නොමැත)")

        # 5. Customers
        with tab_cu:
            st.subheader("👥 Deleted Customers (මකා දැමූ ගනුදෙනුකරුවන්)")
            df_cu = load_data(CUSTOMER_FILE)
            if not df_cu.empty and "Is_Deleted" in df_cu.columns:
                del_cu = df_cu[df_cu["Is_Deleted"] == True]
                if not del_cu.empty:
                    for idx, row in del_cu.iterrows():
                        cols = st.columns([1, 1.2, 2, 1.5, 1.5])
                        if cols[0].button("🔄 Restore", key=f"res_cu_{idx}"):
                            df_cu.loc[idx, "Is_Deleted"] = False
                            save_data(df_cu, CUSTOMER_FILE)
                            st.success("Customer Profile Restored!")
                            st.rerun()
                        if cols[1].button("❌ Perm Delete", key=f"perm_cu_{idx}"):
                            df_cu = df_cu.drop(idx)
                            save_data(df_cu, CUSTOMER_FILE)
                            st.warning("Customer Profile Permanently Deleted!")
                            st.rerun()
                        cols[2].write(str(row['Customer Name']))
                        cols[3].write(str(row['Phone']))
                        cols[4].write(f"Pts: {row['Loyalty Points']}")
                else:
                    st.info("No deleted customer profiles in Recycle Bin. (මකා දැමූ ගනුදෙනුකරුවන් නොමැත)")
            else:
                st.info("No deleted customer profiles in Recycle Bin. (මකා දැමූ ගනුදෙනුකරුවන් නොමැත)")

        # 6. Suppliers
        with tab_sup:
            st.subheader("🏭 Deleted Suppliers (මකා දැමූ සපයන්නන්)")
            df_sup = load_data(SUPPLIER_FILE)
            if not df_sup.empty and "Is_Deleted" in df_sup.columns:
                del_sup = df_sup[df_sup["Is_Deleted"] == True]
                if not del_sup.empty:
                    for idx, row in del_sup.iterrows():
                        cols = st.columns([1, 1.2, 2, 1.5, 1.5])
                        if cols[0].button("🔄 Restore", key=f"res_sup_{idx}"):
                            df_sup.loc[idx, "Is_Deleted"] = False
                            save_data(df_sup, SUPPLIER_FILE)
                            st.success("Supplier Profile Restored!")
                            st.rerun()
                        if cols[1].button("❌ Perm Delete", key=f"perm_sup_{idx}"):
                            df_sup = df_sup.drop(idx)
                            save_data(df_sup, SUPPLIER_FILE)
                            st.warning("Supplier Profile Permanently Deleted!")
                            st.rerun()
                        cols[2].write(str(row['Supplier Name']))
                        cols[3].write(str(row['Phone']))
                        cols[4].write(str(row['Company']))
                else:
                    st.info("No deleted suppliers in Recycle Bin. (මකා දැමූ සපයන්නන් නොමැත)")
            else:
                st.info("No deleted suppliers in Recycle Bin. (මකා දැමූ සපයන්නන් නොමැත)")

        # 7. Returns
        with tab_r:
            st.subheader("🔄 Deleted Returns (මකා දැමූ ආපසු භාරගැනීම්)")
            df_r = load_data(RETURNS_FILE)
            if not df_r.empty and "Is_Deleted" in df_r.columns:
                del_r = df_r[df_r["Is_Deleted"] == True]
                if not del_r.empty:
                    for idx, row in del_r.iterrows():
                        cols = st.columns([1, 1.2, 1.5, 2, 1.5])
                        if cols[0].button("🔄 Restore", key=f"res_r_{idx}"):
                            df_r.loc[idx, "Is_Deleted"] = False
                            save_data(df_r, RETURNS_FILE)
                            st.success("Return Record Restored!")
                            st.rerun()
                        if cols[1].button("❌ Perm Delete", key=f"perm_r_{idx}"):
                            df_r = df_r.drop(idx)
                            save_data(df_r, RETURNS_FILE)
                            st.warning("Return Record Permanently Deleted!")
                            st.rerun()
                        cols[2].write(str(row['Date']))
                        cols[3].write(str(row['Invoice ID']))
                        cols[4].write(f"Rs. {row['Refund Amount']:,.2f}")
                else:
                    st.info("No deleted return records in Recycle Bin. (මකා දැමූ ආපසු භාරගැනීම් නොමැත)")
            else:
                st.info("No deleted return records in Recycle Bin. (මකා දැමූ ආපසු භාරගැනීම් නොමැත)")
