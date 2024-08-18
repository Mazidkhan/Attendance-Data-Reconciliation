const apiUrl = `${url}/device`;

async function fetchDevice() {

    try {
        const response = await fetch(apiUrl, {
            method: 'GET',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            throw new Error('Failed to fetch device.');
        }

        const devices = await response.json();
        const tbody = document.getElementById('devicesTable').querySelector('tbody');
        tbody.innerHTML = '';
        devices.forEach(device => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${device.id}</td>
                <td>${device.device_id}</td>
                <td>${device.tag_name}</td>
                <td>
                    <button class="edit-button" onclick="showPopup('edit', '${device.id}', '${device.device_id}', '${device.tag_name}')">
                    <i class="fas fa-edit"></i>
                    </button>
                    <button class="delete-button" onclick="deleteDevice('${device.id}')">
                    <i class="fas fa-trash-alt"></i>
                    </button>
                </td>
            `;
            tbody.appendChild(row);
        });

    } catch (error) {
        console.error('Error fetching devices:', error);
        alert('Failed to fetch devices. Please try again.');
    }
}

function showPopup(mode, id, device_id, tag_name) {
    const popup = document.getElementById('popup');
    const popupTitle = document.getElementById('popup-title');
    const saveBtn = document.getElementById('popup-save-btn');
    document.getElementById('popup-id').value = id || '';
    document.getElementById('popup-device-id').value = device_id || '';
    document.getElementById('popup-device-tag').value = tag_name || '';

    if (mode === 'add') {
        popupTitle.textContent = 'Add Device';
        saveBtn.setAttribute('onclick', 'saveDevice("add")');
    } else {
        popupTitle.textContent = 'Edit Device';
        saveBtn.setAttribute('onclick', 'saveDevice("edit")');
    }

    popup.style.display = 'flex';
}

function hidePopup() {
    const popup = document.getElementById('popup');
    popup.style.display = 'none';
}

async function saveDevice(mode) {
    const id = document.getElementById('popup-id').value;
    const device_id = document.getElementById('popup-device-id').value;
    const tag_name = document.getElementById('popup-device-tag').value;

    let method = 'POST';
    let url = apiUrl;
    let successMessage = '';

    if (mode === 'edit') {
        method = 'PUT';
        url = `${apiUrl}`;
        successMessage = 'device updated successfully.';
    } else {
        successMessage = 'device added successfully.';
    }

    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({id, device_id,tag_name })
        });

        hidePopup();
        fetchDevice();
        alert(successMessage);
    } catch (error) {
        console.error(`Error ${mode === 'edit' ? 'updating' : 'adding'} device:`, error);
        alert(`Failed to ${mode === 'edit' ? 'update' : 'add'} device. Please try again.`);
    }
}

async function deleteDevice(id) {

    try {
        const response = await fetch(`${apiUrl}/${id}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`,
            }
        });
        fetchDevice();
        alert('device deleted successfully.');
    } catch (error) {
        console.error('Error deleting device:', error);
        alert('Failed to delete device. Please try again.');
    }
}

document.addEventListener('DOMContentLoaded', fetchDevice);
