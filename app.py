import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Sapphire Collection", layout="wide")

# Files for Data Persistence
PRODUCT_FILE = "products.csv"
SALES_FILE = "sales.csv"

# Function to initialize CSV files
def init_files():
    if not os.path.exists(PRODUCT_FILE) or os.stat(PRODUCT_FILE).st_size == 0:
        df_p = pd.DataFrame(columns=["Code", "Product Name", "One Product Price", "Total Meter", "Total Yard"])
        df_p.to_csv(PRODUCT_FILE, index=False)
    
    if not os.path.exists(SALES_FILE) or os.stat(SALES_FILE).st_size == 0:
        df_s = pd.DataFrame(columns=["Date", "Time", "Product Name", "Code", "Meter Amount", "Yard Amount", "One Product Price", "Total Price"])
        df_s.to_csv(SALES_FILE, index=False)

init_files()

def load_products():
    try:
        df = pd.read_csv(PRODUCT_FILE, dtype={"Code": str})
        for col in ["One Product Price", "Total Meter", "Total Yard"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
        return df
    except Exception:
        return pd.DataFrame(columns=["Code", "Product Name", "One Product Price", "Total Meter", "Total Yard"])

def save_products(df):
    df.to_csv(PRODUCT_FILE, index=False)

def load_sales():
    try:
        df = pd.read_csv(SALES_FILE, dtype={"Code": str})
        for col in ["Meter Amount", "Yard Amount", "One Product Price", "Total Price"]:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)
        return df
    except Exception:
        return pd.DataFrame(columns=["Date", "Time", "Product Name", "Code", "Meter Amount", "Yard Amount", "One Product Price", "Total Price"])

def save_sales(df):
    df.to_csv(SALES_FILE, index=False)

# Session State for Page Navigation
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "current_page" not in st.session_state:
    st.session_state["current_page"] = "Main Menu"

