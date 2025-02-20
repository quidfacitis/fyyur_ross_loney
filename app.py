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
from models import Venue, Venuegenres, Citystate, Artist, Artistgenres, Unavailabledays, Show, db
from forms import *
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)

migrate = Migrate(app, db)

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
    """ Fetches the five most recent venues and artists

    Returns:
        The pages/home.html view with the most recent venues and artists data
    """

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
  """ Organizes venues by city-state, as well as past and upcoming shows for each venue

    Returns:
        The pages/venues.html view with the organized venue data
  """

  cs = Citystate.query.order_by('state').all() # order alphabetically by state
  data = [] # list of all venues by city-state

  for i in range(0, len(cs)):
      venues = []
      for j in range(0, len(cs[i].venues)):
          v = Venue.query.get(cs[i].venues[j].id)
          shows = v.shows
          current_date = datetime.now()
          upcoming_shows = 0
          if len(shows) > 0:
              for k in range(0, len(shows)):
                  if shows[k].start_time > current_date:
                      upcoming_shows += 1
          venues.append({
            "id": v.id,
            "name": v.name,
            "num_upcoming_shows": upcoming_shows
          })
      if len(venues) > 0:
          data.append({
            "city": cs[i].city,
            "state": cs[i].state,
            "venues": venues
          })

  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
    """ Fetches venues that partially match a case-insensitive search_term from request.form

      Returns:
          The pages/search_venues.html view with the venue search results data
    """
    search_term = request.form.get('search_term')
    venues = Venue.query.filter(Venue.name.ilike(f"%{search_term}%")).all() # ilike = case-insensitive
    data = []
    for i in range(0, len(venues)):
        v = venues[i]
        shows = v.shows
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
  """ Fetches a specific venue's data using its ID, as well as its genres and shows.
    The shows are divided into "past_shows" and "upcoming_shows.""

    Args:
        venue_id: an integer that acts as the primary key of a specific venue

    Returns:
        The pages/show_venue.html view with the specific venue data
  """
  v = Venue.query.get(venue_id)
  g = v.genres
  genres = [];
  for i in range(0, len(g)):
      genres.append(g[i].genre)

  past_shows = []
  upcoming_shows = []

  shows = v.shows
  current_date = datetime.now()
  if len(shows) > 0:
      for i in range(0, len(shows)):
          artist = shows[i].artist
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
  """ Fetches the VenueForm

    Returns:
        The forms/new_venue.html view with VenueForm data
  """
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
    """ Creates a new venue, along with its associated genres and, if applicable, a new citystate, and saves them to the database in their respective "Venue," "Venuegenres" and "Citystate" tables.

      Returns:
          A redirect to the url_for('index')
    """
    f = request.form

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
    return redirect(url_for('index'))

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    """ Deletes a specific venue via its ID. Its associated "orphan" shows and genres
    are also automatically deleted in the database.

      Args:
          venue_id: an integer that acts as the primary key of a specific venue

      Returns:
          A redirect to the url_for('index')
    """
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
  """ Fetches all artists and extracts each one's "id" and "name" to be displayed

    Returns:
        The pages/artists.html view with the artists data
  """
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
  """ Fetches artists that partially match a case-insensitive search_term from request.form

    Returns:
        The pages/search_artists.html view with the artist search results data
  """
  search_term = request.form.get('search_term')
  artists = Artist.query.filter(Artist.name.ilike(f"%{search_term}%")).all() # ilike = case-insensitive
  data = []
  for i in range(0, len(artists)):
      a = artists[i]
      shows = a.shows
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
    """ Fetches a specific artists's data using its ID, as well as its genres,
        days_not_available, and shows. The shows are divided into "past_shows" and "upcoming_shows.""

      Args:
        artist_id: an integer that acts as the primary key of a specific artist

      Returns:
        The pages/show_artist.html view with the specific artist data
    """
    a = Artist.query.get(artist_id)
    g = a.genres
    genres = [];
    for i in range(0, len(g)):
        genres.append(g[i].genre)

    days_not_available = []

    # ud == "unavailable days"
    ud = a.days_not_available
    if len(ud) > 0:
        for i in range(0, len(ud)):
            days_not_available.append(ud[i].day)

    past_shows = []
    upcoming_shows = []

    shows = a.shows
    current_date = datetime.now()
    if len(shows) > 0:
        for i in range(0, len(shows)):
            venue = shows[i].venue
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
        "days_not_available": days_not_available,
    }

    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    """Fetches the ArtistForm and populates it with the existing data for the selected artist,
    which includes the artist's genres and days_not_available.

    Args:
        artist_id: an integer that acts as the primary key of a specific artist

    Returns:
        The forms/edit_artist.html view, along with the ArtistForm and the selected artist's data
    """
    a = Artist.query.get(artist_id)
    g = a.genres
    genres = [];
    for i in range(0, len(g)):
        genres.append(g[i].genre)

    days_not_available = []

    # ud == "unavailable days"
    ud = a.days_not_available
    if len(ud) > 0:
        for i in range(0, len(ud)):
            days_not_available.append(ud[i].day)

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
        "image_link": a.image_link,
        "days_not_available": days_not_available,
    }

    form = ArtistForm(data=artist)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    """Updates a specific artist using their ID, as well as updating the artist's associated genres, days_not_available and city-state.

    Args:
        artist_id: an integer that acts as the primary key of a specific artist

    Returns:
        A redirect to the url_for('show_artist'), along with the updated artist's ID
    """
    f = request.form

    seeking_venue = False;
    if 'seeking_venue' in f:
        seeking_venue = True;

    genres = request.form.getlist('genres')
    days_not_available = request.form.getlist('days_not_available')
    artist = Artist.query.get(artist_id)

    try:
        citystate = Citystate.query.filter_by(city=f['city'], state=f['state']).first()
        if citystate == None:
            citystate = Citystate(city=f['city'], state=f['state'])
            db.session.add(citystate)
            db.session.flush() # this gives you citystate.id
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

        db.session.query(Unavailabledays).filter_by(artist_id=artist_id).delete()

        for day in days_not_available:
            new_day = Unavailabledays(day=day, artist_id=artist_id)
            db.session.add(new_day)
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
    """Fetches the VenueForm and populates it with the existing data for the selected venue,
    which includes the venue's genres.

    Args:
        venue_id: an integer that acts as the primary key of a specific venue

    Returns:
        The forms/edit_venue.html view, along with the VenueForm and the selected venue's data
    """
    v = Venue.query.get(venue_id)
    g = v.genres
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
    """Updates a specific venue using its ID, as well as updating the venues's associated genres and city-state.

    Args:
        venue_id: an integer that acts as the primary key of a specific venue

    Returns:
        A redirect to the url_for('show_venue'), along with the updated venue's ID
    """
    f = request.form

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
  """Fetches ArtistForm

  Returns:
    The forms/new_artist.html view with the ArtistForm data
  """
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    """ Creates a new artist, along with its associated genres, days_not_available, and if applicable, a new citystate, and saves them to the database in their respective "Artiste," "Artistgenres" and "Citystate" tables.

      Returns:
          A redirect to the url_for('index')
    """
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
        artist = Artist(name=f['name'], city=f['city'], state=f['state'], phone=f['phone'], facebook_link=f['facebook_link'], image_link=f['image_link'], website=f['website'], seeking_description=f['seeking_description'], seeking_venue=seeking_venue, citystate_id=citystate.id)
        db.session.add(artist)
        db.session.flush() # this gives you access to artist.id
        artist_id = artist.id
        for g in genres:
            new_genre = Artistgenres(genre=g, artist_id=artist_id)
            db.session.add(new_genre)
            db.session.flush()
        if 'days_not_available' in f: # add unavailable days to the 'unavailabledays' table
            unavailabledays = request.form.getlist('days_not_available')
            for day in unavailabledays:
                new_day = Unavailabledays(day=day, artist_id=artist_id)
                db.session.add(new_day)
                db.session.flush()
        db.session.commit()
        flash('Artist ' + f['name'] + ' was successfully listed!')
    except:
        db.session.rollback()
        flash('An error occurred. Artist ' + f['name'] + ' could not be listed.')
    finally:
        db.session.close()
    return redirect(url_for('index'))

