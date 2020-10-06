#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_migrate import Migrate
from datetime import datetime
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

migrate = Migrate(app, db)


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
    citystate_id = db.Column(db.Integer, db.ForeignKey('citystate.id'), nullable=False)

class Artistgenres(db.Model):
    __tablename__ = 'artistgenres'
    id = db.Column(db.Integer, primary_key=True)
    genre = db.Column(db.String(), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)

class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():

    venues = Venue.query.order_by(Venue.id.desc()).limit(5).all()
    artists = Artist.query.order_by(Artist.id.desc()).limit(5).all()

    recent_venues = []
    recent_artists = []

    for i in range(0, len(venues)):
        v = venues[i]
        recent_venues.append({
            "venue_id": v.id,
            "venue_name": v.name,
            "venue_image_link": v.image_link
        })
    for i in range(0, len(artists)):
        a = artists[i]
        recent_artists.append({
            "artist_id": a.id,
            "artist_name": a.name,
            "artist_image_link": a.image_link
        })

    data = {
        "recent_venues_count": len(recent_venues),
        "recent_artists_count": len(recent_artists),
        "recent_venues": recent_venues,
        "recent_artists": recent_artists
    }

    return render_template('pages/home.html', data=data)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  cs = Citystate.query.order_by('state').all() # order alphabetically by state
  data = [] # list of all venues by city-state

  for i in range(0, len(cs)):
      venues = []
      for j in range(0, len(cs[i].venues)):
          shows = Show.query.filter_by(venue_id=cs[i].venues[j].id).all()
          current_date = datetime.now()
          upcoming_shows = 0
          if len(shows) > 0:
              for k in range(0, len(shows)):
                  if shows[k].start_time > current_date:
                      upcoming_shows += 1
          venues.append({
            "id": cs[i].venues[j].id,
            "name": cs[i].venues[j].name,
            "num_upcoming_shows": upcoming_shows
          })
      if len(venues) > 0:
          data.append({
            "city": cs[i].city,
            "state": cs[i].state,
            "venues": venues
          })

  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
    search_term = request.form.get('search_term')
    venues = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all() # ilike = case-insensitive
    data = []
    for i in range(0, len(venues)):
        v = venues[i]
        shows = Show.query.filter_by(venue_id=v.id).all()
        current_date = datetime.now()
        upcoming_shows = 0
        if len(shows) > 0:
            for i in range(0, len(shows)):
                if shows[i].start_time > current_date:
                    upcoming_shows += 1
        data.append({
            "id": v.id,
            "name": v.name,
            "num_upcoming_shows": upcoming_shows
        })
    response = {
        "count": len(data),
        "data": data
    }
    return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id

  v = Venue.query.get(venue_id)
  g =  Venuegenres.query.filter_by(venue_id=venue_id).all()
  genres = [];
  for i in range(0, len(g)):
      genres.append(g[i].genre)

  past_shows = []
  upcoming_shows = []

  shows = Show.query.filter_by(venue_id=venue_id).all()
  current_date = datetime.now()
  if len(shows) > 0:
      for i in range(0, len(shows)):
          artist = Artist.query.get(shows[i].artist_id)
          if shows[i].start_time > current_date:
              upcoming_shows.append({
                "artist_id": shows[i].artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(shows[i].start_time)
              })
          else:
              past_shows.append({
                "artist_id": shows[i].artist_id,
                "artist_name": artist.name,
                "artist_image_link": artist.image_link,
                "start_time": str(shows[i].start_time)
              })

  data = {
    "id": v.id,
    "name": v.name,
    "genres": genres,
    "address": v.address,
    "city": v.city,
    "state": v.state,
    "phone": v.phone,
    "website": v.website,
    "facebook_link": v.facebook_link,
    "seeking_talent": v.seeking_talent,
    "seeking_description": v.seeking_description,
    "image_link": v.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": len(past_shows),
    "upcoming_shows_count": len(upcoming_shows),
  }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    f = request.form
    print(request.form)
    seeking_talent = False;

    if 'seeking_talent' in f:
        seeking_talent = True;

    genres = request.form.getlist('genres')

    try:
        citystate = Citystate.query.filter_by(city=f['city'], state=f['state']).first()
        if citystate == None:
            citystate = Citystate(city=f['city'], state=f['state'])
            db.session.add(citystate)
            db.session.flush() # this gives you citystate.id
            print("NEW CITY-STATE ID: ", citystate.id)
        venue = Venue(name=f['name'], city=f['city'], state=f['state'], address=f['address'], phone=f['phone'], facebook_link=f['facebook_link'], image_link=f['image_link'], website=f['website'], seeking_description=f['seeking_description'], seeking_talent=seeking_talent, citystate_id=citystate.id)
        db.session.add(venue)
        db.session.flush() # this gives you access to venue.id
        venue_id = venue.id
        for g in genres:
            new_genre = Venuegenres(genre=g, venue_id=venue_id)
            db.session.add(new_genre)
            db.session.flush()
        db.session.commit()
        flash('Venue ' + f['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' + f['name'] + ' could not be listed.')
    finally:
        db.session.close()
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    try:
        venue = Venue.query.get(venue_id)
        db.session.delete(venue)
        db.session.commit()
        flash('Venue ' + venue.name + ' was successfully deleted!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' + venue.name + ' could not be deleted.')
    finally:
        db.session.close()
    return redirect(url_for('index'))


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  a = Artist.query.all()
  data = []
  for i in range(0, len(a)):
      data.append({
      "id": a[i].id,
      "name": a[i].name
      })

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():

  search_term = request.form.get('search_term')
  artists = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all() # ilike = case-insensitive
  data = []
  for i in range(0, len(artists)):
      a = artists[i]
      shows = Show.query.filter_by(artist_id=a.id).all()
      current_date = datetime.now()
      upcoming_shows = 0
      if len(shows) > 0:
          for i in range(0, len(shows)):
              if shows[i].start_time > current_date:
                  upcoming_shows += 1
      data.append({
          "id": a.id,
          "name": a.name,
          "num_upcoming_shows": upcoming_shows
      })
  response = {
      "count": len(data),
      "data": data
  }

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id

    a = Artist.query.get(artist_id)
    g =  Artistgenres.query.filter_by(artist_id=artist_id).all()
    genres = [];
    for i in range(0, len(g)):
        genres.append(g[i].genre)

    past_shows = []
    upcoming_shows = []

    shows = Show.query.filter_by(artist_id=artist_id).all()
    current_date = datetime.now()
    if len(shows) > 0:
        for i in range(0, len(shows)):
            venue = Venue.query.get(shows[i].venue_id)
            if shows[i].start_time > current_date:
                upcoming_shows.append({
                  "venue_id": shows[i].venue_id,
                  "venue_name": venue.name,
                  "venue_image_link": venue.image_link,
                  "start_time": str(shows[i].start_time)
                })
            else:
                past_shows.append({
                  "venue_id": shows[i].venue_id,
                  "venue_name": venue.name,
                  "venue_image_link": venue.image_link,
                  "start_time": str(shows[i].start_time)
                })

    data = {
        "id": a.id,
        "name": a.name,
        "genres": genres,
        "city": a.city,
        "state": a.state,
        "phone": a.phone,
        "website": a.website,
        "facebook_link": a.facebook_link,
        "seeking_venue": a.seeking_venue,
        "seeking_description": a.seeking_description,
        "image_link": a.image_link,
        "past_shows": past_shows,
        "upcoming_shows": upcoming_shows,
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

    a = Artist.query.get(artist_id)
    g =  Artistgenres.query.filter_by(artist_id=artist_id).all()
    genres = [];
    for i in range(0, len(g)):
        genres.append(g[i].genre)

    artist = {
        "id": a.id,
        "name": a.name,
        "genres": genres,
        "city": a.city,
        "state": a.state,
        "phone": a.phone,
        "website": a.website,
        "facebook_link": a.facebook_link,
        "seeking_venue": a.seeking_venue,
        "seeking_description": a.seeking_description,
        "image_link": a.image_link
    }

    form = ArtistForm(data=artist)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    f = request.form

    seeking_venue = False;
    if 'seeking_venue' in f:
        seeking_venue = True;

    genres = request.form.getlist('genres')

    artist = Artist.query.get(artist_id)

    try:
        citystate = Citystate.query.filter_by(city=f['city'], state=f['state']).first()
        if citystate == None:
            citystate = Citystate(city=f['city'], state=f['state'])
            db.session.add(citystate)
            db.session.flush() # this gives you citystate.id
            print("NEW CITY-STATE ID: ", citystate.id)
        artist.name = f['name']
        artist.city = f['city']
        artist.state = f['state']
        artist.phone = f['phone']
        artist.facebook_link = f['facebook_link']
        artist.image_link = f['image_link']
        artist.website = f['website']
        artist.seeking_description = f['seeking_description']
        artist.seeking_venue = seeking_venue
        artist.citystate_id = citystate.id

        db.session.query(Artistgenres).filter_by(artist_id=artist_id).delete()

        for g in genres:
            new_genre = Artistgenres(genre=g, artist_id=artist_id)
            db.session.add(new_genre)
            db.session.flush()
        db.session.commit()
        flash('Artist ' + f['name'] + ' was successfully updated!')
    except:
        db.session.rollback()
        flash('An error occurred. Artist ' + f['name'] + ' could not be updated.')
    finally:
        db.session.close()

    return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

    v = Venue.query.get(venue_id)
    g =  Venuegenres.query.filter_by(venue_id=venue_id).all()
    genres = [];
    for i in range(0, len(g)):
        genres.append(g[i].genre)

    venue = {
        "id": v.id,
        "name": v.name,
        "genres": genres,
        "address": v.address,
        "city": v.city,
        "state": v.state,
        "phone": v.phone,
        "website": v.website,
        "facebook_link": v.facebook_link,
        "seeking_talent": v.seeking_talent,
        "seeking_description": v.seeking_description,
        "image_link": v.image_link
    }

    form = VenueForm(data=venue)

    return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

    f = request.form
    print(request.form)

    seeking_talent = False;
    if 'seeking_talent' in f:
        seeking_talent = True;

    genres = request.form.getlist('genres')

    venue = Venue.query.get(venue_id)

    try:
        citystate = Citystate.query.filter_by(city=f['city'], state=f['state']).first()
        if citystate == None:
            citystate = Citystate(city=f['city'], state=f['state'])
            db.session.add(citystate)
            db.session.flush() # this gives you citystate.id
            print("NEW CITY-STATE ID: ", citystate.id)
        print('MADE IT PAST CITY-STATE QUERY')
        print('CITYSTATE ID IS ', citystate.id)
        print('SEEKING_TALENT IS ', seeking_talent)
        venue.name = f['name']
        venue.city = f['city']
        venue.state = f['state']
        venue.address = f['address']
        venue.phone = f['phone']
        venue.facebook_link = f['facebook_link']
        venue.image_link = f['image_link']
        venue.website = f['website']
        venue.seeking_description = f['seeking_description']
        venue.seeking_talent = seeking_talent
        venue.citystate_id = citystate.id

        db.session.query(Venuegenres).filter_by(venue_id=venue_id).delete()
        print('MADE IT PAST VENUEGENRES DELETE')

        for g in genres:
            new_genre = Venuegenres(genre=g, venue_id=venue_id)
            db.session.add(new_genre)
            db.session.flush()
        db.session.commit()
        flash('Venue ' + f['name'] + ' was successfully updated!')
    except:
        db.session.rollback()
        flash('An error occurred. Venue ' + f['name'] + ' could not be updated.')
    finally:
        db.session.close()


    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
    f = request.form

    seeking_venue = False;

    if 'seeking_venue' in f:
        seeking_venue = True;

    genres = request.form.getlist('genres')

    try:
        citystate = Citystate.query.filter_by(city=f['city'], state=f['state']).first()
        if citystate == None:
            citystate = Citystate(city=f['city'], state=f['state'])
            db.session.add(citystate)
            db.session.flush() # this gives you citystate.id
            print("NEW CITY-STATE ID: ", citystate.id)
        artist = Artist(name=f['name'], city=f['city'], state=f['state'], phone=f['phone'], facebook_link=f['facebook_link'], image_link=f['image_link'], website=f['website'], seeking_description=f['seeking_description'], seeking_venue=seeking_venue, citystate_id=citystate.id)
        db.session.add(artist)
        db.session.flush() # this gives you access to venue.id
        artist_id = artist.id
        for g in genres:
            new_genre = Artistgenres(genre=g, artist_id=artist_id)
            db.session.add(new_genre)
            db.session.flush()
        db.session.commit()
        flash('Artist ' + f['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Artist ' + f['name'] + ' could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    try:
        artist = Artist.query.get(artist_id)
        db.session.delete(artist)
        db.session.commit()
        flash('Artist ' + artist.name + ' was successfully deleted!')
    except:
        db.session.rollback()
        flash('An error occurred. Artist ' + artist.name + ' could not be deleted.')
    finally:
        db.session.close()
    return redirect(url_for('index'))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
     # displays list of shows at /shows
    shows = Show.query.all()

    data = []
    for i in range(0, len(shows)):
        venue_name = Venue.query.get(shows[i].venue_id).name
        artist = Artist.query.get(shows[i].artist_id)
        data.append({
            "venue_id": shows[i].venue_id,
            "venue_name": venue_name,
            "artist_id": shows[i].artist_id,
            "artist_name": artist.name,
            "artist_image_link": artist.image_link,
            "start_time": str(shows[i].start_time)
        })

    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
     # called to create new shows in the db, upon submitting new show listing form
    f = request.form

    try:
        show = Show(artist_id = f['artist_id'], venue_id = f['venue_id'], start_time = str(f['start_time']))
        db.session.add(show)
        db.session.commit()
        flash('Show was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. The show could not be listed.')
    finally:
        db.session.close()

    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
