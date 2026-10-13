from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from html import escape

app = FastAPI(title="ReWear Marketplace")

products = [
    {"id": 1, "name": "Denim Jacket", "price": 2000,
     "size": "M", "condition": "Very Good", "emoji": "🧥"},
    {"id": 2, "name": "Floral Dress", "price": 1500,
     "size": "S", "condition": "Excellent", "emoji": "👗"},
    {"id": 3, "name": "Casual Shirt", "price": 900,
     "size": "L", "condition": "Good", "emoji": "👚"},
]

orders = []
commission_rate = 0.12


class NewProduct(BaseModel):
    name: str
    price: float
    size: str = "M"
    condition: str = "Good"
    emoji: str = "👕"


class NewOrder(BaseModel):
    product_id: int


@app.get("/", response_class=HTMLResponse)
def home():
    cards = ""
    for p in products:
        cards += f"""
        <div class="card">
          <div class="photo">{escape(p['emoji'])}</div>
          <h3>{escape(p['name'])}</h3>
          <p>Size: {escape(p['size'])} ·
             {escape(p['condition'])}</p>
          <h3>Rs. {p['price']:,.0f}</h3>
          <button onclick="buy({p['id']})">
            Buy Now
          </button>
        </div>
        """

    return f"""
    <!DOCTYPE html>
    <html>
    <head>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>ReWear | Pre-loved Fashion</title>
    <style>
      * {{ box-sizing: border-box; }}
      body {{ margin:0; font-family:Arial,sans-serif;
        background:#f8f7f2; color:#243b32; }}
      header {{ background:#214d3b; color:white;
        padding:24px 7%; }}
      header h1 {{ margin:0; font-size:34px; }}
      nav {{ margin-top:12px; }}
      nav a {{ color:white; margin-right:18px;
        text-decoration:none; }}
      .hero {{ padding:55px 7%; background:#e2ecdf; }}
      .hero h2 {{ font-size:36px; margin-bottom:10px; }}
      .hero p {{ font-size:17px; }}
      section {{ padding:28px 7%; }}
      .products {{ display:grid;
        grid-template-columns:repeat(auto-fit,minmax(210px,1fr));
        gap:20px; }}
      .card {{ background:white; border-radius:16px;
        padding:18px; box-shadow:0 3px 14px #0001; }}
      .photo {{ height:140px; display:grid;
        place-items:center; background:#f0eee6;
        border-radius:12px; font-size:65px; }}
      button {{ background:#285840; color:white;
        border:0; padding:12px 16px; border-radius:8px;
        cursor:pointer; }}
      input, select {{ padding:11px; margin:6px 0;
        width:100%; border:1px solid #ccd5cb;
        border-radius:7px; }}
      .panel {{ max-width:550px; background:white;
        padding:22px; border-radius:14px; margin:12px 0; }}
      #message {{ font-weight:bold; margin-top:12px; }}
      footer {{ background:#214d3b; color:white;
        padding:24px; text-align:center; }}
    </style>
    </head>
    <body>
    <header>
      <h1>♻ ReWear</h1>
      <p>Give clothes a second life.</p>
      <nav>
        <a href="#shop">Shop</a>
        <a href="#sell">Sell Clothes</a>
        <a href="#commission">Commission</a>
      </nav>
    </header>

    <div class="hero">
      <h2>Pre-loved fashion, new beginnings.</h2>
      <p>Discover affordable fashion and make sustainable choices.</p>
      <button onclick="location.href='#shop'">Explore Clothes</button>
    </div>

    <section id="shop">
      <h2>Discover Pre-loved Clothes</h2>
      <input id="search" placeholder="Search clothes..."
        oninput="filterProducts()">
      <div class="products" id="products">{cards}</div>
    </section>

    <section id="sell">
      <h2>Sell Your Clothes</h2>
      <div class="panel">
        <form id="sellForm">
          <label>Clothing name</label>
          <input name="name" required maxlength="80"
            placeholder="e.g. Blue Denim Jacket">
          <label>Price in rupees</label>
          <input name="price" type="number" min="1"
            max="10000000" required>
          <label>Size</label>
          <select name="size">
            <option>S</option><option selected>M</option>
            <option>L</option><option>XL</option>
          </select>
          <label>Condition</label>
          <select name="condition">
            <option>Excellent</option>
            <option>Very Good</option><option>Good</option>
          </select>
          <button type="submit">Add Listing</button>
        </form>
        <p id="sellMessage"></p>
      </div>
    </section>

    <section id="commission">
      <h2>ReWear Commission Calculator</h2>
      <div class="panel">
        <label>Clothing price (Rs.)</label>
        <input id="price" type="number" value="2000" min="0">
        <button onclick="calculate()">Calculate Earnings</button>
        <p id="result">ReWear: Rs. 240 · Seller: Rs. 1,760</p>
      </div>
    </section>

    <footer>ReWear © 2026 · Fashion with a second life ♻</footer>

    <script>
    async function buy(id) {
      const r = await fetch('/api/orders', {
        method: 'POST',
        headers: {'Content-Type':'application/json'},
        body: JSON.stringify({product_id:id})
      });
      const d = await r.json();
      alert(d.message || d.detail || 'Please try again');
    }

    function calculate() {
      const p = Number(document.getElementById('price').value);
      if (!Number.isFinite(p) || p < 0) {
        alert('Enter a valid price');
        return;
      }
      const fee = p * 0.12;
      document.getElementById('result').textContent =
        'ReWear commission: Rs. ' + fee.toFixed(2) +
        ' | Seller earns: Rs. ' + (p-fee).toFixed(2);
    }

    document.getElementById('sellForm').onsubmit =
      async function(e) {
        e.preventDefault();
        const f = new FormData(this);
        const data = Object.fromEntries(f.entries());
        data.price = Number(data.price);
        data.emoji = '👕';
        const r = await fetch('/api/products', {
          method:'POST',
          headers:{'Content-Type':'application/json'},
          body:JSON.stringify(data)
        });
        const d = await r.json();
        document.getElementById('sellMessage').textContent =
          d.message || d.detail || 'Done';
        if (r.ok) setTimeout(() => location.reload(), 700);
      };

    function filterProducts() {
      const q = document.getElementById('search').value.toLowerCase();
      document.querySelectorAll('#products .card').forEach(card => {
        card.style.display = card.innerText.toLowerCase().includes(q)
          ? '' : 'none';
      });
    }
    </script>
    </body>
    </html>
    """


@app.post("/api/products")
def add_product(p: NewProduct):
    if p.price <= 0:
        from fastapi import HTTPException
        raise HTTPException(400, "Price must be greater than zero")

    item = p.model_dump()
    item["id"] = max((x["id"] for x in products), default=0) + 1
    products.append(item)
    return {"message": "Listing added successfully!"}


@app.post("/api/orders")
def place_order(order: NewOrder):
    product = next(
        (p for p in products if p["id"] == order.product_id), None
    )
    if product is None:
        from fastapi import HTTPException
        raise HTTPException(404, "Product not found")

    price = product["price"]
    commission = round(price * commission_rate, 2)
    seller_earning = round(price - commission, 2)

    record = {
        "order_id": len(orders) + 1,
        "product": product["name"],
        "price": price,
        "commission": commission,
        "seller_earning": seller_earning,
        "status": "Demo order"
    }
    orders.append(record)

    return {
        "message": (
            f"Demo order created! Price Rs. {price:,.2f}; "
            f"ReWear commission Rs. {commission:,.2f}; "
            f"seller earning Rs. {seller_earning:,.2f}. "
            "No payment was collected."
        ),
        "order": record
    }


@app.get("/api/orders")
def get_orders():
    return orders
