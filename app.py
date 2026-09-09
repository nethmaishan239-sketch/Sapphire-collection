import streamlit as st
import pandas as pd
import os
from datetime import datetime
import barcode
from barcode.writer import ImageWriter
import urllib.parse

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

# ==================== 3. HELPER & DATA HANDLING FUNCTIONS ====================
def load_data(file_path):
    if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
        return pd.DataFrame()
    try:
        df = pd.read_csv(file_path, dtype={"Code": str, "Phone": str, "Invoice ID": str})
        if "Is_Deleted" not in df.columns:
            df["Is_Deleted"] = False
        else:
            df["Is_Deleted"] = df["Is_Deleted"].fillna(False).astype(bool)
        if "Code" in df.columns:
            df["Code"] = df["Code"].astype(str).str.strip()
        return df
    except Exception as e:
        st.error(f"දත්ත පූරණය කිරීමේ දෝෂයක් ({file_path}): {e}")
        return pd.DataFrame()

def save_data(df, file_path):
    try:
        df.to_csv(file_path, index=False)
    except Exception as e:
        st.error(f"දත්ත සුරැකීමේ දෝෂයක් ({file_path}): {e}")

def init_files():
    files_schema = {
        PRODUCT_FILE: ["Code", "Product Name", "Cost Price", "Selling Price", "Total Meter", "Total Yard", "Total Quantity (Pcs)", "Total Kg", "Total Liter", "Min Threshold", "Supplier", "Is_Deleted"],
        SALES_FILE: ["Invoice ID", "Date", "Time", "Product Name", "Code", "Meter Amount", "Yard Amount", "Quantity (Pcs)", "Kg Amount", "Liter Amount", "Warranty", "Cost Price", "Selling Price", "Discount", "Points Used", "Total Price", "Profit", "Payment Method", "Customer", "Is_Deleted"],
        EXPENSES_FILE: ["Date", "Description", "Amount", "Is_Deleted"],
        CREDIT_FILE: ["Customer Name", "Phone", "Due Balance", "Last Date", "Is_Deleted"],
        CUSTOMER_FILE: ["Customer Name", "Phone", "Loyalty Points", "Is_Deleted"],
        SUPPLIER_FILE: ["Supplier Name", "Phone", "Company", "Pending Payable", "Is_Deleted"],
        RETURNS_FILE: ["Date", "Invoice ID", "Product Name", "Code", "Returned Qty", "Refund Amount", "Reason", "Is_Deleted"]
    }
    for file_path, columns in files_schema.items():
        if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
            pd.DataFrame(columns=columns).to_csv(file_path, index=False)

init_files()

# ==================== 4. SESSION STATE MANAGEMENT ====================
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

for key in ["form_meter", "form_yard", "form_pcs", "form_kg", "form_liter"]:
    if key not in st.session_state:
        st.session_state[key] = 0.0

# ==================== 5. LOGIN PAGE UI ====================
if not st.session_state["logged_in"]:
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #1E88E5;'>SAPPHIRE COLLECTION POS</h1>", unsafe_allow_html=True)
    st.markdown("<h4 style='text-align: center; color: #555;'>ව්‍යාපාර සහ තොග කළමනාකරණ පද්ධතිය</h4>", unsafe_allow_html=True)
    st.markdown("---")

    col1, col2, col3 = st.columns([1, 1.5, 1])
    with col2:
        st.subheader("🔐 පරිශීලක පිවිසුම (User Login)")
        role_selected = st.selectbox("භාවිතා කරන අංශය (Select Role):", ["Admin (පරිපාලක)", "Cashier (කැෂියර්)"])
        pwd_input = st.text_input("මුරපදය ඇතුළත් කරන්න (Password):", type="password", key="login_pwd")
        
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("🚀 පද්ධතියට පිවිසෙන්න (Login)", type="primary", use_container_width=True):
            if "Admin" in role_selected and pwd_input == "1234":
                st.session_state["logged_in"] = True
                st.session_state["user_role"] = "Admin"
                st.session_state["current_page"] = "Main Menu"
                st.rerun()
            elif "Cashier" in role_selected and pwd_input == "0000":
                st.session_state["logged_in"] = True
                st.session_state["user_role"] = "Cashier"
                st.session_state["current_page"] = "Main Menu"
                st.rerun()
            else:
                st.error("❌ වැරදි මුරපදයක්! කරුණාකර නැවත උත්සාහ කරන්න.")

