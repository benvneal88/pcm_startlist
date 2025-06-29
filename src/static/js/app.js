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
});
