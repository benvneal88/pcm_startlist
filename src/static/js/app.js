document.addEventListener('DOMContentLoaded', function() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert:not(.alert-danger)');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Dynamic race loading for start list generation
    const databaseSelect = document.getElementById('database_select');
    const raceSelect = document.getElementById('race_select');
    
    if (databaseSelect && raceSelect) {
        databaseSelect.addEventListener('change', function() {
            const databaseId = this.value;
            if (databaseId) {
                loadRaces(databaseId);
            } else {
                raceSelect.innerHTML = '<option value="">Select a database first</option>';
                raceSelect.disabled = true;
            }
        });
    }

    function loadRaces(databaseId) {
        const loading = document.getElementById('loading_races');
        if (loading) loading.classList.add('show');
        
        raceSelect.disabled = true;
        raceSelect.innerHTML = '<option value="">Loading races...</option>';

        fetch(`/api/races/${databaseId}`)
            .then(response => response.json())
            .then(races => {
                raceSelect.innerHTML = '<option value="">Select a race</option>';
                races.forEach(race => {
                    const option = document.createElement('option');
                    option.value = race.race_id;
                    option.textContent = race.race_name;
                    raceSelect.appendChild(option);
                });
                raceSelect.disabled = false;
            })
            .catch(error => {
                console.error('Error loading races:', error);
                raceSelect.innerHTML = '<option value="">Error loading races</option>';
            })
            .finally(() => {
                if (loading) loading.classList.remove('show');
            });
    }

    // Start List functionality
    function viewStartList(databaseId, raceName, raceYear) {
        const modal = new bootstrap.Modal(document.getElementById('startListModal'));
        const content = document.getElementById('startListContent');
        
        // Show loading spinner
        content.innerHTML = `
            <div class="text-center">
                <div class="spinner-border" role="status">
                    <span class="visually-hidden">Loading...</span>
                </div>
                <p class="mt-2">Loading start list details...</p>
            </div>
        `;
        
        modal.show();
        
        // Fetch start list data
        fetch(`/api/start_list/${databaseId}/${encodeURIComponent(raceName)}/${raceYear}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    content.innerHTML = `<div class="alert alert-danger">${data.error}</div>`;
                } else {
                    content.innerHTML = formatStartListData(data);
                }
            })
            .catch(error => {
                console.error('Error loading start list:', error);
                content.innerHTML = '<div class="alert alert-danger">Error loading start list data</div>';
            });
    }

    function formatStartListData(data) {
        let html = `<h6>${data.race_name} ${data.race_year}</h6>`;
        html += '<div class="table-responsive">';
        html += '<table class="table table-sm">';
        html += '<thead><tr><th>Team</th><th>Cyclist</th></tr></thead>';
        html += '<tbody>';
        
        data.cyclists.forEach(cyclist => {
            html += `<tr><td>${cyclist.team_name}</td><td>${cyclist.cyclist_name}</td></tr>`;
        });
        
        html += '</tbody></table></div>';
        return html;
    }

    function exportStartList(databaseId, raceName, raceYear) {
        window.open(`/api/export_start_list/${databaseId}/${encodeURIComponent(raceName)}/${raceYear}`, '_blank');
    }

    // Form submission handling
    const generateForm = document.getElementById('generateStartListForm');
    if (generateForm) {
        generateForm.addEventListener('submit', function(e) {
            const btn = document.getElementById('generateBtn');
            const spinner = btn.querySelector('.spinner-border');
            
            btn.disabled = true;
            spinner.classList.remove('d-none');
            btn.innerHTML = '<span class="spinner-border spinner-border-sm" role="status"></span> Generating...';
        });
    }
});
