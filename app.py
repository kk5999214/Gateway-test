from flask import Flask, request, redirect, jsonify
import uuid
import urllib.parse

app = Flask(__name__)

# 💀🔥 FAKE DATABASE
orders_db = {}

# 1. THE STOREFRONT (2-Column dynamic design)
@app.route('/')
def index():
    return '''
        <!DOCTYPE html>
        <html>
        <head>
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
        </head>
        <body style="font-family:'Inter', sans-serif; display:flex; justify-content:center; align-items:center; height:100vh; margin:0; background:#f3f4f6;">
            <div style="background:white; padding:40px; border-radius:16px; box-shadow:0 10px 25px rgba(0,0,0,0.05); width:100%; max-width:500px; text-align:center;">
                <h2 style="color:#111827; margin-bottom:24px; font-weight:700;">Merchant Test Portal</h2>
                <form action="/checkout" method="POST" style="display:flex; flex-direction:column; gap:20px;">
                    
                    <div style="display:flex; gap:16px;">
                        <div style="flex:1; text-align:left;">
                            <label style="font-size:12px; color:#6b7280; font-weight:600; margin-bottom:6px; display:block;">COMPANY NAME</label>
                            <input type="text" name="store_name" placeholder="e.g. Nike" required style="width:100%; padding:12px; font-size:15px; border:1px solid #d1d5db; border-radius:8px; box-sizing:border-box;">
                        </div>
                        <div style="flex:1; text-align:left;">
                            <label style="font-size:12px; color:#6b7280; font-weight:600; margin-bottom:6px; display:block;">AMOUNT (₹)</label>
                            <input type="number" name="amount" placeholder="e.g. 500" step="0.01" required style="width:100%; padding:12px; font-size:15px; border:1px solid #d1d5db; border-radius:8px; box-sizing:border-box;">
                        </div>
                    </div>
                    
                    <button type="submit" style="padding:16px; background:#3b82f6; color:white; font-weight:bold; font-size:16px; border:none; border-radius:8px; cursor:pointer; box-shadow:0 4px 12px rgba(59,130,246,0.3); transition:0.2s;">Initiate Secure Checkout</button>
                </form>
            </div>
        </body>
        </html>
    '''

# 2. THE HANDSHAKE (Redirects to Gateway)
@app.route('/checkout', methods=['POST'])
def checkout():
    amount = request.form.get('amount')
    raw_store_name = request.form.get('store_name')
    
    # 💀🔥 URL Encode to prevent breakages!
    store_name = urllib.parse.quote(raw_store_name)
    
    txn_id = f"TXN_{uuid.uuid4().hex[:8].upper()}" 
    
    orders_db[txn_id] = "PENDING"
    
    # 💀🔥 URL Encode the redirect string too!
    raw_redirect_url = "https://gateway-test-m689.onrender.com/order-status"
    redirect_url = urllib.parse.quote(raw_redirect_url)
    
    gateway_url = f"https://pay.techbittu.in/?store={store_name}&amount={amount}&txn={txn_id}&redirect_url={redirect_url}"
    return redirect(gateway_url)

# 3. THE GHOST PROTOCOL (S2S Webhook Receiver)
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400
        
    txn_id = data.get('txn_id')
    status = data.get('status')
    
    if txn_id in orders_db:
        orders_db[txn_id] = status 
        print(f"💀 WEBHOOK SUCCESS: Updated {txn_id} to {status.upper()}")
        return jsonify({"message": "Webhook processed"}), 200
    
    return jsonify({"error": "Transaction not found"}), 404

# 4. THE FINAL DESTINATION
@app.route('/order-status')
def order_status():
    txn_id = request.args.get('txn')
    actual_status = orders_db.get(txn_id, "NOT_FOUND")
    
    if actual_status == "success":
        return f"<div style='text-align:center; margin-top:50px;'><h1 style='color:#10b981; font-family:sans-serif;'>✅ Order Confirmed!</h1><p style='font-family:sans-serif; color:#6b7280;'>TXN: {txn_id}</p></div>"
    elif actual_status == "failed":
        return f"<div style='text-align:center; margin-top:50px;'><h1 style='color:#ef4444; font-family:sans-serif;'>❌ Order Failed!</h1><p style='font-family:sans-serif; color:#6b7280;'>TXN: {txn_id}</p></div>"
    elif actual_status == "PENDING":
        return f"<div style='text-align:center; margin-top:50px;'><h1 style='color:#f59e0b; font-family:sans-serif;'>⏳ Order Pending...</h1><p style='font-family:sans-serif; color:#6b7280;'>TXN: {txn_id}</p></div>"
    else:
        return f"<div style='text-align:center; margin-top:50px;'><h1 style='color:#6b7280; font-family:sans-serif;'>❓ Invalid Transaction</h1></div>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
