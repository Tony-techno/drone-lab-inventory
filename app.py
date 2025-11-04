# app.py - PHASE 4: COMPLETELY FIXED VERSION
import streamlit as st
import qrcode
import io
from datetime import datetime
import uuid

# Initialize session state
if 'inventory' not in st.session_state:
    st.session_state.inventory = {
        'storages': {
            'storage_1': {
                'id': 'storage_1',
                'name': 'Main Storage',
                'type': 'shelf',
                'location': 'Drone Lab AIC',
                'description': 'Primary storage for drone equipment',
                'items': [
                    {'name': 'DJI Mavic 3', 'quantity': '2 units', 'status': 'Available', 'category': 'Drones'},
                    {'name': 'LiPo Batteries', 'quantity': '10 units', 'status': 'Available', 'category': 'Batteries'}
                ],
                'last_updated': '2024-01-01',
                'created_date': '2024-01-01'
            }
        },
        'categories': [
            'Drones', 'Batteries', 'Controllers', 'Propellers', 'Cameras', 
            'Sensors', 'Chargers', 'Tools', 'Electronics', 'Stationary', 'Other'
        ],
        'status_options': ['Available', 'In Use', 'Maintenance', 'Broken', 'Reserved'],
        'storage_types': ['shelf', 'cabinet', 'drawer', 'rack', 'storage_room', 'toolbox', 'other']
    }

# Initialize UI states
if 'editing_item' not in st.session_state:
    st.session_state.editing_item = None
if 'adding_item' not in st.session_state:
    st.session_state.adding_item = False
if 'adding_storage' not in st.session_state:
    st.session_state.adding_storage = False
if 'editing_storage' not in st.session_state:
    st.session_state.editing_storage = None
if 'view_mode' not in st.session_state:
    st.session_state.view_mode = 'dashboard'
if 'delete_confirm' not in st.session_state:
    st.session_state.delete_confirm = None
if 'delete_item_confirm' not in st.session_state:
    st.session_state.delete_item_confirm = None

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

def generate_storage_id():
    """Generate unique storage ID"""
    return f"storage_{uuid.uuid4().hex[:8]}"

def main_dashboard():
    """Main dashboard view"""
    st.set_page_config(
        page_title="Drone Lab Inventory",
        page_icon="🚁",
        layout="wide"
    )
    
    st.title("🚁 Drone Lab AIC - Inventory System")
    st.markdown("### 🚀 PHASE 4 ACTIVE - STORAGE MANAGEMENT")
    st.markdown("---")
    
    # Quick actions
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        if st.button("➕ Add Storage", use_container_width=True):
            st.session_state.adding_storage = True
            st.rerun()
    with col2:
        if st.button("📊 View All Items", use_container_width=True):
            st.session_state.view_mode = 'all_items'
            st.rerun()
    with col3:
        if st.button("🏠 Dashboard", use_container_width=True):
            st.session_state.view_mode = 'dashboard'
            st.rerun()
    
    st.markdown("---")
    
    # Show basic stats
    total_storages = len(st.session_state.inventory['storages'])
    total_items = sum(len(storage['items']) for storage in st.session_state.inventory['storages'].values())
    
    available_items = 0
    for storage in st.session_state.inventory['storages'].values():
        for item in storage['items']:
            if item['status'] == 'Available':
                available_items += 1
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Storage Units", total_storages)
    with col2:
        st.metric("Total Items", total_items)
    with col3:
        st.metric("Available Items", available_items)
    with col4:
        # Central QR Code
        app_url = get_app_url()
        central_qr = generate_qr_code(app_url)
        if central_qr:
            st.image(central_qr, width=80)
            st.caption("Central QR")
    
    st.markdown("---")
    
    # Show storages
    st.subheader("📊 Storage Management")
    
    if not st.session_state.inventory['storages']:
        st.info("🚁 No storage units yet. Click 'Add Storage' to create your first one!")
    else:
        for storage_id, storage in st.session_state.inventory['storages'].items():
            show_storage_with_management(storage_id, storage, app_url)
    
    st.markdown("---")
    st.success("✅ Phase 4 Complete: Storage management system added!")

def all_items_view():
    """View all items across all storages"""
    st.title("📋 All Drone Lab Items")
    
    # Back button
    if st.button("← Back to Dashboard"):
        st.session_state.view_mode = 'dashboard'
        st.rerun()
    
    st.markdown("---")
    
    all_items = []
    for storage_id, storage in st.session_state.inventory['storages'].items():
        for item in storage['items']:
            all_items.append({
                'storage_name': storage['name'],
                'storage_location': storage['location'],
                'storage_id': storage_id,
                **item
            })
    
    if not all_items:
        st.info("📭 No items found in any storage.")
        return
    
    # Display all items
    for i, item in enumerate(all_items):
        col1, col2, col3, col4, col5 = st.columns([2, 2, 1, 1, 1])
        
        with col1:
            st.write(f"**{item['name']}**")
            st.caption(f"Storage: {item['storage_name']}")
        
        with col2:
            st.write(item['quantity'])
            st.caption(f"Location: {item['storage_location']}")
        
        with col3:
            st.write(item['category'])
        
        with col4:
            status_icon = get_status_icon(item['status'])
            st.write(f"{status_icon} {item['status']}")
        
        with col5:
            if st.button("✏️ Edit", key=f"edit_all_{i}"):
                # Find the exact item index
                storage_items = st.session_state.inventory['storages'][item['storage_id']]['items']
                for idx, storage_item in enumerate(storage_items):
                    if (storage_item['name'] == item['name'] and 
                        storage_item['quantity'] == item['quantity'] and 
                        storage_item.get('category', 'Other') == item.get('category', 'Other')):
                        st.session_state.editing_item = (item['storage_id'], idx)
                        st.rerun()
                        break

