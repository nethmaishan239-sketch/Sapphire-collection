import streamlit as st
import pandas as pd
import os
from datetime import datetime

# Page Configuration
st.set_page_config(page_title="Sapphire Collection", layout="wide")

# Files for Data Persistence
PRODUCT_FILE = "products.csv"
SALES_FILE = "sales.csv"

# Function to initialize CSV files if they don't exist or are empty
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

# ------------ 🔒 LOGGING / PASSWORD PROTECTION ------------
st.title("Sapphire Collection")

password = st.text_input("🔑 Logging (Password):", type="password")

if password != "1234":
    if password != "":
        st.error("වැරදි Password එකක්! කරුණාකර නිවැරදි Password එක ඇතුළත් කරන්න.")
    st.stop()

# ------------ MAIN MENU ------------
st.markdown("---")
menu = st.radio("Navigation", ["Product", "Bill Issue", "Stock", "Today sell"], horizontal=True)
st.markdown("---")

# ==================== 1. PRODUCT ====================
if menu == "Product":
    st.header("📦 Product")
    
    df_products = load_products()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("➕ Product එකක් එකතු කිරීම / වෙනස් කිරීම")
        with st.form("add_product_form", clear_on_submit=True):
            p_name = st.text_input("Product Name (භාණ්ඩයේ නම)").strip()
            p_code = st.text_input("Code (කේතය)").strip()
            p_price = st.number_input("One Product Price (ඒකක මිල Rs.)", min_value=0.0, step=10.0)
            p_meter = st.number_input("Initial Total Meter (ආරම්භක මීටර් ප්‍රමාණය)", min_value=0.0, step=0.5)
            p_yard = st.number_input("Initial Total Yard (ආරම්භක යාඩ් ප්‍රමාණය)", min_value=0.0, step=0.5)
            
            submit_p = st.form_submit_button("Save Product")
            
            if submit_p:
                if not p_code or not p_name:
                    st.error("කරුණාකර Code එක සහ Product Name එක දෙකම ඇතුළත් කරන්න.")
                else:
                    if p_code in df_products["Code"].astype(str).values:
                        df_products.loc[df_products["Code"].astype(str) == p_code, ["Product Name", "One Product Price", "Total Meter", "Total Yard"]] = [p_name, p_price, p_meter, p_yard]
                        st.success(f"Product '{p_name}' (Code: {p_code}) Update විය!")
                    else:
                        new_row = pd.DataFrame([{
                            "Code": p_code,
                            "Product Name": p_name,
                            "One Product Price": p_price,
                            "Total Meter": p_meter,
                            "Total Yard": p_yard
                        }])
                        df_products = pd.concat([df_products, new_row], ignore_index=True)
                        st.success(f"Product '{p_name}' සාර්ථකව ඇතුළත් විය!")
                    save_products(df_products)
                    st.rerun()

    with col2:
        st.subheader("🗑️ Product එකක් මකා දැමීම")
        if not df_products.empty:
            delete_code = st.selectbox("මකා දැමීමට අවශ්‍ය Product එක තෝරන්න:", df_products["Code"].astype(str) + " - " + df_products["Product Name"])
            if st.button("Delete Product", type="primary"):
                selected_code = delete_code.split(" - ")[0]
                df_products = df_products[df_products["Code"].astype(str) != selected_code]
                save_products(df_products)
                st.success("Product එක සාර්ථකව මකා දමන ලදී!")
                st.rerun()
        else:
            st.info("දැනට ඇතුළත් කළ Products නොමැත.")

    st.subheader("📋 Product List")
    if not df_products.empty:
        st.dataframe(df_products[["Product Name", "Code", "One Product Price"]], use_container_width=True)
    else:
        st.info("Products නොමැත.")

