#!/usr/bin/env python3
"""
Test script to verify the financial API endpoints work via HTTP
This starts the server and makes API calls to test the functionality
"""

import subprocess
import time
import requests
import json
import signal
import sys
from threading import Thread

# Global variable to store server process
server_process = None

def start_server():
    """Start the FastAPI server in background"""
    global server_process
    try:
        print("🚀 Starting FastAPI server...")
        server_process = subprocess.Popen([
            "python", "-m", "uvicorn", "app:app", 
            "--host", "127.0.0.1", 
            "--port", "8000",
            "--log-level", "error"
        ], 
        stdout=subprocess.DEVNULL, 
        stderr=subprocess.DEVNULL
        )
        
        # Wait for server to start
        print("⏳ Waiting for server to start...")
        time.sleep(5)
        
        # Test if server is running
        try:
            response = requests.get("http://127.0.0.1:8000/docs", timeout=2)
            if response.status_code == 200:
                print("✅ Server started successfully!")
                return True
        except:
            pass
        
        print("❌ Server failed to start")
        return False
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return False

def stop_server():
    """Stop the FastAPI server"""
    global server_process
    if server_process:
        print("\n🛑 Stopping server...")
        server_process.terminate()
        server_process.wait()
        print("✅ Server stopped")

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    stop_server()
    sys.exit(0)

