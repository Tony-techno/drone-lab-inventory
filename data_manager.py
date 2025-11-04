# data_manager.py - Data persistence system
import json
import os
import streamlit as st
from datetime import datetime
import uuid

DATA_FILE = "inventory_data.json"

def load_inventory():
    """Load inventory from JSON file"""
    try:
        if os.path.exists(DATA_FILE):
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        else:
            return get_default_inventory()
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return get_default_inventory()

def save_inventory(inventory):
    """Save inventory to JSON file"""
    try:
        with open(DATA_FILE, 'w') as f:
            json.dump(inventory, f, indent=2)
        return True
    except Exception as e:
        st.error(f"Error saving data: {e}")
        return False

def get_default_inventory():
    """Return default inventory structure"""
    return {
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
                'last_updated': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'created_date': datetime.now().strftime("%Y-%m-%d")
            }
        },
        'categories': [
            'Drones', 'Batteries', 'Controllers', 'Propellers', 'Cameras', 
            'Sensors', 'Chargers', 'Tools', 'Electronics', 'Stationary', 'Other'
        ],
        'status_options': ['Available', 'In Use', 'Maintenance', 'Broken', 'Reserved'],
        'storage_types': ['shelf', 'cabinet', 'drawer', 'rack', 'storage_room', 'toolbox', 'other']
    }

def generate_storage_id():
    """Generate unique storage ID"""
    return f"storage_{uuid.uuid4().hex[:8]}"