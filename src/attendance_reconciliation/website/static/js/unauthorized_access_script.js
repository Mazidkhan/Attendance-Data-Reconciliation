const apiUrl = `${url}/unauthorized_access`;
let unauthorized_access = [];

async function fetchUnauthorizedAccess() {
    try {
        const response = await fetch(apiUrl, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch unauthorized details.');
        }

        unauthorized_access = await response.json();
        renderUnauthorizedAccess(unauthorized_access);
    } catch (error) {
        console.error('Error fetching unauthorized_access:', error);
        alert('Failed to fetch unauthorized_access. Please try again.');
    }
}

function renderUnauthorizedAccess(data) {
    const tbody = document.getElementById('unauthorizedTable').querySelector('tbody');
    tbody.innerHTML = '';

    if (data.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="5">No unauthorized data available. Please apply filters to view data.</td>';
        tbody.appendChild(row);
        return;
    }

    data.forEach(unauthorized_access => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${unauthorized_access.id}</td>
            <td>${unauthorized_access.device_id}</td>
            <td>${unauthorized_access.tag_name}</td>
            <td>${unauthorized_access.rfid}</td>
            <td>${unauthorized_access.time}</td>
        `;
        tbody.appendChild(row);
    });
}

function showPopup(mode, id = '', device_id = '', rfid = '', time = '') {
    const popup = document.getElementById('popup');
    const popupTitle = document.getElementById('popup-title');
    const saveBtn = document.getElementById('popup-save-btn');
    document.getElementById('popup-id').value = id;
    document.getElementById('popup-device_id').value = device_id;
    document.getElementById('popup-rfid').value = rfid;
    document.getElementById('popup-time').value = time;

    if (mode === 'add') {
        popupTitle.textContent = 'Add Unauthorized Access';
        saveBtn.setAttribute('onclick', 'saveUnauthorizedAccess("add")');
    } else {
        popupTitle.textContent = 'Edit Unauthorized Access';
        saveBtn.setAttribute('onclick', 'saveUnauthorizedAccess("edit")');
    }

    popup.style.display = 'flex';
}

function hidePopup() {
    const popup = document.getElementById('popup');
    popup.style.display = 'none';
}

async function saveUnauthorizedAccess(mode) {
    const id = document.getElementById('popup-id').value;
    const device_id = document.getElementById('popup-device_id').value;
    const rfid = document.getElementById('popup-rfid').value;
    const time = document.getElementById('popup-time').value;

    let method = 'POST';
    let url = apiUrl;
    let successMessage = '';

    if (mode === 'edit') {
        method = 'PUT';
        url = `${apiUrl}/${id}`;
        successMessage = 'Unauthorized access updated successfully.';
    } else {
        successMessage = 'Unauthorized access added successfully.';
    }

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ device_id, rfid, time })
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error(`Error: ${response.status} - ${errorText}`);
            throw new Error(`Failed to ${mode === 'edit' ? 'update' : 'add'} employee. Status: ${response.status}`);
        }

        hidePopup();
        fetchUnauthorizedAccess();
        alert(successMessage);

    } catch (error) {
        console.error(`Error ${mode === 'edit' ? 'updating' : 'adding'}:`, error);
        alert(`Failed to ${mode === 'edit' ? 'update' : 'add'}. Please try again.`);
    }
}

async function deleteUnauthorizedAccess(id) {
    try {
        const response = await fetch(`${apiUrl}/${id}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const errorText = await response.text();
            console.error(`Error: ${response.status} - ${errorText}`);
            throw new Error('Failed to delete.');
        }

        fetchUnauthorizedAccess();
        alert('Deleted successfully.');

    } catch (error) {
        console.error('Error deleting:', error);
        alert('Failed to delete. Please try again.');
    }
}

function filterUnauthorized() {
    const fromDate = document.getElementById('from-date').value;
    const toDate = document.getElementById('to-date').value;

    if (!fromDate || !toDate) {
        alert('Please select both from and to dates.');
        return;
    }

    const from = new Date(fromDate);
    const to = new Date(toDate);

    // Set the end of the day for the "to" date
    to.setHours(23, 59, 59, 999);

    if (from > to) {
        alert('The "from" date cannot be later than the "to" date.');
        return;
    }

    filteredUnauthorizedAccess = unauthorized_access.filter(employee => {
        const employeeTime = new Date(employee.time);
        return employeeTime >= from && employeeTime <= to;
    });

    renderUnauthorizedAccess(filteredUnauthorizedAccess);
}


document.addEventListener('DOMContentLoaded', fetchUnauthorizedAccess);
