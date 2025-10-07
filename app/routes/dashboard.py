from flask import Blueprint, render_template, request, redirect, url_for, flash
from app import db

bp = Blueprint('dashboard', __name__)

@bp.route('/') # default route
def index():
    
    return render_template('dashboard/index.html')