def show_storage_with_management(storage_id, storage, app_url):
    """Show storage with full management options"""
    col_left, col_right = st.columns([3, 1])
    
    with col_left:
        with st.expander(f"📦 {storage['name']} ({len(storage['items'])} items)", expanded=True):
            # Storage info with edit button
            col_info, col_edit = st.columns([3, 1])
            with col_info:
                st.write(f"**Location:** {storage['location']}")
                st.write(f"**Type:** {storage['type'].title()}")
                if 'description' in storage and storage['description']:
                    st.write(f"**Description:** {storage['description']}")
                if 'last_updated' in storage:
                    st.write(f"**Last Updated:** {storage['last_updated']}")
            
            with col_edit:
                if st.button("⚙️ Manage", key=f"manage_{storage_id}"):
                    st.session_state.editing_storage = storage_id
                    st.rerun()
            
            st.markdown("---")
            
            # Items management
            st.write("**Items:**")
            if storage['items']:
                for i, item in enumerate(storage['items']):
                    col_item, col_edit, col_delete = st.columns([3, 1, 1])
                    
                    with col_item:
                        status_icon = get_status_icon(item['status'])
                        st.write(f"{status_icon} **{item['name']}** ({item['quantity']})")
                        st.caption(f"Category: {item.get('category', 'Other')}")
                    
                    with col_edit:
                        if st.button("✏️", key=f"edit_{storage_id}_{i}"):
                            st.session_state.editing_item = (storage_id, i)
                            st.rerun()
                    
                    with col_delete:
                        delete_key = f"delete_{storage_id}_{i}"
                        if st.button("🗑️", key=delete_key):
                            st.session_state.delete_item_confirm = (storage_id, i, item['name'])
                            st.rerun()
            
            # Show delete confirmation if needed
            if (st.session_state.delete_item_confirm and 
                st.session_state.delete_item_confirm[0] == storage_id):
                storage_id_confirm, item_index, item_name = st.session_state.delete_item_confirm
                st.error(f"Are you sure you want to delete '{item_name}'?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Yes, Delete", key=f"confirm_del_{storage_id}_{item_index}"):
                        delete_item(storage_id_confirm, item_index)
                        st.session_state.delete_item_confirm = None
                        st.rerun()
                with col2:
                    if st.button("❌ Cancel", key=f"cancel_del_{storage_id}_{item_index}"):
                        st.session_state.delete_item_confirm = None
                        st.rerun()
            
            if not storage['items']:
                st.info("📭 No items in this storage")
            
            # Add item button
            if st.button("➕ Add New Item", key=f"add_{storage_id}", use_container_width=True):
                st.session_state.adding_item = storage_id
                st.rerun()
    
    with col_right:
        # QR code section
        storage_url = f"{app_url}?storage={storage_id}"
        storage_qr = generate_qr_code(storage_url)
        
        if storage_qr:
            st.image(storage_qr, width=120)
            st.caption(f"QR for {storage['name']}")
            
            st.download_button(
                "📥 Download QR",
                storage_qr,
                f"qr_{storage['name'].replace(' ', '_')}.png",
                "image/png",
                key=f"download_{storage_id}",
                use_container_width=True
            )
        
        # Storage quick stats
        st.markdown("---")
        available_count = sum(1 for item in storage['items'] if item['status'] == 'Available')
        st.metric("Available", available_count)
        st.metric("Total", len(storage['items']))

