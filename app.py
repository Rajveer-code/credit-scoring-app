"""
NBCFDC Digital Lending Platform - Complete Flask Application
Installation: pip install flask
Run: python app.py
"""
from flask import Flask, render_template, redirect, url_for, session, request, jsonify
import os
import json
from datetime import datetime
import sys # Import the sys module for logging

# FIX: Explicitly tell Flask the name of the template folder.
app = Flask(__name__, template_folder='Templates')

app.secret_key = 'nbcfdc_sih_2024_secret_key_change_in_production'

# Mock user data with complete profiles
USERS = {
    'beneficiary': {
        'password': 'demo123',
        'role': 'beneficiary',
        'name': 'Rajesh Kumar',
        'id': 'NBCFDC-2024-1847',
        'credit_score': 782,
        'repayment_score': 85,
        'consumption_score': 78,
        'composite_score': 82,
        'risk_band': 'Low Risk - High Need',
        'active_loans': 1,
        'total_borrowed': 250000,
        'loan_history': [
            {'date': '2023-01-15', 'amount': 100000, 'status': 'Completed', 'repaid': 100},
            {'date': '2023-08-20', 'amount': 150000, 'status': 'Active', 'repaid': 65}
        ]
    },
    'admin': {
        'password': 'admin123',
        'role': 'admin',
        'name': 'Admin User',
        'id': 'ADMIN-001'
    }
}

# Mock beneficiary database for admin view
BENEFICIARIES = [
    {'id': 'NBCFDC-2024-1847', 'name': 'Rajesh Kumar', 'score': 782, 'band': 'Low Risk - High Need', 'status': 'Active'},
    {'id': 'NBCFDC-2024-1523', 'name': 'Priya Sharma', 'score': 845, 'band': 'Low Risk - Low Need', 'status': 'Active'},
    {'id': 'NBCFDC-2024-1689', 'name': 'Anil Verma', 'score': 620, 'band': 'High Risk - High Need', 'status': 'Under Review'},
    {'id': 'NBCFDC-2024-1734', 'name': 'Sunita Devi', 'score': 580, 'band': 'High Risk - Low Need', 'status': 'Inactive'},
    {'id': 'NBCFDC-2024-1891', 'name': 'Vikram Singh', 'score': 790, 'band': 'Low Risk - High Need', 'status': 'Active'},
]

@app.route('/')
def index():
    print("DEBUG: Reached root route '/'", file=sys.stderr)
    if 'user' in session:
        print("DEBUG: User in session, redirecting to dashboard.", file=sys.stderr)
        return redirect(url_for('dashboard'))
    print("DEBUG: No user in session, redirecting to login.", file=sys.stderr)
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    print("DEBUG: Reached /login route.", file=sys.stderr)
    # If user is already logged in, redirect them to the dashboard
    if 'user' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        print(f"DEBUG: Login attempt for username: {username}", file=sys.stderr)

        if username in USERS and USERS[username]['password'] == password:
            session['user'] = username
            session['role'] = USERS[username]['role']
            session['name'] = USERS[username]['name']
            session['user_id'] = USERS[username]['id']
            
            if username == 'beneficiary':
                session['credit_score'] = USERS[username]['credit_score']
                session['risk_band'] = USERS[username]['risk_band']
            
            print("DEBUG: Login successful, redirecting to dashboard.", file=sys.stderr)
            return redirect(url_for('dashboard'))
        else:
            print("DEBUG: Invalid credentials.", file=sys.stderr)
            return render_template('login.html', error='Invalid credentials')
    
    print("DEBUG: Serving login page.", file=sys.stderr)
    return render_template('login.html')

@app.route('/logout')
def logout():
    print("DEBUG: Logging out user.", file=sys.stderr)
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    print("DEBUG: Reached /dashboard route.", file=sys.stderr)
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_data = USERS.get(session['user'], {})
    return render_template('dashboard.html', 
                             name=session.get('name'), 
                             user_id=session.get('user_id'),
                             role=session.get('role'),
                             user_data=user_data)

@app.route('/credit-score')
def credit_score():
    print("DEBUG: Reached /credit-score route.", file=sys.stderr)
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_data = USERS.get(session['user'], {})
    return render_template('credit_score.html', 
                             name=session.get('name'),
                             user_id=session.get('user_id'),
                             user_data=user_data)

@app.route('/new-loan')
def new_loan():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_data = USERS.get(session['user'], {})
    return render_template('new_loan.html', 
                             name=session.get('name'),
                             user_id=session.get('user_id'),
                             user_data=user_data)

@app.route('/loan-status')
def loan_status():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    user_data = USERS.get(session['user'], {})
    return render_template('loan_status.html', 
                             name=session.get('name'),
                             user_id=session.get('user_id'),
                             user_data=user_data)

@app.route('/income-verification')
def income_verification():
    if 'user' not in session:
        return redirect(url_for('login'))
    
    return render_template('income_verification.html', 
                             name=session.get('name'),
                             user_id=session.get('user_id'))

@app.route('/admin-analytics')
def admin_analytics():
    if 'user' not in session or session.get('role') != 'admin':
        return redirect(url_for('dashboard'))
    
    return render_template('admin_analytics.html', 
                             name=session.get('name'),
                             beneficiaries=BENEFICIARIES)

# API endpoints for dynamic features
@app.route('/api/submit-loan', methods=['POST'])
def submit_loan():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    data = request.get_json()
    return jsonify({
        'success': True,
        'loan_id': 'LOAN-' + datetime.now().strftime('%Y%m%d%H%M%S'),
        'amount': data.get('amount'),
        'status': 'APPROVED',
        'message': 'Loan approved instantly! Funds will be transferred within 24 hours.'
    })

@app.route('/api/repeat-loan', methods=['POST'])
def repeat_loan():
    if 'user' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    return jsonify({
        'success': True,
        'loan_id': 'LOAN-RPT-' + datetime.now().strftime('%Y%m%d%H%M%S'),
        'amount': 150000,
        'status': 'APPROVED',
        'processing_time': '45 seconds',
        'message': 'Repeat loan approved! 50% faster than traditional process.'
    })

if __name__ == '__main__':
    # This part is for local development only and will not run on Render
    app.run(debug=True, port=5000)