@app.route('/artists/<artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
    """ Deletes a specific artist via its ID. Its associated "orphan" shows, genres,
    and days_not_available are also automatically deleted in the database.

      Args:
          artist_id: an integer that acts as the primary key of a specific artist

      Returns:
          A redirect to the url_for('index')
    """
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
    """ Fetches all shows and their essential artist and venue information to be displayed

      Returns:
          The pages/shows.html view with the shows data
    """
    shows = Show.query.all()

    data = []
    for i in range(0, len(shows)):
        data.append({
            "venue_id": shows[i].venue_id,
            "venue_name": shows[i].venue.name,
            "artist_id": shows[i].artist_id,
            "artist_name": shows[i].artist.name,
            "artist_image_link": shows[i].artist.image_link,
            "start_time": str(shows[i].start_time)
        })

    return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  """Fetches ShowForm

  Returns:
    The forms/new_show.html view with the ShowForm data
  """
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
    """Creates a new show and adds it to the database. If a show's start_date falls
    on a day of the week the artist is not available, the show is not created, and an error
    message is displayed to the user.

    Returns:
        A redirect to url_for('index')
    """

    f = request.form

    datetime_object = datetime.strptime(f['start_time'], '%Y-%m-%d %H:%M:%S')
    weekdays = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    weekday = weekdays[datetime_object.weekday()]

    a = Artist.query.get(f['artist_id'])

    # ud == "unavailable days"
    ud = a.days_not_available

    # Check if show conflicts with artist's availability
    if len(ud) > 0:
        ud_artist = []
        for i in range(0, len(ud)):
            ud_artist.append(ud[i].day)
        if weekday in ud_artist:
            flash('Unable to create show. Artist not available on ' + weekday + 's.')
            return redirect(url_for('index'))

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

    return redirect(url_for('index'))

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
