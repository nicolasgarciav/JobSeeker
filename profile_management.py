from flask import Blueprint, request, jsonify
from extensions import db, ma
from models import User, JobListing
from flask_login import login_required, current_user
from sqlalchemy import or_

profile_management_bp = Blueprint('profile_management', __name__)

# User profile update
@profile_management_bp.route('/update_profile', methods=['PUT'])
@login_required
def update_profile():
    data = request.get_json()

    user = current_user

    user.skills = data.get('skills', user.skills)
    user.experience = data.get('experience', user.experience)
    user.company_name = data.get('company_name', user.company_name)
    user.company_description = data.get('company_description', user.company_description)
    user.company_website = data.get('company_website', user.company_website)

    if 'password' in data:
        user.password = data['password']

    db.session.commit()

    return jsonify({"message": "User profile updated successfully"}), 200

# Search functionality
@profile_management_bp.route('/search', methods=['GET'])
def search():
    keyword = request.args.get('keyword', '')
    location = request.args.get('location', '')

    query = JobListing.query.filter(
        or_(JobListing.title.contains(keyword), JobListing.description.contains(keyword))
    )

    if location:
        query = query.join(User).filter(User.location.contains(location))

    job_listings = query.all()

    job_listings_list = [{"id": listing.id, "title": listing.title, "description": listing.description, "employer_id": listing.employer_id} for listing in job_listings]
    return jsonify(job_listings_list), 200

# Pagination
@profile_management_bp.route('/users')
def get_users():
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)

    users = User.query.paginate(page, per_page, error_out=False)
    users_list = [{"id": user.id, "username": user.username, "email": user.email} for user in users.items]

    return jsonify(users_list), 200

@profile_management_bp.route('/job_listings', methods=['GET'])
def job_listings():
    if request.method == 'GET':
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)

        job_listings = JobListing.query.paginate(page, per_page, error_out=False)
        job_listings_list = [{"id": listing.id, "title": listing.title, "description": listing.description, "employer_id": listing.employer_id} for listing in job_listings.items]

        return jsonify(job_listings_list), 200
