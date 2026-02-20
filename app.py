from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify,render_template_string
import mysql.connector as mq
from mysql.connector import Error
from markupsafe import Markup
import requests
from datetime import datetime
import qrcode
from PIL import Image, ImageDraw, ImageFont
import blockchain
import winsound
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret_key'
myblockchain = blockchain.Blockchain()

def dbconnection():
    con = mq.connect(host='localhost', database='fakeproduct',user='root',password='root')
    return con

@app.route('/')
def home():
    return render_template('index.html', title='home')

@app.route('/loginpage')
def loginpage():
    return render_template('login.html',title='login')

@app.route('/userregisterpage')
def registerpage():
    return render_template('userregister.html',title='register')

@app.route('/addproductpage')
def addproductpage():
    return render_template('addproduct.html',title='addproduct')

@app.route('/sellproductpage')
def sellproductpage():
    return render_template('sellproduct.html',title='sell product')

@app.route('/verifyproductspage')
def verifyproductspage():
    return render_template('verifyproducts.html',title='verify')

@app.route('/customerfeedbackpage')
def customerfeedbackpage():
    con = dbconnection()
    cursor = con.cursor()
    cursor.execute("select * from seller")
    res = cursor.fetchall()
    return render_template('customerfeedback.html',title='feedback',res=res)

@app.route('/sellergivefeedbackpage')
def sellergivefeedbackpage():
    con = dbconnection()
    cursor = con.cursor()
    cursor.execute("select * from manufacturer")
    res = cursor.fetchall()
    return render_template('sellergivefeedback.html',title='feedback',res=res)

@app.route('/viewsellerfeedbackspage')
def viewsellerfeedbackspage():
    con = dbconnection()
    cursor = con.cursor()
    cursor.execute("select * from customerfeedbacks left join customer on customerfeedbacks.cid=customer.id  where customerfeedbacks.sid={}  order by customerfeedbacks.id desc".format(
        int(session['sid'])))
    res = cursor.fetchall()
    # Convert the rating values to floats
    res_with_float_ratings = [(item[0], float(item[1]), item[2], item[3], item[4], item[5], item[6],item[7]) for item in res]
    return render_template('sellerfeedbacks.html',res=res_with_float_ratings)

@app.route('/viewmanufacturerfeedbackspage')
def viewmanufacturerfeedbackspage():
    con = dbconnection()
    cursor = con.cursor()
    cursor.execute("select * from sellerfeedbacks left join seller on sellerfeedbacks.sid=seller.id  where sellerfeedbacks.mid={}  order by sellerfeedbacks.id desc".format(
        int(session['mid'])))
    res = cursor.fetchall()

    # Convert the rating values to floats
    res_with_float_ratings = [(item[0], float(item[1]), item[2], item[3], item[4], item[5], item[6], item[7]) for item in res]

    # Calculate average rating
    avg_rating = round(sum([r[1] for r in res_with_float_ratings]) / len(res_with_float_ratings), 1) if res_with_float_ratings else 0

    return render_template('manufacfeedbacks.html', res=res_with_float_ratings, avg_rating=avg_rating)


@app.route('/mviewproductspage')
def mviewproductspage():
    con = dbconnection()
    cursor = con.cursor()
    cursor.execute("select * from products where mid={}".format(int(session['mid'])))
    res = cursor.fetchall()
    if res==[]:
        flash("Products Not Found")
    return render_template('mviewproducts.html',res=res)

@app.route('/cviewproductspage')
def cviewproductspage():
    con = dbconnection()
    cursor = con.cursor()
    cursor.execute("select * from products")
    res = cursor.fetchall()
    if res==[]:
        flash("Products Not Found")
    return render_template('cviewproducts.html',res=res)

@app.route('/sellproduct')
def sellproduct():
    id = request.args.get("id")
    con = dbconnection()
    cursor = con.cursor()
    cursor.execute("select * from seller ")
    res = cursor.fetchall()
    if res==[]:
        flash("Sellers Not Found")
    return render_template('sellerslist.html',res=res,id=id)

@app.route('/soldproductspage')
def soldproductspage():
    con = dbconnection()
    cursor = con.cursor()
    cursor.execute("select * from transactions left join products on transactions.pid=products.id left join seller on transactions.sid=seller.id where transactions.mid={} order by transactions.id desc".format(
        int(session['mid'])
    ))
    res = cursor.fetchall()
    if res==[]:
        flash("Products Not Found")
    return render_template('soldproducts.html',res=res)


