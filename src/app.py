from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sys
import os

from model.model_api import AppDatabase
from utils import logger_helper, commons

logger = logger_helper.get_logger(__name__)

app = Flask('PCMStartListGenerator')
app.secret_key = 'your-secret-key-here'  # Change this in production

# Initialize database with PostgreSQL support
db_url = os.getenv('DATABASE_URL')
db = AppDatabase(db_url=db_url)

@app.route('/')
def index():
    """Home page with navigation to all features"""
    return render_template('index.html')

@app.route('/databases')
def list_databases():
    """List all PCM databases"""
    try:
        databases = db.get_pcm_databases()
        return render_template('databases.html', databases=databases)
    except Exception as e:
        logger.error(f"Error listing databases: {str(e)}")
        flash(f"Error loading databases: {str(e)}", 'error')
        return render_template('databases.html', databases=[])

@app.route('/import_database', methods=['GET', 'POST'])
def import_database():
    """Import a new PCM database"""
    if request.method == 'POST':
        pcm_database_name = request.form.get('pcm_database_name')
        pcm_version = request.form.get('pcm_version', '2025')
        
        try:
            db.import_pcm_data(pcm_version, pcm_database_name)
            flash(f"Successfully imported database '{pcm_database_name}' for PCM {pcm_version}", 'success')
            return redirect(url_for('list_databases'))
        except Exception as e:
            logger.error(f"Error importing database: {str(e)}")
            flash(f"Error importing database: {str(e)}", 'error')
    
    return render_template('import_database.html')

@app.route('/races/<int:database_id>')
def show_races(database_id):
    """Show races for a specific database"""
    race_name_filter = request.args.get('race_name', '')
    
    try:
        races = db.get_pcm_races(database_id, race_name_filter if race_name_filter else None)
        # Get database info for display
        databases = db.get_pcm_databases()
        database_info = None
        for db_row in databases:
            if db_row['id'] == database_id:
                database_info = db_row
                break
        
        return render_template('races.html', 
                             races=races, 
                             database_id=database_id,
                             database_info=database_info,
                             race_name_filter=race_name_filter)
    except Exception as e:
        logger.error(f"Error loading races: {str(e)}")
        flash(f"Error loading races: {str(e)}", 'error')
        return redirect(url_for('list_databases'))

@app.route('/start_lists')
def show_start_lists():
    """Show all existing start lists"""
    pcm_version = request.args.get('pcm_version')
    pcm_database_name = request.args.get('pcm_database_name')
    
    try:
        start_lists = db.get_start_lists(pcm_version, pcm_database_name)
        databases = db.get_pcm_databases()
        return render_template('start_lists.html', 
                             start_lists=start_lists,
                             databases=databases,
                             selected_version=pcm_version,
                             selected_database=pcm_database_name)
    except Exception as e:
        logger.error(f"Error loading start lists: {str(e)}")
        flash(f"Error loading start lists: {str(e)}", 'error')
        return render_template('start_lists.html', start_lists=[], databases=[])

@app.route('/generate_start_list', methods=['GET', 'POST'])
def generate_start_list():
    """Generate a new start list"""
    if request.method == 'POST':
        database_id = request.form.get('database_id')
        race_id = request.form.get('race_id')
        race_year = request.form.get('race_year')
        
        try:
            # Here you would call your start list generation logic
            # This would need to be implemented based on your existing API
            flash(f"Start list generation initiated for race {race_id} in year {race_year}", 'info')
            return redirect(url_for('show_start_lists'))
        except Exception as e:
            logger.error(f"Error generating start list: {str(e)}")
            flash(f"Error generating start list: {str(e)}", 'error')
    
    # Get databases for the form
    try:
        databases = db.get_pcm_databases()
        return render_template('generate_start_list.html', databases=databases)
    except Exception as e:
        logger.error(f"Error loading databases for start list generation: {str(e)}")
        flash(f"Error loading databases: {str(e)}", 'error')
        return render_template('generate_start_list.html', databases=[])

@app.route('/api/races/<int:database_id>')
def api_get_races(database_id):
    """API endpoint to get races for a database (for AJAX calls)"""
    try:
        races = db.get_pcm_races(database_id)
        return jsonify([dict(row) for row in races])
    except Exception as e:
        logger.error(f"API error getting races: {str(e)}")
        return jsonify([]), 500

if __name__ == '__main__':
    logger.info(f"Starting application on port {commons.APP_PORT}")
    app.run(debug=False, host='0.0.0.0', port=commons.APP_PORT)
