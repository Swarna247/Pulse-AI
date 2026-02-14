"""
Authentication Module
Simple admin authentication for the triage system
"""

import hashlib
import streamlit as st
from typing import Optional, Tuple


class AuthManager:
    """Manages user authentication"""
    
    def __init__(self):
        # In production, store hashed passwords in a secure database
        # For demo purposes, using hardcoded credentials
        self.users = {
            "admin@gmail.com": {
                "password_hash": self._hash_password("admin@123"),
                "role": "admin",
                "name": "Administrator"
            }
        }
    
    def _hash_password(self, password: str) -> str:
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def authenticate(self, username: str, password: str) -> Tuple[bool, Optional[dict]]:
        """
        Authenticate user credentials
        
        Args:
            username: User email
            password: User password
            
        Returns:
            (success, user_info) tuple
        """
        if username not in self.users:
            return False, None
        
        user = self.users[username]
        password_hash = self._hash_password(password)
        
        if password_hash == user["password_hash"]:
            return True, {
                "username": username,
                "role": user["role"],
                "name": user["name"]
            }
        
        return False, None
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated in current session"""
        return st.session_state.get('authenticated', False)
    
    def get_current_user(self) -> Optional[dict]:
        """Get current authenticated user info"""
        if self.is_authenticated():
            return st.session_state.get('user_info')
        return None
    
    def login(self, username: str, password: str) -> bool:
        """
        Login user and store in session
        
        Returns:
            True if login successful
        """
        success, user_info = self.authenticate(username, password)
        
        if success:
            st.session_state.authenticated = True
            st.session_state.user_info = user_info
            return True
        
        return False
    
    def logout(self):
        """Logout current user"""
        st.session_state.authenticated = False
        st.session_state.user_info = None
        # Clear other session data
        if 'patient_queue' in st.session_state:
            st.session_state.patient_queue = []
        if 'parsed_data' in st.session_state:
            st.session_state.parsed_data = None
        if 'voice_extracted_data' in st.session_state:
            st.session_state.voice_extracted_data = None


def show_login_page():
    """Display login page"""
    st.markdown("""
    <style>
        .login-container {
            max-width: 400px;
            margin: 100px auto;
            padding: 2rem;
            background: white;
            border-radius: 10px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        .login-header {
            text-align: center;
            color: #1e3a8a;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
        }
        .login-subtitle {
            text-align: center;
            color: #64748b;
            margin-bottom: 2rem;
        }
    </style>
    """, unsafe_allow_html=True)
    
    # Center the login form
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<div class="login-header">🏥 Smart Triage</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-subtitle">Admin Login</div>', unsafe_allow_html=True)
        
        # Login form
        with st.form("login_form"):
            username = st.text_input(
                "Email",
                placeholder="admin@gmail.com",
                help="Enter your admin email"
            )
            
            password = st.text_input(
                "Password",
                type="password",
                placeholder="Enter password",
                help="Enter your password"
            )
            
            submit = st.form_submit_button("🔐 Login", use_container_width=True)
            
            if submit:
                if not username or not password:
                    st.error("⚠️ Please enter both email and password")
                else:
                    auth_manager = AuthManager()
                    if auth_manager.login(username, password):
                        st.success("✅ Login successful! Redirecting...")
                        st.rerun()
                    else:
                        st.error("❌ Invalid credentials. Please try again.")
        
        # Demo credentials info
        with st.expander("ℹ️ Demo Credentials"):
            st.info("""
            **Admin Account:**
            - Email: admin@gmail.com
            - Password: admin@123
            """)
        
        # Footer
        st.markdown("---")
        st.caption("Smart Patient Triage System v1.0")
        st.caption("AI-Powered Clinical Decision Support")


def show_logout_button():
    """Display logout button in sidebar"""
    auth_manager = AuthManager()
    user_info = auth_manager.get_current_user()
    
    if user_info:
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"👤 **{user_info['name']}**")
        st.sidebar.caption(f"Role: {user_info['role'].title()}")
        st.sidebar.caption(f"Email: {user_info['username']}")
        
        if st.sidebar.button("🚪 Logout", use_container_width=True):
            auth_manager.logout()
            st.rerun()


def require_authentication(func):
    """Decorator to require authentication for a function"""
    def wrapper(*args, **kwargs):
        auth_manager = AuthManager()
        if not auth_manager.is_authenticated():
            show_login_page()
            st.stop()
        return func(*args, **kwargs)
    return wrapper