# ==================== 🔒 1. LOGING PAGE ====================
if not st.session_state["logged_in"]:
    st.markdown("<h1 style='text-align: center;'>Loging</h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        pwd_input = st.text_input("Password:", type="password", key="login_pwd")
        if st.button("Login", type="primary", use_container_width=True):
            if pwd_input == "1234":
                st.session_state["logged_in"] = True
                st.session_state["current_page"] = "Main Menu"
                st.rerun()
            else:
                st.error("වැරදි Password එකක්! නිවැරදි Password එක ඇතුළත් කරන්න.")

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

    # ==================== 2. MAIN MENU (SAPPHIRE COLLECTION) ====================
    if st.session_state["current_page"] == "Main Menu":
        st.markdown("<h1 style='text-align: center;'>Sapphire Collection</h1>", unsafe_allow_html=True)
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("📦\n\nProduct", use_container_width=True):
                st.session_state["current_page"] = "Product"
                st.rerun()
        with col2:
            if st.button("🧾\n\nBill Issue", use_container_width=True):
                st.session_state["current_page"] = "Bill Issue"
                st.rerun()
        with col3:
            if st.button("📊\n\nStock", use_container_width=True):
                st.session_state["current_page"] = "Stock"
                st.rerun()
                
        st.markdown("<br>", unsafe_allow_html=True)
        
        col4, col5 = st.columns(2)
        with col4:
            if st.button("📈\n\nToday sell", use_container_width=True):
                st.session_state["current_page"] = "Today sell"
                st.rerun()
        with col5:
            if st.button("📄\n\nInvoice", use_container_width=True):
                st.session_state["current_page"] = "Invoice"
                st.rerun()

    # ==================== 3. PRODUCT PAGE ====================
    elif st.session_state["current_page"] == "Product":
        st.title("Product")
        df_products = load_products()
        
        col1, col2 = st.columns([1, 1])
        with col1:
            st.subheader("➕ Product එකක් එකතු කිරීම")
            with st.form("add_product_form", clear_on_submit=True):
                p_name = st.text_input("Product Name").strip()
                p_code = st.text_input("code").strip()
                p_price = st.number_input("One Product Price (Rs.)", min_value=0.0, step=10.0)
                p_meter = st.number_input("Initial Total Meter", min_value=0.0, step=0.5)
                p_yard = st.number_input("Initial Total Yard", min_value=0.0, step=0.5)
                
                if st.form_submit_button("Save Product"):
                    if not p_code or not p_name:
                        st.error("Code සහ Product Name ඇතුළත් කරන්න.")
                    else:
                        if p_code in df_products["Code"].astype(str).values:
                            df_products.loc[df_products["Code"].astype(str) == p_code, ["Product Name", "One Product Price", "Total Meter", "Total Yard"]] = [p_name, p_price, p_meter, p_yard]
                            st.success("Product එක Update විය!")
                        else:
                            new_row = pd.DataFrame([{"Code": p_code, "Product Name": p_name, "One Product Price": p_price, "Total Meter": p_meter, "Total Yard": p_yard}])
                            df_products = pd.concat([df_products, new_row], ignore_index=True)
                            st.success("Product එක සාර්ථකව එකතු විය!")
                        save_products(df_products)
                        st.rerun()

        with col2:
            st.subheader("🗑️ Product එකක් මකා දැමීම")
            if not df_products.empty:
                delete_code = st.selectbox("මකා දැමීමට Product එක තෝරන්න:", df_products["Code"].astype(str) + " - " + df_products["Product Name"])
                if st.button("Delete Product", type="primary"):
                    selected_code = delete_code.split(" - ")[0]
                    df_products = df_products[df_products["Code"].astype(str) != selected_code]
                    save_products(df_products)
                    st.success("Product එක මකා දමන ලදී!")
                    st.rerun()

        st.subheader("📋 Product List")
        if not df_products.empty:
            df_display = df_products[["Product Name", "Code"]].rename(columns={"Code": "code"})
            st.dataframe(df_display, use_container_width=True)
        else:
            st.info("දැනට Products නොමැත.")

    # ==================== 4. BILL ISSUE PAGE ====================
    elif st.session_state["current_page"] == "Bill Issue":
        st.title("Bill Issue")
        df_products = load_products()
        
        if df_products.empty:
            st.warning("පළමුව 'Product' අංශයෙන් භාණ්ඩ ඇතුළත් කරන්න.")
        else:
            # 🔍 Product Search Bar
            search_query = st.text_input("🔍 Product Name හෝ Code එක ගසා සොයන්න (Search):", "").strip()
            
            # Filter products based on search query
            if search_query:
                filtered_products = df_products[
                    df_products["Code"].astype(str).str.contains(search_query, case=False, na=False) |
                    df_products["Product Name"].str.contains(search_query, case=False, na=False)
                ]
            else:
                filtered_products = df_products

            if filtered_products.empty:
                st.error("ඔබ සෙවූ Code එකට හෝ Name එකට අදාළ Product එකක් හමු නොවීය.")
            else:
                product_options = filtered_products["Code"].astype(str) + " - " + filtered_products["Product Name"]
                selected_prod_str = st.selectbox("Product එක තෝරන්න (Select Product):", product_options)
                
                selected_code = selected_prod_str.split(" - ")[0]
                product_row = filtered_products[filtered_products["Code"].astype(str) == selected_code].iloc[0]
                
                p_name = product_row["Product Name"]
                p_price = float(product_row["One Product Price"])
                curr_meter = float(product_row["Total Meter"])
                curr_yard = float(product_row["Total Yard"])
                
                st.info(f"📌 **තෝරාගත් භාණ්ඩය:** {p_name} | **Stock:** {curr_meter} m, {curr_yard} yd")
                
                col_b1, col_b2 = st.columns(2)
                with col_b1:
                    sell_meter = st.number_input("Meter Amount:", min_value=0.0, step=0.1)
                with col_b2:
                    sell_yard = st.number_input("Yard Amount:", min_value=0.0, step=0.1)
                    
                unit_price = st.number_input("One Product Price (Rs.):", value=p_price, min_value=0.0, step=10.0)
                total_price = (sell_meter + sell_yard) * unit_price
                
                st.markdown(f"### 💵 Total Price: **Rs. {total_price:,.2f}**")
                
                if st.button("🛒 Print & Issue Bill", type="primary"):
                    if sell_meter <= 0 and sell_yard <= 0:
                        st.error("Meter හෝ Yard ප්‍රමාණයක් ඇතුළත් කරන්න.")
                    elif sell_meter > curr_meter or sell_yard > curr_yard:
                        st.error("තොගයේ ප්‍රමාණවත් තරම් ප්‍රමාණ නොමැත!")
                    else:
                        df_products.loc[df_products["Code"].astype(str) == selected_code, "Total Meter"] = curr_meter - sell_meter
                        df_products.loc[df_products["Code"].astype(str) == selected_code, "Total Yard"] = curr_yard - sell_yard
                        save_products(df_products)
                        
                        df_sales = load_sales()
                        now = datetime.now()
                        new_sale = pd.DataFrame([{
                            "Date": now.strftime("%Y-%m-%d"),
                            "Time": now.strftime("%H:%M:%S"),
                            "Product Name": p_name,
                            "Code": selected_code,
                            "Meter Amount": sell_meter,
                            "Yard Amount": sell_yard,
                            "One Product Price": unit_price,
                            "Total Price": total_price
                        }])
                        df_sales = pd.concat([df_sales, new_sale], ignore_index=True)
                        save_sales(df_sales)
                        
                        st.success("✅ බිල්පත සාර්ථකව නිකුත් කරන ලදී!")
                        st.rerun()

        st.subheader("📋 Bill Issue Records")
        df_sales = load_sales()
        if not df_sales.empty:
            df_bill_disp = df_sales.copy()
            df_bill_disp["mitar and yar amount"] = df_bill_disp["Meter Amount"].astype(str) + "m / " + df_bill_disp["Yard Amount"].astype(str) + "yd"
            df_bill_disp.rename(columns={"One Product Price": "one product Price", "Total Price": "total Price"}, inplace=True)
            st.dataframe(df_bill_disp[["Product Name", "Code", "mitar and yar amount", "one product Price", "total Price"]], use_container_width=True)

    # ==================== 5. STOCK PAGE ====================
    elif st.session_state["current_page"] == "Stock":
        st.title("Stock")
        df_products = load_products()
        
        if not df_products.empty:
            df_stock_display = df_products.copy()
            df_stock_display["total Price"] = (df_stock_display["Total Meter"] + df_stock_display["Total Yard"]) * df_stock_display["One Product Price"]
            df_stock_display.rename(columns={
                "Total Meter": "total mitar",
                "Total Yard": "total yar",
                "One Product Price": "One product Price"
            }, inplace=True)
            
            st.dataframe(df_stock_display[["Product Name", "Code", "total mitar", "total yar", "One product Price", "total Price"]], use_container_width=True)
            
            st.subheader("➕ Stock එකතු කිරීම")
            with st.form("update_stock_form"):
                update_prod = st.selectbox("Product එක තෝරන්න:", df_products["Code"].astype(str) + " - " + df_products["Product Name"])
                add_meter = st.number_input("එකතු කරන Meter ප්‍රමාණය:", min_value=0.0, step=1.0)
                add_yard = st.number_input("එකතු කරන Yard ප්‍රමාණය:", min_value=0.0, step=1.0)
                
                if st.form_submit_button("Update Stock"):
                    u_code = update_prod.split(" - ")[0]
                    df_products.loc[df_products["Code"].astype(str) == u_code, "Total Meter"] += add_meter
                    df_products.loc[df_products["Code"].astype(str) == u_code, "Total Yard"] += add_yard
                    save_products(df_products)
                    st.success("Stock Update විය!")
                    st.rerun()
        else:
            st.info("දැනට Stock හි භාණ්ඩ නොමැත.")

    # ==================== 6. TODAY SELL PAGE ====================
    elif st.session_state["current_page"] == "Today sell":
        st.title("Today sell")
        df_sales = load_sales()
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        df_today = df_sales[df_sales["Date"] == today_str] if not df_sales.empty else pd.DataFrame()
        
        if not df_today.empty:
            st.metric(label="💰 අද දින මුළු ආදායම", value=f"Rs. {df_today['Total Price'].sum():,.2f}")
            
            df_today_disp = df_today.copy()
            df_today_disp["mitar and yar amount"] = df_today_disp["Meter Amount"].astype(str) + "m / " + df_today_disp["Yard Amount"].astype(str) + "yd"
            df_today_disp.rename(columns={"One Product Price": "one product Price", "Total Price": "total Price"}, inplace=True)
            
            st.dataframe(df_today_disp[["Time", "Product Name", "Code", "mitar and yar amount", "one product Price", "total Price"]], use_container_width=True)
            
            st.subheader("🗑️ Sales Record එකක් මකා දැමීම")
            sale_indices = df_today.index.tolist()
            sale_labels = [f"ID: {idx} | {df_today.loc[idx, 'Time']} - {df_today.loc[idx, 'Product Name']} (Rs. {df_today.loc[idx, 'Total Price']})" for idx in sale_indices]
            
            selected_sale = st.selectbox("මකා දැමීමට විකුණුම් සටහන තෝරන්න:", sale_labels)
            if st.button("Delete Record", type="primary"):
                sel_idx = int(selected_sale.split(" | ")[0].replace("ID: ", ""))
                df_sales = df_sales.drop(sel_idx)
                save_sales(df_sales)
                st.success("විකුණුම් සටහන මකා දමන ලදී!")
                st.rerun()
        else:
            st.info("අද දින තවමත් අලෙවියන් සිදු වී නොමැත.")

    # ==================== 7. INVOICE PAGE ====================
    elif st.session_state["current_page"] == "Invoice":
        st.title("📄 Invoice")
        df_sales = load_sales()
        
        if df_sales.empty:
            st.warning("දැනට නිකුත් කරන ලද බිල්පත් නොමැත.")
        else:
            sale_options = [
                f"ID #{idx} | {row['Date']} {row['Time']} | {row['Product Name']} (Rs. {row['Total Price']:,.2f})"
                for idx, row in df_sales.iterrows()
            ]
            selected_invoice = st.selectbox("Print / Download කිරීමට Invoice එකක් තෝරන්න:", sale_options)
            
            sel_idx = int(selected_invoice.split(" | ")[0].replace("ID #", ""))
            inv_data = df_sales.loc[sel_idx]
            
            # Formatted HTML Receipt View
            invoice_html = f"""
            <div style="border: 2px solid #4CAF50; padding: 20px; border-radius: 10px; background-color: #1e1e1e; color: #ffffff; max-width: 500px; margin: auto;">
                <h2 style="text-align: center; color: #4CAF50; margin-bottom: 5px;">SAPPHIRE COLLECTION</h2>
                <p style="text-align: center; margin-top: 0; font-size: 14px;">Official Sales Receipt</p>
                <hr style="border: 1px dashed #4CAF50;">
                <p><strong>Date:</strong> {inv_data['Date']} &nbsp;&nbsp;&nbsp; <strong>Time:</strong> {inv_data['Time']}</p>
                <p><strong>Invoice No:</strong> INV-{sel_idx+1000}</p>
                <hr style="border: 1px dashed #4CAF50;">
                <table style="width: 100%; text-align: left; border-collapse: collapse;">
                    <tr>
                        <th style="padding: 8px; border-bottom: 1px solid #555;">Item</th>
                        <th style="padding: 8px; border-bottom: 1px solid #555;">Code</th>
                        <th style="padding: 8px; border-bottom: 1px solid #555;">Qty (m/yd)</th>
                        <th style="padding: 8px; border-bottom: 1px solid #555;">Price</th>
                    </tr>
                    <tr>
                        <td style="padding: 8px;">{inv_data['Product Name']}</td>
                        <td style="padding: 8px;">{inv_data['Code']}</td>
                        <td style="padding: 8px;">{inv_data['Meter Amount']}m / {inv_data['Yard Amount']}yd</td>
                        <td style="padding: 8px;">Rs. {inv_data['One Product Price']:,.2f}</td>
                    </tr>
                </table>
                <hr style="border: 1px dashed #4CAF50;">
                <h3 style="text-align: right; color: #4CAF50;">Total Amount: Rs. {inv_data['Total Price']:,.2f}</h3>
                <p style="text-align: center; font-size: 12px; margin-top: 20px;">Thank You for Shopping with Us!</p>
            </div>
            """
            
            st.markdown(invoice_html, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Download Receipt Button
            st.download_button(
                label="📥 Download Invoice (HTML)",
                data=invoice_html,
                file_name=f"Invoice_{inv_data['Code']}_{inv_data['Date']}.html",
                mime="text/html",
                use_container_width=True
            )
