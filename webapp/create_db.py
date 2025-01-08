# create_db.py

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship

db = SQLAlchemy()

class Text(db.Model):
    __tablename__ = "texts"

    message_id = db.Column('message_id', db.Integer, primary_key=True)
    text = db.Column('text', db.Text)

    # Обратное отношение для Morph
    morphs = relationship('Morph', back_populates='text')  # , lazy='dynamic'
    my_metadata = relationship('Metadata', back_populates='text', uselist=False)

class Author(db.Model):
    __tablename__ = "authors"
    author_id = db.Column('author_id', db.Integer, primary_key=True)
    author_tg_id = db.Column('author_tg_id', db.Integer, primary_key=True)

class Community(db.Model):
    __tablename__ = "communities"
    community_id = db.Column('community_id', db.Integer, primary_key=True)
    community_name = db.Column('community_name', db.Text)

class Source(db.Model):
    __tablename__ = "sourses"
    source_id = db.Column('sourse_id', db.Integer, primary_key=True)
    source_name = db.Column('sourse_name', db.Text)

class Theme(db.Model):
    __tablename__ = "themes"
    theme_id = db.Column('theme_id', db.Integer, primary_key=True)
    theme_name = db.Column('theme_name', db.Text)

class Metadata(db.Model):
    __tablename__ = "metadata"
    message_id_meta = db.Column('message_id', db.Integer, ForeignKey('texts.message_id'), primary_key=True)
    text = relationship('Text', back_populates='my_metadata')
    author_id_meta = db.Column('author_id', db.Integer, ForeignKey('authors.author_id'))
    author = relationship('Author')
    source_id_meta = db.Column('sourse_id', db.Integer, ForeignKey('sourses.sourse_id'))
    source = relationship('Source')
    community_id_meta = db.Column('community_id', db.Integer, ForeignKey('communities.community_id'))
    community = relationship('Community')
    theme_id_meta = db.Column('theme_id', db.Integer, ForeignKey('themes.theme_id'))
    theme = relationship('Theme')

    date = db.Column('date', db.DateTime)

class Morph(db.Model):
    __tablename__ = "morphs"
    word_id = db.Column('id', db.Integer, primary_key=True)
    message_id_word = db.Column('message_id', db.Integer, ForeignKey('texts.message_id'))
    token = db.Column('text', db.Text)
    lemma = db.Column('lemma', db.Text)
    upos = db.Column('upos', db.Text)
    head = db.Column('head', db.Integer)
    deprel = db.Column('deprel', db.Text)
    start_char = db.Column('start_char', db.Integer)
    end_char = db.Column('end_char', db.Integer)
    ner = db.Column('ner', db.Text)
    feats = db.Column('feats', db.Text)
    misc = db.Column('misc', db.Text)

    # Добавляем отношение к Text
    text = relationship('Text', back_populates='morphs')