@app.route('/purchasedproductspage')
def purchasedproductspage():
    con = dbconnection()
    cursor = con.cursor()
    cursor.execute("select * from transactions left join products on transactions.pid=products.id left join manufacturer on transactions.mid=manufacturer.id where transactions.sid={} order by transactions.id desc".format(
        int(session['sid'])
    ))
    res = cursor.fetchall()
    if res==[]:
        flash("Products Not Found")
    return render_template('purchasedproducts.html',res=res)


@app.route('/userregister', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
       
        name = request.form['name']
        email = request.form['email']
        phone = request.form['phone']
        ras = request.form['ras']
        address = request.form['address']
        password = request.form['password']
        con = dbconnection()
        cursor = con.cursor()
        if ras=="Manufacturer":
            cursor.execute("select * from manufacturer where email='{}' or phone='{}'".format(email,phone))
            res = cursor.fetchall()
            if res==[]:
                cursor.execute("insert into manufacturer (name,email,phone,address,password)values('{}','{}','{}','{}','{}')".format(
                    name,email,phone,address,password))
                con.commit()
                con.close()
                flash("Registration success")
                return redirect(url_for('loginpage'))
            else:
                flash("Email id or phone number already exist.")
                return redirect(url_for('registerpage'))
        elif ras=="Seller":
            cursor.execute("select * from seller where email='{}' or phone='{}'".format(email,phone))
            res = cursor.fetchall()
            if res==[]:
                cursor.execute("insert into seller (name,email,phone,address,password)values('{}','{}','{}','{}','{}')".format(
                    name,email,phone,address,password))
                con.commit()
                con.close()
                flash("Registration success")
                return redirect(url_for('loginpage'))
            else:
                flash("Email id or phone number already exist.")
                return redirect(url_for('registerpage'))
                
        else:
            cursor.execute("select * from Customer where email='{}' or phone='{}'".format(email,phone))
            res = cursor.fetchall()
            if res==[]:
                cursor.execute("insert into Customer(name,email,phone,address,password)values('{}','{}','{}','{}','{}')".format(
                    name,email,phone,address,password))
                con.commit()
                con.close()
                flash("Registration success")
                return redirect(url_for('loginpage'))
            else:
                flash("Email id or phone number already exist.")
                return redirect(url_for('registerpage'))
            
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        ltype = request.form['ltype']
        con = dbconnection()
        cursor = con.cursor()
        if ltype=='Manufacturer':
            cursor.execute("select * from Manufacturer where email='{}' and password='{}'".format(email,password))
            res = cursor.fetchall()
            if res==[]:
                flash("Failed! Invalid Email or Password")
                return redirect(url_for('loginpage'))
            else:
                session['mid']=res[0][0]
                return redirect(url_for('addproductpage'))
        elif ltype=='Seller':
            cursor.execute("select * from seller where email='{}' and password='{}'".format(email,password))
            res = cursor.fetchall()
            if res==[]:
                flash("Failed! Invalid Email or Password")
                return redirect(url_for('loginpage'))
            else:
                session['sid']=res[0][0]
                return redirect(url_for('purchasedproductspage'))
            
        elif ltype=='Customer':
            cursor.execute("select * from customer where email='{}' and password='{}'".format(email,password))
            res = cursor.fetchall()
            if res==[]:
                flash("Failed! Invalid Email or Password")
                return redirect(url_for('loginpage'))
            else:
                session['cid']=res[0][0]
                return redirect(url_for('verifyproductspage'))


def generate_qr(pname, pid, price):
    # Set image dimensions and background color
    id_card_width, id_card_height = 400, 600
    background_color = (255, 255, 255)  # White background

    # Create a blank ID card image
    id_card = Image.new('RGB', (id_card_width, id_card_height), background_color)
    draw = ImageDraw.Draw(id_card)

    # Load font
    font = ImageFont.truetype("arial.ttf", size=20)

    # Generate and place the QR code
    qr = qrcode.make(pid)
    qr = qr.resize((210, 210))
    qr_x, qr_y = 95, 200  # Place QR code in the middle of the ID card
    id_card.paste(qr, (qr_x, qr_y))

    # Add product details below the QR code
    text_start_y = qr_y + 210 + 10  # QR code bottom + padding
    draw.text((id_card_width // 2, text_start_y), f"Product Name: {pname}", font=font, fill="black", anchor="ms")
    draw.text((id_card_width // 2, text_start_y + 40), f"Product Id: {pid}", font=font, fill="black", anchor="ms")
    draw.text((id_card_width // 2, text_start_y + 80), f"Price: {price}", font=font, fill="black", anchor="ms")

    # Save the ID card
    id_card_path = f"static/uploads/qrcodes/{pid}.png"
    id_card.save(id_card_path)
    return id_card_path

@app.route('/saveproduct', methods=['GET', 'POST'])
def saveproduct():
    pname = request.form['pname']
    pid = request.form['pid']
    price = request.form['price']
    des = request.form['des']
    mfg_date = request.form['mfg_date']
    exp_date = request.form['exp_date']
    ingredients = request.form['ingredients']
    image_file = request.files['image']  # Image input field name should be 'image'

    con = dbconnection()
    cursor = con.cursor()

    cursor.execute("SELECT * FROM products WHERE pid = %s", (pid,))
    res = cursor.fetchall()

    if res == []:
        # Save image
        image_filename = None
        if image_file and image_file.filename != '':
            filename = secure_filename(image_file.filename)
            image_filename = f"{pid}_{filename}"
            image_path = os.path.join('static/images/productimages', image_filename)
            image_file.save(image_path)

        # Generate QR code path
        qr_path = generate_qr(pname, pid, price)

        # Insert product details along with image filename
        cursor.execute("""
            INSERT INTO products (pname, pid, price, des, qrpath, productimage,mid,mfg_date,exp_date,ingredients )
            VALUES (%s, %s, %s, %s, %s, %s, %s,%s, %s, %s)
        """, (pname, pid, price, des, qr_path,image_filename, int(session['mid']),mfg_date,exp_date,ingredients ))
        
        con.commit()
        con.close()

        flash("Product Saved. Download QR code from Product List.")
        return redirect(url_for('addproductpage'))
    else:
        flash("Product ID already exists.")
        con.close()
        return redirect(url_for('addproductpage'))


@app.route('/search_product')
def search_product():
    con = dbconnection()
    cursor = con.cursor()

    search_query = request.args.get('query', '')
    if search_query:
        # Secure parameterized query
        cursor.execute("""
            SELECT * FROM products 
            WHERE (pname LIKE %s OR pid LIKE %s) AND mid = %s
        """, (f"%{search_query}%", f"%{search_query}%", int(session['mid'])))

    res = cursor.fetchall()
    con.close()

    if res:
        return render_template_string("""
    {% for r in res %}
    <div class="bg-white rounded-lg shadow-md overflow-hidden">
        <div class="bg-pink-100 text-pink-600 font-bold text-center py-2">Product Details</div>
        <img src="{{ url_for('static', filename='images/productimages/' + r[6]) }}" alt="Product Image" class="w-full h-48 object-cover">
        <div class="p-4">
            <p class="mb-2"><span class="font-semibold text-pink-600">Product Name:</span> {{ r[1] }}</p>
            <p class="mb-2"><span class="font-semibold text-pink-600">Product ID:</span> {{ r[2] }}</p>
            <p class="mb-2"><span class="font-semibold text-pink-600">Price:</span> ₹{{ r[3] }}</p>
            <p class="mb-2">
                <span class="font-semibold text-pink-600">Description:</span>
                <textarea rows="2" readonly class="w-full mt-1 p-2 bg-gray-100 rounded text-sm resize-none">{{ r[4] }}</textarea>
            </p>

            <!-- Manufacturing Date -->
            <p class="mb-2"><span class="font-semibold text-pink-600">Manufacturing Date:</span> {{ r[8] }}</p>

            <!-- Expiry Date -->
            <p class="mb-2"><span class="font-semibold text-pink-600">Expiry Date:</span> {{ r[9] }}</p>

            <!-- Ingredients -->
            <p class="mb-2">
                <span class="font-semibold text-pink-600">Ingredients:</span>
                <textarea rows="2" readonly class="w-full mt-1 p-2 bg-gray-100 rounded text-sm resize-none">{{ r[10] }}</textarea>
            </p>

            <div class="flex flex-col gap-2 mt-4">
                <a href="sellproduct?id={{ r[0] }}" 
                   class="text-center bg-pink-500 hover:bg-pink-600 text-white py-2 rounded-md font-semibold">
                   Sell Product
                </a>
                <a href="../{{ r[5] }}" 
                   class="text-center bg-gray-800 hover:bg-gray-900 text-white py-2 rounded-md font-semibold" 
                   download>
                   Download QR Code
                </a>
            </div>
        </div>
    </div>
    {% endfor %}
""", res=res)

    else:
        return '<p class="text-red-500 font-semibold">Products Not Found.</p>'

@app.route('/search_product2')
def search_product2():
    con = dbconnection()
    cursor = con.cursor()

    search_query = request.args.get('query', '')
    if search_query:
        # Secure parameterized query
        cursor.execute("""
            SELECT * FROM products 
            WHERE (pname LIKE %s OR pid LIKE %s) AND mid = %s
        """, (f"%{search_query}%", f"%{search_query}%", int(session['mid'])))

    res = cursor.fetchall()
    con.close()

    if res:
        return render_template_string("""
            {% for r in res %}
            <div class="bg-white rounded-lg shadow-md overflow-hidden">
                <div class="bg-pink-100 text-pink-600 font-bold text-center py-2">Product Details</div>
                <img src="../static/images/productimages/{{ r[6] }}" alt="Product Image"
                    class="w-full h-48 object-cover">
                <div class="p-4">
                    <p class="mb-2"><span class="font-semibold text-pink-600">Product Name:</span> {{ r[1] }}</p>
                    <p class="mb-2"><span class="font-semibold text-pink-600">Product ID:</span> {{ r[2] }}</p>
                    <p class="mb-2"><span class="font-semibold text-pink-600">Price:</span> ₹{{ r[3] }}</p>
                    <p class="mb-2">
                        <span class="font-semibold text-pink-600">Description:</span>
                        <textarea rows="3" readonly
                            class="w-full mt-1 p-2 bg-gray-100 rounded text-sm resize-none">{{ r[4] }}</textarea>
                    </p>

                </div>
            </div>
            {% endfor %}
        """, res=res)
    else:
        return '<p class="text-red-500 font-semibold">Products Not Found.</p>'



@app.route('/sell')
def sell():
    sid = request.args.get('sid')
    pid = request.args.get('pid')
    con = dbconnection()
    cursor = con.cursor()
    cursor.execute("select * from products where id={} and mid={}".format(int(pid),int(session['mid'])))
    res = cursor.fetchall()
    productserialid = res[0][2]
    cursor.execute("insert into transactions (sid,mid,pid,productserial) values ({},{},{},'{}')".format(
       int(sid), int(session['mid']), int(pid), productserialid
    ))
    con.commit()
    cursor.close()
    con.close()
    myblockchain.add_block(sid, session['mid'], productserialid)
    myblockchain.save_chain()
    flash("Product Sold and Details Stored in BlockChain")
    return redirect(url_for('mviewproductspage'))


@app.route('/checkproductqr/<decodedText>', methods=['GET'])
def mark_attendance(decodedText):
    winsound.Beep(1000,1000)
    con = dbconnection()
    cursor = con.cursor()
    qrdata = decodedText.strip()
    verificationresult="Fake"

    # Check if the USN exists in the student registration table
    cursor.execute("SELECT * from products where pid='{}'".format(
        qrdata
    ))
    result = cursor.fetchall()
    blocks = myblockchain.get_blocks()
    for block in blocks:
        if block[4] is not None:  # Ensure block[2] is not None
            if qrdata in block[4]:
                verificationresult="Genuine"
            else:
                verificationresult="Fake"
                
    if not result and verificationresult=="Fake":
        return jsonify({"message": "Product seems to be fake Details not found in BlockChain"}), 404

    return jsonify({"message":" Product is Genuine! "})

@app.route('/csavefeedback', methods=['GET', 'POST'])
def csavefeedback():
    if request.method == 'POST':
        sid = request.form['sid']
        star = request.form['star']
        description = request.form['description']
        con = dbconnection()
        cursor = con.cursor()
        cursor.execute("insert into customerfeedbacks(rating,description,cid,sid)values('{}','{}',{},{})".format(
            int(star),description,int(session['cid']),int(sid)))
        con.commit()
        con.close()
        message = Markup("<h3>Success! Feedback sent</h3>")
        flash(message)
        return redirect(url_for('customerfeedbackpage'))
    
@app.route('/ssavefeedback', methods=['GET', 'POST'])
def ssavefeedback():
    if request.method == 'POST':
        mid = request.form['mid']
        star = request.form['star']
        description = request.form['description']
        con = dbconnection()
        cursor = con.cursor()
        cursor.execute("insert into sellerfeedbacks(rating,description,sid,mid)values('{}','{}',{},{})".format(
            int(star),description,int(session['sid']),int(mid)))
        con.commit()
        con.close()
        message = Markup("<h3>Success! Feedback sent</h3>")
        flash(message)
        return redirect(url_for('sellergivefeedbackpage'))
































if __name__ == '__main__':
    app.run(debug=True,host='0.0.0.0',port=5000)