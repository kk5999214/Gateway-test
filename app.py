from flask import Flask, request, redirect, jsonify
import uuid

app = Flask(__name__)

# 💀🔥 FAKE DATABASE
orders_db = {}

# 1. THE STOREFRONT
@app.route('/')
def index():
    return '''
        <div style="font-family:sans-serif; text-align:center; margin-top:50px;">
            <h2 style="color:#333;">Welcome to TechBittu Store</h2>
            <form action="/checkout" method="POST">
                <input type="number" name="amount" value="100.32" step="0.01" readonly style="padding:10px; font-size:16px; border:1px solid #ccc; border-radius:5px; margin-right:10px;">
                <button type="submit" style="padding:10px 20px; background:#3b82f6; color:white; font-weight:bold; border:none; border-radius:5px; cursor:pointer;">Pay with Slice Gateway</button>
            </form>
        </div>
    '''

# 2. THE HANDSHAKE (Redirects to Gateway)
@app.route('/checkout', methods=['POST'])
def checkout():
    amount = request.form.get('amount')
    txn_id = f"TXN_{uuid.uuid4().hex[:8].upper()}" 
    
    orders_db[txn_id] = "PENDING"
    store_name = "TechBittuStore"
    redirect_url = "https://gateway-test-m689.onrender.com/order-status" 
    
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
        return f"<div style='text-align:center; margin-top:50px;'><h1 style='color:#10b981; font-family:sans-serif;'>✅ Order Confirmed!</h1><p style='font-family:sans-serif;'>TXN: {txn_id}</p></div>"
    elif actual_status == "failed":
        return f"<div style='text-align:center; margin-top:50px;'><h1 style='color:#ef4444; font-family:sans-serif;'>❌ Order Failed!</h1><p style='font-family:sans-serif;'>TXN: {txn_id}</p></div>"
    elif actual_status == "PENDING":
        return f"<div style='text-align:center; margin-top:50px;'><h1 style='color:#f59e0b; font-family:sans-serif;'>⏳ Order Pending...</h1><p style='font-family:sans-serif;'>TXN: {txn_id}</p></div>"
    else:
        return f"<div style='text-align:center; margin-top:50px;'><h1 style='color:#6b7280; font-family:sans-serif;'>❓ Invalid Transaction</h1></div>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
