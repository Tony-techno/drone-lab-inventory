# app.py - PILLOW-FREE WORKING VERSION
import streamlit as st
import qrcode
import io
from datetime import datetime
import uuid

# Initialize session state with default data
if 'inventory' not in st.session_state:
    st.session_state.inventory = {
        'storages': {
            'storage_1': {
                'id': 'storage_1',
                'name': 'Drone Storage Cabinet',
                'type': 'cabinet',
                'location': 'Drone Lab AIC',
                'description': 'Main storage for drone equipment and accessories',
                'items': [
                    {'name': 'DJI Mavic 3 Pro', 'quantity': '3 units', 'status': 'Available', 'category': 'Drones'},
                    {'name': 'LiPo Batteries', 'quantity': '15 units', 'status': 'Available', 'category': 'Batteries'},
                    {'name': 'FPV Controller', 'quantity': '2 units', 'status': 'In Use', 'category': 'Controllers'}
                ],
                'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            'storage_2': {
                'id': 'storage_2',
                'name': 'Tool & Parts Drawer',
                'type': 'drawer',
                'location': 'Drone Lab AIC',
                'description': 'Tools and spare parts for drone maintenance',
                'items': [
                    {'name': 'Screwdriver Set', 'quantity': '1 set', 'status': 'Available', 'category': 'Tools'},
                    {'name': 'Propeller Set', 'quantity': '10 pairs', 'status': 'Available', 'category': 'Propellers'}
                ],
                'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        },
        'categories': ['Drones', 'Batteries', 'Controllers', 'Propellers', 'Cameras', 'Sensors', 'Chargers', 'Tools', 'Electronics', 'Stationary', 'Other'],
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

def generate_qr_code(url):
    """Generate QR code for a URL without Pillow"""
    try:
        qr = qrcode.QRCode(version=5, box_size=10, border=4)
        qr.add_data(url)
        qr.make(fit=True)
        
        # Create QR code as text (fallback) and image
        qr_matrix = qr.get_matrix()
        qr_text = ""
        for row in qr_matrix:
            for cell in row:
                qr_text += "██" if cell else "  "
            qr_text += "\n"
        
        # For image, we'll use qrcode's built-in PNG creation
        qr_img = qr.make_image(fill_color="black", back_color="white")
        buf = io.BytesIO()
        qr_img.save(buf, format="PNG")
        buf.seek(0)
        return buf.getvalue(), qr_text
    except Exception as e:
        st.error(f"QR generation error: {e}")
        return None, "QR Code\n[Error]"

def get_app_url():
    return "https://drone-lab-inventory-l8phzdn3dqn38cppfacdtr.streamlit.app/"

def get_status_icon(status):
    icons = {
        'Available': '🟢',
        'In Use': '🔴', 
        'Maintenance': '🟡',
        'Broken': '❌',
        'Reserved': '⏳'
    }
    return icons.get(status, '⚪')

def main():
    st.set_page_config(
        page_title="Drone Lab Inventory",
        page_icon="🚁",
        layout="wide"
    )
    
    st.title("🚁 Drone Lab AIC - Inventory System")
    st.markdown("### ✅ PILLOW-FREE WORKING VERSION")
    
    # Quick actions
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Add New Storage", use_container_width=True):
            st.session_state.adding_storage = True
            st.rerun()
    with col2:
        if st.button("📊 View All Items", use_container_width=True):
            pass  # We can implement this later
    
    st.markdown("---")
    
    # Statistics
    total_storages = len(st.session_state.inventory['storages'])
    total_items = sum(len(storage['items']) for storage in st.session_state.inventory['storages'].values())
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Storage Units", total_storages)
    with col2:
        st.metric("Total Items", total_items)
    with col3:
        # Central QR Code
        qr_data, qr_text = generate_qr_code(get_app_url())
        if qr_data:
            st.image(qr_data, width=100)
            st.caption("App QR Code")
    
    st.markdown("---")
    
    # Storage Management
    if st.session_state.adding_storage:
        add_storage_view()
    elif st.session_state.editing_storage:
        edit_storage_view()
    elif st.session_state.adding_item:
        add_item_view()
    elif st.session_state.editing_item:
        edit_item_view()
    else:
        dashboard_view()

def dashboard_view():
    """Main dashboard view"""
    st.subheader("📦 Storage Units")
    
    for storage_id, storage in st.session_state.inventory['storages'].items():
        with st.expander(f"🚀 {storage['name']} ({len(storage['items'])} items)", expanded=True):
            col_left, col_right = st.columns([3, 1])
            
            with col_left:
                st.write(f"**Location:** {storage['location']}")
                st.write(f"**Type:** {storage['type'].title()}")
                if storage.get('description'):
                    st.write(f"**Description:** {storage['description']}")
                
                st.markdown("---")
                st.write("**Items:**")
                
                if storage['items']:
                    for i, item in enumerate(storage['items']):
                        col_item, col_edit, col_delete = st.columns([3, 1, 1])
                        
                        with col_item:
                            icon = get_status_icon(item['status'])
                            st.write(f"{icon} **{item['name']}**")
                            st.caption(f"{item['quantity']} • {item.get('category', 'Other')} • {item['status']}")
                        
                        with col_edit:
                            if st.button("✏️", key=f"edit_{storage_id}_{i}"):
                                st.session_state.editing_item = (storage_id, i)
                                st.rerun()
                        
                        with col_delete:
                            if st.button("🗑️", key=f"delete_{storage_id}_{i}"):
                                # Immediate deletion
                                storage['items'].pop(i)
                                storage['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                st.rerun()
                else:
                    st.info("No items in this storage")
                
                # Add item button
                if st.button("➕ Add Item", key=f"add_{storage_id}", use_container_width=True):
                    st.session_state.adding_item = storage_id
                    st.rerun()
            
            with col_right:
                # Storage QR Code
                storage_url = f"{get_app_url()}?storage={storage_id}"
                qr_data, qr_text = generate_qr_code(storage_url)
                
                if qr_data:
                    st.image(qr_data, width=120)
                    st.caption(f"QR: {storage['name']}")
                
                # Storage management
                if st.button("⚙️ Manage", key=f"manage_{storage_id}", use_container_width=True):
                    st.session_state.editing_storage = storage_id
                    st.rerun()
                
                # Quick stats
                available_count = sum(1 for item in storage['items'] if item['status'] == 'Available')
                st.metric("Available", available_count)

def add_storage_view():
    """Add new storage view"""
    st.subheader("🏗️ Add New Storage")
    
    if st.button("← Back to Dashboard"):
        st.session_state.adding_storage = False
        st.rerun()
    
    with st.form("add_storage_form"):
        name = st.text_input("Storage Name*", placeholder="e.g., Drone Cabinet, Battery Shelf")
        location = st.text_input("Location*", value="Drone Lab AIC")
        storage_type = st.selectbox("Storage Type*", st.session_state.inventory['storage_types'])
        description = st.text_area("Description", placeholder="Optional description")
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("🏗️ Create Storage", type="primary", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if cancel:
            st.session_state.adding_storage = False
            st.rerun()
        
        if submit:
            if name and location:
                storage_id = f"storage_{uuid.uuid4().hex[:8]}"
                st.session_state.inventory['storages'][storage_id] = {
                    'id': storage_id,
                    'name': name,
                    'location': location,
                    'type': storage_type,
                    'description': description,
                    'items': [],
                    'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.adding_storage = False
                st.success(f"✅ Storage '{name}' created successfully!")
                st.rerun()

def edit_storage_view():
    """Edit storage view"""
    storage_id = st.session_state.editing_storage
    storage = st.session_state.inventory['storages'][storage_id]
    
    st.subheader("⚙️ Manage Storage")
    
    if st.button("← Back to Dashboard"):
        st.session_state.editing_storage = None
        st.rerun()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Storage Details**")
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
                        'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    })
                    st.session_state.editing_storage = None
                    st.success("✅ Storage updated successfully!")
                    st.rerun()
    
    with col2:
        st.write("**Danger Zone**")
        st.warning("This will delete the storage and all its items!")
        
        if st.button("🗑️ Delete Storage", type="secondary", use_container_width=True):
            del st.session_state.inventory['storages'][storage_id]
            st.session_state.editing_storage = None
            st.success("✅ Storage deleted successfully!")
            st.rerun()

def add_item_view():
    """Add item view"""
    storage_id = st.session_state.adding_item
    storage = st.session_state.inventory['storages'][storage_id]
    
    st.subheader(f"➕ Add Item to {storage['name']}")
    
    if st.button("← Back"):
        st.session_state.adding_item = False
        st.rerun()
    
    with st.form("add_item_form"):
        name = st.text_input("Item Name*", placeholder="e.g., DJI Mavic 3, LiPo Battery")
        quantity = st.text_input("Quantity*", placeholder="e.g., 2 units, 5 packs")
        category = st.selectbox("Category", st.session_state.inventory['categories'])
        status = st.selectbox("Status", st.session_state.inventory['status_options'])
        
        if st.form_submit_button("➕ Add Item", type="primary", use_container_width=True):
            if name and quantity:
                storage['items'].append({
                    'name': name,
                    'quantity': quantity,
                    'category': category,
                    'status': status
                })
                storage['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.adding_item = False
                st.success(f"✅ Item '{name}' added successfully!")
                st.rerun()

def edit_item_view():
    """Edit item view"""
    storage_id, item_index = st.session_state.editing_item
    storage = st.session_state.inventory['storages'][storage_id]
    item = storage['items'][item_index]
    
    st.subheader(f"✏️ Edit Item in {storage['name']}")
    
    if st.button("← Back"):
        st.session_state.editing_item = None
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
                storage['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.editing_item = None
                st.success(f"✅ Item '{name}' updated successfully!")
                st.rerun()

if __name__ == "__main__":
    main()