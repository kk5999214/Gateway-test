from flask import Flask, request, redirect, jsonify
import uuid

app = Flask(__name__)

# 💀🔥 FAKE DATABASE: In a real app, this is MySQL/PostgreSQL.
# It stores orders as { "TXN_123": "PENDING" }
orders_db = {}

# 1. THE STOREFRONT
@app.route('/')
def index():
    return '''
        <h2 style="font-family:sans-serif; color:#333;">Welcome to TechBittu Store</h2>
        <form action="/checkout" method="POST">
            <input type="number" name="amount" value="100.32" step="0.01" readonly style="padding:10px; font-size:16px;">
            <button type="submit" style="padding:10px 20px; background:#3b82f6; color:white; border:none; border-radius:5px; cursor:pointer;">Pay with Slice Gateway</button>
        </form>
    '''

# 2. THE HANDSHAKE (Redirects to your Gateway)
@app.route('/checkout', methods=['POST'])
def checkout():
    amount = request.form.get('amount')
    txn_id = f"TXN_{uuid.uuid4().hex[:8].upper()}" # Generates a random TXN ID
    
    # Save to database as PENDING before redirecting
    orders_db[txn_id] = "PENDING"
    
    store_name = "TechBittuStore"
    # IMPORTANT: Change this URL to your actual Render URL for this test app once deployed!
    redirect_url = "https://your-merchant-app.onrender.com/order-status" 
    
    gateway_url = f"https://pay.techbittu.in/?store={store_name}&amount={amount}&txn={txn_id}&redirect_url={redirect_url}"
    return redirect(gateway_url)

# 3. THE GHOST PROTOCOL (Server-to-Server Webhook Receiver)
@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.json
    if not data:
        return jsonify({"error": "No data received"}), 400
        
    txn_id = data.get('txn_id')
    status = data.get('status')
    
    # Verify the transaction exists in our database
    if txn_id in orders_db:
        # Update the database with the background webhook status!
        orders_db[txn_id] = status 
        print(f"💀 WEBHOOK RECEIVED: Updated {txn_id} to {status}")
        return jsonify({"message": "Webhook processed successfully"}), 200
    
    return jsonify({"error": "Transaction not found"}), 404

# 4. THE FINAL DESTINATION (Verifies DB, not the URL)
@app.route('/order-status')
def order_status():
    txn_id = request.args.get('txn')
    
    # CRITICAL: We don't trust the URL status. We check our own database!
    actual_status = orders_db.get(txn_id, "NOT_FOUND")
    
    if actual_status == "success":
        return f"<h1 style='color:green; font-family:sans-serif;'>✅ Order Confirmed! (TXN: {txn_id})</h1>"
    elif actual_status == "failed":
        return f"<h1 style='color:red; font-family:sans-serif;'>❌ Order Failed! (TXN: {txn_id})</h1>"
    elif actual_status == "PENDING":
        return f"<h1 style='color:orange; font-family:sans-serif;'>⏳ Order is still pending...</h1>"
    else:
        return f"<h1 style='color:gray; font-family:sans-serif;'>❓ Invalid Transaction</h1>"

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
  
