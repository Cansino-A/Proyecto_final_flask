document.addEventListener("DOMContentLoaded", function() {
    const usersTableBody = document.getElementById("users-table-body");
    const userSearch = document.getElementById("user-search");
    const sortBy = document.getElementById("sort-by");
    const sortDirection = document.getElementById("sort-direction");
    const resetFilters = document.getElementById("reset-filters");
    const pagination = document.getElementById("pagination");
    const createUserForm = document.getElementById("createUserForm");
    
    // Inicializar modales solo si el usuario es admin
    let confirmDeleteModal = null;
    let confirmDeleteButton = null;
    let deleteConfirmationText = null;
    
    if (IS_ADMIN) {
        confirmDeleteModal = new bootstrap.Modal(document.getElementById('confirmDeleteModal'));
        confirmDeleteButton = document.getElementById('confirmDeleteButton');
        deleteConfirmationText = document.getElementById('deleteConfirmationText');
    }
    
    let currentPage = 1;
    let currentSortDirection = "asc";
    let userToDelete = null;

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
    }

    // Función para cargar usuarios
    function loadUsers(page = 1) {
        const searchTerm = userSearch.value;
        const sortValue = sortBy.value;
        
        fetch(`/api/users?page=${page}&search=${searchTerm}&sort=${sortValue}&order=${currentSortDirection}`)
            .then(response => {
                if (!response.ok) {
                    throw new Error('Error al cargar usuarios');
                }
                return response.json();
            })
            .then(data => {
                if (!data.users || !Array.isArray(data.users)) {
                    throw new Error('Formato de datos inválido');
                }

                // Limpiar la tabla antes de agregar nuevos datos
                usersTableBody.innerHTML = '';

                // Agregar cada usuario a la tabla
                data.users.forEach(user => {
                    const row = document.createElement('tr');
                    row.innerHTML = `
                        <td>${user.username}</td>
                        <td>${user.steam_name}</td>
                        <td>${user.riot_info}</td>
                        <td>${user.highest_rank}</td>
                        <td>${user.total_achievements}</td>
                        ${IS_ADMIN ? `
                        <td>
                            <button class="btn btn-sm btn-primary edit-btn" onclick="openEditModal(${user.id}, '${user.username}')">Editar</button>
                            <button class="btn btn-sm btn-danger delete-btn" onclick="showDeleteConfirmation(${user.id}, '${user.username}')">Eliminar</button>
                        </td>` : ''}
                    `;
                    usersTableBody.appendChild(row);
                });

                setupPagination(data.total_pages, page);
            })
            .catch(error => {
                console.error('Error al cargar usuarios:', error);
                showToast('Error al cargar usuarios: ' + error.message, 'danger');
                usersTableBody.innerHTML = `<tr><td colspan="${IS_ADMIN ? '6' : '5'}" class="text-center">Error al cargar usuarios</td></tr>`;
            });
    }

    // Función para configurar la paginación
    function setupPagination(totalPages, currentPage) {
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
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    showToast('Usuario creado correctamente', 'success');
                    loadUsers(currentPage);
                    this.reset();
                } else {
                    showToast('Error al crear usuario: ' + data.error, 'danger');
                }
            })
            .catch(error => {
                showToast('Error al crear usuario', 'danger');
                console.error('Error:', error);
            });
        });
    }

    // Función para mostrar confirmación de eliminación
    window.showDeleteConfirmation = function(userId, username) {
        if (!IS_ADMIN) return;
        userToDelete = userId;
        deleteConfirmationText.innerHTML = `
            ¿Estás seguro de que deseas eliminar al usuario <strong>${username}</strong>? Esta acción no se puede deshacer.
        `;
        confirmDeleteModal.show();
    };

    // Confirmar eliminación
    if (confirmDeleteButton) {
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
    }

    // Función para abrir modal de edición
    window.openEditModal = function(userId, username) {
        if (!IS_ADMIN) return;
        
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

    // Cargar la primera página al inicio
    loadUsers(currentPage);
});
