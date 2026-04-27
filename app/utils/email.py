import aiosmtplib
from email.message import EmailMessage

async def  send_email(to_email:str,subject:str,body:str):

    message = EmailMessage()
    message["From"] = "your_email@gmail.com"
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)   

    await aiosmtplib.send(
        message,
        hostname="smtp.gmail.com",
        port=587,
        start_tls=True,
        username="sahilswork9@gmail.com",
        password="husb ijup qlqq ixaj",  # 🔥 NOT your Gmail password
    )


    # ✅ Create reusable templates
async def send_welcome_email(user):
    await send_email(
        user.email,
        "🎉 Welcome to Our Store!",
        f"""
Hi {user.name},

Welcome aboard! 🚀

Your account has been successfully created.

Now you can:
✅ Browse products  
✅ Add items to cart  
✅ Place orders  
✅ Track your purchases  

👉 Start shopping and explore amazing deals today!

We’re excited to have you with us ❤️  
Your Store Team
"""
    )

async def send_login_email(user):
    await send_email(
        user.email,
        "🔐 Login Alert",
        f"""
Hi {user.name},

We noticed a login to your account.

📅 Time: Just now  
📧 Account: {user.email}

If this was you, no action is needed.

❗ If you did NOT log in:
- Please change your password immediately
- Contact our support team

Your security is our priority 🔒

Stay safe,  
Your Store Team
"""
    )

async def send_logout_email(user):
    await send_email(
        user.email,
        "🚪 Logout Alert",
        f"""
Hi {user.name},

You have successfully logged out of your account.

📅 Time: Just now  
📧 Account: {user.email}

If this was you, no action is needed.

❗ If you did NOT log out:
- Your account may be accessed from another device
- Please log in and change your password immediately
- Contact our support team

Your security is our priority 🔒

Stay safe,  
Your Store Team
"""
    )

async def send_cart_email(user, product):
    await send_email(
        user.email,
        "🛒 Item Added to Your Cart",
        f"""
Hi {user.name},

Great choice! 🎉

The following item has been successfully added to your cart:

Product: {product.name}
Price: ₹{product.price}

You can continue shopping or proceed to checkout anytime.

👉 Visit"""
    )

async def send_order_email(user, order):
    try:
        # Extract required fields
        order_id = order.id
        order_date = order.created_at.strftime("%d-%m-%Y %I:%M %p")
        status = order.status

        await send_email(
            user.email,
            "🛒 Order Confirmed 🎉",
            f"""
Hi {user.name} 👋,

🎉 Your order has been placed successfully!

🧾 Order Details:
━━━━━━━━━━━━━━━━━━━━━━
🆔 Order ID   : #{order_id}
📅 Order Date : {order_date}
📦 Status     : {status}
━━━━━━━━━━━━━━━━━━━━━━

🚚 We are processing your order and will update you soon.

💙 Thanks for shopping with us!

- Your Team 🛍️
"""
        )
    except Exception as e:
        print("Email Error:", e)    
async def send_status_email(user, order):
    await send_email(
        user.email,
        "🚚 Order Status Update",
        f"""
Hi {user.name},

Good news! 🎉

Your order status has been updated.

🧾 Order ID: #{order.id}  
📦 Current Status: {order.status}

We are working hard to deliver your order as quickly as possible.

👉 Stay tuned — we’ll keep you updated on further progress.

Thank you for your patience and trust ❤️  
Your Store Team
"""
    )
    await send_email(
        user.email,
        "Order Status Updated 🚚",
        f"Your order #{order.id} is now {order.status}."
    )       