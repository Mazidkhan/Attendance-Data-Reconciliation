const apiUrl = `${url}/secured/users`;

async function fetchUser() {

    try {
        const response = await fetch(apiUrl, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch user.');
        }

        const users = await response.json();
        const tbody = document.getElementById('usersTable').querySelector('tbody');
        tbody.innerHTML = '';
        users.forEach(user => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${user.id}</td>
                <td>${user.name}</td>
                <td>${user.loginId}</td>
                <td>${user.role}</td>
                <td>${user.active}</td>
                <td>
                    <button class="edit-button" onclick="showPopup('edit', '${user.id}', '${user.name}', '${user.loginId}', '${user.role}', '${user.active}')">
                    <i class="fas fa-edit"></i>
                    </button>
                    <button class="delete-button" onclick="deleteUser('${user.id}')">
                    <i class="fas fa-trash-alt"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });

    } catch (error) {
        console.error('Error fetching Users:', error);
        alert('Failed to fetch Users. Please try again.');
    }
}

function showPopup(mode, id, name, loginId, role, active) {
    const popup = document.getElementById('popup');
    const popupTitle = document.getElementById('popup-title');
    const saveBtn = document.getElementById('popup-save-btn');
    document.getElementById('popup-id').value = id || '';
    document.getElementById('popup-user_name').value = name || '';
    document.getElementById('popup-loginid').value = loginId || '';
    document.getElementById('popup-active').value = active || '';
    document.getElementById('popup-role').value= role || '';


    if (mode === 'add') {
        popupTitle.textContent = 'Add Attendance';
        saveBtn.setAttribute('onclick', 'saveUser("add")');
    } else {
        popupTitle.textContent = 'Edit Attendance';
        saveBtn.setAttribute('onclick', 'saveUser("edit")');
    }

    popup.style.display = 'flex';
}

function hidePopup() {
    const popup = document.getElementById('popup');
    popup.style.display = 'none';
}

async function saveUser(mode) {
    const id = document.getElementById('popup-id').value;
    const name = document.getElementById('popup-user_name').value;
    const loginId = document.getElementById('popup-loginid').value;
    const active = document.getElementById('popup-active').value;
    const role = document.getElementById('popup-role').value;

    let method = 'POST';
    let url = apiUrl;
    let successMessage = '';

    if (mode === 'edit') {
        method = 'PUT';
        url = `${apiUrl}`;
        successMessage = 'User updated successfully.';
    } else {
        successMessage = 'User added successfully.';
    }

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({id, name, loginId, role, active })
        });

        if (!response.ok) {
            throw new Error(`Failed to ${mode === 'edit' ? 'update' : 'add'} User.`);
        }

        const result = await response.json();
        console.log(result);
        hidePopup();
        fetchUser();
        alert(successMessage);

    } catch (error) {
        console.error(`Error ${mode === 'edit' ? 'updating' : 'adding'} User:`, error);
        alert(`Failed to ${mode === 'edit' ? 'update' : 'add'} User. Please try again.`);
    }
}

async function deleteUser(id) {

    try {
        const response = await fetch(`${apiUrl}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            },
            body: JSON.stringify({ userId: id })
        });


        const result = await response.json();
        console.log(result);
        fetchUser();
        alert('User deleted successfully.');

    } catch (error) {
        console.error('Error deleting user:', error);
        alert('Failed to delete user. Please try again.');
    }
}

document.addEventListener('DOMContentLoaded', fetchUser);