# ==================== 2. BILL ISSUE ====================
elif menu == "Bill Issue":
    st.header("🧾 Bill Issue")
    
    df_products = load_products()
    
    if df_products.empty:
        st.warning("කරුණාකර පළමුව 'Product' අංශයෙන් භාණ්ඩ ඇතුළත් කරන්න.")
    else:
        product_options = df_products["Code"].astype(str) + " - " + df_products["Product Name"]
        selected_prod_str = st.selectbox("Product Name / Code තෝරන්න:", product_options)
        
        selected_code = selected_prod_str.split(" - ")[0]
        product_row = df_products[df_products["Code"].astype(str) == selected_code].iloc[0]
        
        p_name = product_row["Product Name"]
        p_price = float(product_row["One Product Price"])
        curr_meter = float(product_row["Total Meter"])
        curr_yard = float(product_row["Total Yard"])
        
        st.info(f"📌 **තෝරාගත් භාණ්ඩය:** {p_name} | **Code:** {selected_code} | **දැනට ඇති Stock:** {curr_meter} Meters, {curr_yard} Yards")
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            sell_meter = st.number_input("Meter Amount (මීටර් ප්‍රමාණය):", min_value=0.0, step=0.1)
        with col_b2:
            sell_yard = st.number_input("Yard Amount (යාඩ් ප්‍රමාණය):", min_value=0.0, step=0.1)
            
        unit_price = st.number_input("One Product Price (Rs.):", value=p_price, min_value=0.0, step=10.0)
        
        total_units = sell_meter + sell_yard
        total_price = total_units * unit_price
        
        st.markdown(f"### 💵 Total Price: **Rs. {total_price:,.2f}**")
        
        if st.button("🛒 Print & Issue Bill", type="primary"):
            if sell_meter <= 0 and sell_yard <= 0:
                st.error("කරුණාකර Meter හෝ Yard ප්‍රමාණයක් ඇතුළත් කරන්න.")
            elif sell_meter > curr_meter or sell_yard > curr_yard:
                st.error("තොගයේ (Stock) ප්‍රමාණවත් තරම් Meter / Yard නොමැත!")
            else:
                # Deduct stock
                df_products.loc[df_products["Code"].astype(str) == selected_code, "Total Meter"] = curr_meter - sell_meter
                df_products.loc[df_products["Code"].astype(str) == selected_code, "Total Yard"] = curr_yard - sell_yard
                save_products(df_products)
                
                # Add to sales
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
                
                st.success("✅ බිල්පත සාර්ථකව නිකුත් කරන ලදී! Stock එක අඩු වී Today Sell එකට ඇතුළත් විය.")
                
                # Printable Receipt Summary
                st.markdown("---")
                st.subheader("🧾 Sapphire Collection - Receipt")
                st.write(f"**Date & Time:** {now.strftime('%Y-%m-%d %H:%M:%S')}")
                st.write(f"**Product Name:** {p_name}")
                st.write(f"**Code:** {selected_code}")
                st.write(f"**Meter Amount:** {sell_meter} m")
                st.write(f"**Yard Amount:** {sell_yard} yd")
                st.write(f"**One Product Price:** Rs. {unit_price:,.2f}")
                st.write(f"### **Total Price:** Rs. {total_price:,.2f}")
                st.markdown("---")

# ==================== 3. STOCK ====================
elif menu == "Stock":
    st.header("📊 Stock")
    
    df_products = load_products()
    
    if not df_products.empty:
        df_stock_display = df_products.copy()
        df_stock_display["Total Price"] = (df_stock_display["Total Meter"] + df_stock_display["Total Yard"]) * df_stock_display["One Product Price"]
        
        # Displaying exact columns requested: Product Name, Code, Total meter, Total yard, One product Price, Total Price
        df_stock_display = df_stock_display[["Product Name", "Code", "Total Meter", "Total Yard", "One Product Price", "Total Price"]]
        df_stock_display.rename(columns={"Total Meter": "Total meter", "Total Yard": "Total yard", "One Product Price": "One product Price", "Total Price": "Total Price"}, inplace=True)
        
        st.dataframe(df_stock_display, use_container_width=True)
        
        st.subheader("➕ Stock එකතු කිරීම (Add Stock)")
        with st.form("update_stock_form"):
            update_prod = st.selectbox("Stock එකතු කිරීමට Product එක තෝරන්න:", df_products["Code"].astype(str) + " - " + df_products["Product Name"])
            add_meter = st.number_input("එකතු කරන Meter ප්‍රමාණය:", min_value=0.0, step=1.0)
            add_yard = st.number_input("එකතු කරන Yard ප්‍රමාණය:", min_value=0.0, step=1.0)
            
            submit_stock = st.form_submit_button("Update Stock")
            if submit_stock:
                u_code = update_prod.split(" - ")[0]
                df_products.loc[df_products["Code"].astype(str) == u_code, "Total Meter"] += add_meter
                df_products.loc[df_products["Code"].astype(str) == u_code, "Total Yard"] += add_yard
                save_products(df_products)
                st.success("Stock එක සාර්ථකව Update විය!")
                st.rerun()
    else:
        st.info("දැනට Stock හි භාණ්ඩ නොමැත.")

# ==================== 4. TODAY SELL ====================
elif menu == "Today sell":
    st.header("📈 Today sell")
    
    df_sales = load_sales()
    today_str = datetime.now().strftime("%Y-%m-%d")
    
    df_today = df_sales[df_sales["Date"] == today_str] if not df_sales.empty else pd.DataFrame()
    
    if not df_today.empty:
        total_today_income = df_today["Total Price"].sum()
        st.metric(label="💰 අද දින මුළු ආදායම (Total Revenue Today)", value=f"Rs. {total_today_income:,.2f}")
        
        st.subheader("📋 අද දින අලෙවි වූ ලැයිස්තුව")
        st.dataframe(df_today[["Time", "Product Name", "Code", "Meter Amount", "Yard Amount", "One Product Price", "Total Price"]], use_container_width=True)
        
        st.markdown("---")
        st.subheader("🗑️ Sales Record එකක් මකා දැමීම")
        sale_indices = df_today.index.tolist()
        sale_labels = [f"ID: {idx} | {df_today.loc[idx, 'Time']} - {df_today.loc[idx, 'Product Name']} (Rs. {df_today.loc[idx, 'Total Price']})" for idx in sale_indices]
        
        selected_sale = st.selectbox("මකා දැමීමට අවශ්‍ය විකුණුම් සටහන තෝරන්න:", sale_labels)
        if st.button("Delete Record", type="primary"):
            sel_idx = int(selected_sale.split(" | ")[0].replace("ID: ", ""))
            df_sales = df_sales.drop(sel_idx)
            save_sales(df_sales)
            st.success("විකුණුම් සටහන සාර්ථකව මකා දමන ලදී!")
            st.rerun()
    else:
        st.info("අද දින තවමත් අලෙවියන් සිදු වී නොමැත.")
