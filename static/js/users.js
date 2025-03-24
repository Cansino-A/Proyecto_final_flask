document.addEventListener("DOMContentLoaded", function() {
    const usersTableBody = document.getElementById("users-table-body");
    const userSearch = document.getElementById("user-search");
    const sortBy = document.getElementById("sort-by");
    const sortDirection = document.getElementById("sort-direction");
    const resetFilters = document.getElementById("reset-filters");
    const pagination = document.getElementById("pagination");
    const createUserForm = document.getElementById("createUserForm");
    const confirmDeleteModal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));
    const confirmDeleteButton = document.getElementById('confirmDeleteButton');
    const deleteConfirmationText = document.getElementById('deleteConfirmationText');
    
    let currentPage = 1;
    let currentSortDirection = "asc";
    let userToDelete = null;

   // Función para cargar usuarios
    const loadUsers = (page = 1) => {
        fetch(`/api/users?page=${page}`)
            .then(response => response.json())
            .then(data => {
                usersTableBody.innerHTML = data.users.map(user => `
                    <tr>
                        <td>${user.username}</td>
                        <td>${user.highest_rank}</td>
                        <td>${user.total_achievements}</td>
                        ${current_user.username === "admin" ? `
                        <td>
                            <button class="btn btn-sm btn-primary edit-btn" data-id="${user.id}">Editar</button>
                            <button class="btn btn-sm btn-danger delete-btn" data-id="${user.id}">Eliminar</button>
                        </td>` : ''}
                    </tr>
                `).join('');
                setupPagination(data.total_pages, page);
            });
    };

    // Configurar eventos
    document.addEventListener('click', function(e) {
        if (e.target.classList.contains('delete-btn')) {
            const userId = e.target.dataset.id;
            if (confirm('¿Eliminar usuario?')) {
                fetch(`/api/users/${userId}`, { method: 'DELETE' })
                    .then(() => loadUsers(currentPage));
            }
        }
        
        if (e.target.classList.contains('edit-btn')) {
            const userId = e.target.dataset.id;
            const newPassword = prompt('Nueva contraseña:');
            if (newPassword) {
                fetch(`/api/users/${userId}`, {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ password: newPassword })
                }).then(() => loadUsers(currentPage));
            }
        }
    });

    // Resto del código (paginación, ordenación, etc.)
    function updatePagination(totalPages, currentPage) {
        pagination.innerHTML = "";
        for (let i = 1; i <= totalPages; i++) {
            const li = document.createElement("li");
            li.className = `page-item ${i === currentPage ? 'active' : ''}`;
            const link = document.createElement("a");
            link.className = "page-link";
            link.href = "#";
            link.textContent = i;
            link.onclick = (e) => {
                e.preventDefault();
                currentPage = i;
                loadUsers(currentPage);
            };
            li.appendChild(link);
            pagination.appendChild(li);
        }
    }

    // Event listeners
    userSearch.addEventListener("input", () => {
        currentPage = 1;
        loadUsers(currentPage);
    });

    sortBy.addEventListener("change", () => {
        currentPage = 1;
        loadUsers(currentPage);
    });

    sortDirection.addEventListener("click", () => {
        currentSortDirection = currentSortDirection === "asc" ? "desc" : "asc";
        sortDirection.innerHTML = currentSortDirection === "asc" 
            ? '<i class="fas fa-arrow-up"></i>' 
            : '<i class="fas fa-arrow-down"></i>';
        loadUsers(currentPage);
    });

    resetFilters.addEventListener("click", () => {
        userSearch.value = "";
        sortBy.value = "username";
        currentSortDirection = "asc";
        sortDirection.innerHTML = '<i class="fas fa-arrow-up"></i>';
        currentPage = 1;
        loadUsers(currentPage);
    });

    // Cargar la primera página al inicio
    loadUsers(currentPage);
});

// Función para abrir modal de edición
window.openEditModal = function(userId, username) {
    document.getElementById('usernameInput').value = username;
    document.getElementById('passwordInput').value = '';
    
    const saveButton = document.getElementById('saveUserButton');
    saveButton.onclick = function() {
        const newUsername = document.getElementById('usernameInput').value;
        const newPassword = document.getElementById('passwordInput').value;
        
        fetch(`/api/users/${userId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                username: newUsername,
                password: newPassword
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                loadUsers(currentPage);
                bootstrap.Modal.getInstance(document.getElementById('editUserModal')).hide();
                showToast('Usuario actualizado correctamente', 'success');
            } else {
                showToast('Error al actualizar usuario: ' + data.error, 'danger');
            }
        })
        .catch(error => {
            showToast('Error al actualizar usuario', 'danger');
            console.error('Error:', error);
        });
    };
    
    new bootstrap.Modal(document.getElementById('editUserModal')).show();
};

// Función para eliminar usuario
function confirmDelete(userId) {
    if (confirm("Are you sure you want to delete this user?")) {
        fetch(`/api/users/${userId}`, { method: "DELETE" })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    location.reload();
                } else {
                    alert("Error deleting user: " + data.error);
                }
            });
    }
}

    // Función para mostrar confirmación de eliminación
    window.showDeleteConfirmation = function(userId, username) {
        userToDelete = userId;
        deleteConfirmationText.innerHTML = `
            ¿Estás seguro de que deseas eliminar al usuario <strong>${username}</strong>? Esta acción no se puede deshacer.
        `;
        confirmDeleteModal.show();
    };

    // Confirmar eliminación
    confirmDeleteButton.addEventListener('click', function() {
        if (userToDelete) {
            fetch(`/api/users/${userToDelete}`, { method: "DELETE" })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        loadUsers(currentPage);
                        showToast('Usuario eliminado correctamente', 'success');
                    } else {
                        showToast('Error al eliminar usuario: ' + data.error, 'danger');
                    }
                    confirmDeleteModal.hide();
                })
                .catch(error => {
                    showToast('Error al eliminar usuario', 'danger');
                    console.error('Error:', error);
                });
        }
    });

    // Crear usuario
    if (createUserForm) {
        createUserForm.addEventListener('submit', function(e) {
            e.preventDefault();
            const formData = new FormData(this);
            const data = {
                username: formData.get('username'),
                password: formData.get('password')
            };

            fetch('/api/users', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(data)
            }).then(response => {
                if (response.ok) loadUsers(currentPage);
                else alert('Error al crear usuario');
            });
        });
    }

// Función para mostrar notificaciones
function showToast(message, type) {
    const toastContainer = document.getElementById('notification');
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} alert-dismissible fade show`;
    toast.style.position = 'fixed';
    toast.style.top = '20px';
    toast.style.right = '20px';
    toast.style.zIndex = '9999';
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    toastContainer.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 5000);

    loadUsers();
}
