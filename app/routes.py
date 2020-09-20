from datetime import datetime
from flask import render_template, flash, redirect, url_for, request
from flask_login import current_user, login_user, logout_user, login_required
from werkzeug.urls import url_parse
from app import appl, db
from app.forms import LoginForm, RegistrationForm, FootballForm, RecieptForm, PetForm, EditProfileForm, \
    ResetPasswordForm, PostForm, ResetPasswordRequestForm
from app.models import User, Post
from app.email import send_password_reset_email


@appl.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()


@appl.route("/", methods=["GET", "POST"])
@appl.route("/index", methods=["GET", "POST"])
@login_required
def index():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash("Your post was added!")
        return redirect(url_for("index"))
    page = request.args.get("page", 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, appl.config["POSTS_PER_PAGE"], False)
    next_url = url_for("index", page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for("index", page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("index.html", title="Home page", form=form,
                           posts=posts.items, next_url=next_url, prev_url=prev_url)


@appl.route("/explore")
@login_required
def explore():
    page = request.args.get("page", 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, appl.config["POSTS_PER_PAGE"], False)
    next_url = url_for("explore", page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for("explore", page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("index.html", title="Explore", posts=posts.items,
                           next_url=next_url, prev_url=prev_url)

@appl.route("/login", methods=["GET", "POST"])
def login():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash("Invalid username or password")
            return redirect(url_for("login"))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get("next")
        if not next_page or url_parse(next_page).netloc != "":
            return redirect(url_for("index"))
        return redirect(next_page)
    return render_template("login.html", title="Sign In", form=form)


@appl.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("index"))


@appl.route("/register", methods=["GET", "POST"])
def register():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash("Congradulation, you are now a rgistered user")
        return redirect(url_for("login"))
    return render_template("register.html", title="Register", form=form)


@appl.route("/user/<username>")
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404(
        description="User with username >> {} << is not found".format(username))
    page = request.args.get("page", 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, appl.config["POSTS_PER_PAGE"], False)
    next_url = url_for("user", username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for("user", username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template("user.html", user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@appl.route("/users")
def users():
    users = User.query.all()
    return render_template("users.html", users=users)


@appl.route("/edit_profile", methods=["GET", "POST"])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        current_user.set_password(form.new_password.data)
        db.session.commit()
        flash("Your changes have been saved.")
        return redirect(url_for("edit_profile"))
    elif request.method == "GET":
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template("edit_profile.html", title="Edit profile", form=form)


@appl.route("/reset_password_request", methods=["GET", "POST"])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash("Check your email to reset your password")
        return redirect(url_for("login"))
    return render_template("reset_password_request.html", title='Reset Password', form=form)


@appl.route("/reset_password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for("index"))
    user = User.verify_reset_password_token(token)
    if not user:
        # add flash("user not found or time expired")
        return redirect(url_for("index"))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.new_password.data)
        db.session.commit()
        flash("Your password has been changed.")
        return redirect(url_for("login"))
    return render_template("reset_password.html", form=form)


@appl.route("/follow/<username>")
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("User {} not found.".format(username))
        return redirect(url_for("index"))
    if user == current_user:
        flash("You cannot follow yourself!")
        return redirect(url_for("user", username=username))
    current_user.follow(user)
    db.session.commit()
    flash("You are following {}!".format(username))
    return redirect(url_for("user", username=username))


@appl.route("/unfollow/<username>")
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash("User {} not found.".format(username))
        return redirect(url_for("index"))
    if user == current_user:
        flash("You cannot unfollow yourself!")
        return redirect(url_for("user", username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash("You are not following {} now.".format(username))
    return redirect(url_for("user", username=username))



###
@appl.route("/football", methods=["GET", "POST"])
@login_required
def football():
    form = FootballForm()
    if form.validate_on_submit():
        flash("{} {} с номером {} был добавлен в твою команду".format(
            "".join(form.position.data), form.player_name.data, form.player_number.data))
        return redirect(url_for('football'))
    return render_template("football.html", form=form)


@appl.route("/reciept", methods=["GET", "POST"])
def reciept():
    recform = RecieptForm()
    if recform.validate_on_submit():
        if recform.salt.data == ["2"]:
            salt = "не "
        else:
            salt = ""
        flash("Вы доабавили новый рецепт и {}посолили".format(salt))
        return redirect(url_for('reciept'))
    return render_template("reciept.html", form=recform)


@appl.route("/pet", methods=["GET", "POST"])
def pet():
    form = PetForm()
    if form.validate_on_submit():
        flash("You added 2 pets: {} {} and {} {}")#.format(
            #form.pet_1.data, form.pet_1_name.data, form.pet_2.data, form.pet_2_name.data))
        return redirect(url_for('pet'))
    return render_template("pet.html", form=form)
