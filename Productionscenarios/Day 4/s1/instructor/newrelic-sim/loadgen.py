# Posts transactions to app.py so that New Relic receives traffic. Standard library only.
import os, random, time, urllib.request
BASE = os.environ.get("TARGET", "http://app:8080")
NAMES = ["CheckoutController#processPayment","OrderController#createOrder","InventoryController#reserveStock",
         "NotificationController#sendConfirmation","PaymentController#refund","OrderController#getOrderStatus"]
WEIGHTS = [20, 25, 20, 15, 5, 15]
while True:
    n = random.choices(NAMES, WEIGHTS)[0]
    try: urllib.request.urlopen(urllib.request.Request(f"{BASE}/tx/{n.replace('#','%23')}", method="POST"), timeout=15)
    except Exception: pass
    time.sleep(0.2)
