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
    let currentSortDirection = "desc";  // Dirección de ordenación actual (descendente por defecto)
    let downloadCheckInterval = null; // Variable para almacenar el intervalo
    
    // Establecer el valor por defecto del selector de ordenación
    if (sortBy) {
        sortBy.value = "playtime";
    }

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
                                        <img src="${game.image}" width="100" class="me-3 rounded game-image">
                                        <div class="d-flex flex-column">
                                            <strong class="text-truncate game-title">${game.name}</strong>
                                            <span class="text-muted">${game.playtime} horas jugadas</span>
                                        </div>
                                    </div>
                                    <span class="badge bg-primary rounded-pill achievements-badge">
                                        ${(game.achieved_achievements.length > 0 || game.pending_achievements.length > 0) ? 
                                            `${game.achieved_achievements.length}/${game.achieved_achievements.length + game.pending_achievements.length} logros` : 
                                            'Sin logros'}
                                    </span>
                                </button>
                            </h2>
                            <div id="collapse${game.id}" class="accordion-collapse collapse" aria-labelledby="heading${game.id}" data-bs-parent="#games-container">
                                <div class="accordion-body">
                                    <div class="row">
                                        <div class="col-md-6">
                                            <h5 class="mb-3">Logros obtenidos</h5>
                                            <div class="achievements-list obtained-achievements">
                                                ${game.achieved_achievements.length > 0 ? 
                                                    game.achieved_achievements.map(achievement => `
                                                        <div class="achievement-item">
                                                            <i class="fas fa-trophy text-warning"></i>
                                                            <span>${achievement.name}</span>
                                                        </div>
                                                    `).join('') :
                                                    '<div class="achievement-item">No hay logros obtenidos</div>'
                                                }
                                            </div>
                                        </div>
                                        <div class="col-md-6">
                                            <h5 class="mb-3">Logros pendientes</h5>
                                            <div class="achievements-list pending-achievements">
                                                ${game.pending_achievements.length > 0 ?
                                                    game.pending_achievements.map(achievement => `
                                                        <div class="achievement-item">
                                                            <i class="fas fa-lock text-secondary"></i>
                                                            <span>${achievement.name}</span>
                                                        </div>
                                                    `).join('') :
                                                    '<div class="achievement-item">No hay logros pendientes</div>'
                                                }
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </div>
                    `;
                    gamesContainer.innerHTML += gameHtml;
                });

                // Añadir efectos hover a las tarjetas de juegos
                const gameCards = document.querySelectorAll(".game-card");
                gameCards.forEach(card => {
                    card.addEventListener("mouseenter", () => {
                        card.style.transform = "scale(1.02)";
                        card.style.boxShadow = "0 4px 8px rgba(0,0,0,0.2)";
                    });
                    card.addEventListener("mouseleave", () => {
                        card.style.transform = "scale(1)";
                        card.style.boxShadow = "0 2px 4px rgba(0,0,0,0.1)";
                    });
                });

                // Añadir efectos hover a las imágenes de juegos
                const gameImages = document.querySelectorAll(".game-image");
                gameImages.forEach(img => {
                    img.addEventListener("mouseenter", () => {
                        img.style.transform = "scale(1.1)";
                        img.style.transition = "transform 0.3s ease";
                    });
                    img.addEventListener("mouseleave", () => {
                        img.style.transform = "scale(1)";
                    });
                });

                // Añadir efectos hover a los títulos de juegos
                const gameTitles = document.querySelectorAll(".game-title");
                gameTitles.forEach(title => {
                    title.addEventListener("mouseenter", () => {
                        title.style.color = "#007bff";
                        title.style.transition = "color 0.3s ease";
                    });
                    title.addEventListener("mouseleave", () => {
                        title.style.color = "inherit";
                    });
                });

                // Añadir efectos hover a los logros
                const achievementItems = document.querySelectorAll(".achievement-item");
                achievementItems.forEach(item => {
                    item.addEventListener("mouseenter", () => {
                        item.style.transform = "translateX(5px)";
                        item.style.transition = "transform 0.3s ease";
                    });
                    item.addEventListener("mouseleave", () => {
                        item.style.transform = "translateX(0)";
                    });
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
        const progressBarContainer = document.getElementById("progress-bar-container");
        if (!progressBarContainer) return; // Si no existe el contenedor, no hacer nada

        fetch("/api/check_download_status")
            .then(response => response.json())
            .then(data => {
                if (!data.download_complete) {
                    // Mostrar la barra de progreso
                    progressBarContainer.style.display = "block";
                    progressBar.style.width = `${data.progress}%`;
                    progressBar.textContent = `${data.progress}%`;
                    progressMessage.textContent = `Cargando juegos... (${data.progress}%)`;
                } else {
                    // Ocultar la barra de progreso cuando la descarga esté completa
                    progressBarContainer.style.display = "none";
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