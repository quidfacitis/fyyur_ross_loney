from flask_sqlalchemy import SQLAlchemy
db = SQLAlchemy()

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(200))
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    genres = db.relationship('Venuegenres', cascade='all, delete-orphan', backref='venue', lazy=True)
    shows = db.relationship('Show', cascade='all, delete-orphan', backref='venue', lazy=True)
    citystate_id = db.Column(db.Integer, db.ForeignKey('citystate.id'), nullable=False)

class Venuegenres(db.Model):
    __tablename__ = 'venuegenres'
    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)

class Citystate(db.Model):
    __tablename__ = 'citystate'
    id = db.Column(db.Integer, primary_key=True)
    city = db.Column(db.String(), nullable=False)
    state = db.Column(db.String(), nullable=False)
    venues = db.relationship('Venue', cascade='all, delete-orphan', backref='citystate', lazy=True)
    artists = db.relationship('Artist', cascade='all, delete-orphan', backref='citystate', lazy=True)

class Artist(db.Model):
    __tablename__ = 'Artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(200))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(500))
    genres = db.relationship('Artistgenres', cascade='all, delete-orphan', backref='artist', lazy=True)
    shows = db.relationship('Show', cascade='all, delete-orphan', backref='artist', lazy=True)
    days_not_available = db.relationship('Unavailabledays', cascade='all, delete-orphan', backref='artist', lazy=True)
    citystate_id = db.Column(db.Integer, db.ForeignKey('citystate.id'), nullable=False)

class Artistgenres(db.Model):
    __tablename__ = 'artistgenres'
    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)

class Unavailabledays(db.Model):
    __tablename__ = 'unavailabledays'
    id = db.Column(db.Integer, primary_key=True)
    day = db.Column(db.String(), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)

class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
