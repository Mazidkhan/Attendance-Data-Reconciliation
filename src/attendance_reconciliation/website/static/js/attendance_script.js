const apiUrl = `${url}/attendance`;
let attendances = [];
let filteredAttendances = []; // Global variable to hold filtered data

// Fetch attendance data on page load but don't render it initially
async function fetchAttendance() {
    try {
        const response = await fetch(apiUrl, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            const errorMessage = await response.text();
            throw new Error(`Failed to fetch attendances. Status: ${response.status}. Message: ${errorMessage}`);
        }

        attendances = await response.json(); // Store fetched attendances
        filteredAttendances = []; // Initialize filteredAttendances
        renderAttendance([]); // Render an empty table or message
    } catch (error) {
        console.error('Error fetching attendances:', error);
        alert('Failed to fetch attendances. Please try again.');
    }
}

// Render attendance data or a placeholder message
function renderAttendance(data) {
    const tbody = document.getElementById('attendanceTable').querySelector('tbody');
    tbody.innerHTML = '';

    if (data.length === 0) {
        const row = document.createElement('tr');
        row.innerHTML = '<td colspan="5">No attendance data available. Please apply filters to view data.</td>';
        tbody.appendChild(row);
        return;
    }

    // Sort the data by attendance_date in descending order
    data.sort((a, b) => new Date(b.attendance_date) - new Date(a.attendance_date));

    // Render the sorted data
    data.forEach(attendance => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${attendance.id}</td>
            <td>${attendance.employee}</td>
            <td>${attendance.status}</td>
            <td>${attendance.attendance_date}</td>
        `;
        tbody.appendChild(row);
    });
}


// Show popup for adding or editing attendance
function showPopup(mode, id, employee_name, erpnext_id, status, attendance_date) {
    const popup = document.getElementById('popup');
    const popupTitle = document.getElementById('popup-title');
    const saveBtn = document.getElementById('popup-save-btn');
    document.getElementById('popup-id').value = id || '';
    document.getElementById('popup-employee_name').value = employee_name || '';
    document.getElementById('popup-erpnext_id').value = erpnext_id || '';
    document.getElementById('popup-status').value = status || '';
    document.getElementById('popup-attendance_date').value = attendance_date || '';

    if (mode === 'add') {
        popupTitle.textContent = 'Add Attendance';
        saveBtn.setAttribute('onclick', 'saveAttendance("add")');
    } else {
        popupTitle.textContent = 'Edit Attendance';
        saveBtn.setAttribute('onclick', 'saveAttendance("edit")');
    }

    popup.style.display = 'flex';
}

// Hide the popup
function hidePopup() {
    const popup = document.getElementById('popup');
    popup.style.display = 'none';
}

// Save attendance (add or edit)
async function saveAttendance(mode) {
    const id = document.getElementById('popup-id').value;
    const employee_name = document.getElementById('popup-employee_name').value;
    const erpnext_id = document.getElementById('popup-erpnext_id').value;
    const status = document.getElementById('popup-status').value;
    const date = document.getElementById('popup-attendance_date').value;

    let method = 'POST';
    let url = apiUrl;
    let successMessage = '';

    if (mode === 'edit') {
        method = 'PUT';
        url = `${apiUrl}/${id}`;
        successMessage = 'Attendance updated successfully.';
    } else {
        successMessage = 'Attendance added successfully.';
    }

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ employee_name, status, date, erpnext_id })
        });

        const result = await response.text();

        if (!response.ok) {
            throw new Error(`Failed to ${mode === 'edit' ? 'update' : 'add'} attendance. Status: ${response.status}. Message: ${result}`);
        }

        console.log(result);
        hidePopup();
        fetchAttendance(); // Re-fetch attendance data to update table
        alert(successMessage);

    } catch (error) {
        console.error(`Error ${mode === 'edit' ? 'updating' : 'adding'} attendance:`, error);
        alert(`Failed to ${mode === 'edit' ? 'update' : 'add'} attendance. Please try again.`);
    }
}

// Delete attendance
async function deleteAttendance(id) {
    try {
        const response = await fetch(`${apiUrl}/${id}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        const result = await response.text();

        if (!response.ok) {
            throw new Error(`Failed to delete attendance. Status: ${response.status}. Message: ${result}`);
        }

        console.log(result);
        fetchAttendance(); // Re-fetch attendance data to update table
        alert('Attendance deleted successfully.');

    } catch (error) {
        console.error('Error deleting attendance:', error);
        alert('Failed to delete attendance. Please try again.');
    }
}

// Apply filters to attendance data
function filterAttendance() {
    const fromDate = document.getElementById('from-date').value;
    const toDate = document.getElementById('to-date').value;
    const erpnextId = document.getElementById('erpnext-id').value.trim();

    if (!fromDate || !toDate) {
        alert('Please select both from and to dates.');
        return;
    }

    const from = new Date(fromDate);
    const to = new Date(toDate);

    if (from > to) {
        alert('The "from" date cannot be later than the "to" date.');
        return;
    }

    filteredAttendances = attendances.filter(attendance => {
        const attendanceDate = new Date(attendance.attendance_date);
        const isWithinDateRange = attendanceDate >= from && attendanceDate <= to;
        const matchesErpnextId = !erpnextId || attendance.erpnext_id.includes(erpnextId);
        return isWithinDateRange && matchesErpnextId;
    });

    renderAttendance(filteredAttendances);
}

// Download filtered data as CSV
function downloadCSV() {
    if (filteredAttendances.length === 0) {
        alert('No filtered data to download.');
        return;
    }

    // Define the CSV header
    const header = [
        'ID', 'Employee Name', 'ERPNext ID', 'Status', 'Date'
    ];

    // Convert data to CSV
    const csvRows = [];
    csvRows.push(header.join(','));

    filteredAttendances.forEach(attendance => {
        const row = [
            attendance.id,
            attendance.employee,
            attendance.erpnext_id,
            attendance.status,
            attendance.attendance_date
        ];
        csvRows.push(row.join(','));
    });

    // Create a Blob from the CSV data
    const csvData = new Blob([csvRows.join('\n')], { type: 'text/csv' });
    const url = URL.createObjectURL(csvData);

    // Create a link element, set its href to the Blob URL, and trigger a download
    const link = document.createElement('a');
    link.href = url;
    link.download = 'attendance_data.csv';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    // Clean up URL object
    URL.revokeObjectURL(url);
}

// Event listener to fetch attendance data on page load
document.addEventListener('DOMContentLoaded', fetchAttendance);
