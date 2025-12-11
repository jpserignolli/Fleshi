from time import timezone
from zoneinfo import ZoneInfo
from datetime import datetime, timezone
from appfleshi import database, login_manager
from flask_login import UserMixin
from sqlalchemy import Table, Column, Integer, ForeignKey


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


# Tabela auxiliar para o relacionamento de seguidores/seguidos
followers = database.Table('followers',
                           database.Column('follower_id', database.Integer, database.ForeignKey('user.id'),
                                           primary_key=True),
                           database.Column('followed_id', database.Integer, database.ForeignKey('user.id'),
                                           primary_key=True)
                           )


class User(database.Model, UserMixin):
    id = database.Column(database.Integer, primary_key=True)
    username = database.Column(database.String(20), unique=True, nullable=False)
    email = database.Column(database.String(100), unique=True, nullable=False)
    password = database.Column(database.String(60), nullable=False)
    photos = database.relationship("Photo", backref="user", lazy=True)

    # Novo relacionamento: quem este usuário está seguindo (o "followed")
    followed = database.relationship(
        'User', secondary=followers,
        primaryjoin=(followers.c.follower_id == id),
        secondaryjoin=(followers.c.followed_id == id),
        backref=database.backref('followers', lazy='dynamic'),
        lazy='dynamic'
    )

    def follow(self, user):
        """Faz o usuário atual seguir outro usuário."""
        if not self.is_following(user):
            self.followed.append(user)

    def unfollow(self, user):
        """Faz o usuário atual deixar de seguir outro usuário."""
        if self.is_following(user):
            self.followed.remove(user)

    def is_following(self, user):
        """Verifica se o usuário atual está seguindo o outro usuário."""
        return self.followed.filter(
            followers.c.followed_id == user.id
        ).count() > 0


class Photo(database.Model):
    id = database.Column(database.Integer, primary_key=True)
    file_name = database.Column(database.String(255), nullable=False, default='default.png')
    upload_date = database.Column(database.DateTime(timezone=True), nullable=False,
                                  default=lambda: datetime.now(timezone.utc))
    user_id = database.Column(database.Integer, database.ForeignKey('user.id'), nullable=False)