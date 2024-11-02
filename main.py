import webbrowser

from debugpy.adapter import components

from tabs import *
from emailVerification import *
from datetime import datetime
import time
from database import get_updated_data


google_sheet_url = "https://docs.google.com/spreadsheets/d/1ZudQZq_OOMLZr5qojWo9y5UzBhA_BK-neIn15jpZUUo/edit?usp=sharing"

previous_update = time.time()
if 'last_login_time' not in st.session_state:
    st.session_state.last_login_time = None
if 'last_update_time' not in st.session_state:
    st.session_state.last_update_time = None


def add_feedback_button():
    feedback_url = "https://forms.gle/FqewDcoaZx7cSeyX7"

    # Use st.markdown with a hyperlink instead of webbrowser
    st.sidebar.markdown(f"""
    <a href="{feedback_url}" target="_blank" style="
        display: inline-block;
        width: 100%;
        padding: 12px 20px;
        background: rgba(74, 144, 226, 0.1);
        color: white;
        border: 1px solid rgba(74, 144, 226, 0.3);
        border-radius: 10px;
        text-align: center;
        text-decoration: none;
        transition: all 0.3s ease;
    " onmouseover="this.style.background='rgba(74, 144, 226, 0.2)'" 
       onmouseout="this.style.background='rgba(74, 144, 226, 0.1)'">
    ⚠️ Report Issues
    </a>
    """, unsafe_allow_html=True)


# Alternative method using JavaScript if needed
def add_feedback_button_js():
    feedback_url = "https://forms.gle/FqewDcoaZx7cSeyX7"

    components.html(f"""
    <script>
        function openFeedbackForm() {{
            window.open('{feedback_url}', '_blank');
        }}
    </script>
    <button onclick="openFeedbackForm()" style="
        width: 100%;
        padding: 12px 20px;
        background: rgba(74, 144, 226, 0.1);
        color: white;
        border: 1px solid rgba(74, 144, 226, 0.3);
        border-radius: 10px;
        transition: all 0.3s ease;
    ">
    ⚠ Report Issues
    </button>
    """, height=50)


st.markdown("""
    <style>
    /* Hide GitHub link and footer */
    #MainMenu {display: none;}
    footer {display: none;}

    /* Hide profile elements */
    .css-1v3fvcr > div:last-child {
        display: none;
    }

    /* Hide viewer badge */
    .viewerBadge_container__1QSob,
    .viewerBadge_link__1S137,
    .viewerBadge_text__1JaDK {
        display: none !important;
    }

    /* Hide deployment info */
    .stDeployButton {
        display: none !important;
    }

    /* Hide all footer elements */
    footer[data-testid="stFooter"] {
        display: none;
    }

    /* Hide profile elements */
    section[data-testid="stSidebar"] .css-1q1n0ol {
        display: none;
    }

    /* Additional selectors to hide GitHub-related elements */
    .st-emotion-cache-1wbqy5l,
    .st-emotion-cache-h5rgaw,
    .st-emotion-cache-1w51zti {
        display: none !important;
    }

    /* Hide "Made with Streamlit" footer */
    .st-emotion-cache-164nlkn {
        display: none !important;
    }

    /* Hide GitHub icon and related elements */
    .st-emotion-cache-1l4w6pd,
    .st-emotion-cache-1p1nwyz {
        display: none !important;
    }
    </style>
""", unsafe_allow_html=True)

# STREAMLIT INTERFACE
st.title("VIT - Internship Tracker")



# Your existing styling code
st.markdown("""
    <style>
        .st-emotion-cache-1wqrzgl {  
            min-width: 400px;
            max-width: 450px;
        }
        /* Rest of your CSS styles */
    </style>
""", unsafe_allow_html=True)


# Disclaimer section
with st.expander("Disclaimer", expanded=False):
    st.error("""
    Please Note That:

- The data is scraped from placements mail from 28-July-2024.
- It may not be accurate or up-to-date.
- The Stipend information is not available for some of the companies.
- The average and median Stipend stats have been considered only of the known stipend information given by the company only.
- All campus 2026 batch data is only considered.
- It only includes data of CSE and its specialization and IT mainly.
""")



