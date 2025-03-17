// static/js/dashboard_steam.js
document.addEventListener("DOMContentLoaded", function() {
    const progressBarContainer = document.getElementById("progress-bar-container");
    const progressBar = document.getElementById("progress-bar");
    const progressMessage = document.getElementById("progress-message");
    const gamesContainer = document.getElementById("games-container");
    const paginationTop = document.getElementById("pagination-top");
    const paginationBottom = document.getElementById("pagination-bottom");
    const totalAchievementsElement = document.getElementById("total-achievements");

    let currentPage = 1;  // Página actual
    let totalPages = 1;   // Total de páginas
    let isDownloading = false;  // Estado de la descarga

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

    // Actualizar inmediatamente al cargar la página
    updateTotalAchievements();

    // Función para cargar juegos con paginación
function loadGames(page) {
    fetch(`/dashboard/steam?page=${page}`, {
        headers: { 'X-Requested-With': 'XMLHttpRequest' }
    })
    .then(response => response.json())
    .then(data => {
        // Limpiar el contenedor de juegos
        gamesContainer.innerHTML = "";

        // Añadir los juegos al contenedor
        data.games.forEach(game => {
            const gameHtml = `
                <div class="accordion-item mb-3 game-card" style="transition: transform 0.2s, box-shadow 0.2s;">
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
                            <!-- Sub-acordeón para logros obtenidos -->
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

                            <!-- Sub-acordeón para logros pendientes -->
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

        // Añadir efecto hover a las tarjetas de juegos de Steam
        const gameCards = document.querySelectorAll(".game-card"); // Selector específico para las tarjetas de juegos de Steam
        gameCards.forEach(card => {
            card.addEventListener("mouseenter", () => {
                card.style.transform = "scale(1.02)";
                card.style.boxShadow = "0 4px 8px rgba(0, 0, 0, 0.2)";
            });
            card.addEventListener("mouseleave", () => {
                card.style.transform = "scale(1)";
                card.style.boxShadow = "0 2px 4px rgba(0, 0, 0, 0.1)";
            });
        });
    })
    .catch(error => {
        console.error("Error cargando juegos:", error);
    });
}

    // Actualizar paginación
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
                link.onclick = (event) => {
                    event.preventDefault();  // Prevenir el comportamiento predeterminado del enlace
                    currentPage = i;        // Actualizar la página actual
                    loadGames(currentPage); // Cargar los juegos de la página seleccionada
                };
                li.appendChild(link);
                pagination.appendChild(li);
            }
        };

        updatePaginator("pagination-top");
        updatePaginator("pagination-bottom");
    }

    // Cargar la primera página al inicio
    loadGames(currentPage);

    // Verificar el estado de la descarga cada 3 segundos
    setInterval(() => {
        fetch("/api/check_download_status")
            .then(response => response.json())
            .then(data => {
                if (!data.download_complete) {
                    // Actualizar la barra de progreso
                    progressBar.style.width = `${data.progress}%`;
                    progressBar.textContent = `${data.progress}%`;
                    progressMessage.textContent = `Cargando juegos... (${data.progress}%)`;

                    // Recargar los juegos para mostrar los nuevos
                    loadGames(currentPage);
                } else {
                    // Ocultar la barra de progreso
                    progressBarContainer.style.display = "none";
                }
            })
            .catch(error => {
                console.error("Error verificando estado de descarga:", error);
            });
    }, 3000);  // Verificar cada 3 segundos
});