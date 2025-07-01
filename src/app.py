from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, send_file, Response
import sys
import os
import io

from api import AppAPI
from utils import logger_helper, commons

logger = logger_helper.get_logger(__name__)

app = Flask('PCMStartListGenerator')
app.secret_key = 'your-secret-key-here'  # Change this in production

api = AppAPI()

@app.route('/import_database', methods=['POST'])
def import_database():
    """Handle database import from modal"""
    existing_file = request.form.get('existing_pcm_database_file')
    uploaded_file = request.files.get('pcm_database_file')
    pcm_database_name = request.form.get('pcm_database_name')
    pcm_version = request.form.get('pcm_version', commons.PCM_VERSIONS[0])
    
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
            
        return redirect(url_for('index'))
    except Exception as e:
        logger.error(f"Error importing database: {str(e)}")
        flash(f"Error importing database: {str(e)}", 'error')
        return redirect(url_for('index'))

@app.route('/', methods=['GET', 'POST'])
def index():
    """Simplified step-by-step homepage"""
    pcm_database_id = request.args.get('pcm_database_id', type=int)
    pcm_race_id = request.args.get('pcm_race_id', type=int)
    race_filter = request.args.get('race_filter', '')
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    if request.method == 'POST':
        # Handle start list generation
        race_year = request.form.get('race_year')
        start_list_race_name = request.form.get('start_list_race_name')
        start_list_url = request.form.get('start_list_url')
        force_refresh = request.form.get('force_refresh') == 'on'
        
        try:
            flash(f"Start list generation initiated for race {pcm_race_id} in year {race_year}", 'success')
            generated_file_path = api.generate_start_list(pcm_database_id, pcm_race_id, race_year, start_list_race_name, start_list_url, force_refresh)
            return redirect(url_for('index', pcm_database_id=pcm_database_id, pcm_race_id=pcm_race_id))
        except Exception as e:
            logger.error(f"Error generating start list: {str(e)}")
            flash(f"Error generating start list: {str(e)}", 'error')
            return redirect(url_for('index', pcm_database_id=pcm_database_id, pcm_race_id=pcm_race_id))
    
    try:
        # Get all databases
        databases = api.get_pcm_databases()
        
        # Get available SQLite files for import modal
        available_files = []
        if os.path.exists(commons.PCM_DATABASE_PATH):
            for file in os.listdir(commons.PCM_DATABASE_PATH):
                if file.lower().endswith(('.sqlite', '.db')):
                    file_path = os.path.join(commons.PCM_DATABASE_PATH, file)
                    file_size = os.path.getsize(file_path)
                    available_files.append({
                        'name': file,
                        'size': file_size
                    })
        
        selected_database = None
        selected_race = None
        races = []
        total_races = 0
        total_pages = 0
        existing_start_lists = []
        
        # Step 1: Get selected database
        if pcm_database_id:
            selected_database = api.get_pcm_database(pcm_database_id)
        
        # Step 2: Get races with pagination
        if selected_database:
            all_races = api.get_pcm_races(pcm_database_id, race_filter if race_filter else None)
            total_races = len(all_races)
            total_pages = (total_races + per_page - 1) // per_page
            
            # Paginate races
            start_idx = (page - 1) * per_page
            end_idx = start_idx + per_page
            races = all_races[start_idx:end_idx]
            
            # Get selected race
            if pcm_race_id:
                selected_race = api.get_pcm_race(pcm_database_id, pcm_race_id)

        # Get existing start lists
        existing_start_lists = api.get_start_lists(pcm_database_id, pcm_race_id)
        
        return render_template('index.html',
                             databases=databases,
                             selected_database=selected_database,
                             selected_race=selected_race,
                             races=races,
                             total_races=total_races,
                             total_pages=total_pages,
                             page=page,
                             race_filter=race_filter,
                             existing_start_lists=existing_start_lists,
                             pcm_versions=commons.PCM_VERSIONS,
                             available_files=available_files)
    
    except Exception as e:
        logger.error(f"Error loading homepage: {str(e)}")
        flash(f"Error loading data: {str(e)}", 'error')
        return render_template('index.html',
                             databases=[],
                             pcm_versions=commons.PCM_VERSIONS,
                             available_files=[])

@app.route('/download/<int:start_list_race_id>')
def download_start_list(start_list_race_id):
    """Download the generated start list XML file"""
    try:
        result = api.download_start_list(start_list_race_id)
        
        if result is None:
            flash("Start list file not found. Please generate it first.", 'error')
            return redirect(url_for('index'))
        
        file_path, file_content = result
        
        # Get the filename from the path
        filename = os.path.basename(file_path)
        
        # Create a file-like object from the content
        file_obj = io.BytesIO(file_content.encode('utf-8'))
        
        return send_file(
            file_obj,
            as_attachment=True,
            download_name=filename,
            mimetype='application/xml'
        )
        
    except Exception as e:
        logger.error(f"Error downloading start list: {str(e)}")
        flash(f"Error downloading start list: {str(e)}", 'error')
        return redirect(url_for('index'))

if __name__ == '__main__':
    logger.info(f"Starting application on port {commons.APP_PORT}")
    app.run(debug=False, host='0.0.0.0', port=commons.APP_PORT)
