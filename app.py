# app.py - PHASE 3: Item Management System
import streamlit as st
import qrcode
import io
from datetime import datetime

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
                ],
                'last_updated': '2024-01-01'
            }
        },
        'categories': ['Equipment', 'Tool', 'Electronic', 'Chemical', 'Glassware', 'Other'],
        'status_options': ['Available', 'In Use', 'Maintenance', 'Broken', 'Reserved']
    }

# Initialize editing states
if 'editing_item' not in st.session_state:
    st.session_state.editing_item = None
if 'adding_item' not in st.session_state:
    st.session_state.adding_item = False

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
    """Get the current app URL"""
    return "https://drone-lab-inventory-l8phzdn3dqn38cppfacdtr.streamlit.app/"

def get_status_icon(status):
    """Get icon for item status"""
    icons = {
        'Available': '🟢',
        'In Use': '🔴',
        'Maintenance': '🟡', 
        'Broken': '❌',
        'Reserved': '⏳'
    }
    return icons.get(status, '⚪')

def main_dashboard():
    """Main dashboard view"""
    st.set_page_config(
        page_title="Lab Inventory",
        page_icon="📦",
        layout="wide"
    )
    
    st.title("📦 Lab Inventory System")
    st.markdown("### 🚀 PHASE 3 ACTIVE - ITEM MANAGEMENT")
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
    
    # Show storages with management options
    st.subheader("📊 Storage Management")
    
    for storage_id, storage in st.session_state.inventory['storages'].items():
        show_storage_with_management(storage_id, storage, app_url)
    
    st.markdown("---")
    st.success("✅ Phase 3 Complete: Item management system added!")

def show_storage_with_management(storage_id, storage, app_url):
    """Show storage with item management options"""
    col_left, col_right = st.columns([3, 1])
    
    with col_left:
        with st.expander(f"📦 {storage['name']} ({len(storage['items'])} items)", expanded=True):
            st.write(f"**Location:** {storage['location']}")
            st.write(f"**Type:** {storage['type']}")
            if 'last_updated' in storage:
                st.write(f"**Last Updated:** {storage['last_updated']}")
            
            # Items with management buttons
            st.write("**Items:**")
            if storage['items']:
                for i, item in enumerate(storage['items']):
                    col_item, col_edit, col_delete = st.columns([3, 1, 1])
                    
                    with col_item:
                        status_icon = get_status_icon(item['status'])
                        st.write(f"{status_icon} {item['name']} ({item['quantity']})")
                    
                    with col_edit:
                        if st.button("✏️", key=f"edit_{storage_id}_{i}"):
                            st.session_state.editing_item = (storage_id, i)
                            st.rerun()
                    
                    with col_delete:
                        if st.button("🗑️", key=f"delete_{storage_id}_{i}"):
                            delete_item(storage_id, i)
                            st.rerun()
            else:
                st.info("No items in this storage")
            
            # Add item button
            if st.button("➕ Add New Item", key=f"add_{storage_id}"):
                st.session_state.adding_item = storage_id
                st.rerun()
    
    with col_right:
        # QR code
        storage_url = f"{app_url}?storage={storage_id}"
        storage_qr = generate_qr_code(storage_url)
        
        if storage_qr:
            st.image(storage_qr, width=120)
            st.caption(f"QR for {storage['name']}")
            
            st.download_button(
                "📥 Download QR",
                storage_qr,
                f"qr_{storage_id}.png",
                "image/png",
                key=f"download_{storage_id}"
            )

def add_item_view(storage_id):
    """View for adding a new item"""
    st.title("➕ Add New Item")
    
    storage = st.session_state.inventory['storages'][storage_id]
    st.write(f"**Storage:** {storage['name']}")
    st.markdown("---")
    
    with st.form(f"add_item_form_{storage_id}"):
        name = st.text_input("Item Name*", placeholder="Enter item name")
        quantity = st.text_input("Quantity*", placeholder="e.g., 5 units, 200ml")
        category = st.selectbox("Category", st.session_state.inventory['categories'])
        status = st.selectbox("Status", st.session_state.inventory['status_options'])
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("➕ Add Item", type="primary", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if cancel:
            st.session_state.adding_item = False
            st.rerun()
            
        if submit:
            if name and quantity:
                add_item_to_storage(storage_id, name, quantity, category, status)
                st.session_state.adding_item = False
                st.success(f"✅ Item '{name}' added successfully!")
                st.rerun()
            else:
                st.error("Please fill in item name and quantity")

def edit_item_view():
    """View for editing an item"""
    storage_id, item_index = st.session_state.editing_item
    storage = st.session_state.inventory['storages'][storage_id]
    item = storage['items'][item_index]
    
    st.title("✏️ Edit Item")
    st.write(f"**Storage:** {storage['name']}")
    st.markdown("---")
    
    with st.form("edit_item_form"):
        name = st.text_input("Item Name*", value=item['name'])
        quantity = st.text_input("Quantity*", value=item['quantity'])
        category = st.selectbox("Category", st.session_state.inventory['categories'],
                               index=st.session_state.inventory['categories'].index(item.get('category', 'Other')))
        status = st.selectbox("Status", st.session_state.inventory['status_options'],
                             index=st.session_state.inventory['status_options'].index(item['status']))
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if cancel:
            st.session_state.editing_item = None
            st.rerun()
            
        if submit:
            if name and quantity:
                update_item(storage_id, item_index, name, quantity, category, status)
                st.session_state.editing_item = None
                st.success(f"✅ Item '{name}' updated successfully!")
                st.rerun()
            else:
                st.error("Please fill in item name and quantity")

# CRUD Operations
def add_item_to_storage(storage_id, name, quantity, category, status):
    """Add item to storage"""
    st.session_state.inventory['storages'][storage_id]['items'].append({
        'name': name,
        'quantity': quantity,
        'category': category,
        'status': status
    })
    # Update timestamp
    st.session_state.inventory['storages'][storage_id]['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def update_item(storage_id, item_index, name, quantity, category, status):
    """Update item details"""
    st.session_state.inventory['storages'][storage_id]['items'][item_index].update({
        'name': name,
        'quantity': quantity,
        'category': category,
        'status': status
    })
    # Update timestamp
    st.session_state.inventory['storages'][storage_id]['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def delete_item(storage_id, item_index):
    """Delete an item"""
    item_name = st.session_state.inventory['storages'][storage_id]['items'][item_index]['name']
    del st.session_state.inventory['storages'][storage_id]['items'][item_index]
    # Update timestamp
    st.session_state.inventory['storages'][storage_id]['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.success(f"✅ Item '{item_name}' deleted successfully!")

# Main application router
def main():
    # Handle different views
    if st.session_state.get('editing_item'):
        edit_item_view()
    elif st.session_state.get('adding_item'):
        add_item_view(st.session_state.adding_item)
    else:
        main_dashboard()

if __name__ == "__main__":
    main()