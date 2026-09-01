import streamlit as st
import pandas as pd
import os
from datetime import datetime

# වෙබ් අඩවියේ මූලික සැකසුම්
st.set_page_config(page_title="Sapphire Collection POS", layout="wide")

# ---------------- 🔒 PASSWORD PROTECTION ----------------
password = st.text_input("🔒 කරුණාකර කඩේ Password එක ඇතුළත් කරන්න:", type="password")

if password != "1234":  # "1234" වෙනුවට ඔබට අවශ්‍ය වෙනත් රහස් අංකයක් මෙහි යෙදිය හැක
    if password != "":
        st.error("වැරදි Password එකක්! කරුණාකර නිවැරදි අංකය දෙන්න.")
    st.stop()  # නිවැරදි Password එක දෙන තුරු ඇප් එක ඉදිරියට ක්‍රියාත්මක වීම නවත්වයි

# දත්ත ගබඩා කරන ෆයිල් (Files)
PRODUCT_FILE = "products.csv"
SALES_FILE = "sales.csv"

# අලුතින් ෆයිල් හැදීම (නැතිනම් පමණක්)
if not os.path.exists(PRODUCT_FILE):
    df_prod = pd.DataFrame(columns=["Product_Code", "Name", "Price", "Initial_Stock"])
    df_prod.to_csv(PRODUCT_FILE, index=False)

if not os.path.exists(SALES_FILE):
    df_sales = pd.DataFrame(columns=["Date", "Product_Code", "Quantity", "Unit_Price", "Total"])
    df_sales.to_csv(SALES_FILE, index=False)

def load_products():
    return pd.read_csv(PRODUCT_FILE)

def load_sales():
    return pd.read_csv(SALES_FILE)

# පැත්තේ ඇති මෙනුව (Sidebar Menu)
st.sidebar.title("💎 Sapphire Collection")
menu = st.sidebar.radio("අංශය තෝරන්න:", ["🛒 Bill Issue", "📦 Product", "📊 Stock", "📈 Today Sell"])

# ---------------- 1. PRODUCT (භාණ්ඩ ඇතුළත් කිරීම) ----------------
if menu == "📦 Product":
    st.header("📦 නව භාණ්ඩ ඇතුළත් කිරීම (Products)")
    
    with st.form("product_form"):
        col1, col2 = st.columns(2)
        with col1:
            code = st.text_input("Product Code (භාණ්ඩ කේතය)")
            name = st.text_input("Product Name (භාණ්ඩයේ නම)")
        with col2:
            price = st.number_input("Unit Price (මිල රු.)", min_value=0.0, step=10.0)
            stock = st.number_input("Initial Stock (මුල් තොගය)", min_value=0, step=1)
        
        submit = st.form_submit_button("භාණ්ඩය ඇතුළත් කරන්න")

        if submit:
            if code and name:
                df = load_products()
                if code in df['Product_Code'].values:
                    st.error("මෙම කේතය දැනටමත් පද්ධතියේ ඇත!")
                else:
                    new_data = pd.DataFrame({"Product_Code": [code], "Name": [name], "Price": [price], "Initial_Stock": [stock]})
                    df = pd.concat([df, new_data], ignore_index=True)
                    df.to_csv(PRODUCT_FILE, index=False)
                    st.success(f"{name} පද්ධතියට සාර්ථකව එකතු කරන ලදී!")
            else:
                st.warning("කරුණාකර කේතය සහ නම ඇතුළත් කරන්න.")
                
    st.subheader("දැනට පවතින භාණ්ඩ ලැයිස්තුව")
    st.dataframe(load_products(), use_container_width=True)

