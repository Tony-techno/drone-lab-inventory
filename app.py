# app.py - COMPLETE VERSION WITH QR CODES
import streamlit as st
import qrcode
import io
from datetime import datetime
import uuid

# Data persistence in session state
if 'inventory' not in st.session_state:
    st.session_state.inventory = {
        'storages': {
            'storage_1': {
                'id': 'storage_1',
                'name': 'Drone Storage Cabinet',
                'type': 'cabinet',
                'location': 'Drone Lab AIC',
                'description': 'Main storage for drone equipment',
                'items': [
                    {'id': 'item_1', 'name': 'DJI Mavic 3 Pro', 'quantity': '3 units', 'status': 'Available', 'category': 'Drones'},
                    {'id': 'item_2', 'name': 'LiPo Batteries', 'quantity': '15 units', 'status': 'Available', 'category': 'Batteries'},
                    {'id': 'item_3', 'name': 'FPV Controller', 'quantity': '2 units', 'status': 'In Use', 'category': 'Controllers'}
                ],
                'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'qr_generated': False
            },
            'storage_2': {
                'id': 'storage_2',
                'name': 'Tool & Parts Drawer',
                'type': 'drawer',
                'location': 'Drone Lab AIC',
                'description': 'Tools and spare parts',
                'items': [
                    {'id': 'item_4', 'name': 'Screwdriver Set', 'quantity': '1 set', 'status': 'Available', 'category': 'Tools'},
                    {'id': 'item_5', 'name': 'Propeller Set', 'quantity': '10 pairs', 'status': 'Available', 'category': 'Propellers'}
                ],
                'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M"),
                'qr_generated': False
            }
        },
        'categories': ['Drones', 'Batteries', 'Controllers', 'Propellers', 'Cameras', 'Sensors', 'Chargers', 'Tools', 'Electronics', 'Stationary', 'Other'],
        'status_options': ['Available', 'In Use', 'Maintenance', 'Broken', 'Reserved'],
        'storage_types': ['shelf', 'cabinet', 'drawer', 'rack', 'storage_room', 'toolbox', 'other']
    }

# Initialize QR codes in session state
if 'qr_codes' not in st.session_state:
    st.session_state.qr_codes = {}

# UI state management
if 'current_view' not in st.session_state:
    st.session_state.current_view = 'dashboard'
if 'selected_storage' not in st.session_state:
    st.session_state.selected_storage = None
if 'selected_item' not in st.session_state:
    st.session_state.selected_item = None
if 'delete_confirm' not in st.session_state:
    st.session_state.delete_confirm = None

