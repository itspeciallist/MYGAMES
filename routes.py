import os
from datetime import datetime, timedelta
from flask import render_template, url_for, flash, redirect, request, abort, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from app import app, db
from models import User, Game, Comment, GameReaction, UserBan
from forms import (LoginForm, RegisterForm, ProfileUpdateForm, PasswordChangeForm, 
                   GameForm, CommentForm, BanForm, AssignRoleForm)
from utils import save_picture, admin_required, moderator_required, can_manage_games, format_datetime

@app.route('/')
def index():
    """Home page with game listings"""
    page = request.args.get('page', 1, type=int)
    genre = request.args.get('genre', '', type=str)
    search = request.args.get('search', '', type=str)
    
    query = Game.query
    
    if genre:
        query = query.filter_by(genre=genre)
    
    if search:
        query = query.filter(Game.title.contains(search) | Game.description.contains(search))
    
    games = query.order_by(Game.created_at.desc()).paginate(
        page=page, per_page=12, error_out=False)
    
    # Get available genres
    genres = db.session.query(Game.genre).distinct().all()
    genres = [g[0] for g in genres]
    
    return render_template('index.html', games=games, genres=genres, 
                         current_genre=genre, search_query=search)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """User login"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user and check_password_hash(user.password_hash, form.password.data):
            if user.is_active_ban():
                flash('თქვენი ანგარიში დაბანილია.', 'danger')
                return redirect(url_for('login'))
            
            login_user(user)
            next_page = request.args.get('next')
            flash(f'კეთილი იყოს თქვენი დაბრუნება, {user.username}!', 'success')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('არასწორი მომხმარებელის სახელი ან პაროლი.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """User registration"""
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    form = RegisterForm()
    if form.validate_on_submit():
        # Check if username or email already exists
        existing_user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.email.data)
        ).first()
        
        if existing_user:
            if existing_user.username == form.username.data:
                flash('მომხმარებელის სახელი უკვე არსებობს. გთხოვთ აირჩიოთ სხვა.', 'danger')
            else:
                flash('ელექტრონული ფოსტა უკვე რეგისტრირებულია. გთხოვთ აირჩიოთ სხვა.', 'danger')
            return render_template('register.html', form=form)
        
        user = User(
            username=form.username.data,
            email=form.email.data,
            password_hash=generate_password_hash(form.password.data)
        )
        db.session.add(user)
        db.session.commit()
        
        flash('რეგისტრაცია წარმატებული! ახლა შეგიძლიათ შესვლა.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
@login_required
def logout():
    """User logout"""
    logout_user()
    flash('შენ გახვედი სისტემიდან.', 'info')
    return redirect(url_for('index'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """User profile management"""
    if current_user.is_active_ban():
        flash('თქვენი ანგარიში დაბანილია.', 'danger')
        return redirect(url_for('index'))
    
    form = ProfileUpdateForm()
    password_form = PasswordChangeForm()
    
    if form.validate_on_submit() and 'update_profile' in request.form:
        # Check if username is being changed and if allowed
        if form.username.data != current_user.username:
            if not current_user.can_change_username():
                flash('შენ შეგიძლია თვეში წადში მხოლოდ ერთხელ შეშაცვალო მომხმარებელის სახელი.', 'danger')
                return redirect(url_for('profile'))
            
            # Check if new username exists
            existing = User.query.filter_by(username=form.username.data).first()
            if existing:
                flash('მომხმარებელის სახელი უკვე არსებობს.', 'danger')
                return redirect(url_for('profile'))
            
            current_user.username = form.username.data
            current_user.last_name_change = datetime.utcnow()
        
        # Check if email is being changed
        if form.email.data != current_user.email:
            existing = User.query.filter_by(email=form.email.data).first()
            if existing:
                flash('ელექტრონული ფოსტა უკვე არსებობს.', 'danger')
                return redirect(url_for('profile'))
            current_user.email = form.email.data
        
        # Handle profile image upload
        if form.profile_image.data:
            picture_file = save_picture(form.profile_image.data)
            current_user.profile_image = picture_file
        
        db.session.commit()
        flash('პროფილი წარმატებულად განაიხლა!', 'success')
        return redirect(url_for('profile'))
    
    if password_form.validate_on_submit() and 'change_password' in request.form:
        if check_password_hash(current_user.password_hash, password_form.current_password.data):
            current_user.password_hash = generate_password_hash(password_form.new_password.data)
            db.session.commit()
            flash('პაროლი წარმატებულად შეიცვალა!', 'success')
            return redirect(url_for('profile'))
        else:
            flash('მიმდინარე პაროლი არასწორია.', 'danger')
    
    # Pre-populate form
    if request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    
    return render_template('profile.html', form=form, password_form=password_form)

@app.route('/game/<int:game_id>')
def game_detail(game_id):
    """Game detail page"""
    game = Game.query.get_or_404(game_id)
    comments = Comment.query.filter_by(game_id=game_id).order_by(Comment.created_at.desc()).all()
    
    user_reaction = None
    if current_user.is_authenticated:
        user_reaction = GameReaction.query.filter_by(
            user_id=current_user.id, game_id=game_id
        ).first()
    
    comment_form = CommentForm()
    
    return render_template('game_detail.html', game=game, comments=comments, 
                         user_reaction=user_reaction, form=comment_form)

@app.route('/add_comment/<int:game_id>', methods=['POST'])
@login_required
def add_comment(game_id):
    """Add comment to game"""
    if current_user.is_active_ban():
        flash('თქვენი ანგარიში დაბანილია.', 'danger')
        return redirect(url_for('game_detail', game_id=game_id))
    
    game = Game.query.get_or_404(game_id)
    form = CommentForm()
    
    if form.validate_on_submit():
        comment = Comment(
            content=form.content.data,
            user_id=current_user.id,
            game_id=game_id
        )
        db.session.add(comment)
        db.session.commit()
        flash('კომენტარი შემატებულია!', 'success')
    
    return redirect(url_for('game_detail', game_id=game_id))

@app.route('/react/<int:game_id>/<reaction_type>')
@login_required
def react_to_game(game_id, reaction_type):
    """Add/remove reaction to game"""
    if current_user.is_active_ban():
        return jsonify({'error': 'Account banned'}), 403
    
    if reaction_type not in ['like', 'dislike']:
        return jsonify({'error': 'Invalid reaction'}), 400
    
    game = Game.query.get_or_404(game_id)
    existing_reaction = GameReaction.query.filter_by(
        user_id=current_user.id, game_id=game_id
    ).first()
    
    if existing_reaction:
        if existing_reaction.reaction_type == reaction_type:
            # Remove reaction if same type
            db.session.delete(existing_reaction)
            db.session.commit()
            flash('რეაქცია წაშალა!', 'info')
        else:
            # Change reaction type
            existing_reaction.reaction_type = reaction_type
            db.session.commit()
            flash(f'რეაქცია შეიცვალა {reaction_type}-ად!', 'success')
    else:
        # Add new reaction
        reaction = GameReaction(
            reaction_type=reaction_type,
            user_id=current_user.id,
            game_id=game_id
        )
        db.session.add(reaction)
        db.session.commit()
        flash(f'შენ მიუტითე {reaction_type} ამ თამაშს!', 'success')
    
    return redirect(url_for('game_detail', game_id=game_id))

@app.route('/add_game', methods=['GET', 'POST'])
@moderator_required
def add_game():
    """Add new game (moderator/admin only)"""
    form = GameForm()
    
    if form.validate_on_submit():
        game = Game(
            title=form.title.data,
            description=form.description.data,
            genre=form.genre.data,
            download_link=form.download_link.data,
            image_url=form.image_url.data,
            added_by_id=current_user.id
        )
        db.session.add(game)
        db.session.commit()
        flash('თამაში შემატებულია!', 'success')
        return redirect(url_for('index'))
    
    return render_template('add_game.html', form=form)

@app.route('/edit_game/<int:game_id>', methods=['GET', 'POST'])
@moderator_required
def edit_game(game_id):
    """Edit game (moderator/admin only)"""
    game = Game.query.get_or_404(game_id)
    form = GameForm()
    
    if form.validate_on_submit():
        game.title = form.title.data
        game.description = form.description.data
        game.genre = form.genre.data
        game.download_link = form.download_link.data
        game.image_url = form.image_url.data
        db.session.commit()
        flash('თამაში შესრულებულია!', 'success')
        return redirect(url_for('game_detail', game_id=game_id))
    
    # Pre-populate form
    if request.method == 'GET':
        form.title.data = game.title
        form.description.data = game.description
        form.genre.data = game.genre
        form.download_link.data = game.download_link
        form.image_url.data = game.image_url
    
    return render_template('add_game.html', form=form, game=game)

@app.route('/delete_game/<int:game_id>')
@moderator_required
def delete_game(game_id):
    """Delete game (moderator/admin only)"""
    game = Game.query.get_or_404(game_id)
    db.session.delete(game)
    db.session.commit()
    flash('თამაში წაშალა!', 'success')
    return redirect(url_for('index'))

@app.route('/moderator_dashboard')
@moderator_required
def moderator_dashboard():
    """Moderator dashboard"""
    recent_games = Game.query.order_by(Game.created_at.desc()).limit(10).all()
    recent_comments = Comment.query.order_by(Comment.created_at.desc()).limit(10).all()
    total_games = Game.query.count()
    total_users = User.query.count()
    total_comments = Comment.query.count()
    
    stats = {
        'total_games': total_games,
        'total_users': total_users,
        'total_comments': total_comments
    }
    
    return render_template('moderator_dashboard.html', 
                         recent_games=recent_games,
                         recent_comments=recent_comments,
                         stats=stats)

@app.route('/admin_dashboard')
@admin_required
def admin_dashboard():
    """Admin dashboard"""
    recent_games = Game.query.order_by(Game.created_at.desc()).limit(10).all()
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    recent_comments = Comment.query.order_by(Comment.created_at.desc()).limit(10).all()
    
    # Statistics
    total_games = Game.query.count()
    total_users = User.query.count()
    total_comments = Comment.query.count()
    total_admins = User.query.filter_by(role='admin').count()
    total_moderators = User.query.filter_by(role='moderator').count()
    banned_users = User.query.filter_by(is_banned=True).count()
    
    stats = {
        'total_games': total_games,
        'total_users': total_users,
        'total_comments': total_comments,
        'total_admins': total_admins,
        'total_moderators': total_moderators,
        'banned_users': banned_users
    }
    
    return render_template('admin_dashboard.html', 
                         recent_games=recent_games,
                         recent_users=recent_users,
                         recent_comments=recent_comments,
                         stats=stats)

@app.route('/manage_users')
@admin_required
def manage_users():
    """Manage users (admin only)"""
    page = request.args.get('page', 1, type=int)
    users = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=20, error_out=False)
    
    return render_template('manage_users.html', users=users)

@app.route('/ban_user/<int:user_id>', methods=['GET', 'POST'])
@moderator_required
def ban_user(user_id):
    """Ban user"""
    user = User.query.get_or_404(user_id)
    
    # Prevent self-banning and protect admins
    if user.id == current_user.id:
        flash('შენ ვერ შეგიძლია საკუთარ თავის დაბანვა.', 'danger')
        return redirect(request.referrer or url_for('index'))
    
    if user.role == 'admin':
        flash('ადმინისტრატორების დაბანვა მშა ვერაა.', 'danger')
        return redirect(request.referrer or url_for('index'))
    
    # Moderators can only apply 1-day bans, admins can set custom duration
    if current_user.role == 'moderator':
        # Apply 1-day ban
        user.is_banned = True
        user.ban_expires_at = datetime.utcnow() + timedelta(days=1)
        
        ban_record = UserBan(
            user_id=user.id,
            banned_by_id=current_user.id,
            reason='Banned by moderator',
            expires_at=user.ban_expires_at
        )
        db.session.add(ban_record)
        db.session.commit()
        
        flash(f'მომხმარებელი {user.username} დაბანილია 1 დღით.', 'success')
    else:
        # Admin can set custom ban duration
        form = BanForm()
        if form.validate_on_submit():
            user.is_banned = True
            
            if form.permanent.data:
                user.ban_expires_at = None
                expires_at = None
            else:
                expires_at = datetime.utcnow() + timedelta(days=form.duration_days.data)
                user.ban_expires_at = expires_at
            
            ban_record = UserBan(
                user_id=user.id,
                banned_by_id=current_user.id,
                reason=form.reason.data,
                expires_at=expires_at
            )
            db.session.add(ban_record)
            db.session.commit()
            
            duration_text = "permanently" if form.permanent.data else f"for {form.duration_days.data} days"
            flash(f'მომხმარებელი {user.username} დაბანილია {duration_text}.', 'success')
            return redirect(url_for('manage_users'))
        
        return render_template('ban_user.html', user=user, form=form)
    
    return redirect(request.referrer or url_for('index'))

@app.route('/unban_user/<int:user_id>')
@admin_required
def unban_user(user_id):
    """Unban user (admin only)"""
    user = User.query.get_or_404(user_id)
    user.is_banned = False
    user.ban_expires_at = None
    db.session.commit()
    
    flash(f'მომხმარებელს {user.username} სახწაფე კელ დაუბრუნდა.', 'success')
    return redirect(request.referrer or url_for('manage_users'))

@app.route('/assign_role/<int:user_id>', methods=['GET', 'POST'])
@admin_required
def assign_role(user_id):
    """Assign role to user (admin only)"""
    user = User.query.get_or_404(user_id)
    form = AssignRoleForm()
    
    if form.validate_on_submit():
        old_role = user.role
        user.role = form.role.data
        db.session.commit()
        
        flash(f'მომხმარებელის {user.username} როლი შეიცვალა {old_role}-დან {form.role.data}-მდე.', 'success')
        return redirect(url_for('manage_users'))
    
    # Pre-populate form
    if request.method == 'GET':
        form.role.data = user.role
    
    return render_template('assign_role.html', user=user, form=form)

@app.route('/delete_comment/<int:comment_id>')
@moderator_required
def delete_comment(comment_id):
    """Delete comment (moderator/admin only)"""
    comment = Comment.query.get_or_404(comment_id)
    game_id = comment.game_id
    db.session.delete(comment)
    db.session.commit()
    
    flash('კომენტარი წაშალა.', 'success')
    return redirect(url_for('game_detail', game_id=game_id))

# Error handlers
@app.errorhandler(403)
def forbidden(error):
    return render_template('403.html'), 403

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template('500.html'), 500

# Template context processors
@app.context_processor
def utility_processor():
    return dict(format_datetime=format_datetime, can_manage_games=can_manage_games)
