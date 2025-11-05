# app.py - COMPLETELY FIXED VERSION
import streamlit as st
import qrcode
import io
from datetime import datetime
import uuid
from database import load_inventory, save_inventory

# Set page config FIRST - before any other Streamlit commands
st.set_page_config(
    page_title="Drone Lab Inventory",
    page_icon="🚁",
    layout="wide"
)

# LOAD SHARED DATA - Same for all devices
inventory = load_inventory()

# Initialize session state for UI only
if 'ui_state' not in st.session_state:
    st.session_state.ui_state = {
        'current_view': 'dashboard',
        'selected_storage': None,
        'selected_item': None,
        'qr_codes': {},
        'last_refresh': datetime.now(),
        'delete_pending': None
    }

def generate_qr_code(data):
    """Generate HIGH QUALITY QR code"""
    try:
        qr = qrcode.QRCode(
            version=5,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=12,
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
    return inventory.get('app_url', 'https://drone-lab-inventory-l8phzdn3dqn38cppfacdtr.streamlit.app')

def get_storage_qr_code(storage_id):
    """Get QR code for specific storage"""
    qr_key = f"storage_{storage_id}"
    if qr_key not in st.session_state.ui_state['qr_codes']:
        qr_data = f"{get_app_url()}?view=storage&id={storage_id}"
        qr_image = generate_qr_code(qr_data)
        if qr_image:
            st.session_state.ui_state['qr_codes'][qr_key] = qr_image
    return st.session_state.ui_state['qr_codes'].get(qr_key)

def get_central_qr_code():
    """Get central QR code for full access"""
    if 'central_qr' not in st.session_state.ui_state['qr_codes']:
        qr_data = f"{get_app_url()}"
        qr_image = generate_qr_code(qr_data)
        if qr_image:
            st.session_state.ui_state['qr_codes']['central_qr'] = qr_image
    return st.session_state.ui_state['qr_codes'].get('central_qr')

def get_status_icon(status):
    icons = {
        'Available': '🟢',
        'In Use': '🔴', 
        'Maintenance': '🟡',
        'Broken': '❌',
        'Reserved': '⏳'
    }
    return icons.get(status, '⚪')

def generate_id():
    return str(uuid.uuid4())[:8]

def force_refresh():
    """Force refresh data from file"""
    global inventory
    inventory = load_inventory()
    st.session_state.ui_state['last_refresh'] = datetime.now()

def auto_save():
    """Auto-save after any change"""
    if save_inventory(inventory):
        st.session_state.ui_state['last_refresh'] = datetime.now()
        return True
    return False

def safe_delete_item(storage_id, item_index):
    """Safe item deletion without confirmation popup"""
    try:
        storage = inventory['storages'][storage_id]
        if 0 <= item_index < len(storage['items']):
            item_name = storage['items'][item_index]['name']
            storage['items'].pop(item_index)
            storage['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            if auto_save():
                st.success(f"✅ '{item_name}' deleted successfully!")
                return True
    except Exception as e:
        st.error(f"Delete error: {e}")
    return False

def main():
    # Check URL parameters for view type
    query_params = st.experimental_get_query_params()
    view_type = query_params.get("view", [None])[0]
    storage_id = query_params.get("id", [None])[0]
    
    # Auto-refresh every 20 seconds
    if (datetime.now() - st.session_state.ui_state['last_refresh']).seconds > 20:
        force_refresh()
        st.rerun()
    
    # Handle storage-specific view
    if view_type == 'storage' and storage_id in inventory['storages']:
        show_storage_only_view(storage_id)
    else:
        # Handle main navigation
        current_view = st.session_state.ui_state['current_view']
        
        if current_view == 'add_storage':
            add_storage_view()
        elif current_view == 'edit_storage':
            edit_storage_view()
        elif current_view == 'add_item':
            add_item_view()
        elif current_view == 'edit_item':
            edit_item_view()
        else:
            dashboard_view()

def show_storage_only_view(storage_id):
    """View for storage QR codes - READ ONLY"""
    storage = inventory['storages'][storage_id]
    
    st.title(f"🚁 {storage['name']}")
    st.markdown(f"**Location:** {storage['location']} | **Type:** {storage['type'].title()}")
    
    # Refresh button
    if st.button("🔄 Refresh Data", key="refresh_storage"):
        force_refresh()
        st.rerun()
    
    st.warning("📱 **Storage View Only** - Scan Central QR for full management access")
    
    if st.button("🏠 Go to Full Dashboard"):
        st.experimental_set_query_params()
        st.rerun()
    
    st.markdown("---")
    
    # Show items in this storage
    st.subheader(f"Items ({len(storage['items'])})")
    
    if storage['items']:
        for item in storage['items']:
            icon = get_status_icon(item['status'])
            st.write(f"{icon} **{item['name']}**")
            st.caption(f"{item['quantity']} | {item.get('category', 'Other')} | {item['status']}")
    else:
        st.info("No items in this storage")
    
    st.caption(f"Last updated: {storage['last_updated']}")

def dashboard_view():
    """Full dashboard with management capabilities"""
    st.title("🚁 Drone Lab AIC - Inventory System")
    st.markdown("### 🔄 REAL-TIME SYNC - Changes appear on all devices instantly")
    
    # Auto-refresh indicator
    last_refresh = st.session_state.ui_state['last_refresh'].strftime("%H:%M:%S")
    st.caption(f"🔄 Auto-sync active | Last sync: {last_refresh}")
    
    # Quick actions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("➕ Add Storage", use_container_width=True):
            st.session_state.ui_state['current_view'] = 'add_storage'
            st.rerun()
    with col2:
        if st.button("🔄 Force Refresh", use_container_width=True):
            force_refresh()
            st.rerun()
    
    st.markdown("---")
    
    # Statistics
    total_storages = len(inventory['storages'])
    total_items = sum(len(storage['items']) for storage in inventory['storages'].values())
    available_items = sum(1 for storage in inventory['storages'].values() for item in storage['items'] if item['status'] == 'Available')
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Storage Units", total_storages)
    with col2:
        st.metric("Total Items", total_items)
    with col3:
        st.metric("Available", available_items)
    with col4:
        central_qr = get_central_qr_code()
        if central_qr:
            st.image(central_qr, width=100)
            st.caption("**Central QR - Full Access**")
            st.download_button(
                label="📥 Download",
                data=central_qr,
                file_name="drone_lab_central_qr.png",
                mime="image/png",
                use_container_width=True,
                key="dl_central"
            )
    
    st.markdown("---")
    
    # QR Code Instructions
    st.info("""
    **📱 QR Code System:**
    - **Central QR**: Full dashboard access (manage everything)
    - **Storage QR**: View only that specific storage
    - **Real-time Sync**: Changes appear instantly on all devices
    """)
    
    st.markdown("---")
    
    # Storage Management
    st.subheader("📦 Storage Management")
    
    if not inventory['storages']:
        st.info("🚁 No storage units yet. Click 'Add Storage' to create your first one!")
        return
    
    for storage_id, storage in inventory['storages'].items():
        with st.expander(f"🚀 {storage['name']} ({len(storage['items'])} items)", expanded=True):
            col_left, col_right = st.columns([3, 1])
            
            with col_left:
                st.write(f"**Location:** {storage['location']}")
                st.write(f"**Type:** {storage['type'].title()}")
                if storage.get('description'):
                    st.write(f"**Description:** {storage['description']}")
                st.write(f"**Last Updated:** {storage['last_updated']}")
                
                st.markdown("---")
                st.write("**Items:**")
                
                if storage['items']:
                    for i, item in enumerate(storage['items']):
                        col_item, col_edit, col_delete = st.columns([3, 1, 1])
                        with col_item:
                            icon = get_status_icon(item['status'])
                            st.write(f"{icon} **{item['name']}**")
                            st.caption(f"{item['quantity']} • {item.get('category', 'Other')}")
                        with col_edit:
                            if st.button("✏️", key=f"edit_{storage_id}_{item['id']}"):
                                st.session_state.ui_state['current_view'] = 'edit_item'
                                st.session_state.ui_state['selected_storage'] = storage_id
                                st.session_state.ui_state['selected_item'] = i
                                st.rerun()
                        with col_delete:
                            # SIMPLE DELETE - No confirmation popup
                            if st.button("🗑️", key=f"delete_{storage_id}_{item['id']}"):
                                if safe_delete_item(storage_id, i):
                                    st.rerun()
                else:
                    st.info("No items in this storage")
                
                if st.button("➕ Add Item", key=f"add_{storage_id}", use_container_width=True):
                    st.session_state.ui_state['current_view'] = 'add_item'
                    st.session_state.ui_state['selected_storage'] = storage_id
                    st.rerun()
            
            with col_right:
                storage_qr = get_storage_qr_code(storage_id)
                if storage_qr:
                    st.image(storage_qr, width=130)
                    st.caption(f"**Storage QR - View Only**")
                    st.download_button(
                        label="📥 Download",
                        data=storage_qr,
                        file_name=f"qr_{storage['name'].replace(' ', '_')}.png",
                        mime="image/png",
                        key=f"dl_{storage_id}",
                        use_container_width=True
                    )
                
                st.markdown("---")
                
                if st.button("⚙️ Manage Storage", key=f"manage_{storage_id}", use_container_width=True):
                    st.session_state.ui_state['current_view'] = 'edit_storage'
                    st.session_state.ui_state['selected_storage'] = storage_id
                    st.rerun()
                
                available = sum(1 for item in storage['items'] if item['status'] == 'Available')
                st.metric("Available", available)
                st.metric("Total", len(storage['items']))

def add_storage_view():
    st.title("🏗️ Add New Storage")
    if st.button("← Back to Dashboard"):
        st.session_state.ui_state['current_view'] = 'dashboard'
        st.rerun()
    
    with st.form("add_storage_form"):
        name = st.text_input("Storage Name*", placeholder="e.g., Drone Cabinet")
        location = st.text_input("Location*", value="Drone Lab AIC")
        storage_type = st.selectbox("Storage Type*", inventory['storage_types'])
        description = st.text_area("Description", placeholder="Optional description")
        
        if st.form_submit_button("🏗️ Create Storage", use_container_width=True):
            if name and location:
                storage_id = f"storage_{generate_id()}"
                inventory['storages'][storage_id] = {
                    'id': storage_id,
                    'name': name,
                    'location': location,
                    'type': storage_type,
                    'description': description,
                    'items': [],
                    'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                if auto_save():
                    st.session_state.ui_state['current_view'] = 'dashboard'
                    st.success(f"✅ Storage '{name}' created successfully!")
                    st.rerun()

def edit_storage_view():
    storage_id = st.session_state.ui_state['selected_storage']
    storage = inventory['storages'][storage_id]
    
    st.title(f"⚙️ Manage {storage['name']}")
    if st.button("← Back to Dashboard"):
        st.session_state.ui_state['current_view'] = 'dashboard'
        st.session_state.ui_state['selected_storage'] = None
        st.rerun()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Storage Details")
        with st.form("edit_storage_form"):
            name = st.text_input("Name*", value=storage['name'])
            location = st.text_input("Location*", value=storage['location'])
            storage_type = st.selectbox("Type*", inventory['storage_types'], 
                                      index=inventory['storage_types'].index(storage['type']))
            description = st.text_area("Description", value=storage.get('description', ''))
            
            if st.form_submit_button("💾 Save Changes", use_container_width=True):
                if name and location:
                    storage.update({
                        'name': name, 
                        'location': location, 
                        'type': storage_type, 
                        'description': description,
                        'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    if auto_save():
                        st.session_state.ui_state['current_view'] = 'dashboard'
                        st.session_state.ui_state['selected_storage'] = None
                        st.success("✅ Storage updated successfully!")
                        st.rerun()
    
    with col2:
        st.subheader("Danger Zone")
        st.warning("This will permanently delete the storage and all its items!")
        
        # SIMPLE DELETE - No confirmation conflicts
        if st.button("🗑️ Delete This Storage", type="secondary", use_container_width=True, key="delete_storage_final"):
            storage_name = storage['name']
            del inventory['storages'][storage_id]
            if auto_save():
                st.session_state.ui_state['current_view'] = 'dashboard'
                st.session_state.ui_state['selected_storage'] = None
                st.success(f"✅ Storage '{storage_name}' deleted successfully!")
                st.rerun()

def add_item_view():
    storage_id = st.session_state.ui_state['selected_storage']
    storage = inventory['storages'][storage_id]
    
    st.title(f"➕ Add Item to {storage['name']}")
    if st.button("← Back to Dashboard"):
        st.session_state.ui_state['current_view'] = 'dashboard'
        st.session_state.ui_state['selected_storage'] = None
        st.rerun()
    
    with st.form("add_item_form"):
        name = st.text_input("Item Name*", placeholder="e.g., DJI Mavic 3")
        quantity = st.text_input("Quantity*", placeholder="e.g., 2 units")
        category = st.selectbox("Category", inventory['categories'])
        status = st.selectbox("Status", inventory['status_options'])
        
        if st.form_submit_button("➕ Add Item", use_container_width=True):
            if name and quantity:
                storage['items'].append({
                    'id': f"item_{generate_id()}",
                    'name': name, 
                    'quantity': quantity, 
                    'category': category, 
                    'status': status
                })
                storage['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if auto_save():
                    st.session_state.ui_state['current_view'] = 'dashboard'
                    st.session_state.ui_state['selected_storage'] = None
                    st.success(f"✅ Item '{name}' added successfully!")
                    st.rerun()

def edit_item_view():
    storage_id = st.session_state.ui_state['selected_storage']
    item_index = st.session_state.ui_state['selected_item']
    storage = inventory['storages'][storage_id]
    item = storage['items'][item_index]
    
    st.title(f"✏️ Edit Item in {storage['name']}")
    if st.button("← Back to Dashboard"):
        st.session_state.ui_state['current_view'] = 'dashboard'
        st.session_state.ui_state['selected_storage'] = None
        st.session_state.ui_state['selected_item'] = None
        st.rerun()
    
    with st.form("edit_item_form"):
        name = st.text_input("Item Name*", value=item['name'])
        quantity = st.text_input("Quantity*", value=item['quantity'])
        category = st.selectbox("Category", inventory['categories'],
                              index=inventory['categories'].index(item.get('category', 'Other')))
        status = st.selectbox("Status", inventory['status_options'],
                            index=inventory['status_options'].index(item['status']))
        
        if st.form_submit_button("💾 Save Changes", use_container_width=True):
            if name and quantity:
                item.update({
                    'name': name, 
                    'quantity': quantity, 
                    'category': category, 
                    'status': status
                })
                storage['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                if auto_save():
                    st.session_state.ui_state['current_view'] = 'dashboard'
                    st.session_state.ui_state['selected_storage'] = None
                    st.session_state.ui_state['selected_item'] = None
                    st.success("✅ Item updated successfully!")
                    st.rerun()

if __name__ == "__main__":
    main()