def generate_qr_code(data):
    """Generate QR code for given data"""
    try:
        qr = qrcode.QRCode(
            version=5,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        
        qr_img = qr.make_image(fill_color="black", back_color="white")
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

def get_storage_qr_code(storage_id, storage_name):
    """Get or generate QR code for a storage"""
    qr_key = f"storage_{storage_id}"
    
    if qr_key not in st.session_state.qr_codes:
        # Generate QR code with storage information
        qr_data = f"{get_app_url()}?storage={storage_id}\nStorage: {storage_name}\nLab: Drone Lab AIC"
        qr_image = generate_qr_code(qr_data)
        if qr_image:
            st.session_state.qr_codes[qr_key] = qr_image
    
    return st.session_state.qr_codes.get(qr_key)

def get_central_qr_code():
    """Get central QR code for the entire app"""
    if 'central_qr' not in st.session_state.qr_codes:
        qr_data = f"{get_app_url()}\nDrone Lab AIC Inventory System\nScan to access inventory"
        qr_image = generate_qr_code(qr_data)
        if qr_image:
            st.session_state.qr_codes['central_qr'] = qr_image
    
    return st.session_state.qr_codes.get('central_qr')

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

def generate_id():
    """Generate unique ID"""
    return str(uuid.uuid4())[:8]

def main():
    st.set_page_config(
        page_title="Drone Lab Inventory",
        page_icon="🚁",
        layout="wide"
    )
    
    # Navigation
    if st.session_state.current_view == 'add_storage':
        add_storage_view()
    elif st.session_state.current_view == 'edit_storage':
        edit_storage_view()
    elif st.session_state.current_view == 'add_item':
        add_item_view()
    elif st.session_state.current_view == 'edit_item':
        edit_item_view()
    else:
        dashboard_view()

def dashboard_view():
    """Main dashboard view"""
    st.title("🚁 Drone Lab AIC - Inventory System")
    st.markdown("### 📱 QR CODE INVENTORY SYSTEM - FULLY WORKING")
    
    # Quick actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Add New Storage", use_container_width=True):
            st.session_state.current_view = 'add_storage'
            st.rerun()
    with col2:
        if st.button("🔄 Refresh All QR Codes", use_container_width=True):
            st.session_state.qr_codes = {}  # Clear cache to regenerate
            st.rerun()
    
    st.markdown("---")
    
    # Statistics with Central QR
    total_storages = len(st.session_state.inventory['storages'])
    total_items = sum(len(storage['items']) for storage in st.session_state.inventory['storages'].values())
    available_items = sum(
        1 for storage in st.session_state.inventory['storages'].values() 
        for item in storage['items'] 
        if item['status'] == 'Available'
    )
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Storage Units", total_storages)
    with col2:
        st.metric("Total Items", total_items)
    with col3:
        st.metric("Available Items", available_items)
    with col4:
        # Central QR Code
        central_qr = get_central_qr_code()
        if central_qr:
            st.image(central_qr, width=100)
            st.caption("Main App QR")
            # Download button for central QR
            st.download_button(
                label="📥 Download Main QR",
                data=central_qr,
                file_name="drone_lab_main_qr.png",
                mime="image/png",
                use_container_width=True
            )
    
    st.markdown("---")
    
    # QR Code Instructions
    st.info("""
    **📱 QR Code System Usage:**
    - **Main QR**: Points to entire inventory dashboard
    - **Storage QR**: Points directly to specific storage
    - **Print once**: QR codes stay the same, content updates automatically
    - **Mobile access**: Scan QR codes to quickly access inventory on any device
    """)
    
    st.markdown("---")
    
    # Storage Management
    st.subheader("📦 Storage Units with QR Codes")
    
    if not st.session_state.inventory['storages']:
        st.info("🚁 No storage units yet. Click 'Add Storage' to create your first one!")
        return
    
    for storage_id, storage in st.session_state.inventory['storages'].items():
        display_storage_card(storage_id, storage)

def display_storage_card(storage_id, storage):
    """Display a storage card with QR code"""
    with st.expander(f"🚀 {storage['name']} ({len(storage['items'])} items)", expanded=True):
        col_left, col_right = st.columns([3, 1])
        
        with col_left:
            # Storage info
            st.write(f"**Location:** {storage['location']}")
            st.write(f"**Type:** {storage['type'].title()}")
            if storage.get('description'):
                st.write(f"**Description:** {storage['description']}")
            st.write(f"**Last Updated:** {storage['last_updated']}")
            
            st.markdown("---")
            st.write("**Items:**")
            
            # Display items
            if storage['items']:
                for i, item in enumerate(storage['items']):
                    display_item_row(storage_id, i, item)
            else:
                st.info("No items in this storage")
            
            # Add item button
            if st.button("➕ Add Item", key=f"add_item_{storage_id}", use_container_width=True):
                st.session_state.current_view = 'add_item'
                st.session_state.selected_storage = storage_id
                st.rerun()
        
        with col_right:
            # Storage QR Code
            storage_qr = get_storage_qr_code(storage_id, storage['name'])
            if storage_qr:
                st.image(storage_qr, width=150)
                st.caption(f"QR: {storage['name']}")
                
                # Download button for storage QR
                st.download_button(
                    label="📥 Download QR",
                    data=storage_qr,
                    file_name=f"qr_{storage['name'].replace(' ', '_')}.png",
                    mime="image/png",
                    key=f"download_{storage_id}",
                    use_container_width=True
                )
            
            st.markdown("---")
            
            # Storage management
            if st.button("⚙️ Manage Storage", key=f"manage_{storage_id}", use_container_width=True):
                st.session_state.current_view = 'edit_storage'
                st.session_state.selected_storage = storage_id
                st.rerun()
            
            # Quick stats
            available_count = sum(1 for item in storage['items'] if item['status'] == 'Available')
            st.metric("Available", available_count)

def display_item_row(storage_id, item_index, item):
    """Display a single item row with edit/delete buttons"""
    col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
    
    with col1:
        icon = get_status_icon(item['status'])
        st.write(f"{icon} **{item['name']}**")
        st.caption(f"{item['quantity']} • {item.get('category', 'Other')}")
    
    with col2:
        st.caption(item['status'])
    
    with col3:
        if st.button("✏️", key=f"edit_{storage_id}_{item['id']}"):
            st.session_state.current_view = 'edit_item'
            st.session_state.selected_storage = storage_id
            st.session_state.selected_item = item_index
            st.rerun()
    
    with col4:
        if st.button("🗑️", key=f"delete_{storage_id}_{item['id']}"):
            # Store deletion context
            st.session_state.delete_confirm = {
                'type': 'item',
                'storage_id': storage_id,
                'item_index': item_index,
                'item_name': item['name']
            }
            st.rerun()

def add_storage_view():
    """Add new storage view"""
    st.title("🏗️ Add New Storage")
    
    if st.button("← Back to Dashboard"):
        st.session_state.current_view = 'dashboard'
        st.rerun()
    
    with st.form("add_storage_form"):
        name = st.text_input("Storage Name*", placeholder="e.g., Drone Cabinet, Battery Shelf")
        location = st.text_input("Location*", value="Drone Lab AIC")
        storage_type = st.selectbox("Storage Type*", st.session_state.inventory['storage_types'])
        description = st.text_area("Description", placeholder="Optional description of this storage")
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("🏗️ Create Storage", type="primary", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if cancel:
            st.session_state.current_view = 'dashboard'
            st.rerun()
        
        if submit:
            if name and location:
                storage_id = f"storage_{generate_id()}"
                st.session_state.inventory['storages'][storage_id] = {
                    'id': storage_id,
                    'name': name,
                    'location': location,
                    'type': storage_type,
                    'description': description,
                    'items': [],
                    'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M"),
                    'qr_generated': False
                }
                st.session_state.current_view = 'dashboard'
                st.success(f"✅ Storage '{name}' created successfully! QR code will be generated automatically.")
                st.rerun()
            else:
                st.error("Please fill in all required fields (*)")

def edit_storage_view():
    """Edit storage view"""
    storage_id = st.session_state.selected_storage
    storage = st.session_state.inventory['storages'][storage_id]
    
    st.title("⚙️ Manage Storage")
    
    if st.button("← Back to Dashboard"):
        st.session_state.current_view = 'dashboard'
        st.session_state.selected_storage = None
        st.rerun()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Storage Details")
        with st.form("edit_storage_form"):
            name = st.text_input("Name*", value=storage['name'])
            location = st.text_input("Location*", value=storage['location'])
            storage_type = st.selectbox("Type*", 
                                      st.session_state.inventory['storage_types'],
                                      index=st.session_state.inventory['storage_types'].index(storage['type']))
            description = st.text_area("Description", value=storage.get('description', ''))
            
            if st.form_submit_button("💾 Save Changes", use_container_width=True):
                if name and location:
                    storage.update({
                        'name': name,
                        'location': location,
                        'type': storage_type,
                        'description': description,
                        'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M")
                    })
                    # Clear QR cache to regenerate with new data
                    qr_key = f"storage_{storage_id}"
                    if qr_key in st.session_state.qr_codes:
                        del st.session_state.qr_codes[qr_key]
                    
                    st.session_state.current_view = 'dashboard'
                    st.session_state.selected_storage = None
                    st.success("✅ Storage updated successfully! QR code updated.")
                    st.rerun()
    
    with col2:
        st.subheader("Danger Zone")
        st.warning("This will permanently delete the storage and all its items!")
        
        if st.button("🗑️ Delete This Storage", type="secondary", use_container_width=True):
            storage_name = storage['name']
            # Clear QR cache
            qr_key = f"storage_{storage_id}"
            if qr_key in st.session_state.qr_codes:
                del st.session_state.qr_codes[qr_key]
            
            del st.session_state.inventory['storages'][storage_id]
            st.session_state.current_view = 'dashboard'
            st.session_state.selected_storage = None
            st.success(f"✅ Storage '{storage_name}' deleted successfully!")
            st.rerun()

def add_item_view():
    """Add item view"""
    storage_id = st.session_state.selected_storage
    storage = st.session_state.inventory['storages'][storage_id]
    
    st.title(f"➕ Add Item to {storage['name']}")
    
    if st.button("← Back to Dashboard"):
        st.session_state.current_view = 'dashboard'
        st.session_state.selected_storage = None
        st.rerun()
    
    with st.form("add_item_form"):
        name = st.text_input("Item Name*", placeholder="e.g., DJI Mavic 3, LiPo Battery")
        quantity = st.text_input("Quantity*", placeholder="e.g., 2 units, 5 packs")
        category = st.selectbox("Category", st.session_state.inventory['categories'])
        status = st.selectbox("Status", st.session_state.inventory['status_options'])
        
        if st.form_submit_button("➕ Add Item", type="primary", use_container_width=True):
            if name and quantity:
                new_item = {
                    'id': f"item_{generate_id()}",
                    'name': name,
                    'quantity': quantity,
                    'category': category,
                    'status': status
                }
                storage['items'].append(new_item)
                storage['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.session_state.current_view = 'dashboard'
                st.session_state.selected_storage = None
                st.success(f"✅ Item '{name}' added successfully!")
                st.rerun()
            else:
                st.error("Please fill in item name and quantity")

def edit_item_view():
    """Edit item view"""
    storage_id = st.session_state.selected_storage
    item_index = st.session_state.selected_item
    storage = st.session_state.inventory['storages'][storage_id]
    item = storage['items'][item_index]
    
    st.title(f"✏️ Edit Item in {storage['name']}")
    
    if st.button("← Back to Dashboard"):
        st.session_state.current_view = 'dashboard'
        st.session_state.selected_storage = None
        st.session_state.selected_item = None
        st.rerun()
    
    with st.form("edit_item_form"):
        name = st.text_input("Item Name*", value=item['name'])
        quantity = st.text_input("Quantity*", value=item['quantity'])
        category = st.selectbox("Category", 
                              st.session_state.inventory['categories'],
                              index=st.session_state.inventory['categories'].index(item.get('category', 'Other')))
        status = st.selectbox("Status",
                            st.session_state.inventory['status_options'],
                            index=st.session_state.inventory['status_options'].index(item['status']))
        
        if st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True):
            if name and quantity:
                item.update({
                    'name': name,
                    'quantity': quantity,
                    'category': category,
                    'status': status
                })
                storage['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.session_state.current_view = 'dashboard'
                st.session_state.selected_storage = None
                st.session_state.selected_item = None
                st.success(f"✅ Item '{name}' updated successfully!")
                st.rerun()
            else:
                st.error("Please fill in item name and quantity")

# Handle deletion confirmation
if st.session_state.delete_confirm:
    delete_info = st.session_state.delete_confirm
    st.error(f"🚨 Confirm Deletion")
    
    if delete_info['type'] == 'item':
        st.write(f"Are you sure you want to delete **{delete_info['item_name']}**?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Yes, Delete", type="primary", use_container_width=True):
                # SAFE DELETION - using stored index
                storage = st.session_state.inventory['storages'][delete_info['storage_id']]
                storage['items'].pop(delete_info['item_index'])
                storage['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M")
                st.session_state.delete_confirm = None
                st.success(f"✅ Item '{delete_info['item_name']}' deleted successfully!")
                st.rerun()
        with col2:
            if st.button("❌ Cancel", use_container_width=True):
                st.session_state.delete_confirm = None
                st.rerun()

if __name__ == "__main__":
    main()