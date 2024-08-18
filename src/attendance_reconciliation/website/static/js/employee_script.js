const apiUrl = `${url}/employees`;
let employeesData = [];


async function fetchEmployee() {
    try {
        const response = await fetch(apiUrl, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch employees.');
        }

        employeesData = await response.json();
        displayEmployees(employeesData);

    } catch (error) {
        console.error('Error fetching employees:', error);
        alert('Failed to fetch employees. Please try again.');
    }
}

function displayEmployees(employees) {
    const tbody = document.getElementById('employeeTable').querySelector('tbody');
    tbody.innerHTML = '';

    employees.forEach(employee => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${employee.id}</td>
            <td>${employee.employee_name}</td>
            <td>${employee.erpnext_id}</td>
            <td>${employee.rfid}</td>
            <td>${employee.tag_name}</td>
            <td>
                <button class="edit-button" onclick="showPopup('edit', ${employee.id}, '${employee.employee_name}', '${employee.erpnext_id}', '${employee.rfid}', '${employee.tag_name}')">
                <i class="fas fa-edit"></i>
                </button>
                <button class="delete-button" onclick="deleteEmployee(${employee.id})">
                <i class="fas fa-trash-alt"></i>
                </button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

function filterRFID() {
    const rfidValue = document.getElementById('rfid').value.trim();
    const filteredEmployees = employeesData.filter(employee => {
        return employee.rfid === rfidValue ;
    });
    displayEmployees(filteredEmployees);
}

function showPopup(mode, id = '', employee_name = '', erpnext_id = '', rfid = '', tag_name = '') {
    const popup = document.getElementById('popup');
    const popupTitle = document.getElementById('popup-title');
    const saveBtn = document.getElementById('popup-save-btn');
    document.getElementById('popup-id').value = id;
    document.getElementById('popup-employee_name').value = employee_name;
    document.getElementById('popup-erpnext_id').value = erpnext_id;
    document.getElementById('popup-rfid').value = rfid;
    document.getElementById('popup-tag').value = tag_name;

    if (mode === 'add') {
        popupTitle.textContent = 'Add Employee';
        saveBtn.setAttribute('onclick', 'saveEmployee("add")');
    } else {
        popupTitle.textContent = 'Edit Employee';
        saveBtn.setAttribute('onclick', 'saveEmployee("edit")');
    }

    popup.style.display = 'flex';
}

function hidePopup() {
    const popup = document.getElementById('popup');
    popup.style.display = 'none';
}

async function saveEmployee(mode) {
    const id = document.getElementById('popup-id').value;
    const employee_name = document.getElementById('popup-employee_name').value;
    const erpnext_id = document.getElementById('popup-erpnext_id').value;
    const rfid = document.getElementById('popup-rfid').value;
    const tag_name = document.getElementById('popup-tag').value;

    let method = 'POST';
    let url = apiUrl;
    let successMessage = '';

    if (mode === 'edit') {
        method = 'PUT';
        url = `${apiUrl}/${id}`;
        successMessage = 'Employee updated successfully.';
    } else {
        successMessage = 'Employee added successfully.';
    }

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ employee_name, erpnext_id, rfid, tag_name })
        });

        const contentType = response.headers.get('Content-Type');
        if (!response.ok) {
            const errorText = await response.text();
            console.error(`Error: ${response.status} - ${errorText}`);
            throw new Error(`Failed to ${mode === 'edit' ? 'update' : 'add'} employee. Status: ${response.status}`);
        }

        if (contentType && contentType.includes('application/json')) {
            const result = await response.json();
            console.log(result);
        } else {
            const resultText = await response.text();
            console.log(resultText);
        }

        hidePopup();
        fetchEmployee();
        alert(successMessage);

    } catch (error) {
        console.error(`Error ${mode === 'edit' ? 'updating' : 'adding'} employee:`, error);
        alert(`Failed to ${mode === 'edit' ? 'update' : 'add'} employee. Please try again.`);
    }
}

async function deleteEmployee(id) {
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
            throw new Error('Failed to delete employee.');
        }

        const contentType = response.headers.get('Content-Type');
        if (contentType && contentType.includes('application/json')) {
            const result = await response.json();
            console.log(result);
        } else {
            const resultText = await response.text();
            console.log(resultText);
        }

        fetchEmployee();
        alert('Employee deleted successfully.');

    } catch (error) {
        console.error('Error deleting employee:', error);
        alert('Failed to delete employee. Please try again.');
    }
}

document.addEventListener('DOMContentLoaded', fetchEmployee);