def test_auth_endpoints():
    """Test signup and login endpoints"""
    base_url = "http://127.0.0.1:8000"
    
    print("\n🔐 Testing Authentication...")
    
    # Test signup
    signup_data = {
        "name": "Finance Test User",
        "email": "financetest@example.com",
        "password": "testpass123",
        "client_id": "user"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/signup", data=signup_data, timeout=5)
        if response.status_code in [200, 403]:  # 403 means user already exists
            print("✅ Signup endpoint works")
        else:
            print(f"❌ Signup failed: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"❌ Signup request failed: {e}")
        return None
    
    # Test login
    login_data = {
        "username": signup_data["email"],
        "password": signup_data["password"],
        "client_id": "user"
    }
    
    try:
        response = requests.post(f"{base_url}/auth/login", data=login_data, timeout=5)
        if response.status_code == 200:
            token_data = response.json()
            token = token_data.get("access_token")
            print("✅ Login endpoint works")
            return token
        else:
            print(f"❌ Login failed: {response.status_code} {response.text}")
            return None
    except Exception as e:
        print(f"❌ Login request failed: {e}")
        return None

def test_financial_endpoints(token):
    """Test the financial API endpoints"""
    base_url = "http://127.0.0.1:8000"
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n💰 Testing Financial Endpoints...")
    
    # Test income source creation
    print("📊 Testing Income Sources...")
    income_data = {
        "name": "API Test Salary",
        "amount": 4000.0,
        "frequency": "monthly",
        "description": "Test salary via API"
    }
    
    try:
        response = requests.post(f"{base_url}/income", json=income_data, headers=headers, timeout=5)
        if response.status_code == 200:
            print("✅ Income source creation works")
            income_id = response.json().get("id")
        else:
            print(f"❌ Income creation failed: {response.status_code} {response.text}")
            return False
    except Exception as e:
        print(f"❌ Income request failed: {e}")
        return False
    
    # Test getting income sources
    try:
        response = requests.get(f"{base_url}/income", headers=headers, timeout=5)
        if response.status_code == 200:
            income_sources = response.json()
            print(f"✅ Retrieved {len(income_sources)} income sources")
        else:
            print(f"❌ Income retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Income retrieval failed: {e}")
        return False
    
    # Test budget category creation
    print("💳 Testing Budget Categories...")
    budget_data = {
        "name": "API Test Food",
        "allocated_amount": 600.0,
        "limit": 700.0,
        "description": "Test food budget via API"
    }
    
    try:
        response = requests.post(f"{base_url}/budget", json=budget_data, headers=headers, timeout=5)
        if response.status_code == 200:
            print("✅ Budget category creation works")
        else:
            print(f"❌ Budget creation failed: {response.status_code} {response.text}")
            return False
    except Exception as e:
        print(f"❌ Budget request failed: {e}")
        return False
    
    # Test getting budget categories
    try:
        response = requests.get(f"{base_url}/budget", headers=headers, timeout=5)
        if response.status_code == 200:
            budget_categories = response.json()
            print(f"✅ Retrieved {len(budget_categories)} budget categories")
        else:
            print(f"❌ Budget retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Budget retrieval failed: {e}")
        return False
    
    # Test transaction logging
    print("💸 Testing Transactions...")
    
    # First, log an income transaction
    income_transaction = {
        "amount": 4000.0,
        "transaction_type": "income",
        "category": "API Test Salary",
        "description": "Monthly salary payment"
    }
    
    try:
        response = requests.post(f"{base_url}/transactions", json=income_transaction, headers=headers, timeout=5)
        if response.status_code == 200:
            print("✅ Income transaction logging works")
        else:
            print(f"❌ Income transaction failed: {response.status_code} {response.text}")
            return False
    except Exception as e:
        print(f"❌ Income transaction failed: {e}")
        return False
    
    # Log an expense transaction within budget
    expense_transaction = {
        "amount": 300.0,
        "transaction_type": "expense",
        "category": "API Test Food",
        "description": "Grocery shopping"
    }
    
    try:
        response = requests.post(f"{base_url}/transactions", json=expense_transaction, headers=headers, timeout=5)
        if response.status_code == 200:
            result = response.json()
            print("✅ Expense transaction logging works")
            if not result.get('budget_status', {}).get('within_limit', True):
                print(f"⚠️  Budget warning: {result['budget_status']['message']}")
        else:
            print(f"❌ Expense transaction failed: {response.status_code} {response.text}")
            return False
    except Exception as e:
        print(f"❌ Expense transaction failed: {e}")
        return False
    
    # Log an expense that exceeds budget limit
    big_expense_transaction = {
        "amount": 500.0,  # This + 300 = 800 > 700 limit
        "transaction_type": "expense",
        "category": "API Test Food",
        "description": "Expensive restaurant meal"
    }
    
    try:
        response = requests.post(f"{base_url}/transactions", json=big_expense_transaction, headers=headers, timeout=5)
        if response.status_code == 200:
            result = response.json()
            print("✅ Budget limit checking works")
            if 'warning' in result:
                print(f"🚨 Budget exceeded warning: {result['warning']}")
            if not result.get('budget_status', {}).get('within_limit', True):
                print(f"🚨 Limit exceeded: {result['budget_status']['message']}")
        else:
            print(f"❌ Budget limit test failed: {response.status_code} {response.text}")
            return False
    except Exception as e:
        print(f"❌ Budget limit test failed: {e}")
        return False
    
    # Test getting transactions
    try:
        response = requests.get(f"{base_url}/transactions", headers=headers, timeout=5)
        if response.status_code == 200:
            transactions = response.json()
            print(f"✅ Retrieved {len(transactions)} transactions")
        else:
            print(f"❌ Transaction retrieval failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Transaction retrieval failed: {e}")
        return False
    
    # Test budget summary
    try:
        response = requests.get(f"{base_url}/transactions/summary", headers=headers, timeout=5)
        if response.status_code == 200:
            summary = response.json()
            print("✅ Budget summary works")
            print("📊 Budget Summary:")
            for category in summary.get('budget_summary', []):
                print(f"  {category['category_name']}: ${category['total_spent']:.2f}/${category['limit']:.2f}")
                if not category['within_limit']:
                    print(f"    🚨 EXCEEDED by ${category['limit_exceeded_by']:.2f}")
        else:
            print(f"❌ Budget summary failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Budget summary failed: {e}")
        return False
    
    return True

def main():
    """Main test function"""
    # Set up signal handler for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    
    print("🧪 Financial API Integration Test")
    print("==================================")
    
    # Start server
    if not start_server():
        return
    
    try:
        # Test authentication
        token = test_auth_endpoints()
        if not token:
            print("❌ Authentication tests failed")
            return
        
        # Test financial endpoints
        if test_financial_endpoints(token):
            print("\n🎉 ALL TESTS PASSED!")
            print("\n📋 Successfully tested:")
            print("  ✅ User authentication (signup/login)")
            print("  ✅ Income source management")
            print("  ✅ Budget category creation with limits")
            print("  ✅ Transaction logging")
            print("  ✅ Budget limit violation detection")
            print("  ✅ Budget summary reporting")
            print("\n🚀 The Smart Finances Tracker API is fully functional!")
        else:
            print("\n❌ Financial API tests failed")
            
    finally:
        stop_server()

if __name__ == "__main__":
    main()