with st.sidebar.container():
    if 'register_mode' not in st.session_state:
        st.session_state.register_mode = False
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.previous_login = None
    if 'otp_sent' not in st.session_state:
        st.session_state.otp_sent = False
    if 'registration_step' not in st.session_state:
        st.session_state.registration_step = 1  # New state to track registration progress

    if st.session_state.register_mode:
        st.header("Register")

        # Step 1: Email and Password Input
        if st.session_state.registration_step == 1:
            new_email = st.text_input("Email for Registration", key="reg_email").lower()
            new_pwd = st.text_input("Password for Registration", type="password", key="reg_pwd")
            repwd = st.text_input("Re-enter Password", type="password", key="reg_repwd")

            col1, col2 = st.columns(2)
            msg = []
            with col1:
                if st.button("Register", key="reg_button"):
                    if not new_email or not new_pwd or not repwd:
                        msg.append("Email and Password are required!")
                    elif check_email_exists(new_email):
                        msg.append("Email already exists! Please use a different email or login.")
                    elif new_pwd != repwd:
                        msg.append("Passwords do not match!")
                    else:
                        st.session_state.temp_email = new_email  # Store email temporarily
                        st.session_state.temp_pwd = new_pwd  # Store password temporarily
                        st.session_state.sent_otp = generate_otp()
                        send_otp(new_email, st.session_state.sent_otp, "registration")
                        st.session_state.otp_sent = True
                        st.session_state.registration_step = 2  # Move to OTP verification
                        st.rerun()  # Force refresh to show OTP input

            with col2:
                if st.button("Already a User? Login Here", key="switch_to_login"):
                    st.session_state.register_mode = False
                    st.rerun()

            with st.container():
                for message in msg:
                    st.error(message)

        # Step 2: OTP Verification
        elif st.session_state.registration_step == 2:
            st.info("An OTP has been sent to your email for verification.")
            entered_otp = st.text_input("Enter OTP", type="password", key="reg_otp")

            col1, col2, col3 = st.columns(3)
            messages = []
            with col1:
                if st.button("Verify OTP", key="verify_otp"):
                    if st.session_state.get('sent_otp') is None:
                        messages.append(["OTP has expired or was not generated. Please request a new OTP.", 3])
                    elif verify_otp(str(st.session_state.sent_otp), entered_otp):
                        # Verify user registration data is stored
                        registration_success = register_user(st.session_state.temp_email, st.session_state.temp_pwd)
                        if registration_success:
                            messages.append(["Registration successful! You can now log in.", 1])
                            st.sidebar.success("Registration successful! You can now log in.")
                            time.sleep(2)
                            # Reset all registration-related states only after successful registration
                            st.session_state.register_mode = False
                            st.session_state.otp_sent = False
                            st.session_state.registration_step = 1
                            st.session_state.pop('temp_email', None)
                            st.session_state.pop('temp_pwd', None)
                            st.session_state.pop('sent_otp', None)
                            st.rerun()  # Move to login page after rerun
                        else:
                            messages.append(["Registration failed. Email may already exist or data could not be saved.", 3])
                    else:
                        messages.append(["Invalid OTP. Please try again.", 3])
            with col3:
                if st.button("Login Here", key="switch_to_login"):
                    st.session_state.register_mode = False
                    st.rerun()

            with col2:
                if st.button("Resend OTP", key="resend_otp"):
                    st.session_state.sent_otp = generate_otp()
                    send_otp(st.session_state.temp_email, st.session_state.sent_otp, "registration")
                    messages.append(["New OTP has been sent to your email.", 2])

            with st.container():
                for msg, state in messages:
                    if state == 1:
                        st.success(msg)
                    elif state == 2:
                        st.info(msg)
                    else:
                        st.error(msg)


    else:
        # Login mode code remains mostly the same
        if st.session_state.logged_in:
            if 'temp_message' not in st.session_state:
                st.session_state.temp_message = ""
            if 'message_time' not in st.session_state:
                st.session_state.message_time = None
            st.markdown("""
                <style>
                /* Welcome text */
                .welcome-text {
                    color: #ffffff;
                    font-size: 28px;
                    font-weight: bold;
                    text-align: center;
                    margin: 25px 0;
                    font-family: 'Helvetica Neue', sans-serif;
                    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
                }

                /* User info card */
                .user-info {
                    background: rgba(74, 144, 226, 0.1);
                    border-radius: 15px;
                    padding: 20px;
                    margin: 15px 0;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(74, 144, 226, 0.2);
                }

                .user-info p {
                    color: #e0e0e0;
                    margin: 8px 0;
                    font-size: 17px;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }

                /* Section headers */
                .section-header {
                    color: #4a90e2;
                    font-size: 20px;
                    font-weight: 600;
                    margin: 30px 0 15px 0;
                    padding-bottom: 10px;
                    border-bottom: 2px solid #4a90e2;
                }

                /* Button styling */
                .stButton > button {
                    width: 100%;
                    background: rgba(74, 144, 226, 0.1);
                    color: white;
                    border: 1px solid rgba(74, 144, 226, 0.3);
                    padding: 12px 20px;
                    border-radius: 10px;
                    font-weight: 500;
                    margin: 8px 0;
                    transition: all 0.3s ease;
                    backdrop-filter: blur(5px);
                }

                .stButton > button:hover {
                    background: rgba(74, 144, 226, 0.2);
                    border-color: rgba(74, 144, 226, 0.5);
                    transform: translateY(-2px);
                }

                /* Logout button specific */
                .logout-btn {
                    background: rgba(255, 75, 75, 0.1) !important;
                    border-color: rgba(255, 75, 75, 0.3) !important;
                }

                .logout-btn:hover {
                    background: rgba(255, 75, 75, 0.2) !important;
                    border-color: rgba(255, 75, 75, 0.5) !important;
                }
                </style>
            """, unsafe_allow_html=True)

            with st.sidebar:

                # Welcome and user info
                st.markdown(f'<div class="welcome-text">Welcome!</div>', unsafe_allow_html=True)
                from datetime import datetime


                def format_date(timestamp):
                    try:
                        # If it's a float/unix timestamp
                        return datetime.fromtimestamp(float(timestamp)).strftime("%d-%b-%Y %I:%M:%S %p")
                    except (ValueError, TypeError):
                        try:
                            # If it's already a formatted date string
                            return datetime.strptime(str(timestamp), "%d-%b-%Y %I:%M:%S %p").strftime(
                                "%d-%b-%Y %I:%M:%S %p")
                        except (ValueError, TypeError):
                            return "No updates yet"


                previous_update = format_date(
                    st.session_state.last_update_time) if st.session_state.last_update_time else "No updates yet"
                if st.session_state.previous_login and st.session_state.previous_login.lower() != 'null':
                    try:
                        last_login_time = datetime.strptime(st.session_state.previous_login, "%Y-%m-%d %H:%M:%S.%f")
                        last_login_text = last_login_time.strftime("%d-%b-%Y %I:%M:%S %p")
                    except ValueError:
                        last_login_text = "Invalid date format"
                else:
                    last_login_text = "First login"

                st.markdown(f"""
                <div class="user-info">
                    <p>📧 {st.session_state.email}</p>
                    <p>🕒 Last Login: {last_login_text}</p>                    
                    <p>🕒 Last Data Update: {previous_update} <p>
                </div>
                """, unsafe_allow_html=True)

                # Report Issues Button (Google Form)
                feedback_url = "https://forms.gle/FqewDcoaZx7cSeyX7"
                messages = []
                add_feedback_button()

                # Logout button
                if st.button("🚪 Logout", key="logout_button", help="Click to logout"):
                    st.session_state.logged_in = False
                    st.session_state.previous_login = None
                    st.session_state.email = None
                    st.rerun()

                with st.container():
                    for message in messages:
                        st.success(message)


        else:
            st.header("Login")
            email = st.text_input("Email", key="login_email").lower()
            pwd = st.text_input("Password", type="password", key="login_pwd")

            col1, col2, col3 = st.columns([1, 1, 1])
            messages = []  # List to hold all messages

            with col1:
                if st.button("Login Now !!", key="login_button"):
                    if not email or not pwd:
                        messages.append("Email and Password are required!")
                    else:
                        valid_domains = ['@admin.in', '@vitstudent.ac.in', '@vitapstudent.ac.in']
                        if any(email.endswith(domain) for domain in valid_domains):
                            try:
                                is_authenticated, error_message, last_login = authenticate(email, pwd)
                                if is_authenticated:
                                    st.session_state.logged_in = True
                                    st.session_state.previous_login = last_login
                                    st.session_state.last_login_time = datetime.now()
                                    st.session_state.email = email
                                    st.rerun()
                                else:
                                    messages.append(error_message)
                            except ValueError as e:
                                messages.append(str(e))
                        else:
                            messages.append("Invalid email! Only VIT email ids are allowed.")

            # Forgot Password Process
            with col2:
                if st.button("Forgot Password?", key="forgot_pwd"):
                    st.session_state.forgot_password_mode = True
                    st.rerun()

            if st.session_state.get("forgot_password_mode", False):
                st.header("Forgot Password")
                reset_email = st.text_input("Enter your registered email", key="reset_email").lower()

                # OTP Request for Password Reset
                if st.button("Send OTP", key="send_reset_otp"):
                    if not reset_email:
                        messages.append("Please enter your email.")
                    elif not check_email_exists(reset_email):
                        messages.append("Email not found. Please check your email or register.")
                    else:
                        # Generate and send OTP
                        st.session_state.reset_otp = str(generate_otp())
                        send_otp(reset_email, st.session_state.reset_otp, "password reset")
                        st.session_state.otp_sent = True
                        st.session_state.forgot_password_step = 2
                        st.session_state.temp_email = reset_email
                        st.session_state.reset_otp_entered = ""  # Clear any previous entry
                        st.rerun()

            # OTP Verification for Password Reset
            if st.session_state.get("forgot_password_step", 1) == 2:
                entered_reset_otp = st.text_input("Enter OTP sent to your email", value="", key="reset_otp_input")
                if st.button("Verify OTP", key="verify_reset_otp"):
                    if str(st.session_state.get("reset_otp")) == entered_reset_otp:
                        # Proceed with password reset
                        st.session_state.forgot_password_step = 3
                        st.success("OTP Verified! Set your new password.")
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error("Invalid OTP. Please try again.")

            # Password Reset
            if st.session_state.get("forgot_password_step", 1) == 3:
                new_password = st.text_input("Enter new password", type="password", key="new_reset_password")
                confirm_password = st.text_input("Confirm new password", type="password", key="confirm_reset_password")
                if st.button("Reset Password", key="reset_password_button"):
                    if new_password != confirm_password:
                        st.error("Passwords do not match!")
                    else:
                        update_password(st.session_state.temp_email, new_password)
                        st.success("Password reset successfully! You can now log in.")
                        time.sleep(2)

                        # Clear all reset-related states after successful reset
                        st.session_state.pop("forgot_password_mode", None)
                        st.session_state.pop("reset_otp", None)
                        st.session_state.pop("forgot_password_step", None)
                        st.session_state.pop("temp_email", None)
                        st.rerun()

            with col3:
                if st.button("Register Here", key="switch_to_register"):
                    st.session_state.register_mode = True
                    st.rerun()

            with st.container():
                for message in messages:
                    st.error(message)


current_time = time.time()

# Ensure last_update_time is a float or None
last_update_time = st.session_state.last_update_time
if last_update_time is None or (isinstance(last_update_time, float) and (current_time - last_update_time) > 3600):
    get_updated_data(google_sheet_url)
    st.session_state.last_update_time = current_time


# After handling the sidebar, you can show content based on login state
if st.session_state.logged_in:
    st.write("Welcome to the application!")
    tab1, tab2, tab4, tab3 = st.tabs(["Branch-wise Internships", "Company-wise Internships", "Specific Search", "Overall Stats*"])
    with tab1:
        tab1_content()
    with tab2:
        tab2_content()
    with tab3:
        tab3_content()
    with tab4:
        tab4_content()
else:
    st.write("Please log in to access all features.")
    tab, = st.tabs(["*Overall Stats*"])
    with tab:
        tab3_content()


st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        text-align: center;
        padding: 10px;
        background-color: #808080;
        color: #555;
        font-size: 12px;
        background: rgba(255, 255, 255, 1);
        box-shadow: 0 4px 30px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.46);
    }
    </style>
    <div class="footer">
        &copy; All rights reserved. <br>
        Disclaimer: This application is for informational purposes only.
    </div>
    """,
    unsafe_allow_html=True
)