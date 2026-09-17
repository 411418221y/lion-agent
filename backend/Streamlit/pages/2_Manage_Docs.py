import streamlit as st
import os

st.set_page_config(
    page_title="Manage Docs",
    layout="wide"
)

st.title("📁 Manage Documents")
st.caption("Upload and manage policy documents")

st.divider()


DATA_DIR = "data_docs"

if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)


# ---------------- Upload ----------------

st.subheader("Upload Documents")

uploaded = st.file_uploader(
    "Upload policy files",
    type=["txt", "pdf", "md"],
    accept_multiple_files=True
)


if uploaded:

    for f in uploaded:

        save_path = os.path.join(DATA_DIR, f.name)

        with open(save_path, "wb") as out:
            out.write(f.read())

        st.success(f"Saved: {f.name}")


# ---------------- List ----------------

st.divider()

st.subheader("Stored Documents")


files = []

if os.path.exists(DATA_DIR):
    files = os.listdir(DATA_DIR)


if not files:

    st.info("No documents uploaded yet.")

else:

    for fname in files:

        col1, col2 = st.columns([4, 1])

        with col1:
            st.write("📄", fname)

        with col2:

            if st.button("❌ Delete", key=f"del_{fname}"):

                os.remove(os.path.join(DATA_DIR, fname))
                st.success(f"Deleted: {fname}")
                st.rerun()


# ---------------- Info ----------------

st.divider()

st.info("""
📌 Tips:

• Upload school policy PDFs or TXT files  
• Backend can index these for RAG  
• Restart backend after major updates
""")
