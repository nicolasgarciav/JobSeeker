from flask import Blueprint, request, jsonify
from extensions import db
from models import JobListing, JobApplication, User, SavedJob
from flask_login import login_required


job_seeker_bp = Blueprint('job_seeker', __name__)

@job_seeker_bp.route('/job_listings', methods=['GET'])
def get_job_listings():
    job_listings = JobListing.query.all()
    job_listings_list = [{"id": listing.id, "title": listing.title, "description": listing.description, "employer_id": listing.employer_id} for listing in job_listings]
    return jsonify(job_listings_list), 200

@job_seeker_bp.route('/job_listings/<int:listing_id>', methods=['GET'])
def get_job_listing(listing_id):
    listing = JobListing.query.get_or_404(listing_id)
    response = {
        "id": listing.id,
        "title": listing.title,
        "description": listing.description,
        "employer_id": listing.employer_id
    }
    return jsonify(response), 200

@job_seeker_bp.route('/job_listings/<int:listing_id>/apply', methods=['POST'])
def apply_for_job(listing_id):
    data = request.get_json()

    job_listing = JobListing.query.get_or_404(listing_id)
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    application = JobApplication.query.filter_by(job_listing_id=listing_id, job_seeker_id=user.id).first()
    if application:
        return jsonify({"error": "You have already applied for this job"}), 409

    new_application = JobApplication(job_listing_id=listing_id, job_seeker_id=user.id, cover_letter=data['cover_letter'])
    db.session.add(new_application)
    db.session.commit()

    return jsonify({"message": "Application submitted successfully"}), 201

@job_seeker_bp.route('/job_applications', methods=['GET'])
def get_job_applications():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    job_applications = JobApplication.query.filter_by(job_seeker_id=user.id).all()
    job_applications_list = [{"id": application.id, "job_listing_id": application.job_listing_id, "job_seeker_id": application.job_seeker_id, "cover_letter": application.cover_letter} for application in job_applications]
    return jsonify(job_applications_list), 200

@job_seeker_bp.route('/save_job/<int:listing_id>', methods=['POST'])
@login_required
def save_job(listing_id):
    job_listing = JobListing.query.get_or_404(listing_id)

    saved_job = SavedJob.query.filter_by(job_seeker_id=current_user.id, job_listing_id=listing_id).first()
    if saved_job:
        return jsonify({"error": "Job already saved"}), 400

    new_saved_job = SavedJob(job_seeker_id=current_user.id, job_listing_id=listing_id)
    db.session.add(new_saved_job)
    db.session.commit()

    return jsonify({"message": "Job saved successfully"}), 200

@job_seeker_bp.route('/saved_jobs', methods=['GET'])
@login_required
def get_saved_jobs():
    saved_jobs = SavedJob.query.filter_by(job_seeker_id=current_user.id).all()
    saved_job_listings = [{"id": saved_job.job_listing.id, "title": saved_job.job_listing.title, "description": saved_job.job_listing.description, "employer_id": saved_job.job_listing.employer_id} for saved_job in saved_jobs]
    return jsonify(saved_job_listings), 200

@job_seeker_bp.route('/unsave_job/<int:listing_id>', methods=['DELETE'])
@login_required
def unsave_job(listing_id):
    saved_job = SavedJob.query.filter_by(job_seeker_id=current_user.id, job_listing_id=listing_id).first()
    if not saved_job:
        return jsonify({"error": "Job not found in saved jobs"}), 404

    db.session.delete(saved_job)
    db.session.commit()

    return jsonify({"message": "Job removed from saved jobs"}), 200


