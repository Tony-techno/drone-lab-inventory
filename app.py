# app.py - DRONE LAB INVENTORY MANAGEMENT SYSTEM
import streamlit as st
import qrcode
import io
import json
from datetime import datetime
import pandas as pd
import base64
import uuid

# Page configuration
st.set_page_config(
    page_title="Drone Lab Inventory",
    page_icon="🚁",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize session state for inventory data
if 'inventory' not in st.session_state:
    st.session_state.inventory = {
        'storages': {},
        'categories': [
            'Drone', 'Battery', 'Propeller', 'Camera', 'Controller', 
            'Sensor', 'Electronic', 'Tool', 'Safety', 'Consumable'
        ],
        'status_options': ['Available', 'In Use', 'Maintenance', 'Charging', 'Broken', 'Reserved'],
        'storage_types': ['hangar', 'charging_station', 'tool_cabinet', 'shelf', 'locker', 'workbench'],
        'drone_types': ['Quadcopter', 'Hexacopter', 'Octocopter', 'Fixed Wing', 'Hybrid', 'Mini Drone']
    }

# Initialize form states
if 'last_added_item' not in st.session_state:
    st.session_state.last_added_item = None
if 'last_added_storage' not in st.session_state:
    st.session_state.last_added_storage = None

def generate_qr_code(url):
    """Generate QR code safely"""
    try:
        qr = qrcode.QRCode(
            version=8,
            error_correction=qrcode.constants.ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(url)
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
    """Get the current app URL - UPDATE WITH YOUR ACTUAL URL"""
    return "https://drone-lab-inventory.streamlit.app/"

def get_storage_icon(storage_type):
    """Get icon for storage type"""
    icons = {
        'hangar': '🚁',
        'charging_station': '🔋', 
        'tool_cabinet': '🧰',
        'shelf': '📚',
        'locker': '🔒',
        'workbench': '🛠️'
    }
    return icons.get(storage_type, '📦')

def get_status_icon(status):
    """Get icon for item status"""
    icons = {
        'Available': '🟢',
        'In Use': '🔴', 
        'Maintenance': '🟡',
        'Charging': '🔋',
        'Broken': '❌',
        'Reserved': '⏳'
    }
    return icons.get(status, '⚪')

def get_status_color(status):
    """Get color for status"""
    colors = {
        'Available': 'green',
        'In Use': 'red',
        'Maintenance': 'orange',
        'Charging': 'blue', 
        'Broken': 'gray',
        'Reserved': 'yellow'
    }
    return colors.get(status, 'gray')

def display_qr_with_download(qr_data, filename, caption, width=150):
    """Display QR code with download button"""
    if qr_data:
        col1, col2 = st.columns([2, 1])
        with col1:
            st.image(qr_data, width=width, caption=caption)
        with col2:
            st.download_button(
                "📥 Download",
                qr_data,
                filename,
                "image/png",
                use_container_width=True,
                key=f"dl_{uuid.uuid4()}"
            )
        return True
    return False

def main_dashboard():
    """Central dashboard"""
    st.title("🚁 Drone Lab Inventory Management System")
    st.markdown("---")
    
    app_url = get_app_url()
    
    # Quick stats
    total_storages = len(st.session_state.inventory['storages'])
    total_items = sum(len(storage['items']) for storage in st.session_state.inventory['storages'].values())
    items_in_use = sum(1 for storage in st.session_state.inventory['storages'].values() 
                      for item in storage['items'] if item['status'] == 'In Use')
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("🏠 Storage Units", total_storages)
    with col2:
        st.metric("📦 Total Items", total_items)
    with col3:
        st.metric("🔴 In Use", items_in_use)
    with col4:
        central_qr = generate_qr_code(app_url)
        if central_qr:
            st.image(central_qr, width=100)
            st.caption("Central QR")
    
    st.markdown("---")
    
    # Main content
    if not st.session_state.inventory['storages']:
        show_empty_state()
    else:
        show_storages_grid(app_url)

def show_empty_state():
    """Show empty state with setup options"""
    st.info("🏗️ Welcome to Drone Lab Inventory! Let's set up your first storage unit.")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.subheader("Quick Setup Options")
        
        # Pre-defined storage templates for drone lab
        templates = {
            "Drone Hangar": {"type": "hangar", "location": "Main Lab", "description": "Primary drone storage and maintenance"},
            "Charging Station": {"type": "charging_station", "location": "Charging Area", "description": "Battery charging and storage"},
            "Tool Cabinet": {"type": "tool_cabinet", "location": "Workbench", "description": "Tools and maintenance equipment"},
            "Sensor Shelf": {"type": "shelf", "location": "Sensor Lab", "description": "Camera and sensor storage"}
        }
        
        for name, template in templates.items():
            if st.button(f"➕ Create {name}", key=f"template_{name}", use_container_width=True):
                create_storage_from_template(name, template)
                st.rerun()

def create_storage_from_template(name, template):
    """Create storage from template"""
    storage_id = f"{template['type']}_{name.lower().replace(' ', '_')}"
    
    st.session_state.inventory['storages'][storage_id] = {
        'name': name,
        'type': template['type'],
        'location': template['location'],
        'description': template['description'],
        'items': [],
        'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    
    # Add sample items based on storage type
    if template['type'] == 'hangar':
        st.session_state.inventory['storages'][storage_id]['items'] = [
            {'id': 'DRONE_001', 'name': 'DJI Phantom 4', 'quantity': '1 unit', 'category': 'Drone', 'status': 'Available', 'specs': '4K Camera, 30min flight'},
            {'id': 'BATT_001', 'name': 'LiPo Battery 5000mAh', 'quantity': '3 units', 'category': 'Battery', 'status': 'Charging', 'specs': '4S, 14.8V'}
        ]
    elif template['type'] == 'charging_station':
        st.session_state.inventory['storages'][storage_id]['items'] = [
            {'id': 'CHARGER_001', 'name': 'Smart Charger', 'quantity': '2 units', 'category': 'Electronic', 'status': 'Available', 'specs': '200W, Balance Charger'},
            {'id': 'BATT_002', 'name': 'Spare Batteries', 'quantity': '6 units', 'category': 'Battery', 'status': 'Charging', 'specs': 'Various capacities'}
        ]
    
    st.success(f"✅ {name} created with sample items!")

def show_storages_grid(app_url):
    """Show all storages in a grid"""
    col_left, col_right = st.columns([3, 1])
    
    with col_left:
        st.subheader("📊 Storage Overview")
        
        for storage_id, storage in st.session_state.inventory['storages'].items():
            with st.container():
                show_storage_card(storage_id, storage, app_url)
    
    with col_right:
        show_quick_actions(app_url)

def show_storage_card(storage_id, storage, app_url):
    """Display storage card"""
    col1, col2, col3 = st.columns([3, 1, 1])
    
    with col1:
        icon = get_storage_icon(storage['type'])
        st.write(f"### {icon} {storage['name']}")
        st.write(f"**Location:** {storage['location']} | **Type:** {storage['type'].replace('_', ' ').title()}")
        st.write(f"**Items:** {len(storage['items'])} | **Updated:** {storage['last_updated']}")
        if storage.get('description'):
            st.write(f"*{storage['description']}*")
    
    with col2:
        # QR code for this storage
        storage_url = f"{app_url}?storage={storage_id}"
        qr_data = generate_qr_code(storage_url)
        display_qr_with_download(qr_data, f"qr_{storage_id}.png", f"QR for {storage['name']}", 120)
    
    with col3:
        if st.button("📋 View", key=f"view_{storage_id}", use_container_width=True):
            st.session_state.current_storage = storage_id
            st.rerun()
        
        if st.button("🗑️", key=f"delete_{storage_id}", use_container_width=True):
            st.session_state.storage_to_delete = storage_id
            st.rerun()
    
    # Items preview
    if storage['items']:
        with st.expander(f"📦 Quick View ({len(storage['items'])} items)", expanded=False):
            for item in storage['items'][:4]:
                status_icon = get_status_icon(item['status'])
                st.write(f"{status_icon} **{item['name']}** - {item['quantity']}")
            if len(storage['items']) > 4:
                st.write(f"*... and {len(storage['items']) - 4} more items*")
    
    st.markdown("---")

def show_quick_actions(app_url):
    """Show quick actions sidebar"""
    st.subheader("🎯 Quick Actions")
    
    # Central QR download
    central_qr = generate_qr_code(app_url)
    if central_qr:
        st.download_button(
            "📥 Central QR",
            central_qr,
            "qr_central.png",
            "image/png",
            use_container_width=True
        )
    
    if st.button("➕ New Storage", use_container_width=True, type="primary"):
        st.session_state.show_add_storage = True
        st.rerun()
    
    if st.button("📊 Analytics", use_container_width=True):
        st.session_state.show_analytics = True
        st.rerun()
    
    if st.button("⚙️ Settings", use_container_width=True):
        st.session_state.show_settings = True
        st.rerun()
    
    st.markdown("---")
    
    # Quick search
    st.subheader("🔍 Quick Search")
    search_term = st.text_input("Search items...", key="main_search")
    if search_term:
        show_search_results(search_term)
    
    # System stats
    show_system_stats()

def show_search_results(search_term):
    """Show search results"""
    results = []
    search_lower = search_term.lower()
    
    for storage_id, storage in st.session_state.inventory['storages'].items():
        for item in storage['items']:
            if (search_lower in item['name'].lower() or 
                search_lower in item.get('category', '').lower() or
                search_lower in item.get('specs', '').lower()):
                results.append({'storage': storage, 'item': item, 'storage_id': storage_id})
    
    if results:
        st.write(f"**Found {len(results)} items:**")
        for result in results[:5]:
            status_icon = get_status_icon(result['item']['status'])
            st.write(f"{status_icon} **{result['item']['name']}** in {result['storage']['name']}")
    else:
        st.info("No items found")

def show_system_stats():
    """Show system statistics"""
    total_items = sum(len(storage['items']) for storage in st.session_state.inventory['storages'].values())
    
    if total_items > 0:
        st.subheader("📈 System Stats")
        
        # Status distribution
        status_count = {status: 0 for status in st.session_state.inventory['status_options']}
        category_count = {category: 0 for category in st.session_state.inventory['categories']}
        
        for storage in st.session_state.inventory['storages'].values():
            for item in storage['items']:
                status_count[item['status']] += 1
                category_count[item['category']] += 1
        
        st.write("**By Status:**")
        for status, count in status_count.items():
            if count > 0:
                st.write(f"{get_status_icon(status)} {status}: {count}")
        
        st.write("**By Category:**")
        for category, count in category_count.items():
            if count > 0:
                st.write(f"• {category}: {count}")

def storage_detail_view(storage_id):
    """Detailed view for a specific storage"""
    if storage_id not in st.session_state.inventory['storages']:
        st.error("Storage not found!")
        st.session_state.current_storage = None
        st.rerun()
        return
    
    storage = st.session_state.inventory['storages'][storage_id]
    
    # Custom CSS for clean view
    st.markdown("""
        <style>
            [data-testid="stSidebar"] {display: none;}
            .main > div {padding: 1rem;}
        </style>
    """, unsafe_allow_html=True)
    
    # Header
    col1, col2 = st.columns([3, 1])
    
    with col1:
        icon = get_storage_icon(storage['type'])
        st.title(f"{icon} {storage['name']}")
        st.write(f"**Type:** {storage['type'].replace('_', ' ').title()} | **Location:** {storage['location']}")
        if storage.get('description'):
            st.write(f"**Description:** {storage['description']}")
        st.write(f"**Last Updated:** {storage['last_updated']}")
    
    with col2:
        app_url = get_app_url()
        
        # Storage QR
        storage_url = f"{app_url}?storage={storage_id}"
        qr_data = generate_qr_code(storage_url)
        display_qr_with_download(qr_data, f"qr_{storage_id}.png", "Storage QR", 150)
        
        # Navigation
        st.markdown("---")
        if st.button("🏠 Back to Dashboard", use_container_width=True):
            st.session_state.current_storage = None
            st.rerun()
        
        if st.button("✏️ Edit Storage", use_container_width=True):
            st.session_state.editing_storage = storage_id
            st.rerun()
    
    st.markdown("---")
    
    # Items management
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        show_items_management(storage_id, storage)
    
    with col_right:
        show_add_item_form(storage_id)
        show_storage_analytics(storage)

def show_items_management(storage_id, storage):
    """Show items management section"""
    st.subheader("📋 Inventory Items")
    
    if not storage['items']:
        st.info("This storage is empty. Add some items to get started!")
        return
    
    # Items table view
    for i, item in enumerate(storage['items']):
        with st.container():
            col1, col2, col3 = st.columns([3, 1, 1])
            
            with col1:
                status_icon = get_status_icon(item['status'])
                st.write(f"### {status_icon} {item['name']}")
                st.write(f"**ID:** {item['id']} | **Category:** {item['category']}")
                st.write(f"**Quantity:** {item['quantity']} | **Status:** {item['status']}")
                if item.get('specs'):
                    st.write(f"*{item['specs']}*")
                if item.get('notes'):
                    st.write(f"📝 {item['notes']}")
            
            with col2:
                if st.button("✏️ Edit", key=f"edit_{storage_id}_{i}", use_container_width=True):
                    st.session_state.editing_item = (storage_id, i)
                    st.rerun()
            
            with col3:
                if st.button("🗑️ Delete", key=f"delete_{storage_id}_{i}", use_container_width=True):
                    delete_item(storage_id, i)
                    st.rerun()
            
            st.markdown("---")

def show_add_item_form(storage_id):
    """Show add item form - FIXED to prevent continuous adding"""
    st.subheader("➕ Add New Item")
    
    # Use session state to track form submission
    form_key = f"add_form_{storage_id}"
    if form_key not in st.session_state:
        st.session_state[form_key] = {'submitted': False}
    
    with st.form(form_key, clear_on_submit=True):
        item_name = st.text_input("Item Name*", placeholder="e.g., DJI Mavic 3")
        quantity = st.text_input("Quantity*", placeholder="e.g., 1 unit, 5000mAh")
        category = st.selectbox("Category*", st.session_state.inventory['categories'])
        status = st.selectbox("Status*", st.session_state.inventory['status_options'])
        specs = st.text_input("Specifications", placeholder="e.g., 4K, 30min flight")
        notes = st.text_area("Notes", placeholder="Additional information...")
        
        submitted = st.form_submit_button("➕ Add Item", type="primary", use_container_width=True)
        
        if submitted:
            if item_name and quantity and category and status:
                # Add the item
                add_item_to_storage(storage_id, item_name, quantity, category, status, specs, notes)
                # Set form state to prevent immediate re-adding
                st.session_state[form_key]['submitted'] = True
                st.rerun()
            else:
                st.error("Please fill in all required fields (*)")
    
    # Show storage analytics
    show_storage_analytics(st.session_state.inventory['storages'][storage_id])

def show_storage_analytics(storage):
    """Show storage analytics"""
    st.subheader("📊 Storage Analytics")
    
    if storage['items']:
        status_count = {status: 0 for status in st.session_state.inventory['status_options']}
        for item in storage['items']:
            status_count[item['status']] += 1
        
        st.write("**Items by Status:**")
        for status, count in status_count.items():
            if count > 0:
                color = get_status_color(status)
                st.markdown(f"<span style='color: {color}'>{get_status_icon(status)} {status}: {count}</span>", 
                           unsafe_allow_html=True)
        
        # Quick actions based on status
        if status_count['Maintenance'] > 0:
            st.warning(f"⚠️ {status_count['Maintenance']} items need maintenance")
        if status_count['Broken'] > 0:
            st.error(f"❌ {status_count['Broken']} items are broken")

def add_storage_view():
    """View for adding new storage"""
    st.title("➕ Add New Storage")
    
    with st.form("add_storage_form", clear_on_submit=True):
        name = st.text_input("Storage Name*", placeholder="e.g., Main Drone Hangar")
        storage_type = st.selectbox("Storage Type*", st.session_state.inventory['storage_types'], 
                                   format_func=lambda x: x.replace('_', ' ').title())
        location = st.text_input("Location*", placeholder="e.g., Lab Room A1")
        description = st.text_area("Description", placeholder="Storage purpose and details...")
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("➕ Create Storage", type="primary", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if cancel:
            st.session_state.show_add_storage = False
            st.rerun()
            
        if submit:
            if name and storage_type and location:
                add_new_storage(name, storage_type, location, description)
                st.session_state.show_add_storage = False
                st.rerun()
            else:
                st.error("Please fill in all required fields (*)")

def edit_item_view(storage_id, item_index):
    """View for editing an item"""
    item = st.session_state.inventory['storages'][storage_id]['items'][item_index]
    storage_name = st.session_state.inventory['storages'][storage_id]['name']
    
    st.title(f"✏️ Edit Item - {storage_name}")
    
    with st.form("edit_item_form", clear_on_submit=False):
        name = st.text_input("Item Name*", value=item['name'])
        quantity = st.text_input("Quantity*", value=item['quantity'])
        category = st.selectbox("Category*", st.session_state.inventory['categories'],
                               index=st.session_state.inventory['categories'].index(item['category']))
        status = st.selectbox("Status*", st.session_state.inventory['status_options'],
                             index=st.session_state.inventory['status_options'].index(item['status']))
        specs = st.text_input("Specifications", value=item.get('specs', ''))
        notes = st.text_area("Notes", value=item.get('notes', ''))
        
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
                update_item(storage_id, item_index, name, quantity, category, status, specs, notes)
                st.session_state.editing_item = None
                st.rerun()

# Core CRUD Operations
def add_new_storage(name, storage_type, location, description=""):
    """Add a new storage"""
    storage_id = f"{storage_type}_{name.lower().replace(' ', '_')}"
    
    st.session_state.inventory['storages'][storage_id] = {
        'name': name,
        'type': storage_type,
        'location': location,
        'description': description,
        'items': [],
        'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.success(f"✅ Storage '{name}' created successfully!")

def add_item_to_storage(storage_id, name, quantity, category, status, specs="", notes=""):
    """Add item to storage - FIXED to prevent duplicates"""
    item_id = f"{category[:3].upper()}_{len(st.session_state.inventory['storages'][storage_id]['items']) + 1:03d}"
    
    st.session_state.inventory['storages'][storage_id]['items'].append({
        'id': item_id,
        'name': name,
        'quantity': quantity,
        'category': category,
        'status': status,
        'specs': specs,
        'notes': notes
    })
    
    st.session_state.inventory['storages'][storage_id]['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.success(f"✅ Item '{name}' added to inventory!")

def update_item(storage_id, item_index, name, quantity, category, status, specs="", notes=""):
    """Update item details"""
    st.session_state.inventory['storages'][storage_id]['items'][item_index].update({
        'name': name,
        'quantity': quantity,
        'category': category,
        'status': status,
        'specs': specs,
        'notes': notes
    })
    
    st.session_state.inventory['storages'][storage_id]['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.success(f"✅ Item '{name}' updated successfully!")

def delete_item(storage_id, item_index):
    """Delete an item"""
    item_name = st.session_state.inventory['storages'][storage_id]['items'][item_index]['name']
    del st.session_state.inventory['storages'][storage_id]['items'][item_index]
    st.session_state.inventory['storages'][storage_id]['last_updated'] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.success(f"✅ Item '{item_name}' deleted successfully!")

# Main app routing
def main():
    try:
        # Handle different views
        if hasattr(st.session_state, 'storage_to_delete') and st.session_state.storage_to_delete:
            show_delete_confirmation()
            return
            
        if hasattr(st.session_state, 'show_add_storage') and st.session_state.show_add_storage:
            add_storage_view()
            return
            
        if hasattr(st.session_state, 'editing_storage') and st.session_state.editing_storage:
            edit_storage_view(st.session_state.editing_storage)
            return
            
        if hasattr(st.session_state, 'editing_item') and st.session_state.editing_item:
            storage_id, item_index = st.session_state.editing_item
            edit_item_view(storage_id, item_index)
            return
        
        # Check URL parameters for direct storage access
        query_params = st.experimental_get_query_params()
        if 'storage' in query_params:
            storage_id = query_params['storage'][0]
            if storage_id in st.session_state.inventory['storages']:
                storage_detail_view(storage_id)
                return
        
        # Check session state for storage view
        if hasattr(st.session_state, 'current_storage') and st.session_state.current_storage:
            storage_detail_view(st.session_state.current_storage)
            return
        
        # Default to main dashboard
        main_dashboard()
        
    except Exception as e:
        st.error(f"System error: {str(e)}")
        st.info("Please refresh the page and try again.")
        main_dashboard()

def show_delete_confirmation():
    """Show delete confirmation"""
    storage_id = st.session_state.storage_to_delete
    storage = st.session_state.inventory['storages'][storage_id]
    
    st.title("🗑️ Confirm Deletion")
    st.error(f"⚠️ You are about to delete: **{storage['name']}**")
    st.warning(f"This will remove {len(storage['items'])} items permanently!")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Confirm Delete", type="primary", use_container_width=True):
            del st.session_state.inventory['storages'][storage_id]
            st.session_state.storage_to_delete = None
            st.session_state.current_storage = None
            st.success("Storage deleted successfully!")
            st.rerun()
    with col2:
        if st.button("❌ Cancel", use_container_width=True):
            st.session_state.storage_to_delete = None
            st.rerun()

def edit_storage_view(storage_id):
    """Edit storage details"""
    storage = st.session_state.inventory['storages'][storage_id]
    
    st.title(f"✏️ Edit Storage: {storage['name']}")
    
    with st.form("edit_storage_form"):
        name = st.text_input("Storage Name*", value=storage['name'])
        storage_type = st.selectbox("Storage Type*", st.session_state.inventory['storage_types'],
                                   index=st.session_state.inventory['storage_types'].index(storage['type']),
                                   format_func=lambda x: x.replace('_', ' ').title())
        location = st.text_input("Location*", value=storage['location'])
        description = st.text_area("Description", value=storage.get('description', ''))
        
        col1, col2 = st.columns(2)
        with col1:
            submit = st.form_submit_button("💾 Save Changes", type="primary", use_container_width=True)
        with col2:
            cancel = st.form_submit_button("❌ Cancel", use_container_width=True)
        
        if cancel:
            st.session_state.editing_storage = None
            st.rerun()
            
        if submit:
            if name and storage_type and location:
                update_storage(storage_id, name, storage_type, location, description)
                st.session_state.editing_storage = None
                st.rerun()

def update_storage(storage_id, name, storage_type, location, description=""):
    """Update storage details"""
    st.session_state.inventory['storages'][storage_id].update({
        'name': name,
        'type': storage_type,
        'location': location,
        'description': description,
        'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    st.success(f"✅ Storage '{name}' updated successfully!")

if __name__ == "__main__":
    main()