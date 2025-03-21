// static/js/dashboard_steam.js
document.addEventListener("DOMContentLoaded", function() {
    const progressBarContainer = document.getElementById("progress-bar-container");
    const progressBar = document.getElementById("progress-bar");
    const progressMessage = document.getElementById("progress-message");
    const gamesContainer = document.getElementById("games-container");
    const paginationTop = document.getElementById("pagination-top");
    const paginationBottom = document.getElementById("pagination-bottom");
    const totalAchievementsElement = document.getElementById("total-achievements");

    // Variables para los filtros
    const gameSearch = document.getElementById("game-search");
    const sortBy = document.getElementById("sort-by");
    const sortDirection = document.getElementById("sort-direction");
    const resetFilters = document.getElementById("reset-filters");

    // Añadir variables globales
    let currentPage = 1;  // Página actual
    let totalPages = 1;   // Total de páginas
    let isDownloading = false;  // Estado de la descarga
    let currentSortDirection = "asc";  // Dirección de ordenación actual
    let downloadCheckInterval = null; // Variable para almacenar el intervalo
    

    // Función para actualizar el número de logros obtenidos
     // Función para cargar juegos con filtros
     function loadGames(page) {
        const searchParams = new URLSearchParams({
            page: page,
            search: gameSearch.value,
            sort: sortBy.value,
            order: currentSortDirection
        });

        fetch(`/dashboard/steam?${searchParams.toString()}`, {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        })
        .then(response => response.json())
        .then(data => {
            gamesContainer.innerHTML = "";

            if (data.games && data.games.length > 0) {
                data.games.forEach(game => {
                    const gameHtml = `
                        <div class="accordion-item mb-3 game-card">
                            <h2 class="accordion-header" id="heading${game.id}">
                                <button class="accordion-button collapsed d-flex justify-content-between align-items-center w-100" type="button" data-bs-toggle="collapse" data-bs-target="#collapse${game.id}" aria-expanded="false" aria-controls="collapse${game.id}">
                                    <div class="d-flex align-items-center">
                                        <img src="${game.image}" width="100" class="me-3 rounded">
                                        <div class="d-flex flex-column">
                                            <strong class="text-truncate">${game.name}</strong>
                                            <span class="text-muted">${game.playtime} horas jugadas</span>
                                        </div>
                                    </div>
                                    <div class="d-flex flex-column align-items-center" style="position: absolute; left: 50%; transform: translateX(-50%);">
                                        <span class="badge bg-primary rounded-pill">
                                            ${game.achieved_achievements.length}/${game.achieved_achievements.length + game.pending_achievements.length}
                                        </span>
                                        <small class="text-muted">Logros</small>
                                    </div>
                                </button>
                            </h2>
                            <div id="collapse${game.id}" class="accordion-collapse collapse" aria-labelledby="heading${game.id}" data-bs-parent="#games-container">
                                <div class="accordion-body">
                                    <div class="accordion mb-3" id="achievedAccordion${game.id}">
                                        <div class="accordion-item">
                                            <h2 class="accordion-header" id="achievedHeading${game.id}">
                                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#achievedCollapse${game.id}" aria-expanded="false" aria-controls="achievedCollapse${game.id}">
                                                    <i class="fas fa-trophy me-2"></i>Logros Obtenidos (${game.achieved_achievements.length})
                                                </button>
                                            </h2>
                                            <div id="achievedCollapse${game.id}" class="accordion-collapse collapse" aria-labelledby="achievedHeading${game.id}" data-bs-parent="#achievedAccordion${game.id}">
                                                <div class="accordion-body">
                                                    <ul class="list-group">
                                                        ${game.achieved_achievements.length > 0 ?
                                                            game.achieved_achievements.map(a => `
                                                                <li class="list-group-item">
                                                                    <span class="badge bg-success me-2">✔</span>
                                                                    <strong>${a.name}</strong> - ${a.description}
                                                                    <span class="text-muted ms-2">(Desbloqueado: ${a.unlock_time})</span>
                                                                </li>
                                                            `).join("") :
                                                            `<li class="list-group-item text-muted">No has desbloqueado logros en este juego.</li>`
                                                        }
                                                    </ul>
                                                </div>
                                            </div>
                                        </div>
                                    </div>

                                    <div class="accordion" id="pendingAccordion${game.id}">
                                        <div class="accordion-item">
                                            <h2 class="accordion-header" id="pendingHeading${game.id}">
                                                <button class="accordion-button collapsed" type="button" data-bs-toggle="collapse" data-bs-target="#pendingCollapse${game.id}" aria-expanded="false" aria-controls="pendingCollapse${game.id}">
                                                    <i class="fas fa-lock me-2"></i>Logros Pendientes (${game.pending_achievements.length})
                                                </button>
                                            </h2>
                                            <div id="pendingCollapse${game.id}" class="accordion-collapse collapse" aria-labelledby="pendingHeading${game.id}" data-bs-parent="#pendingAccordion${game.id}">
                                                <div class="accordion-body">
                                                    <ul class="list-group">
                                                        ${game.pending_achievements.length > 0 ?
                                                            game.pending_achievements.map(a => `
                                                                <li class="list-group-item">
                                                                    <span class="badge bg-secondary me-2">🔒</span>
                                                                    <strong>${a.name}</strong> - ${a.description}
                                                                </li>
                                                            `).join("") :
                                                            `<li class="list-group-item text-muted">¡Felicidades! Has desbloqueado todos los logros.</li>`
                                                        }
                                                    </ul>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                    gamesContainer.innerHTML += gameHtml;
                });
            } else {
                gamesContainer.innerHTML = `
                    <div class="alert alert-info text-center">
                        No se encontraron juegos.
                    </div>
                `;
            }

            updatePagination(data.total_pages, page);
            updateTotalAchievements();
        })
        .catch(error => {
            console.error("Error cargando juegos:", error);
            gamesContainer.innerHTML = `
                <div class="alert alert-danger text-center">
                    Error al cargar los juegos. Inténtalo de nuevo más tarde.
                </div>
            `;
        });
    }

    // Función para actualizar la paginación
    function updatePagination(totalPages, currentPage) {
        const updatePaginator = (paginationId) => {
            const pagination = document.getElementById(paginationId);
            pagination.innerHTML = "";

            for (let i = 1; i <= totalPages; i++) {
                const li = document.createElement("li");
                li.className = `page-item ${i === currentPage ? 'active' : ''}`;
                
                const link = document.createElement("a");
                link.className = "page-link";
                link.href = "#";
                link.textContent = i;

                // Añadir parámetros de filtro a los enlaces de paginación
                link.onclick = (event) => {
                    event.preventDefault();
                    currentPage = i;
                    loadGames(currentPage);
                };

                li.appendChild(link);
                pagination.appendChild(li);
            }
        };

        // Actualizar ambas paginaciones (superior e inferior)
        updatePaginator("pagination-top");
        updatePaginator("pagination-bottom");
    }

    // Función para actualizar el número de logros obtenidos
    function updateTotalAchievements() {
        fetch("/api/total_achievements")
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    totalAchievementsElement.textContent = data.total_achievements;
                }
            })
            .catch(error => {
                console.error("Error actualizando logros obtenidos:", error);
            });
    }

    
    // Función para verificar el estado de descarga
    function checkDownloadStatus() {
        fetch("/api/check_download_status")
            .then(response => response.json())
            .then(data => {
                if (!data.download_complete) {
                    // Mostrar la barra de progreso
                    document.getElementById("progress-bar-container").style.display = "block";
                    progressBar.style.width = `${data.progress}%`;
                    progressBar.textContent = `${data.progress}%`;
                    progressMessage.textContent = `Cargando juegos... (${data.progress}%)`;
                } else {
                    // Ocultar la barra de progreso cuando la descarga esté completa
                    document.getElementById("progress-bar-container").style.display = "none";
                    clearInterval(downloadCheckInterval); // Detener el intervalo
                }
            })
            .catch(error => {
                console.error("Error verificando estado de descarga:", error);
            });
    }



    // Función para actualizar el ícono de la flecha
    function updateSortDirectionIcon() {
        sortDirection.innerHTML = currentSortDirection === "asc" 
            ? '<i class="fas fa-arrow-up"></i>' 
            : '<i class="fas fa-arrow-down"></i>';
    }

    // Event listener para el botón de dirección de ordenación
    sortDirection.addEventListener("click", () => {
        // Cambiar entre ascendente y descendente
        currentSortDirection = currentSortDirection === "asc" ? "desc" : "asc";
        
        // Actualizar el ícono de la flecha
        updateSortDirectionIcon();
        
        // Recargar los juegos con la nueva dirección
        currentPage = 1;
        loadGames(currentPage);
    });

    // Event listener para el selector de ordenación
    sortBy.addEventListener("change", () => {
        // Restablecer la dirección a ascendente al cambiar el criterio de ordenación
        currentSortDirection = "asc";
        updateSortDirectionIcon();
        
        // Recargar los juegos
        currentPage = 1;
        loadGames(currentPage);
    });

    // Event listener para el botón de reset
    resetFilters.addEventListener("click", () => {
        gameSearch.value = "";
        sortBy.value = "name";
        currentSortDirection = "asc";
        updateSortDirectionIcon();
        currentPage = 1;
        loadGames(currentPage);
    });

    // Event listener para el buscador
    gameSearch.addEventListener("input", () => {
        currentPage = 1; // Reiniciar a la primera página
        loadGames(currentPage); // Cargar juegos con el nuevo filtro
    });

    // Cargar la primera página al inicio
    loadGames(currentPage);
    // Iniciar la verificación al cargar la página
    downloadCheckInterval = setInterval(checkDownloadStatus, 2000); // Verificar cada 2 segundos
    // Inicializar el ícono de la flecha al cargar la página
    updateSortDirectionIcon();


});