from flask import Flask, request, jsonify, g
from flask_migrate import Migrate
from flask_login import LoginManager, login_required, current_user
from enum import Enum
from datetime import datetime
from flask_login import UserMixin
import importlib
from extensions import db, ma
from models import User, JobListing, Message, UserType
from job_seeker import job_seeker_bp
from profile_management import profile_management_bp



app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///helpmate.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)
ma.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(job_seeker_bp)
app.register_blueprint(profile_management_bp)

@app.route('/')
def index():
    return "Hello, Help Mate!"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()

    user_type = data.get('user_type')
    username = data.get('username')
    email = data.get('email')
    password = data.get('password')
    skills = data.get('skills')
    experience = data.get('experience')
    company_name = data.get('company_name')
    company_description = data.get('company_description')
    company_website = data.get('company_website')

    user = User.query.filter_by(email=email).first()
    if user:
        return jsonify({"error": "User with this email already exists"}), 409

    new_user = User(user_type=UserType[user_type.upper()], username=username, email=email, password=password, skills=skills, experience=experience, company_name=company_name, company_description=company_description, company_website=company_website)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User registered successfully"}), 201

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()

    email = data.get('email')
    password = data.get('password')

    user = User.query.filter_by(email=email).first()
    if user and user.password == password:
        # In a real-world application, you should generate an authentication token here
        return jsonify({"message": "Logged in successfully"}), 200

    return jsonify({"error": "Invalid email or password"}), 401

@app.route('/users')
def get_users():
    users = User.query.all()
    users_list = [{"id": user.id, "username": user.username, "email": user.email} for user in users]
    return jsonify(users_list), 200

@app.route('/job_listings', methods=['GET', 'POST'])
def job_listings():
    if request.method == 'GET':
        job_listings = JobListing.query.all()
        job_listings_list = [{"id": listing.id, "title": listing.title, "description": listing.description, "employer_id": listing.employer_id} for listing in job_listings]
        return jsonify(job_listings_list), 200
    elif request.method == 'POST':
        data = request.get_json()
        new_listing = JobListing(title=data['title'], description=data['description'], employer_id=data['employer_id'])
        db.session.add(new_listing)
        db.session.commit()
        return jsonify({"message": "Job listing created successfully"}), 201

@app.route('/job_listings/<int:listing_id>', methods=['GET', 'PUT', 'DELETE'])
def job_listing(listing_id):
    listing = JobListing.query.get_or_404(listing_id)

    if request.method == 'GET':
        response = {
            "id": listing.id,
            "title": listing.title,
            "description": listing.description,
            "employer_id": listing.employer_id
        }
        return jsonify(response), 200
    elif request.method == 'PUT':
        data = request.get_json()
        listing.title = data['title']
        listing.description = data['description']
        listing.employer_id = data['employer_id']
        db.session.commit()
        return jsonify({"message": "Job listing updated successfully"}), 200
    elif request.method == 'DELETE':
        db.session.delete(listing)
        db.session.commit()
        return jsonify({"message": "Job listing deleted successfully"}), 200

class MessageSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Message
        include_fk = True
        load_instance = True

message_schema = MessageSchema()
messages_schema = MessageSchema(many=True)

@app.route('/send_message', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()

    recipient_id = data.get('recipient_id')
    content = data.get('content')

    if not recipient_id or not content:
        return jsonify({"error": "Missing recipient ID or content"}), 400

    recipient = User.query.get(recipient_id)
    if not recipient:
        return jsonify({"error": "Recipient not found"}), 404

    message = Message(sender_id=current_user.id, recipient_id=recipient_id, content=content)
    db.session.add(message)
    db.session.commit()

    return jsonify({"message": "Message sent successfully"}), 201

@app.route('/conversation/<int:user2_id>', methods=['GET'])
@login_required
def get_conversation(user2_id):
    user1_id = current_user.id

    if not user2_id:
        return jsonify({"error": "Missing recipient ID"}), 400

    recipient = User.query.get(user2_id)
    if not recipient:
        return jsonify({"error": "Recipient not found"}), 404

    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    messages = Message.query.filter(
        (Message.sender_id == user1_id) & (Message.recipient_id == user2_id) |
        (Message.sender_id == user2_id) & (Message.recipient_id == user1_id)
    ).order_by(Message.timestamp.desc()).paginate(page, per_page, error_out=False)

    messages_list = messages_schema.dump(messages.items)

    response = {
        "messages": messages_list,
        "total_pages": messages.pages,
        "current_page": messages.page,
        "has_prev": messages.has_prev,
        "has_next": messages.has_next,
        "prev_page": messages.prev_num,
        "next_page": messages.next_num
    }

    return jsonify(response), 200


profile_management = importlib.import_module("profile_management")
profile_management_bp = profile_management.profile_management_bp

if __name__ == '__main__':
    app.run(debug=True)