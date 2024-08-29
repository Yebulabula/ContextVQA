import streamlit as st
import plotly.graph_objects as go
import os
import numpy as np
import json
import firebase_admin
from firebase_admin import credentials, firestore
import base64
import random



firebase_credentials = os.getenv('FIREBASE_CREDENTIALS')

if firebase_credentials:
    # Decode the base64 encoded credentials
    cred_json = base64.b64decode(firebase_credentials).decode('utf-8')
    cred_dict = json.loads(cred_json)
    cred = credentials.Certificate(cred_dict)

    # Initialize Firebase app if not already initialized
    if not firebase_admin._apps:
        firebase_admin.initialize_app(cred)

    # Set up Firestore client
    db = firestore.client()

    def export_firestore_collection_to_json(collection_name, output_file):
        # Reference to the Firestore collection
        collection_ref = db.collection(collection_name)
        
        # Get all documents in the collection
        docs = collection_ref.stream()

        # Prepare a dictionary to hold the exported data
        data = {}

        # Iterate over documents and collect data
        for doc in docs:
            data[doc.id] = doc.to_dict()

        # Write data to a JSON file
        with open(output_file, 'w') as f:
            json.dump(data, f, indent=2)

        st.write(f"Data exported to {output_file} successfully.")

    # Example: Export data from 'your-collection-name' to 'output.json'
    collection_name = 'ContextReason'
    output_file = 'output.json'

    export_firestore_collection_to_json(collection_name, output_file)