else:
    # ==================== 6. SYSTEM HEADER & NAVIGATION ====================
    top_col1, top_col2, top_col3 = st.columns([3, 2, 1])
    
    with top_col1:
        if st.session_state["current_page"] != "Main Menu":
            if st.button("⬅️ ප්‍රධාන මෙනුවට යන්න (Back)"):
                st.session_state["current_page"] = "Main Menu"
                st.rerun()
        else:
            st.write("📍 **මුල් පිටුව (Dashboard Overview)**")

    with top_col2:
        st.write(f"👤 භාවිතා කරන්නා: **{st.session_state['user_role']}**")

    with top_col3:
        if st.button("🔒 ඉවත් වන්න (Logout)"):
            st.session_state["logged_in"] = False
            st.session_state["user_role"] = None
            st.session_state["current_page"] = "Main Menu"
            st.session_state["cart"] = []
            st.rerun()

    st.markdown("---")

    # ==================== 7. MAIN MENU DASHBOARD ====================
    if st.session_state["current_page"] == "Main Menu":
        st.markdown("<h1 style='text-align: center; color: #333;'>💎 Sapphire Collection POS System</h1>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center;'>කළමනාකරණ අංශයක් තෝරන්න (Select a module)</p>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.subheader("📦 භාණ්ඩ අංශය")
            if st.button("📦 භාණ්ඩ කළමනාකරණය (Product)", use_container_width=True):
                st.session_state["current_page"] = "Product"
                st.rerun()
            if st.button("📖 උදාර පොත - ණය ලේඛනය (Credit Book)", use_container_width=True):
                st.session_state["current_page"] = "Credit Book"
                st.rerun()
            if st.button("👥 පාරිභෝගික ලියාපදිංචිය (Customers)", use_container_width=True):
                st.session_state["current_page"] = "Customers"
                st.rerun()
            if st.button("🏷️ බාර්කෝඩ් සකස්කිරීම (Barcode)", use_container_width=True):
                st.session_state["current_page"] = "Barcode"
                st.rerun()

        with col2:
            st.subheader("🧾 අලෙවි අංශය")
            if st.button("🧾 බිල්පත් නිකුත් කිරීම (Bill Issue)", use_container_width=True):
                st.session_state["current_page"] = "Bill Issue"
                st.rerun()
            if st.button("🔄 භාණ්ඩ නැවත භාරගැනීම (Returns)", use_container_width=True):
                st.session_state["current_page"] = "Returns"
                st.rerun()
            if st.session_state["user_role"] == "Admin":
                if st.button("💸 වියදම් ලුහුබැඳීම (Expenses)", use_container_width=True):
                    st.session_state["current_page"] = "Expenses"
                    st.rerun()

        with col3:
            st.subheader("📊 වාර්තා අංශය")
            if st.button("📊 තොග මට්ටම් පරීක්ෂාව (Stock Levels)", use_container_width=True):
                st.session_state["current_page"] = "Stock"
                st.rerun()
            if st.session_state["user_role"] == "Admin":
                if st.button("📈 විකුණුම් සහ ලාභ වාර්තා (Reports)", use_container_width=True):
                    st.session_state["current_page"] = "Reports"
                    st.rerun()
                if st.button("🏭 සපයන්නන් කළමනාකරණය (Suppliers)", use_container_width=True):
                    st.session_state["current_page"] = "Suppliers"
                    st.rerun()

        if st.session_state["user_role"] == "Admin":
            st.markdown("<br><hr>", unsafe_allow_html=True)
            if st.button("🗑️ ඉවත දැමූ බඳුන (Recycle Bin)", use_container_width=True):
                st.session_state["current_page"] = "Recycle Bin"
                st.rerun()

    # ==================== 8. BARCODE GENERATOR ====================
    elif st.session_state["current_page"] == "Barcode":
        st.title("🏷️ බාර්කෝඩ් ජනක යන්ත්‍රය (Barcode Generator)")
        df_products = load_data(PRODUCT_FILE)
        active_products = df_products[df_products["Is_Deleted"] == False] if not df_products.empty else pd.DataFrame()

        if not active_products.empty:
            sel_p = st.selectbox("බාර්කෝඩ් සෑදීමට භාණ්ඩය තෝරන්න:", active_products["Code"].astype(str) + " - " + active_products["Product Name"])
            code_to_gen = sel_p.split(" - ")[0].strip()

            if st.button("බාර්කෝඩ් මුද්‍රණය කරන්න (Generate Barcode)"):
                try:
                    code128 = barcode.get_barcode_class('code128')
                    my_barcode = code128(code_to_gen, writer=ImageWriter())
                    filename = my_barcode.save(f"barcode_{code_to_gen}")
                    st.image(filename, caption=f"බාර්කෝඩ් අංකය: {code_to_gen}", width=300)
                except Exception as e:
                    st.error(f"බාර්කෝඩ් සැකසීම අසාර්ථකයි: {e}")
        else:
            st.info("සක්‍රීය භාණ්ඩ නොමැත.")

    # ==================== 9. PRODUCT MANAGEMENT ====================
    elif st.session_state["current_page"] == "Product":
        st.title("📦 භාණ්ඩ සහ තොග කළමනාකරණය (Product Management)")
        df_products = load_data(PRODUCT_FILE)
        df_sup = load_data(SUPPLIER_FILE)
        
        active_products = df_products[df_products["Is_Deleted"] == False] if not df_products.empty else pd.DataFrame()
        active_sups = df_sup[df_sup["Is_Deleted"] == False]["Supplier Name"].tolist() if not df_sup.empty else ["Default Supplier"]

        col_left, col_right = st.columns([1, 1])

        with col_left:
            st.subheader("➕ නව භාණ්ඩයක් ඇතුළත් කරන්න (Add Product)")
            with st.form("add_product_form", clear_on_submit=True):
                p_code = st.text_input("🏷️ භාණ්ඩ කේතය / අංකය (Product Code)").strip()
                p_name = st.text_input("📦 භාණ්ඩයේ නම (Product Name)").strip()
                
                p_cost = st.number_input("මිළදී ගත් මිල (Cost Price Rs.)", min_value=0.0, format="%.2f") if st.session_state["user_role"] == "Admin" else 0.0
                p_sell = st.number_input("විකිණුම් මිල (Selling Price Rs.)", min_value=0.0, format="%.2f")
                p_sup = st.selectbox("සපයන්නා (Supplier)", active_sups)

                st.markdown("---")
                st.markdown("<b>මිනුම් ඒකක අනුව ප්‍රමාණයන්:</b>", unsafe_allow_html=True)
                col_p1, col_p2, col_p3, col_p4, col_p5 = st.columns(5)
                p_meter = col_p1.number_input("මීටර්", min_value=0.0, step=0.5)
                p_yard = col_p2.number_input("යට්", min_value=0.0, step=0.5)
                p_qty = col_p3.number_input("කෑලි", min_value=0.0, step=1.0)
                p_kg = col_p4.number_input("කි.ග්‍රෑ", min_value=0.0, step=0.1)
                p_liter = col_p5.number_input("ලීටර්", min_value=0.0, step=0.1)

                p_min = st.number_input("⚠️ අවම තොග සීමාව (Min Reorder Level)", min_value=0.0, value=5.0)

                if st.form_submit_button("භාණ්ඩය සුරකින්න (Save Product Record)"):
                    if p_code and p_name:
                        new_row = pd.DataFrame([{
                            "Code": str(p_code), "Product Name": str(p_name), "Cost Price": float(p_cost),
                            "Selling Price": float(p_sell), "Total Meter": float(p_meter), "Total Yard": float(p_yard),
                            "Total Quantity (Pcs)": float(p_qty), "Total Kg": float(p_kg), "Total Liter": float(p_liter),
                            "Min Threshold": float(p_min), "Supplier": str(p_sup), "Is_Deleted": False
                        }])
                        if not df_products.empty and str(p_code) in df_products["Code"].astype(str).values:
                            df_products = df_products[df_products["Code"].astype(str) != str(p_code)]
                        df_products = pd.concat([df_products, new_row], ignore_index=True)
                        save_data(df_products, PRODUCT_FILE)
                        st.success("භාණ්ඩය සාර්ථකව සුරකින ලදී!")
                        st.rerun()
                    else:
                        st.error("⚠️ කරුණාකර කේතය (Code) සහ නම (Name) යන දෙකම ඇතුළත් කරන්න!")

        with col_right:
            st.subheader("🗑️ භාණ්ඩ ඉවත් කිරීම (Delete Product)")
            if not active_products.empty:
                del_p_sel = st.selectbox("ඉවත් කිරීමට භාණ්ඩය තෝරන්න:", active_products["Code"].astype(str) + " - " + active_products["Product Name"])
                if st.button("🗑️ ඉවත දැමූ බඳුනට යවන්න (Move to Trash)"):
                    code_to_del = del_p_sel.split(" - ")[0].strip()
                    df_products.loc[df_products["Code"].astype(str) == code_to_del, "Is_Deleted"] = True
                    save_data(df_products, PRODUCT_FILE)
                    st.warning("භාණ්ඩය ඉවත දැමූ බඳුනට යවන ලදී!")
                    st.rerun()

        st.markdown("---")
        st.subheader("📋 සක්‍රීය භාණ්ඩ ලැයිස්තුව (Active Products)")
        if not active_products.empty:
            display_df = active_products[["Code", "Product Name", "Selling Price", "Total Meter", "Total Quantity (Pcs)", "Supplier"]].copy()
            display_df["Select_Delete"] = False
            
            edited_df = st.data_editor(
                display_df,
                column_config={"Select_Delete": st.column_config.CheckboxColumn("මකන්න (Delete)", default=False)},
                disabled=["Code", "Product Name", "Selling Price", "Total Meter", "Total Quantity (Pcs)", "Supplier"],
                hide_index=True, use_container_width=True, key="product_table_editor"
            )
            
            marked_codes = edited_df[edited_df["Select_Delete"] == True]["Code"].astype(str).tolist()
            if marked_codes:
                for c in marked_codes:
                    df_products.loc[df_products["Code"].astype(str) == c, "Is_Deleted"] = True
                save_data(df_products, PRODUCT_FILE)
                st.rerun()
        else:
            st.info("සක්‍රීය භාණ්ඩ නොමැත.")

    # ==================== 10. BILL ISSUE & CASHIER ====================
    elif st.session_state["current_page"] == "Bill Issue":
        st.title("🧾 බිල්පත් නිකුත් කිරීමේ අංශය (Bill Issue & Cashier)")
        df_products = load_data(PRODUCT_FILE)
        active_products = df_products[df_products["Is_Deleted"] == False] if not df_products.empty else pd.DataFrame()

        if not active_products.empty:
            col_left, col_right = st.columns([1.1, 0.9])

            with col_left:
                st.subheader("🔍 භාණ්ඩ සෙවීම සහ එකතු කිරීම")
                search_query = st.text_input("බාර්කෝඩ් ස්කෑන් කරන්න හෝ නම/කේතය ටයිප් කරන්න:").strip()
                filtered = active_products[
                    active_products["Code"].astype(str).str.contains(search_query, case=False, na=False) |
                    active_products["Product Name"].str.contains(search_query, case=False, na=False)
                ] if search_query else active_products

                if not filtered.empty:
                    sel_prod = st.selectbox("භාණ්ඩය තෝරන්න:", filtered["Code"].astype(str) + " - " + filtered["Product Name"])
                    sel_code = sel_prod.split(" - ")[0].strip()
                    prod_row = filtered[filtered["Code"].astype(str) == sel_code].iloc[0]

                    st.success(f"විකිණුම් මිල: **රු. {float(prod_row['Selling Price']):,.2f}**")

                    col_b1, col_b2, col_b3, col_b4, col_b5 = st.columns(5)
                    sell_m = col_b1.number_input("මීටර්:", min_value=0.0, step=0.1, value=st.session_state["form_meter"])
                    sell_y = col_b2.number_input("යට්:", min_value=0.0, step=0.1, value=st.session_state["form_yard"])
                    sell_q = col_b3.number_input("කෑලි:", min_value=0.0, step=1.0, value=st.session_state["form_pcs"])
                    sell_kg = col_b4.number_input("කි.ග්‍රෑ:", min_value=0.0, step=0.05, value=st.session_state["form_kg"])
                    sell_l = col_b5.number_input("ලීටර්:", min_value=0.0, step=0.05, value=st.session_state["form_liter"])

                    warranty_val = st.selectbox("වගකීම් කාලය (Warranty):", ["වගකීම් නැත", "මාස 6යි", "වසර 1යි", "වසර 2යි", "වසර 3යි"])
                    unit_qty = sell_m + sell_y + sell_q + sell_kg + sell_l
                    item_total = unit_qty * float(prod_row["Selling Price"])

                    st.markdown(f"#### භාණ්ඩයේ එකතුව: **රු. {item_total:,.2f}**")

                    if st.button("🛒 කරත්තයට එකතු කරන්න (Add to Cart)", use_container_width=True):
                        if unit_qty > 0:
                            st.session_state["cart"].append({
                                "Code": sel_code, "Product Name": prod_row["Product Name"],
                                "Cost Price": float(prod_row["Cost Price"]), "Selling Price": float(prod_row["Selling Price"]),
                                "Meter Amount": sell_m, "Yard Amount": sell_y, "Quantity (Pcs)": sell_q,
                                "Kg Amount": sell_kg, "Liter Amount": sell_l, "Total Qty": unit_qty,
                                "Warranty": warranty_val, "Total Price": item_total,
                                "Profit": item_total - (unit_qty * float(prod_row["Cost Price"]))
                            })
                            st.session_state["form_meter"] = 0.0
                            st.session_state["form_yard"] = 0.0
                            st.session_state["form_pcs"] = 0.0
                            st.session_state["form_kg"] = 0.0
                            st.session_state["form_liter"] = 0.0
                            st.success("කරත්තයට එකතු කරන ලදී!")
                            st.rerun()
                        else:
                            st.warning("කරුණාකර ප්‍රමාණය සඳහන් කරන්න!")

            with col_right:
                st.subheader("🛍️ පාරිභෝගික කරත්තය (Shopping Cart)")
                if len(st.session_state["cart"]) > 0:
                    subtotal = 0.0
                    cart_data = []
                    for idx, item in enumerate(st.session_state["cart"]):
                        cart_data.append({
                            "Cart_ID": idx, "Remove": False, "Product Name": item["Product Name"],
                            "Qty": item["Total Qty"], "Total (Rs.)": item["Total Price"]
                        })
                        subtotal += item["Total Price"]
                    
                    df_cart_table = pd.DataFrame(cart_data)
                    edited_cart = st.data_editor(
                        df_cart_table,
                        column_config={"Remove": st.column_config.CheckboxColumn("ඉවත් කරන්න", default=False)},
                        disabled=["Cart_ID", "Product Name", "Qty", "Total (Rs.)"],
                        hide_index=True, use_container_width=True, key="cart_table_editor"
                    )

                    to_remove_ids = edited_cart[edited_cart["Remove"] == True]["Cart_ID"].tolist()
                    if to_remove_ids:
                        st.session_state["cart"] = [item for i, item in enumerate(st.session_state["cart"]) if i not in to_remove_ids]
                        st.rerun()

                    st.markdown(f"### 💰 මුළු එකතුව (Grand Total): රු. {subtotal:,.2f}")

                    if st.button("🗑️ සම්පූර්ණ කරත්තය හිස් කරන්න (Clear Cart)", type="secondary"):
                        st.session_state["cart"] = []
                        st.rerun()

                    st.markdown("---")
                    cust_phone = st.text_input("📱 පාරිභෝගික දුරකථන අංකය:").strip()
                    pay_method = st.selectbox("ගෙවීම් ක්‍රමය (Payment Method):", ["මුදල් (Cash)", "කාඩ්පත (Card)", "මාර්ගගත මාරු කිරීම (Online Transfer)", "ණයට (Credit)"])

                    if st.button("✅ බිල්පත මුද්‍රණය කර අවසන් කරන්න (Checkout)", type="primary", use_container_width=True):
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
                                "Invoice ID": inv_id, "Date": now_str, "Time": datetime.now().strftime("%H:%M:%S"),
                                "Discount": 0, "Points Used": 0, "Payment Method": pay_method,
                                "Customer": cust_phone if cust_phone else "Guest", "Is_Deleted": False
                            })
                            df_sales = pd.concat([df_sales, pd.DataFrame([new_sale])], ignore_index=True)

                        save_data(df_products, PRODUCT_FILE)
                        save_data(df_sales, SALES_FILE)

                        st.session_state["last_invoice"] = {
                            "id": inv_id, "date": now_str, "items": st.session_state["cart"],
                            "total": subtotal, "payment": pay_method, "phone": cust_phone if cust_phone else ""
                        }
                        st.session_state["cart"] = []
                        st.success("✅ බිල්පත සාර්ථකව සකස් කරන ලදී!")
                        st.rerun()
                else:
                    st.info("කරත්තය හිස්ය.")

        if st.session_state.get("last_invoice"):
            st.markdown("---")
            st.subheader("🖨️ රිසිට්පත (Receipt)")
            inv = st.session_state["last_invoice"]
            
            receipt_html = f"""
            <div style="width: 300px; padding: 15px; border: 1px dashed #333; font-family: monospace; background: #fff; color: #000;">
                <h3 style="text-align: center; margin: 0;">SAPPHIRE COLLECTION</h3>
                <p style="text-align: center; margin: 0;">ප්‍රධාන වීදිය, නගරය</p>
                <p style="text-align: center; margin: 0;">දුරකථන: 077-1234567</p>
                <hr style="border-top: 1px dashed #000;">
                <p><b>බිල් අංකය:</b> {inv['id']}<br><b>දිනය:</b> {inv['date']}</p>
                <hr style="border-top: 1px dashed #000;">
            """
            for it in inv['items']:
                receipt_html += f"<div>{it['Product Name']} x {it['Total Qty']}<span style='float:right;'>රු.{it['Total Price']:,.2f}</span></div>"
            
            receipt_html += f"""
                <hr style="border-top: 1px dashed #000;">
                <h4><b>මුළු එකතුව: <span style="float:right;">රු.{inv['total']:,.2f}</span></b></h4>
                <p>ගෙවීම් ක්‍රමය: {inv['payment']}</p>
                <hr style="border-top: 1px dashed #000;">
                <p style="text-align: center;">ස්තුතියි, නැවත එන්න!</p>
            </div>
            """
            st.components.v1.html(receipt_html, height=380)

            if st.button("🔄 නව බිල්පතක් සකසන්න (New Bill)", type="primary", use_container_width=True):
                st.session_state["last_invoice"] = None
                st.rerun()

            cust_phone_val = inv.get("phone", "").strip()
            if cust_phone_val:
                formatted_phone = "+94" + cust_phone_val[1:] if cust_phone_val.startswith("0") else (cust_phone_val if cust_phone_val.startswith("+") else "+94" + cust_phone_val)
                sms_msg = f"Sapphire Collection වෙතින් මිලදී ගැනීම වෙනුවෙන් ස්තුතියි! බිල් අංකය: {inv['id']}, එකතුව: රු.{inv['total']:,.2f}."
                sms_intent_url = f"sms:{formatted_phone}?body={urllib.parse.quote(sms_msg)}"
                st.markdown(
                    f"""<a href="{sms_intent_url}" target="_blank" style="text-decoration: none;"><button style="background-color: #25D366; color: white; padding: 12px 20px; font-size: 16px; font-weight: bold; border: none; border-radius: 8px; cursor: pointer; width: 100%;">📱 SMS එකක් යවන්න ({formatted_phone})</button></a>""", 
                    unsafe_allow_html=True
                )

    # ==================== 11. REPORTS ====================
    elif st.session_state["current_page"] == "Reports":
        st.title("📈 විකුණුම් සහ ලාභ වාර්තා (Reports)")
        df_sales = load_data(SALES_FILE)
        df_exp = load_data(EXPENSES_FILE)
        active_sales = df_sales[df_sales["Is_Deleted"] == False] if not df_sales.empty else pd.DataFrame()

        if not active_sales.empty:
            st.subheader("📊 දෛනික ආදායම් ප්‍රවණතාව")
            st.line_chart(active_sales.groupby("Date")["Total Price"].sum())

            m1, m2, m3, m4 = st.columns(4)
            total_rev = active_sales['Total Price'].sum()
            total_prof = active_sales['Profit'].sum()
            total_exp = df_exp[df_exp["Is_Deleted"] == False]['Amount'].sum() if not df_exp.empty else 0.0
            
            m1.metric("💰 මුළු ආදායම", f"රු. {total_rev:,.2f}")
            m2.metric("📦 දළ ලාභය", f"රු. {total_prof:,.2f}")
            m3.metric("💸 සාප්පු වියදම්", f"රු. {total_exp:,.2f}")
            m4.metric("💵 ශුද්ධ ලාභය", f"රු. {total_prof - total_exp:,.2f}")

            st.markdown("---")
            st.subheader("📜 විකුණුම් ඉතිහාසය (Sales History)")
            rep_display = active_sales[["Invoice ID", "Date", "Product Name", "Total Price", "Payment Method", "Customer"]].copy()
            rep_display["Select_Delete"] = False
            
            edited_rep = st.data_editor(
                rep_display,
                column_config={"Select_Delete": st.column_config.CheckboxColumn("මකන්න", default=False)},
                disabled=["Invoice ID", "Date", "Product Name", "Total Price", "Payment Method", "Customer"],
                hide_index=True, use_container_width=True, key="sales_table_editor"
            )
            
            marked_invs = edited_rep[edited_rep["Select_Delete"] == True]["Invoice ID"].astype(str).tolist()
            if marked_invs:
                for inv in marked_invs:
                    df_sales.loc[df_sales["Invoice ID"].astype(str) == inv, "Is_Deleted"] = True
                save_data(df_sales, SALES_FILE)
                st.rerun()
        else:
            st.info("විකුණුම් වාර්තා නොමැත.")

    # ==================== 12. STOCK LEVELS ====================
    elif st.session_state["current_page"] == "Stock":
        st.title("📊 තොග මට්ටම් සහ අවවාද (Stock Levels)")
        df_p = load_data(PRODUCT_FILE)
        active_p = df_p[df_p["Is_Deleted"] == False] if not df_p.empty else pd.DataFrame()

        if not active_p.empty:
            st.subheader("📦 සම්පූර්ණ තොග වගුව (Complete Stock Table)")
            stock_display = active_p[["Code", "Product Name", "Total Meter", "Total Quantity (Pcs)", "Total Kg", "Supplier"]].copy()
            stock_display["Select_Delete"] = False
            
            edited_stock = st.data_editor(
                stock_display,
                column_config={"Select_Delete": st.column_config.CheckboxColumn("මකන්න", default=False)},
                disabled=["Code", "Product Name", "Total Meter", "Total Quantity (Pcs)", "Total Kg", "Supplier"],
                hide_index=True, use_container_width=True, key="stock_table_editor"
            )
            marked_codes = edited_stock[edited_stock["Select_Delete"] == True]["Code"].astype(str).tolist()
            if marked_codes:
                for c in marked_codes:
                    df_p.loc[df_p["Code"].astype(str) == c, "Is_Deleted"] = True
                save_data(df_p, PRODUCT_FILE)
                st.rerun()
        else:
            st.info("තොග දත්ත නොමැත.")

    # ==================== 13. EXPENSE TRACKER ====================
    elif st.session_state["current_page"] == "Expenses":
        st.title("💸 සාප්පු වියදම් ලුහුබැඳීම (Expense Tracker)")
        df_exp = load_data(EXPENSES_FILE)
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("➕ නව වියදමක් ඇතුළත් කරන්න")
            with st.form("add_exp_form", clear_on_submit=True):
                exp_desc = st.text_input("වියදම් විස්තරය (Description)").strip()
                exp_amt = st.number_input("මුදල (Rs.)", min_value=0.0, format="%.2f")
                if st.form_submit_button("වියදම සුරකින්න (Save Expense)"):
                    if exp_desc and exp_amt > 0:
                        df_exp = pd.concat([df_exp, pd.DataFrame([{"Date": datetime.now().strftime("%Y-%m-%d"), "Description": exp_desc, "Amount": exp_amt, "Is_Deleted": False}])], ignore_index=True)
                        save_data(df_exp, EXPENSES_FILE)
                        st.success("වියදම සුරකින ලදී!")
                        st.rerun()

        with col2:
            st.subheader("📜 වියදම් ලේඛනය (Expense Log)")
            active_exp = df_exp[df_exp["Is_Deleted"] == False] if not df_exp.empty else pd.DataFrame()
            if not active_exp.empty:
                exp_display = active_exp[["Date", "Description", "Amount"]].copy()
                exp_display["Select_Delete"] = False
                
                edited_exp = st.data_editor(
                    exp_display,
                    column_config={"Select_Delete": st.column_config.CheckboxColumn("මකන්න", default=False)},
                    disabled=["Date", "Description", "Amount"], hide_index=True, use_container_width=True, key="exp_table_editor"
                )
                marked_del = edited_exp[edited_exp["Select_Delete"] == True].index.tolist()
                if marked_del:
                    for i in marked_del:
                        df_exp.loc[active_exp.index[i], "Is_Deleted"] = True
                    save_data(df_exp, EXPENSES_FILE)
                    st.rerun()
            else:
                st.info("වියදම් වාර්තා නොමැත.")

    # ==================== 14. SUPPLIER MANAGEMENT ====================
    elif st.session_state["current_page"] == "Suppliers":
        st.title("🏭 සපයන්නන් කළමනාකරණය (Supplier Management)")
        df_sup = load_data(SUPPLIER_FILE)
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("➕ නව සපයන්නකු ලියාපදිංචි කරන්න")
            with st.form("add_sup_form", clear_on_submit=True):
                sup_n = st.text_input("සපයන්නාගේ නම (Supplier Name)").strip()
                sup_p = st.text_input("දුරකථන අංකය (Phone)").strip()
                sup_c = st.text_input("සමාගමේ නම (Company)").strip()
                if st.form_submit_button("සපයන්නා ලියාපදිංචි කරන්න"):
                    if sup_n:
                        df_sup = pd.concat([df_sup, pd.DataFrame([{"Supplier Name": sup_n, "Phone": sup_p, "Company": sup_c, "Pending Payable": 0.0, "Is_Deleted": False}])], ignore_index=True)
                        save_data(df_sup, SUPPLIER_FILE)
                        st.success("ලියාපදිංචි කරන ලදී!")
                        st.rerun()

        with col2:
            st.subheader("📋 සපයන්නන් ලැයිස්තුව")
            active_sup = df_sup[df_sup["Is_Deleted"] == False] if not df_sup.empty else pd.DataFrame()
            if not active_sup.empty:
                sup_display = active_sup[["Supplier Name", "Phone", "Company"]].copy()
                sup_display["Select_Delete"] = False
                
                edited_sup = st.data_editor(
                    sup_display,
                    column_config={"Select_Delete": st.column_config.CheckboxColumn("මකන්න", default=False)},
                    disabled=["Supplier Name", "Phone", "Company"], hide_index=True, use_container_width=True, key="sup_table_editor"
                )
                marked_del = edited_sup[edited_sup["Select_Delete"] == True].index.tolist()
                if marked_del:
                    for i in marked_del:
                        df_sup.loc[active_sup.index[i], "Is_Deleted"] = True
                    save_data(df_sup, SUPPLIER_FILE)
                    st.rerun()
            else:
                st.info("සපයන්නන් නොමැත.")

    # ==================== 15. CREDIT BOOK ====================
    elif st.session_state["current_page"] == "Credit Book":
        st.title("📖 උදාර පොත - පාරිභෝගික ණය ලේඛනය (Credit Ledger)")
        df_credit = load_data(CREDIT_FILE)
        active_credit = df_credit[df_credit["Is_Deleted"] == False] if not df_credit.empty else pd.DataFrame()

        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("➕ නව ණය මුදලක් ඇතුළත් කරන්න")
            with st.form("add_credit_form", clear_on_submit=True):
                c_name = st.text_input("පාරිභෝගිකයාගේ නම (Customer Name)").strip()
                c_phone = st.text_input("දුරකථන අංකය (Phone)").strip()
                c_due = st.number_input("එතුමට/ඇයට ඇති ණය මුදල (Rs.)", min_value=0.0, format="%.2f")

                if st.form_submit_button("ණය වාර්තාව සුරකින්න"):
                    if c_name and c_due > 0:
                        existing_match = df_credit[(df_credit["Customer Name"].str.lower() == c_name.lower()) & (df_credit["Is_Deleted"] == False)]
                        if not existing_match.empty:
                            idx = existing_match.index[0]
                            df_credit.loc[idx, "Due Balance"] = float(df_credit.loc[idx, "Due Balance"]) + float(c_due)
                            df_credit.loc[idx, "Last Date"] = datetime.now().strftime("%Y-%m-%d")
                        else:
                            df_credit = pd.concat([df_credit, pd.DataFrame([{"Customer Name": str(c_name), "Phone": str(c_phone), "Due Balance": float(c_due), "Last Date": datetime.now().strftime("%Y-%m-%d"), "Is_Deleted": False}])], ignore_index=True)
                        save_data(df_credit, CREDIT_FILE)
                        st.success("ණය වාර්තාව සාර්ථකව සුරකින ලදී!")
                        st.rerun()

        with col2:
            st.subheader("💵 ණය මුදලක් පියවීම (Settle Due)")
            pending_credits = active_credit[active_credit["Due Balance"] > 0] if not active_credit.empty else pd.DataFrame()
            if not pending_credits.empty:
                with st.form("settle_credit_form", clear_on_submit=True):
                    sel_cust = st.selectbox("පාරිභෝගිකයා තෝරන්න:", pending_credits["Customer Name"].tolist())
                    curr_due = float(pending_credits[pending_credits["Customer Name"] == sel_cust]["Due Balance"].iloc[0])
                    st.info(f"ගෙවිය යුතු ඉතිරි ණය මුදල **{sel_cust}**: **රු. {curr_due:,.2f}**")
                    pay_amt = st.number_input("ගවන ලද මුදල (Rs.)", min_value=0.0, max_value=curr_due, format="%.2f")
                    if st.form_submit_button("✅ මුදල අඩු කරන්න"):
                        if pay_amt > 0:
                            idx = df_credit[(df_credit["Customer Name"] == sel_cust) & (df_credit["Is_Deleted"] == False)].index[0]
                            df_credit.loc[idx, "Due Balance"] = curr_due - pay_amt
                            df_credit.loc[idx, "Last Date"] = datetime.now().strftime("%Y-%m-%d")
                            save_data(df_credit, CREDIT_FILE)
                            st.success("ගෙවීම සාර්ථකව සටහන් විය!")
                            st.rerun()
            else:
                st.info("🎉 ගෙවිය යුතු ණය මුදල් කිසිවක් නොමැත!")

        st.markdown("---")
        st.subheader("📋 ණය ලේඛන වාර්තා (Credit Records)")
        if not active_credit.empty:
            cred_display = active_credit[["Customer Name", "Phone", "Due Balance", "Last Date"]].copy()
            cred_display["Select_Delete"] = False
            
            edited_cred = st.data_editor(
                cred_display,
                column_config={"Select_Delete": st.column_config.CheckboxColumn("මකන්න", default=False)},
                disabled=["Customer Name", "Phone", "Due Balance", "Last Date"], hide_index=True, use_container_width=True, key="cred_table_editor"
            )
            marked_del = edited_cred[edited_cred["Select_Delete"] == True].index.tolist()
            if marked_del:
                for i in marked_del:
                    df_credit.loc[active_credit.index[i], "Is_Deleted"] = True
                save_data(df_credit, CREDIT_FILE)
                st.rerun()
        else:
            st.info("ණය වාර්තා නොමැත.")

    # ==================== 16. CUSTOMERS ====================
    elif st.session_state["current_page"] == "Customers":
        st.title("👥 පාරිභෝගික ලියාපදිංචිය (Customer Directory)")
        df_cust = load_data(CUSTOMER_FILE)
        col1, col2 = st.columns([1, 1])

        with col1:
            st.subheader("➕ නව පාරිභෝගිකයකු එකතු කරන්න")
            with st.form("add_cust_form", clear_on_submit=True):
                cust_n = st.text_input("පාරිභෝගිකයාගේ සම්පූර්ණ නම").strip()
                cust_p = st.text_input("දුරකථන අංකය").strip()
                if st.form_submit_button("පාරිභෝගිකයා ලියාපදිංචි කරන්න"):
                    if cust_n:
                        df_cust = pd.concat([df_cust, pd.DataFrame([{"Customer Name": cust_n, "Phone": cust_p, "Loyalty Points": 0, "Is_Deleted": False}])], ignore_index=True)
                        save_data(df_cust, CUSTOMER_FILE)
                        st.success("සාර්ථකව ලියාපදිංචි කරන ලදී!")
                        st.rerun()

        with col2:
            st.subheader("📋 පාරිභෝගික නාමාවලිය")
            active_cust = df_cust[df_cust["Is_Deleted"] == False] if not df_cust.empty else pd.DataFrame()
            if not active_cust.empty:
                cust_display = active_cust[["Customer Name", "Phone", "Loyalty Points"]].copy()
                cust_display["Select_Delete"] = False
                
                edited_cust = st.data_editor(
                    cust_display,
                    column_config={"Select_Delete": st.column_config.CheckboxColumn("මකන්න", default=False)},
                    disabled=["Customer Name", "Phone", "Loyalty Points"], hide_index=True, use_container_width=True, key="cust_table_editor"
                )
                marked_del = edited_cust[edited_cust["Select_Delete"] == True].index.tolist()
                if marked_del:
                    for i in marked_del:
                        df_cust.loc[active_cust.index[i], "Is_Deleted"] = True
                    save_data(df_cust, CUSTOMER_FILE)
                    st.rerun()
            else:
                st.info("පාරිභෝගිකයන් නොමැත.")

    # ==================== 17. RETURNS ====================
    elif st.session_state["current_page"] == "Returns":
        st.title("🔄 භාණ්ඩ නැවත භාරගැනීම සහ මුදල් ආපසු ගෙවීම (Returns)")
        df_sales = load_data(SALES_FILE)
        df_products = load_data(PRODUCT_FILE)
        df_returns = load_data(RETURNS_FILE)

        inv_search = st.text_input("බිල් අංකය (Invoice ID) ඇතුළත් කර සොයන්න:").strip()
        if inv_search:
            matched = df_sales[df_sales["Invoice ID"].astype(str) == inv_search] if not df_sales.empty else pd.DataFrame()
            if not matched.empty:
                st.subheader("හමුවූ බිල්පත් භාණ්ඩ:")
                st.dataframe(matched[["Product Name", "Code", "Selling Price", "Meter Amount", "Yard Amount", "Quantity (Pcs)", "Total Price"]], use_container_width=True)

                with st.form("process_return_form"):
                    ret_p = st.selectbox("නැවත භාරගන්නා භාණ්ඩය තෝරන්න:", matched["Code"].astype(str) + " - " + matched["Product Name"])
                    sel_code = ret_p.split(" - ")[0].strip()
                    item_matched = matched[matched["Code"].astype(str) == sel_code].iloc[0]

                    col_r1, col_r2, col_r3, col_r4, col_r5 = st.columns(5)
                    ret_m = col_r1.number_input("මීටර්:", min_value=0.0, max_value=float(item_matched.get("Meter Amount", 0)), step=0.1)
                    ret_y = col_r2.number_input("යට්:", min_value=0.0, max_value=float(item_matched.get("Yard Amount", 0)), step=0.1)
                    ret_q = col_r3.number_input("කෑලි:", min_value=0.0, max_value=float(item_matched.get("Quantity (Pcs)", 0)), step=1.0)
                    ret_kg = col_r4.number_input("කි.ග්‍රෑ:", min_value=0.0, max_value=float(item_matched.get("Kg Amount", 0)), step=0.05)
                    ret_l = col_r5.number_input("ලීටර්:", min_value=0.0, max_value=float(item_matched.get("Liter Amount", 0)), step=0.05)

                    ret_qty_total = ret_m + ret_y + ret_q + ret_kg + ret_l
                    refund_amt = ret_qty_total * float(item_matched["Selling Price"])
                    st.info(f"ගෙවිය යුතු මුදල් ආපසු ගෙවීම: **රු. {refund_amt:,.2f}**")
                    ret_reason = st.text_area("භාණ්ඩය ආපසු දීමට හේතුව:").strip()

                    if st.form_submit_button("✅ භාරගෙන තොගයට එක් කරන්න"):
                        if ret_qty_total > 0:
                            if sel_code in df_products["Code"].astype(str).values:
                                p_idx = df_products[df_products["Code"].astype(str) == sel_code].index[0]
                                df_products.loc[p_idx, "Total Meter"] = float(df_products.loc[p_idx, "Total Meter"]) + ret_m
                                df_products.loc[p_idx, "Total Yard"] = float(df_products.loc[p_idx, "Total Yard"]) + ret_y
                                df_products.loc[p_idx, "Total Quantity (Pcs)"] = float(df_products.loc[p_idx, "Total Quantity (Pcs)"]) + ret_q
                                df_products.loc[p_idx, "Total Kg"] = float(df_products.loc[p_idx, "Total Kg"]) + ret_kg
                                df_products.loc[p_idx, "Total Liter"] = float(df_products.loc[p_idx, "Total Liter"]) + ret_l
                                save_data(df_products, PRODUCT_FILE)

                            df_returns = pd.concat([df_returns, pd.DataFrame([{
                                "Date": datetime.now().strftime("%Y-%m-%d"), "Invoice ID": inv_search,
                                "Product Name": item_matched["Product Name"], "Code": sel_code,
                                "Returned Qty": ret_qty_total, "Refund Amount": refund_amt,
                                "Reason": ret_reason, "Is_Deleted": False
                            }])], ignore_index=True)
                            save_data(df_returns, RETURNS_FILE)
                            st.success(f"සාර්ථකයි! ආපසු ගෙවූ මුදල රු. {refund_amt:,.2f}")
                            st.rerun()
                        else:
                            st.warning("කරුණාකර ප්‍රමාණය සඳහන් කරන්න!")
            else:
                st.error("අදාළ බිල් අංකය හමු නොවීය.")

        st.markdown("---")
        st.subheader("📜 භාණ්ඩ ආපසු හැරවීමේ ඉතිහාසය")
        active_returns = df_returns[df_returns["Is_Deleted"] == False] if not df_returns.empty else pd.DataFrame()
        if not active_returns.empty:
            ret_display = active_returns[["Date", "Invoice ID", "Product Name", "Refund Amount"]].copy()
            ret_display["Select_Delete"] = False
            
            edited_ret = st.data_editor(
                ret_display,
                column_config={"Select_Delete": st.column_config.CheckboxColumn("මකන්න", default=False)},
                disabled=["Date", "Invoice ID", "Product Name", "Refund Amount"], hide_index=True, use_container_width=True, key="ret_table_editor"
            )
            marked_del = edited_ret[edited_ret["Select_Delete"] == True].index.tolist()
            if marked_del:
                for i in marked_del:
                    df_returns.loc[active_returns.index[i], "Is_Deleted"] = True
                save_data(df_returns, RETURNS_FILE)
                st.rerun()
        else:
            st.info("ආපසු හැරවීමේ වාර්තා නොමැත.")

    # ==================== 18. RECYCLE BIN ====================
    elif st.session_state["current_page"] == "Recycle Bin":
        st.title("🗑️ ඉවත දැමූ බඳුන (Recycle Bin)")
        df_p = load_data(PRODUCT_FILE)
        deleted_p = df_p[df_p["Is_Deleted"] == True] if not df_p.empty else pd.DataFrame()

        if not deleted_p.empty:
            st.subheader("මකා දැමූ භාණ්ඩ ලැයිස්තුව:")
            for idx, row in deleted_p.iterrows():
                cols = st.columns([1, 1, 1.5, 2.5, 1.5])
                code_val = str(row['Code'])
                if cols[0].button("🔄 නැවත ලබාගන්න", key=f"res_{code_val}_{idx}"):
                    df_p.loc[df_p["Code"].astype(str) == code_val, "Is_Deleted"] = False
                    save_data(df_p, PRODUCT_FILE)
                    st.rerun()
                if cols[1].button("❌ සදහටම මකන්න", key=f"perm_{code_val}_{idx}"):
                    df_p = df_p[df_p["Code"].astype(str) != code_val]
                    save_data(df_p, PRODUCT_FILE)
                    st.rerun()
                cols[2].write(str(code_val))
                cols[3].write(str(row['Product Name']))
                cols[4].write(str(row['Supplier']))
        else:
            st.info("ඉවත දැමූ බඳුන සම්පූර්ණයෙන්ම හිස්ය.")