# ---------------- 2. BILL ISSUE (බිල් නිකුත් කිරීම) ----------------
elif menu == "🛒 Bill Issue":
    st.header("🛒 බිල්පත් නිකුත් කිරීම (Bill Issue)")
    
    df_products = load_products()
    if df_products.empty:
        st.warning("පළමුව Product අංශයෙන් භාණ්ඩ ඇතුළත් කරන්න.")
    else:
        product_list = df_products['Product_Code'].astype(str) + " - " + df_products['Name']
        selected_item = st.selectbox("භාණ්ඩය තෝරන්න (Code හෝ නම සොයන්න):", product_list)
        
        if selected_item:
            selected_code = selected_item.split(" - ")[0]
            product_info = df_products[df_products['Product_Code'] == selected_code].iloc[0]
            
            st.info(f"**තෝරාගත් භාණ්ඩය:** {product_info['Name']} | **ඒකකයක මිල:** රු. {product_info['Price']:.2f}")
            
            with st.form("bill_form"):
                qty = st.number_input("ප්‍රමාණය (Quantity)", min_value=1.0, step=1.0)
                total_price = qty * product_info['Price']
                st.write(f"### මුළු මුදල (Total): රු. {total_price:.2f}")
                
                issue_bill = st.form_submit_button("බිල නිකුත් කරන්න (Issue Bill)")
                
                if issue_bill:
                    df_sales = load_sales()
                    now = datetime.now()
                    today_date = now.strftime("%Y-%m-%d")
                    full_datetime = now.strftime("%Y-%m-%d %H:%M:%S")
                    
                    new_sale = pd.DataFrame({
                        "Date": [today_date],
                        "Product_Code": [selected_code],
                        "Quantity": [qty],
                        "Unit_Price": [product_info['Price']],
                        "Total": [total_price]
                    })
                    df_sales = pd.concat([df_sales, new_sale], ignore_index=True)
                    df_sales.to_csv(SALES_FILE, index=False)
                    st.success("බිල සාර්ථකව නිකුත් කරන ලදී! තොගයෙන් අදාළ ප්‍රමාණය අඩු විය.")
                    
                    # --- බිල්පත ප්‍රදර්ශනය කිරීම (Receipt Display) ---
                    receipt_text = f"""
========================================
         SAPPHIRE COLLECTION
========================================
Reg No  : R/Ka/1676
Address : Ambalanwatta, Kahawatta
Tel     : 045 22 739 30 / 071 941 6006 
          070 6416006
Email   : sapphirecollection112@gmail.com
FB      : Sapphire Collection
----------------------------------------
Date & Time : {full_datetime}
----------------------------------------
Product    : {product_info['Name']} ({selected_code})
Unit Price : Rs. {product_info['Price']:.2f}
Quantity   : {qty}
----------------------------------------
TOTAL      : Rs. {total_price:.2f}
========================================
       Thank You! Come Again!
========================================
"""
                    st.text_area("🖨️ පාරිභෝගිකයාගේ බිල්පත (Printable Bill)", receipt_text, height=350)

# ---------------- 3. STOCK (තොග පරීක්ෂාව) ----------------
elif menu == "📊 Stock":
    st.header("📊 තොග තත්ත්වය (Stock)")
    
    df_products = load_products()
    df_sales = load_sales()
    
    search_code = st.text_input("Product Code එක ඇතුළත් කර Search කරන්න:")
    
    if search_code:
        if search_code in df_products['Product_Code'].values:
            prod_info = df_products[df_products['Product_Code'] == search_code].iloc[0]
            
            if not df_sales.empty:
                sold_qty = df_sales[df_sales['Product_Code'] == search_code]['Quantity'].sum()
            else:
                sold_qty = 0
                
            total_stock = prod_info['Initial_Stock']
            current_stock = total_stock - sold_qty
            
            st.subheader(f"භාණ්ඩයේ නම: {prod_info['Name']}")
            
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("ඒකකයක මිල", f"රු. {prod_info['Price']:.2f}")
            col2.metric("මුළු තොගය (Total Stock)", f"{total_stock}")
            col3.metric("විකිණී ඇති ප්‍රමාණය (Sold)", f"{sold_qty}")
            col4.metric("දැනට ඉතිරි තොගය (Current Stock)", f"{current_stock}")
        else:
            st.error("මෙම කේතයට අදාළ භාණ්ඩයක් නොමැත.")

# ---------------- 4. TODAY SELL (අද දින විකුණුම්) ----------------
elif menu == "📈 Today Sell":
    st.header("📈 දෛනික විකුණුම් වාර්තාව (Today Sell)")
    
    df_sales = load_sales()
    
    if df_sales.empty:
        st.info("දැනට කිසිදු විකුණුමක් සිදුවී නොමැත.")
    else:
        selected_date = st.date_input("දිනය තෝරන්න:", datetime.now())
        selected_date_str = selected_date.strftime("%Y-%m-%d")
        
        filtered_sales = df_sales[df_sales['Date'] == selected_date_str]
        
        if filtered_sales.empty:
            st.warning(f"{selected_date_str} දිනට අදාළ විකුණුම් කිසිවක් නැත.")
        else:
            st.write(f"### {selected_date_str} දින විකුණුම් ලැයිස්තුව")
            st.dataframe(filtered_sales, use_container_width=True)
            
            daily_total = filtered_sales['Total'].sum()
            st.success(f"### මෙම දිනයේ මුළු ආදායම: රු. {daily_total:.2f}")
