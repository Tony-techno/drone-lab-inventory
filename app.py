# app.py - PHASE 1: Basic Structure
import streamlit as st

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
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Storage Units", total_storages)
    with col2:
        st.metric("Total Items", total_items)
    
    st.markdown("---")
    
    # Show storages
    st.subheader("Storage Units")
    
    for storage_id, storage in st.session_state.inventory['storages'].items():
        with st.expander(f"📦 {storage['name']} ({len(storage['items'])} items)", expanded=True):
            st.write(f"**Location:** {storage['location']}")
            st.write(f"**Type:** {storage['type']}")
            
            # Show items
            st.write("**Items:**")
            for item in storage['items']:
                st.write(f"- {item['name']} ({item['quantity']}) - {item['status']}")
    
    st.markdown("---")
    st.success("✅ Phase 1 Complete: Basic structure is working!")

if __name__ == "__main__":
    main()