def add_storage_view():
    """View for adding a new storage"""
    st.title("🏗️ Add New Storage")
    
    if st.button("← Back to Dashboard"):
        st.session_state.adding_storage = False
        st.rerun()
    
    st.markdown("---")
    
    with st.form("add_storage_form"):
        name = st.text_input("Storage Name*", placeholder="e.g., Drone Cabinet, Battery Shelf")
        location = st.text_input("Location*", value="Drone Lab AIC")
        storage_type = st.selectbox("Storage Type*", st.session_state.inventory['storage_types'])
        description = st.text_area("Description", placeholder="Optional description of this storage unit")
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("🏗️ Create Storage", type="primary", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if cancel:
            st.session_state.adding_storage = False
            st.rerun()
            
        if submit:
            if name and location and storage_type:
                create_new_storage(name, location, storage_type, description)
                st.session_state.adding_storage = False
                st.success(f"✅ Storage '{name}' created successfully!")
                st.rerun()
            else:
                st.error("Please fill in all required fields (*)")

def edit_storage_view():
    """View for editing storage details - COMPLETELY FIXED"""
    storage_id = st.session_state.editing_storage
    storage = st.session_state.inventory['storages'][storage_id]
    
    st.title("⚙️ Manage Storage")
    
    if st.button("← Back to Dashboard"):
        st.session_state.editing_storage = None
        st.session_state.delete_confirm = None
        st.rerun()
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Storage Details")
        with st.form("edit_storage_form"):
            name = st.text_input("Storage Name*", value=storage['name'])
            location = st.text_input("Location*", value=storage['location'])
            storage_type = st.selectbox("Storage Type*", 
                                      st.session_state.inventory['storage_types'],
                                      index=st.session_state.inventory['storage_types'].index(storage['type']))
            description = st.text_area("Description", 
                                     value=storage.get('description', ''))
            
            col1, col2 = st.columns(2)
            with col1:
                save = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
            with col2:
                cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
            
            if cancel:
                st.session_state.editing_storage = None
                st.rerun()
                
            if save:
                if name and location and storage_type:
                    update_storage(storage_id, name, location, storage_type, description)
                    st.session_state.editing_storage = None
                    st.success(f"✅ Storage '{name}' updated successfully!")
                    st.rerun()
                else:
                    st.error("Please fill in all required fields (*)")
    
    with col2:
        st.subheader("Danger Zone")
        st.warning("This action cannot be undone!")
        
        # DELETE STORAGE BUTTON - COMPLETELY SEPARATE FROM FORM
        if st.session_state.delete_confirm == storage_id:
            st.error(f"🚨 Confirm Deletion")
            st.write(f"Are you sure you want to delete **{storage['name']}**?")
            st.write(f"This will delete **{len(storage['items'])} items** permanently!")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Yes, Delete Forever", type="primary", use_container_width=True):
                    delete_storage(storage_id)
                    st.session_state.delete_confirm = None
                    st.session_state.editing_storage = None
                    st.rerun()
            with col2:
                if st.button("❌ Cancel Deletion", use_container_width=True):
                    st.session_state.delete_confirm = None
                    st.rerun()
        else:
            if st.button("🗑️ Delete This Storage", type="secondary", use_container_width=True, key=f"delete_storage_{storage_id}"):
                st.session_state.delete_confirm = storage_id
                st.rerun()

def add_item_view(storage_id):
    """View for adding a new item"""
    st.title("➕ Add New Item")
    
    storage = st.session_state.inventory['storages'][storage_id]
    st.write(f"**Storage:** {storage['name']}")
    
    if st.button("← Back"):
        st.session_state.adding_item = False
        st.rerun()
    
    st.markdown("---")
    
    with st.form(f"add_item_form_{storage_id}"):
        name = st.text_input("Item Name*", placeholder="e.g., DJI Mavic 3, LiPo Battery")
        quantity = st.text_input("Quantity*", placeholder="e.g., 2 units, 5 packs")
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
    
    if st.button("← Back"):
        st.session_state.editing_item = None
        st.rerun()
    
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

# CRUD Operations for Storages
def create_new_storage(name, location, storage_type, description=""):
    """Create a new storage unit"""
    storage_id = generate_storage_id()
    
    st.session_state.inventory['storages'][storage_id] = {
        'id': storage_id,
        'name': name,
        'location': location,
        'type': storage_type,
        'description': description,
        'items': [],
        'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'created_date': datetime.now().strftime("%Y-%m-%d")
    }

def update_storage(storage_id, name, location, storage_type, description=""):
    """Update storage details"""
    st.session_state.inventory['storages'][storage_id].update({
        'name': name,
        'location': location,
        'type': storage_type,
        'description': description,
        'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })

def delete_storage(storage_id):
    """Delete a storage unit and all its items"""
    storage_name = st.session_state.inventory['storages'][storage_id]['name']
    del st.session_state.inventory['storages'][storage_id]
    st.success(f"✅ Storage '{storage_name}' and all its items deleted successfully!")

# CRUD Operations for Items
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
    """Delete an item - FIXED VERSION"""
    try:
        item_name = st.session_state.inventory['storages'][storage_id]['items'][item_index]['name']
        # Remove the specific item
        del st.session_state.inventory['storages'][storage_id]['items'][item_index]
        # Update timestamp
        st.session_state.inventory['storages'][storage_id]['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.success(f"✅ Item '{item_name}' deleted successfully!")
    except IndexError:
        st.error("❌ Error: Item not found. Please refresh the page.")

# Main application router
def main():
    # Handle different views
    if st.session_state.get('view_mode') == 'all_items':
        all_items_view()
    elif st.session_state.get('editing_storage'):
        edit_storage_view()
    elif st.session_state.get('editing_item'):
        edit_item_view()
    elif st.session_state.get('adding_storage'):
        add_storage_view()
    elif st.session_state.get('adding_item'):
        add_item_view(st.session_state.adding_item)
    else:
        main_dashboard()

if __name__ == "__main__":
    main()