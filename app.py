import streamlit as st
import pandas as pd
import io
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

st.set_page_config(page_title="Stocktake Counter", layout="wide")

st.title("📦 Stocktake Counter")

# --- Step 1: File upload ---
uploaded_file = st.file_uploader("Upload your product file (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file:
    # Load file
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # Standardize column names
    df.columns = [c.strip().capitalize() for c in df.columns]

    # Make sure required columns exist
    if not {"Description", "Qty"}.issubset(df.columns):
        st.error("Your file must have columns named 'Description' and 'Qty'.")
        st.stop()

    # Initialize session state
    if "index" not in st.session_state:
        st.session_state.index = 0
        st.session_state.counts = [0 if pd.isna(q) else int(q) for q in df["Qty"]]
        st.session_state.finished = False

    i = st.session_state.index
    product = df.iloc[i]

    st.subheader(f"Product {i+1} of {len(df)}")
    st.write(f"**Description:** {product['Description']}")
    st.markdown(f"### Current Count: {st.session_state.counts[i]}")

    # --- Keypad ---
    keypad = [
        ["1", "2", "3"],
        ["4", "5", "6"],
        ["7", "8", "9"],
        ["0", "Clear", "Enter"]
    ]

    def handle_input(value):
        if value == "Clear":
            st.session_state.counts[i] = 0
        elif value == "Enter":
            if st.session_state.index < len(df) - 1:
                st.session_state.index += 1
            else:
                st.session_state.finished = True
        else:
            current = str(st.session_state.counts[i])
            if current == "0":
                current = ""
            st.session_state.counts[i] = int(current + value)
        st.rerun()

    for row in keypad:
        cols = st.columns(3)
        for j, label in enumerate(row):
            if cols[j].button(label, use_container_width=True):
                handle_input(label)

    # --- Edit navigation ---
    edit_cols = st.columns(2)
    if edit_cols[0].button("⬅ Previous", use_container_width=True):
        if st.session_state.index > 0:
            st.session_state.index -= 1
            st.rerun()
    if edit_cols[1].button("➡ Next", use_container_width=True):
        if st.session_state.index < len(df) - 1:
            st.session_state.index += 1
            st.rerun()

    # --- Finish ---
    if st.session_state.finished:
        df["Qty"] = st.session_state.counts
        st.success("✅ Counting complete!")

        # Prepare CSV buffer
        buffer = io.StringIO()
        df.to_csv(buffer, index=False)
        buffer.seek(0)

        # Download button
        st.download_button(
            "📥 Download Results",
            data=buffer.getvalue(),
            file_name="stocktake_results.csv",
            mime="text/csv"
        )

        # --- Send Email ---
        sender_email = "stocktake.bot@gmail.com"  # dummy sender
        receiver_email = "lopatifam@hotmail.com"
        subject = "Stocktake Results"
        body = "Attached are your stocktake results."

        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = receiver_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        part = MIMEBase("application", "octet-stream")
        part.set_payload(buffer.getvalue().encode("utf-8"))
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", "attachment; filename=stocktake_results.csv")
        msg.attach(part)

        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.starttls()
                # Replace below with a real Gmail app password if you want this to actually send
                server.login(sender_email, "your-app-password")
                server.send_message(msg)
            st.success(f"📧 Email sent to {receiver_email}")
        except Exception as e:
            st.warning(f"Email not sent (likely missing credentials): {e}")

    # --- Restart button ---
    if st.button("🔄 Restart Session"):
        st.session_state.clear()
        st.rerun()
