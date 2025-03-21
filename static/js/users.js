document.addEventListener("DOMContentLoaded", function() {
    const usersTableBody = document.getElementById("users-table-body");
    const userSearch = document.getElementById("user-search");
    const sortBy = document.getElementById("sort-by");
    const sortDirection = document.getElementById("sort-direction");
    const resetFilters = document.getElementById("reset-filters");
    const pagination = document.getElementById("pagination");

    let currentPage = 1;
    let currentSortDirection = "asc";

    // Función para cargar usuarios
    function loadUsers(page) {
        const searchParams = new URLSearchParams({
            page: page,
            search: userSearch.value,
            sort: sortBy.value,
            order: currentSortDirection
        });

        fetch(`/api/users?${searchParams.toString()}`)
            .then(response => response.json())
            .then(data => {
                usersTableBody.innerHTML = "";
                data.users.forEach(user => {
                    const row = `
                        <tr>
                            <td>${user.username}</td>
                            <td>${user.highest_rank || "Unranked"}</td>
                            <td>${user.total_achievements}</td>
                            ${current_user.username === "admin" ? `
                                <td>
                                    <button class="btn btn-primary btn-sm" onclick="openEditModal(${user.id})">
                                        <i class="fas fa-edit"></i>
                                    </button>
                                    <button class="btn btn-danger btn-sm" onclick="confirmDelete(${user.id})">
                                        <i class="fas fa-trash"></i>
                                    </button>
                                </td>
                            ` : ""}
                        </tr>
                    `;
                    usersTableBody.innerHTML += row;
                });

                updatePagination(data.total_pages, page);
            })
            .catch(error => {
                console.error("Error loading users:", error);
            });
    }

    // Función para actualizar la paginación
    function updatePagination(totalPages, currentPage) {
        pagination.innerHTML = "";
        for (let i = 1; i <= totalPages; i++) {
            const li = document.createElement("li");
            li.className = `page-item ${i === currentPage ? 'active' : ''}`;
            const link = document.createElement("a");
            link.className = "page-link";
            link.href = "#";
            link.textContent = i;
            link.onclick = (event) => {
                event.preventDefault();
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

// Función para abrir el modal de edición
function openEditModal(userId) {
    fetch(`/api/users/${userId}`)
        .then(response => response.json())
        .then(user => {
            document.getElementById("usernameInput").value = user.username;
            document.getElementById("passwordInput").value = "";

            const saveButton = document.getElementById("saveUserButton");
            saveButton.onclick = () => {
                const newUsername = document.getElementById("usernameInput").value;
                const newPassword = document.getElementById("passwordInput").value;

                fetch(`/api/users/${userId}`, {
                    method: "PUT",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ username: newUsername, password: newPassword })
                })
                .then(response => response.json())
                .then(data => {
                    if (data.success) {
                        location.reload();
                    } else {
                        alert("Error updating user: " + data.error);
                    }
                });
            };

            new bootstrap.Modal(document.getElementById("editUserModal")).show();
        });
}

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