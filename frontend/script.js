document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyzeBtn');
    const inputText = document.getElementById('inputText');
    const resultsSection = document.getElementById('results');
    const intentDisplay = document.getElementById('intentDisplay');
    const vesselDisplay = document.getElementById('vesselDisplay');
    const timeDisplay = document.getElementById('timeDisplay');
    const identifiersList = document.getElementById('identifiersList');
    const loadingIndicator = document.getElementById('loading');
    const validationWarning = document.getElementById('validationWarning');
    const validationMessage = document.getElementById('validationMessage');

    // Data Table Elements
    const dataSection = document.getElementById('dataSection');
    const dataTableBody = document.querySelector('#dataTable tbody');

    analyzeBtn.addEventListener('click', async () => {
        const text = inputText.value.trim();
        if (!text) return;

        // UI Reset
        resultsSection.classList.add('hidden');
        dataSection.classList.add('hidden');
        validationWarning.classList.add('hidden');
        loadingIndicator.classList.remove('hidden');
        analyzeBtn.disabled = true;

        try {
            const response = await fetch('http://localhost:8000/api/v1/predict', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    text: text
                })
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            const data = await response.json();
            displayResults(data);

        } catch (error) {
            console.error('Error:', error);
            alert('Failed to fetch results. Ensure backend is running.');
        } finally {
            loadingIndicator.classList.add('hidden');
            analyzeBtn.disabled = false;
        }
    });

    function displayResults(data) {
        resultsSection.classList.remove('hidden');

        // Validation Error Display
        if (data.validation_error) {
            validationWarning.classList.remove('hidden');
            validationMessage.textContent = data.validation_error;
        }

        // 1. Intent
        intentDisplay.textContent = data.intent || "Unknown";

        // 2. Vessel Name
        vesselDisplay.textContent = data.vessel_name || "Not found";

        // 3. Time Horizon
        timeDisplay.textContent = data.time_horizon || "Not specified";

        // 4. Identifiers
        identifiersList.innerHTML = '';
        const ids = data.identifiers;
        let hasIds = false;

        if (ids.mmsi) {
            addListItem(identifiersList, "MMSI", ids.mmsi);
            hasIds = true;
        }
        if (ids.imo) {
            addListItem(identifiersList, "IMO", ids.imo);
            hasIds = true;
        }
        if (ids.call_sign) {
            addListItem(identifiersList, "Call Sign", ids.call_sign);
            hasIds = true;
        }

        if (!hasIds) {
            identifiersList.innerHTML = '<li>No identifiers found</li>';
        }

        // 5. Data Table
        if (data.data && data.data.length > 0) {
            renderTable(data.data);
            dataSection.classList.remove('hidden');
        } else {
            dataSection.classList.add('hidden');
        }
    }

    function renderTable(records) {
        dataTableBody.innerHTML = '';
        records.forEach(record => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${record.timestamp}</td>
                <td>${record.lat.toFixed(4)}</td>
                <td>${record.lon.toFixed(4)}</td>
                <td>${record.sog.toFixed(1)}</td>
                <td>${record.cog.toFixed(1)}</td>
            `;
            dataTableBody.appendChild(row);
        });
    }

    function addListItem(parent, label, value) {
        const li = document.createElement('li');
        li.innerHTML = `<strong>${label}:</strong> ${value}`;
        parent.appendChild(li);
    }
});
