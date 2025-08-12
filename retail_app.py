import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Retail Store Dashboard", layout="wide")

# ---------- Cached Data ----------
@st.cache_data
def get_initial_inventory():
    return pd.DataFrame({
        "Item": ["Rice", "Sugar", "Oil", "Wheat", "Milk"],
        "Stock": [50, 20, 10, 40, 15],
        "Price": [40, 50, 120, 35, 25]
    })

@st.cache_data
def get_initial_suppliers():
    return pd.DataFrame({
        "Supplier": ["ABC Traders", "Fresh Farms", "Oil Depot"],
        "Contact": ["1234567890", "9876543210", "5556667777"]
    })

# ---------- Initialize Session State ----------
if "inventory" not in st.session_state:
    st.session_state.inventory = get_initial_inventory()
if "suppliers" not in st.session_state:
    st.session_state.suppliers = get_initial_suppliers()
if "sales" not in st.session_state:
    st.session_state.sales = pd.DataFrame(columns=["Date", "Item", "Quantity", "Price", "Revenue"])

# ---------- Sidebar Menu ----------
st.sidebar.title("Retail Store Menu")
menu = st.sidebar.radio("Go to", ["Inventory", "Suppliers", "Sales", "Reports"])

# ---------- Inventory ----------
if menu == "Inventory":
    st.title("📦 Inventory Management")
    st.dataframe(st.session_state.inventory)

    with st.form("add_stock_form"):
        st.subheader("Add New Item")
        item = st.text_input("Item Name")
        stock = st.number_input("Stock Quantity", min_value=0)
        price = st.number_input("Price", min_value=0.0)
        submitted = st.form_submit_button("Add Item")

        if submitted and item:
            st.session_state.inventory.loc[len(st.session_state.inventory)] = [item, stock, price]
            st.success(f"Added {item} to inventory!")

# ---------- Suppliers ----------
elif menu == "Suppliers":
    st.title("🏢 Supplier Management")
    st.dataframe(st.session_state.suppliers)

    with st.form("add_supplier_form"):
        st.subheader("Add Supplier")
        supplier = st.text_input("Supplier Name")
        contact = st.text_input("Contact Number")
        submitted = st.form_submit_button("Add Supplier")

        if submitted and supplier:
            st.session_state.suppliers.loc[len(st.session_state.suppliers)] = [supplier, contact]
            st.success(f"Added supplier: {supplier}")

# ---------- Sales ----------
elif menu == "Sales":
    st.title("💰 Sales Entry")
    with st.form("sales_form"):
        date = st.date_input("Date")
        item = st.selectbox("Select Item", st.session_state.inventory["Item"])
        qty = st.number_input("Quantity Sold", min_value=1)
        submitted = st.form_submit_button("Record Sale")

        if submitted:
            price = st.session_state.inventory.loc[st.session_state.inventory["Item"] == item, "Price"].values[0]
            revenue = qty * price
            new_sale = pd.DataFrame([[date, item, qty, price, revenue]],
                                    columns=["Date", "Item", "Quantity", "Price", "Revenue"])
            st.session_state.sales = pd.concat([st.session_state.sales, new_sale], ignore_index=True)

            # Reduce stock
            idx = st.session_state.inventory[st.session_state.inventory["Item"] == item].index[0]
            st.session_state.inventory.at[idx, "Stock"] -= qty

            st.success(f"Sale recorded: {qty} x {item} = ₹{revenue}")

    st.subheader("Sales Records")
    st.dataframe(st.session_state.sales)

# ---------- Reports ----------
elif menu == "Reports":
    st.title("📊 Monthly Reports")

    if not st.session_state.sales.empty:
        st.session_state.sales["Month"] = pd.to_datetime(st.session_state.sales["Date"]).dt.strftime("%Y-%m")
        monthly_report = st.session_state.sales.groupby("Month").agg(
            Quantity=("Quantity", "sum"),
            Revenue=("Revenue", "sum")
        ).reset_index()

        col1, col2 = st.columns(2)
        with col1:
            fig_qty = px.bar(monthly_report, x="Month", y="Quantity", title="Monthly Quantity Sold", text_auto=True)
            st.plotly_chart(fig_qty, use_container_width=True)

        with col2:
            fig_rev = px.bar(monthly_report, x="Month", y="Revenue", title="Monthly Revenue", text_auto=True)
            st.plotly_chart(fig_rev, use_container_width=True)
    else:
        st.info("No sales data available yet.")
