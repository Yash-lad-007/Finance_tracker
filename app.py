import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid
import matplotlib.pyplot as plt

# --- App Setup ---
st.set_page_config(page_title="Freelancer Finance & Invoicing App", layout="wide")

st.title("💼 Simple Finance & Invoicing App for Freelancers")

# --- Initialize session state ---
if "invoices" not in st.session_state:
    st.session_state["invoices"] = []
if "expenses" not in st.session_state:
    st.session_state["expenses"] = []

# --- Sidebar Navigation ---
menu = st.sidebar.radio("📋 Menu", ["Create Invoice", "Track Expense", "Dashboard"])

# ========== INVOICE CREATION ==========
if menu == "Create Invoice":
    st.header("🧾 Create a New Invoice")

    with st.form("invoice_form"):
        client_name = st.text_input("Client Name")
        project_desc = st.text_area("Project / Service Description")
        amount = st.number_input("Invoice Amount (₹)", min_value=0.0, format="%.2f")
        due_date = st.date_input("Due Date", value=date.today())
        submitted = st.form_submit_button("Create Invoice")

        if submitted:
            invoice_id = str(uuid.uuid4())[:8]
            invoice_data = {
                "Invoice ID": invoice_id,
                "Client": client_name,
                "Description": project_desc,
                "Amount": amount,
                "Due Date": due_date,
                "Status": "Pending",
                "Created On": datetime.now().strftime("%Y-%m-%d")
            }
            st.session_state["invoices"].append(invoice_data)
            st.success(f"✅ Invoice {invoice_id} created successfully!")

    if st.session_state["invoices"]:
        st.subheader("📄 All Invoices")
        df_invoices = pd.DataFrame(st.session_state["invoices"])
        st.dataframe(df_invoices)

        # Payment reminder simulation
        st.info("💡 Click below to simulate sending reminders for overdue invoices.")
        if st.button("Send Payment Reminders"):
            overdue = [
                inv for inv in st.session_state["invoices"]
                if inv["Status"] == "Pending" and inv["Due Date"] < date.today()
            ]
            if overdue:
                st.warning(f"📬 Reminders sent for {len(overdue)} overdue invoice(s)!")
            else:
                st.success("✅ No overdue invoices.")

# ========== EXPENSE TRACKING ==========
elif menu == "Track Expense":
    st.header("💸 Add Expense")

    with st.form("expense_form"):
        expense_name = st.text_input("Expense Title")
        expense_amount = st.number_input("Expense Amount (₹)", min_value=0.0, format="%.2f")
        expense_date = st.date_input("Date", value=date.today())
        category = st.selectbox("Category", ["Travel", "Supplies", "Software", "Other"])
        receipt_uploaded = st.file_uploader("Upload Receipt (optional)", type=["png", "jpg", "jpeg", "pdf"])
        add_expense = st.form_submit_button("Add Expense")

        if add_expense:
            expense_id = str(uuid.uuid4())[:8]
            expense_data = {
                "Expense ID": expense_id,
                "Title": expense_name,
                "Amount": expense_amount,
                "Date": expense_date,
                "Category": category
            }
            st.session_state["expenses"].append(expense_data)
            st.success(f"✅ Expense {expense_id} added successfully!")

    if st.session_state["expenses"]:
        st.subheader("📊 Expense List")
        df_expenses = pd.DataFrame(st.session_state["expenses"])
        st.dataframe(df_expenses)

# ========== DASHBOARD ==========
elif menu == "Dashboard":
    st.header("📈 Cash Flow Dashboard")

    df_invoices = pd.DataFrame(st.session_state["invoices"])
    df_expenses = pd.DataFrame(st.session_state["expenses"])

    total_income = df_invoices["Amount"].sum() if not df_invoices.empty else 0
    total_expenses = df_expenses["Amount"].sum() if not df_expenses.empty else 0
    net_balance = total_income - total_expenses

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Income", f"₹{total_income:,.2f}")
    col2.metric("Total Expenses", f"₹{total_expenses:,.2f}")
    col3.metric("Net Balance", f"₹{net_balance:,.2f}")

    # --- Cash Flow Chart ---
    if not df_invoices.empty or not df_expenses.empty:
        st.subheader("📅 Monthly Cash Flow")
        df_invoices["Type"] = "Income"
        df_expenses["Type"] = "Expense"
        combined = pd.concat([
            df_invoices[["Amount", "Created On", "Type"]].rename(columns={"Created On": "Date"}),
            df_expenses[["Amount", "Date", "Type"]]
        ])
        combined["Date"] = pd.to_datetime(combined["Date"])
        combined["Month"] = combined["Date"].dt.to_period("M").astype(str)

        summary = combined.groupby(["Month", "Type"])["Amount"].sum().unstack(fill_value=0)
        summary.plot(kind="bar", figsize=(10, 5))
        plt.title("Income vs Expenses Over Time")
        plt.xlabel("Month")
        plt.ylabel("Amount (₹)")
        st.pyplot(plt)

    else:
        st.info("No data yet. Add invoices and expenses to view your dashboard.")
