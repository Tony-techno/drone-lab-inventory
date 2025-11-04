# app.py - PHASE 2: QR Code System
import streamlit as st
import qrcode
import io

# Initialize session state
if 'inventory' not in st.session_state:
    st.session_state.inventory = {
        'storages': {
            'storage_1': {
                'name': 'Main Storage',
                'type': 'shelf',
                'location': 'Lab Room 101',
                'items': [
                    {'name': 'Sample Item 1', 'quantity': '5 units', 'status': 'Available'},
                    {'name': 'Sample Item 2', 'quantity': '3 units', 'status': 'In Use'}
                ]
            }
        }
    }

def generate_qr_code(url):
    """Generate QR code for a URL"""
    try:
        qr = qrcode.QRCode(
            version=5,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
        qr.make(fit=True)
        qr_img = qr.make_image(fill_color="black", back_color="white")
        
        # Convert to bytes
        buf = io.BytesIO()
        qr_img.save(buf, format="PNG")
        buf.seek(0)
        return buf.getvalue()
    except Exception as e:
        st.error(f"QR generation error: {e}")
        return None

def get_app_url():
    """Get the current app URL - UPDATE THIS WITH YOUR ACTUAL URL"""
    # ⚠️ IMPORTANT: Replace this with your actual Streamlit app URL
    return "https://drone-lab-inventory-l8phzdn3dqn38cppfacdtr.streamlit.app/"

def main():
    st.set_page_config(
        page_title="Lab Inventory",
        page_icon="📦",
        layout="wide"
    )
    
    st.title("📦 Lab Inventory System")
    st.markdown("---")
    
    # Show basic stats
    total_storages = len(st.session_state.inventory['storages'])
    total_items = sum(len(storage['items']) for storage in st.session_state.inventory['storages'].values())
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Storage Units", total_storages)
    with col2:
        st.metric("Total Items", total_items)
    with col3:
        # Central QR Code
        app_url = get_app_url()
        central_qr = generate_qr_code(app_url)
        if central_qr:
            st.image(central_qr, width=100)
            st.caption("Central QR")
    
    st.markdown("---")
    
    # Show storages with QR codes
    st.subheader("Storage Units")
    
    for storage_id, storage in st.session_state.inventory['storages'].items():
        # Create columns for storage card
        col_left, col_right = st.columns([3, 1])
        
        with col_left:
            with st.expander(f"📦 {storage['name']} ({len(storage['items'])} items)", expanded=True):
                st.write(f"**Location:** {storage['location']}")
                st.write(f"**Type:** {storage['type']}")
                
                # Show items
                st.write("**Items:**")
                for item in storage['items']:
                    status_icon = "🟢" if item['status'] == 'Available' else "🔴"
                    st.write(f"{status_icon} {item['name']} ({item['quantity']})")
        
        with col_right:
            # Generate storage-specific QR code
            storage_url = f"{app_url}?storage={storage_id}"
            storage_qr = generate_qr_code(storage_url)
            
            if storage_qr:
                st.image(storage_qr, width=120)
                st.caption(f"QR for {storage['name']}")
                
                # Download button for QR code
                st.download_button(
                    "📥 Download QR",
                    storage_qr,
                    f"qr_{storage_id}.png",
                    "image/png",
                    key=f"download_{storage_id}"
                )
    
    st.markdown("---")
    
    # Instructions
    st.info("**QR Code Usage:**")
    st.write("• **Central QR**: Points to main dashboard")
    st.write("• **Storage QR**: Points directly to this storage")
    st.write("• Print once, update content anytime!")
    
    st.success("✅ Phase 2 Complete: QR Code system added!")

if __name__ == "__main__":
    main()