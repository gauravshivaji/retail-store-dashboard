import streamlit as st
import pandas as pd
import plotly.express as px

# --- Data ---
if "inventory" not in st.session_state:
    st.session_state.inventory = pd.DataFrame({
        "Item": ["Rice", "Sugar", "Oil", "Wheat", "Milk"],
        "Stock": [50, 20, 10, 40, 15],
        "Price": [40, 50, 120, 35, 25]
    })

if "sales" not in st.session_state:
    st.session_state.sales = pd.DataFrame({
        "Date": pd.date_range("2025-08-01", periods=5),
        "Item": ["Rice", "Sugar", "Oil", "Milk", "Rice"],
        "Quantity": [5, 3, 2, 4, 6]
    })

if "suppliers" not in st.session_state:
    st.session_state.suppliers = pd.DataFrame({
        "Supplier": ["ABC Traders", "XYZ Foods"],
        "Contact": ["9876543210", "9123456780"]
    })

# --- Title ---
st.title("🏬 Retail Store Management System")

# --- Inventory Section ---
st.header("📦 Inventory")
st.dataframe(st.session_state.inventory)

low_stock = st.session_state.inventory[st.session_state.inventory["Stock"] < 20]
if not low_stock.empty:
    st.warning("⚠ Low stock items:")
    st.dataframe(low_stock)

# --- Add Sale ---
st.subheader("➕ Record Sale")
sale_item = st.selectbox("Select Item", st.session_state.inventory["Item"])
sale_qty = st.number_input("Quantity Sold", min_value=1, value=1)
if st.button("Add Sale"):
    st.session_state.inventory.loc[st.session_state.inventory["Item"] == sale_item, "Stock"] -= sale_qty
    new_sale = pd.DataFrame({"Date": [pd.Timestamp.now()], "Item": [sale_item], "Quantity": [sale_qty]})
    st.session_state.sales = pd.concat([st.session_state.sales, new_sale], ignore_index=True)
    st.success(f"✅ Sale recorded: {sale_item} - {sale_qty} units")

# --- Add Purchase ---
st.subheader("🛒 Record Purchase")
purchase_item = st.selectbox("Purchase Item", st.session_state.inventory["Item"])
purchase_qty = st.number_input("Quantity Purchased", min_value=1, value=1)
purchase_supplier = st.selectbox("Supplier", st.session_state.suppliers["Supplier"])
if st.button("Add Purchase"):
    st.session_state.inventory.loc[st.session_state.inventory["Item"] == purchase_item, "Stock"] += purchase_qty
    st.success(f"✅ Purchase recorded: {purchase_item} - {purchase_qty} units from {purchase_supplier}")

# --- Suppliers ---
st.header("🏢 Supplier Management")
st.dataframe(st.session_state.suppliers)
new_supplier_name = st.text_input("New Supplier Name")
new_supplier_contact = st.text_input("New Supplier Contact")
if st.button("Add Supplier"):
    if new_supplier_name and new_supplier_contact:
        st.session_state.suppliers = pd.concat([
            st.session_state.suppliers,
            pd.DataFrame({"Supplier": [new_supplier_name], "Contact": [new_supplier_contact]})
        ], ignore_index=True)
        st.success("✅ Supplier added!")

# --- Monthly Sales Report ---
st.header("📊 Monthly Sales Report")
st.session_state.sales["Month"] = st.session_state.sales["Date"].dt.to_period('M').astype(str)
monthly_report = st.session_state.sales.groupby("Month")["Quantity"].sum().reset_index()
st.dataframe(monthly_report)

fig = px.bar(monthly_report, x="Month", y="Quantity", title="Monthly Sales")
st.plotly_chart(fig)
