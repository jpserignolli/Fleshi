from flask import render_template, url_for, redirect, request
from flask_login import login_required, login_user, logout_user, current_user
from appfleshi import app, database, bcrypt
from appfleshi.forms import LoginForm, RegisterForm, PhotoForm
from appfleshi.models import User, Photo
import os
from werkzeug.utils import secure_filename


@app.route('/', methods=['GET', 'POST'])
def homepage():
    login_form = LoginForm()
    if login_form.validate_on_submit():
        user = User.query.filter_by(email=login_form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, login_form.password.data):
            login_user(user)
            return redirect(url_for('profile', user_id=user.id))
    return render_template('homepage.html', form=login_form)

@app.route("/createaccount", methods=['GET', 'POST'])
def createaccount():
    register_form = RegisterForm()
    if register_form.validate_on_submit():
        password = bcrypt.generate_password_hash(register_form.password.data)
        user = User(username=register_form.username.data, email=register_form.email.data, password=password)
        database.session.add(user)
        database.session.commit()
        login_user(user, remember=True)
        return redirect(url_for('profile', user_id=user.id))
    return render_template('createaccount.html', form=register_form)


@app.route("/profile/<user_id>", methods=['GET', 'POST'])
@login_required
def profile(user_id):
    # Garante que 'user' seja o perfil que estamos visitando
    user = User.query.get_or_404(int(user_id))

    # Se estiver visitando seu próprio perfil
    if user.id == current_user.id:
        photo_form = PhotoForm()
        if photo_form.validate_on_submit():
            file = photo_form.photo.data
            secure_name = secure_filename(file.filename)
            patch = os.path.join(os.path.abspath(os.path.dirname(__file__)), app.config["UPLOAD_FOLDER"], secure_name)
            file.save(patch)
            photo = Photo(file_name=secure_name, user_id=current_user.id)
            database.session.add(photo)
            database.session.commit()
        # Passa o 'user' (que é o current_user) e o form
        return render_template('profile.html', user=user, form=photo_form)

    # Se estiver visitando o perfil de outro usuário
    else:
        # Apenas passa o 'user' e 'form=None' (o form de foto é só para o dono do perfil)
        # O template agora usará os métodos `user.is_following(current_user)`
        return render_template('profile.html', user=user, form=None)


@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for('homepage'))

@app.route("/feed")
@login_required
def feed():
    photos = Photo.query.order_by(Photo.upload_date.desc()).all()
    return render_template("feed.html", photos=photos)


@app.route("/search", methods=["GET"])
@login_required
def search():
    query = request.args.get("q", "").strip()

    users = []
    if query:
        users = User.query.filter(User.username.ilike(f"%{query}%")).all()

    return render_template("search.html", users=users, query=query)


# --- Novas Rotas de Follow ---

@app.route('/follow/<user_id>')
@login_required
def follow(user_id):
    user_to_follow = User.query.get(int(user_id))
    if user_to_follow is None:
        # Você pode adicionar um flash message aqui para notificar o usuário
        return redirect(url_for('feed'))

    if user_to_follow == current_user:
        # Não pode seguir a si mesmo
        return redirect(url_for('profile', user_id=user_id))

    current_user.follow(user_to_follow)
    database.session.commit()
    # Redireciona de volta para o perfil do usuário seguido
    return redirect(url_for('profile', user_id=user_id))


@app.route('/unfollow/<user_id>')
@login_required
def unfollow(user_id):
    user_to_unfollow = User.query.get(int(user_id))
    if user_to_unfollow is None:
        return redirect(url_for('feed'))

    current_user.unfollow(user_to_unfollow)
    database.session.commit()
    # Redireciona de volta para o perfil do usuário
    return redirect(url_for('profile', user_id=user_id))
