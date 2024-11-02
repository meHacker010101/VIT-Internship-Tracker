import google
import pandas as pd
import hashlib
import streamlit as st
from datetime import datetime
from google.cloud.firestore import SERVER_TIMESTAMP
import json
from google.oauth2 import service_account
from google.cloud import firestore
import google.auth.transport.requests


def initialize_session_state():
    """Initialize all required session state variables"""
    if 'last_update_time' not in st.session_state:
        st.session_state.last_update_time = "No updates yet"
    if 'current_df' not in st.session_state:
        st.session_state.current_df = None
    if 'data_hash' not in st.session_state:
        st.session_state.data_hash = None


def initialize_firestore(credentials_path):
    """
    Initialize Firestore client with credentials
    """
    try:
        SCOPES = [
            'https://www.googleapis.com/auth/cloud-platform',
            'https://www.googleapis.com/auth/datastore'
        ]
        credentials = service_account.Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
        request = google.auth.transport.requests.Request()
        print('Credential Refreshed')
        credentials.refresh(request)
        return firestore.Client(credentials=credentials)
    except Exception as e:
        st.error(f"Error initializing Firestore: {str(e)}")
        return None


def convert_df_to_dict(df):
    """Convert DataFrame to a Firestore-compatible dictionary"""
    return json.loads(df.to_json(orient='records'))


def convert_dict_to_df(data_dict):
    """Convert Firestore dictionary back to DataFrame"""
    return pd.DataFrame(data_dict)


def get_updated_data(google_sheet_url, credentials_path = "intership-tracker-2a091-firebase-adminsdk-kpbyr-6fdcecabfd.json"):
    """
    Check for updates in Google Sheet and store data in Firestore.
    Only updates Firestore when changes are detected.

    Args:
        google_sheet_url (str): URL of the Google Sheet
        credentials_path (str): Path to the Google Cloud credentials JSON file
    """
    # Initialize session state
    initialize_session_state()

    # Initialize Firestore
    db = initialize_firestore(credentials_path)
    if not db:
        st.error("Failed to initialize Firestore. Please check your credentials.")
        return None

    # Get reference to the document that will store our data
    data_doc = db.collection('sheet_data').document('current_data')

    try:
        # Extract sheet ID from URL
        sheet_id = google_sheet_url.split("/")[5]
        csv_export_url = f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=csv"

        # Read and process the new data from Google Sheet
        new_df = pd.read_csv(csv_export_url)
        new_df.columns = new_df.columns.str.strip()
        new_df.columns = new_df.columns.str.lower()
        new_df['branch_code'] = new_df['registration number'].str[2:5].str.upper()
        new_df['stipend'] = pd.to_numeric(new_df['stipend'], errors='coerce')

        # Calculate hash of the new data
        current_hash = hashlib.md5(pd.util.hash_pandas_object(new_df).values.tobytes()).hexdigest()

        # Get the existing data from Firestore
        doc = data_doc.get()

        if doc.exists:
            stored_data = doc.to_dict()
            last_hash = stored_data.get('data_hash')
            st.session_state.last_update_time = stored_data.get('last_update_time', "No updates yet")
        else:
            last_hash = None

        # Check if data has changed
        if current_hash != last_hash:
            # Convert DataFrame to dictionary for Firestore storage
            sheet_data_dict = convert_df_to_dict(new_df)

            # Update Firestore with new data and metadata
            current_time = datetime.now().strftime("%d-%b-%Y %I:%M:%S %p")
            data_doc.set({
                'sheet_data': sheet_data_dict,
                'data_hash': current_hash,
                'last_update_time': current_time,
                'server_timestamp': SERVER_TIMESTAMP
            })

            # Update session state
            st.session_state.current_df = new_df
            st.session_state.data_hash = current_hash
            st.session_state.last_update_time = current_time

            # Show update notification
            st.sidebar.success(f"Data updated at {current_time}")

        # Return the current DataFrame
        return new_df if new_df is not None else st.session_state.current_df

    except Exception as e:
        st.error(f"Error updating data: {str(e)}")

        # Try to return stored data if available
        try:
            doc = data_doc.get()
            if doc.exists:
                stored_data = doc.to_dict()
                return convert_dict_to_df(stored_data.get('sheet_data', []))
        except Exception:
            pass

        return st.session_state.current_df


def display_update_status():
    """Display the last update time in the sidebar"""
    st.sidebar.info(f"Last updated: {st.session_state.last_update_time}")


# Example usage:
def main():
    st.title("Google Sheet Data Tracker")

    # Initialize session state at the start
    initialize_session_state()

    # Set your Google Sheet URL and credentials path
    google_sheet_url = "https://docs.google.com/spreadsheets/d/1ZudQZq_OOMLZr5qojWo9y5UzBhA_BK-neIn15jpZUUo/edit?usp=sharing"
    credentials_path = "intership-tracker-2a091-firebase-adminsdk-kpbyr-6fdcecabfd.json"

    # Get the data
    df = get_updated_data(google_sheet_url, credentials_path)

    if df is not None:
        # Display the data
        st.dataframe(df)

        # Display update status
        display_update_status()


if __name__ == "__main__":
    main()