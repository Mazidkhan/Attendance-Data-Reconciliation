const apiUrl = `${url}/employees_wfh`;
const daysApiUrl = `${url}/employees_wfh_days`;

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

        const employees = await response.json();
        const tbody = document.getElementById('employeeTable').querySelector('tbody');
        tbody.innerHTML = '';

        for (const employee of employees) {
            const days = await fetchDays(employee.erpnext_id);
            const checkboxContainer = document.createElement('div');
            checkboxContainer.classList.add('checkbox-group');
            checkboxContainer.id = `${employee.erpnext_id}-week-container`;

            for (let i = 1; i <= 6; i++) {
                const checkbox = document.createElement('input');
                checkbox.type = 'checkbox';
                checkbox.value = i;
                checkbox.id = `${employee.erpnext_id}-week-${i}`;
                checkbox.checked = days.includes(i.toString());
                checkboxContainer.appendChild(checkbox);
            
                let labelday = '';
                switch(i) {
                    case 1:
                        labelday = 'M';
                        break;
                    case 2:
                        labelday = 'T';
                        break;
                    case 3:
                        labelday = 'W';
                        break;
                    case 4:
                        labelday = 'T';
                        break;
                    case 5:
                        labelday = 'F';
                        break;
                    case 6:
                        labelday = 'S';
                        break;
                }
            
                const label = document.createElement('label');
                label.htmlFor = checkbox.id;
                label.textContent = labelday;
                checkboxContainer.appendChild(label);
            }
            

            const row = document.createElement('tr');

            const idCell = document.createElement('td');
            idCell.textContent = employee.id;
            row.appendChild(idCell);

            const nameCell = document.createElement('td');
            nameCell.textContent = employee.employee_name;
            row.appendChild(nameCell);

            const erpIdCell = document.createElement('td');
            erpIdCell.textContent = employee.erpnext_id;
            row.appendChild(erpIdCell);

            const checkboxCell = document.createElement('td');
            checkboxCell.appendChild(checkboxContainer);
            row.appendChild(checkboxCell);

            const actionsCell = document.createElement('td');

            const editButton = document.createElement('button');
            editButton.classList.add('edit-button');
            editButton.innerHTML = '<i class="fas fa-edit"></i>';
            editButton.onclick = () => showPopup('edit', employee.id, employee.employee_name, employee.erpnext_id);
            actionsCell.appendChild(editButton);

            const deleteButton = document.createElement('button');
            deleteButton.classList.add('delete-button');
            deleteButton.innerHTML = '<i class="fas fa-trash-alt"></i>';
            deleteButton.onclick = () => deleteEmployee(employee.id);
            actionsCell.appendChild(deleteButton);

            const submitButton = document.createElement('button');
            submitButton.classList.add('submit-button');
            submitButton.innerHTML = '<i class="fas fa-paper-plane"></i>';
            submitButton.onclick = () => handleSubmit(employee.erpnext_id);
            actionsCell.appendChild(submitButton);

            row.appendChild(actionsCell);

            tbody.appendChild(row);
        }

    } catch (error) {
        console.error('Error fetching employees:', error);
        alert('Failed to fetch employees. Please try again.');
    }
}

async function fetchDays(employeeId) {
    try {
        const response = await fetch(`${daysApiUrl}/${employeeId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch days.');
        }

        const data = await response.json();
        console.log('Fetched employee days data:', data.map(dayObj => dayObj.days.toString()));

        return data.map(dayObj => dayObj.days.toString());
    } catch (error) {
        console.error('Error fetching days:', error);
        return [];
    }
}

async function handleSubmit(employeeId) {
    const checkboxContainer = document.getElementById(`${employeeId}-week-container`);

    if (!checkboxContainer) {
        console.error(`Checkbox container not found for employee ID ${employeeId}`);
        return;
    }

    const selectedDays = Array.from(checkboxContainer.querySelectorAll('input[type=checkbox]:checked'))
        .map(checkbox => checkbox.value);

    try {
        // Fetch existing days for the employee
        const existingDaysResponse = await fetch(`${daysApiUrl}/${employeeId}`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`,
                'Content-Type': 'application/json'
            }
        });

        if (!existingDaysResponse.ok) {
            throw new Error('Failed to fetch existing days.');
        }

        const existingDaysData = await existingDaysResponse.json();
        const existingDays = existingDaysData.map(item => item.days.toString());

        // Delete days that are no longer selected
        for (const day of existingDays) {
            if (!selectedDays.includes(day)) {
                await fetch(`${daysApiUrl}/${employeeId}`, {
                    method: 'DELETE',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ days: day })
                });
            }
        }

        // Add new selected days
        for (const day of selectedDays) {
            if (!existingDays.includes(day)) {
                await fetch(daysApiUrl, {
                    method: 'POST',
                    headers: {
                        'Authorization': `Bearer ${token}`,
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({ days: day, erpnext_id: employeeId })
                });
            }
        }

        alert('Data submitted successfully!');
        fetchEmployee(); // Refresh the table to reflect changes

    } catch (error) {
        console.error('Error submitting data:', error);
        alert('Failed to submit data. Please try again.');
    }
}

function showPopup(mode, id = '', employee_name = '', erpnext_id = '') {
    const popup = document.getElementById('popup');
    const popupTitle = document.getElementById('popup-title');
    const saveBtn = document.getElementById('popup-save-btn');
    document.getElementById('popup-id').value = id;
    document.getElementById('popup-employee_name').value = employee_name;
    document.getElementById('popup-erpnext_id').value = erpnext_id;

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

    const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({ employee_name, erpnext_id })
    });
    hidePopup();
    fetchEmployee();
    alert(successMessage);
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

        // Handle empty or non-JSON response
        let result = {};
        try {
            result = await response.json();
        } catch (e) {
            console.error('Response was not valid JSON:', e);
        }
        console.log(result);

        fetchEmployee();
        alert('Employee deleted successfully.');

    } catch (error) {
        console.error('Error deleting employee:', error);
        alert('Failed to delete employee. Please try again.');
    }
}

document.addEventListener('DOMContentLoaded', fetchEmployee);
