from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import sys
import os

from api import AppAPI
from utils import logger_helper, commons

logger = logger_helper.get_logger(__name__)

app = Flask('PCMStartListGenerator')
app.secret_key = 'your-secret-key-here'  # Change this in production

api = AppAPI()

@app.route('/')
def index():
    """Home page with navigation to all features"""
    return render_template('index.html')

@app.route('/databases', methods=['GET', 'POST'])
def list_databases():
    """List all PCM databases and handle import"""
    if request.method == 'POST':
        # Handle database import
        existing_file = request.form.get('existing_pcm_database_file')
        uploaded_file = request.files.get('pcm_database_file')
        pcm_database_name = request.form.get('pcm_database_name')
        pcm_version = request.form.get('pcm_version')
        logger.info(f"Importing PCM database '{pcm_database_name}' for version {pcm_version} from file: {existing_file or uploaded_file.filename if uploaded_file else 'None'}")
        if not pcm_database_name or not pcm_version:
            flash("PCM database name and version are required", 'error')
            return redirect(url_for('list_databases'))
        try:
            if existing_file:
                # Use existing file from PCM directory
                api.import_pcm_database(pcm_version, pcm_database_name)
                flash(f"Successfully imported database '{pcm_database_name}' from '{existing_file}' for PCM {pcm_version}", 'success')
            elif uploaded_file and uploaded_file.filename:
                # Save uploaded file to PCM_DATABASE_PATH
                upload_path = os.path.join(commons.PCM_DATABASE_PATH, uploaded_file.filename)
                uploaded_file.save(upload_path)
                api.import_pcm_database(pcm_version, pcm_database_name)
                flash(f"Successfully imported database '{pcm_database_name}' from uploaded file '{uploaded_file.filename}' for PCM {pcm_version}", 'success')
            else:
                flash("Please select a database file", 'error')
                
            return redirect(url_for('list_databases'))
        except Exception as e:
            logger.error(f"Error importing database: {str(e)}")
            flash(f"Error importing database: {str(e)}", 'error')
    
    # Get databases and available files for display
    try:
        databases = api.get_pcm_databases()
        
        # Get available SQLite files
        available_files = []
        if os.path.exists(commons.PCM_DATABASE_PATH):
            for file in os.listdir(commons.PCM_DATABASE_PATH):
                if file.lower().endswith(('.sqlite', '.db')):
                    file_path = os.path.join(commons.PCM_DATABASE_PATH, file)
                    file_size = os.path.getsize(file_path)
                    file_modified = os.path.getmtime(file_path)
                    available_files.append({
                        'name': file,
                        'size': file_size,
                        'modified': file_modified
                    })
        else:
            logger.error(f"PCM database path '{commons.PCM_DATABASE_PATH}' does not exist.")
        
        return render_template('databases.html', 
                             databases=databases,
                             available_files=available_files,
                             pcm_versions=commons.PCM_VERSIONS)
    except Exception as e:
        logger.error(f"Error listing databases: {str(e)}")
        flash(f"Error loading databases: {str(e)}", 'error')
        return render_template('databases.html', 
                             databases=[],
                             available_files=[],
                             pcm_versions=commons.PCM_VERSIONS)


@app.route('/races/<int:pcm_database_id>')
def show_races(pcm_database_id):
    """Show races for a specific database"""
    race_name_filter = request.args.get('race_name', '')
    
    try:
        # Get database info
        databases = api.get_pcm_databases()
        selected_database = None
        for db_row in databases:
            if db_row['pcm_database_id'] == pcm_database_id:
                selected_database = db_row
                break
        
        if not selected_database:
            flash(f"Database with ID {pcm_database_id} not found", 'error')
            return redirect(url_for('list_databases'))
        
        # Get races for the selected database
        races = api.get_pcm_races(pcm_database_id, race_name_filter if race_name_filter else None)
        
        return render_template('races.html', 
                             races=races,
                             selected_database=selected_database,
                             race_name_filter=race_name_filter)
    except Exception as e:
        logger.error(f"Error loading races: {str(e)}")
        flash(f"Error loading races: {str(e)}", 'error')
        return redirect(url_for('list_databases'))

# Add a route that redirects to databases if no database_id is provided
@app.route('/races')
def show_races_no_db():
    """Redirect to databases page if no database is selected"""
    flash("Please select a database to view its races", 'info')
    return redirect(url_for('list_databases'))

@app.route('/start_lists', methods=['GET', 'POST'])
def start_lists():
    """Show all existing start lists and handle generation"""
    pcm_database_id = request.args.get('pcm_database_id', type=int)
    pcm_race_id = request.args.get('pcm_race_id', type=int)
    
    if request.method == 'POST':
        # Handle start list generation
        pcm_database_id = request.form.get('pcm_database_id', type=int)
        pcm_race_id = request.form.get('pcm_race_id', type=int)
        race_year = request.form.get('race_year')
        force_refresh = request.form.get('force_refresh') == 'on'
        
        try:
            # Here you would call your start list generation logic
            flash(f"Start list generation initiated for race {pcm_race_id} in year {race_year}", 'info')
            return redirect(url_for('start_lists', pcm_database_id=pcm_database_id, pcm_race_id=pcm_race_id))
        except Exception as e:
            logger.error(f"Error generating start list: {str(e)}")
            flash(f"Error generating start list: {str(e)}", 'error')
    
    selected_database = None
    selected_race = None
    start_lists = []
    
    try:
        if pcm_database_id and pcm_race_id:
            # Get database info
            databases = api.get_pcm_databases()
            for db_row in databases:
                if db_row['pcm_database_id'] == pcm_database_id:
                    selected_database = db_row
                    break
            
            # Get race info
            if selected_database:
                selected_race = api.get_pcm_race(pcm_database_id, pcm_race_id)[0]
            
            # Get start lists for this specific database and race
            if selected_database and selected_race:
                start_lists = api.get_start_lists(pcm_database_id, pcm_race_id)
        
        return render_template('start_lists.html', 
                             start_lists=start_lists,
                             selected_database=selected_database,
                             selected_race=selected_race)
    except Exception as e:
        logger.error(f"Error loading start lists: {str(e)}")
        flash(f"Error loading start lists: {str(e)}", 'error')
        return render_template('start_lists.html', 
                             start_lists=[], 
                             selected_database=None,
                             selected_race=None)

@app.route('/api/races/<int:pcm_database_id>')
def api_get_races(pcm_database_id):
    """API endpoint to get races for a database (for AJAX calls)"""
    try:
        races = api.get_pcm_races(pcm_database_id)
        return jsonify([dict(row) for row in races])
    except Exception as e:
        logger.error(f"API error getting races: {str(e)}")
        return jsonify([]), 500

if __name__ == '__main__':
    logger.info(f"Starting application on port {commons.APP_PORT}")
    app.run(debug=False, host='0.0.0.0', port=commons.APP_PORT)
