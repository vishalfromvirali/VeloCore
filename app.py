from flask import Flask, request, render_template, url_for, redirect,session
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail, Message
import uuid
app = Flask(__name__)

# --- Configurations ---
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///new_user4.db'
app.config['SECRET_KEY'] = 'secret'

app.config['MAIL_SERVER'] = 'smtp.gmail.com'       # ✅ fixed typo
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True                  # ✅ fixed TLS key
app.config['MAIL_USERNAME'] = 'bb4106402@gmail.com'
app.config['MAIL_PASSWORD'] = 'qjrhwiwnscjlsvbi'

db = SQLAlchemy(app)
mail = Mail(app)

# --- Database Model ---
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(50), nullable=False)
    mail_recive = db.Column(db.String(50), unique=True, nullable=False)
    coupon = db.Column(db.Boolean, nullable=False)
    coupon_code = db.Column(db.String(50), nullable=False)


def generate_coupon_key():
    return str(uuid.uuid4()).replace('-','').upper()[:12]
# --- Routes ---


@app.route('/', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        user_name = request.form['user']
        password = request.form['password']
        mail_recive = request.form['mail']
        code=generate_coupon_key()
        new_user = User(user=user_name, password=password, mail_recive=mail_recive, coupon=True,coupon_code=code)
        db.session.add(new_user)
        db.session.commit()
        #session['coupon']='COUPON@982984fuhsui2828'
        # Send mail after registration
        msg = Message(
            "Coupon Code for You 🎁",
            sender="bb4106402@gmail.com",
            recipients=[mail_recive],
            body=(f"Your coupon code is: {code}")
        )
        mail.send(msg)
        return redirect(url_for('login'))

    return render_template('index.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_name = request.form['user']
        password = request.form['password']
        user = User.query.filter_by(user=user_name, password=password).first()
        session['user_name']=user_name
        if user:
            return render_template('home.html', username=user.user)
        else:
            return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/coupon_validate', methods=['POST'])
def validate():
    # Get current logged-in user from session
    session_user = session.get('user_name')
    if not session_user:
        return redirect(url_for('login'))

    user = User.query.filter_by(user=session_user).first()
    coupon = request.form.get('coupon_code')

    # ✅ Check if user exists and coupon is valid
    if user and coupon == user.coupon_code and user.coupon:
        msg = Message(
            "Your coupon code validated successfully",
            sender="bb4106402@gmail.com",
            recipients=[user.mail_recive],
            body="Thank you for using the coupon code"
        )
        mail.send(msg)

        # Mark coupon as used
        user.coupon = False
        db.session.commit()

        return redirect(url_for('home', flag='True',f='True'))

    # Coupon invalid or user not found
    return redirect(url_for('home', flag='False',f='True'))

@app.route('/home')
def home():
    fl=request.args.get('flag')
    return render_template('home.html',flag=fl)


@app.route('/logout')
def logout():
    session.clear()
    return render_template('index.html')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        print("✅ Database created successfully")
    app.run(debug=False,host='0.0.0.0',port=5000)
