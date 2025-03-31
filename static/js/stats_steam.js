document.addEventListener("DOMContentLoaded", function() {
    const statsContainer = document.getElementById("steam-summoner-stats");
    const userNameContainer = document.getElementById("user-name");

    if (!statsContainer) {
        console.error("❌ Error: Elementos no encontrados en el DOM.");
        return;
    }

    // Mostrar indicadores de carga
    statsContainer.innerHTML = `
        <div class="card shadow mb-4">
            <div class="card-body text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p class="mt-2">Cargando estadísticas...</p>
            </div>
        </div>
    `;

    // Obtener las estadísticas del usuario
    fetch('/api/steam/user-stats')
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.error || "Error al obtener estadísticas");
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.error && data.error !== "No hay cuenta de Steam vinculada") {
                statsContainer.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-circle"></i> Error al cargar las estadísticas: ${data.error}
                    </div>
                `;
                return;
            }

            // Mostrar el nombre del usuario
            if (userNameContainer && data.username) {
                userNameContainer.innerHTML = `<i class="fas fa-user-circle me-2"></i>${data.username}`;
            }

            mostrarEstadisticasGenerales(data);
            mostrarGraficos(data);
        })
        .catch(error => {
            console.error("❌ Error al obtener estadísticas:", error);
            if (error.message !== "No hay cuenta de Steam vinculada") {
                statsContainer.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-circle"></i> Error al cargar las estadísticas: ${error.message}
                    </div>
                `;
            }
        });
});

function mostrarEstadisticasGenerales(data) {
    const statsContainer = document.getElementById("steam-summoner-stats");
    if (!statsContainer) return;

    const statsHTML = `
        <div class="card shadow hover-card mb-4">
            <div class="card-body">
                <h5 class="card-title d-flex align-items-center">
                    <i class="fas fa-chart-line me-2"></i>
                    Estadísticas Generales
                </h5>
                <div class="row">
                    <div class="col-md-6">
                        <div class="stat-item mb-3">
                            <i class="fas fa-gamepad me-2 text-primary"></i>
                            <strong>Total de juegos:</strong> ${data.totalGames}
                        </div>
                        <div class="stat-item mb-3">
                            <i class="fas fa-check-circle me-2 text-success"></i>
                            <strong>Juegos completados:</strong> ${data.completedGames}
                        </div>
                        <div class="stat-item mb-3">
                            <i class="fas fa-trophy me-2 text-warning"></i>
                            <strong>Logros desbloqueados:</strong> ${data.totalAchievements}
                        </div>
                    </div>
                    <div class="col-md-6">
                        <div class="stat-item mb-3">
                            <i class="fas fa-clock me-2 text-info"></i>
                            <strong>Horas totales jugadas:</strong> ${data.totalPlaytime}
                        </div>
                        <div class="stat-item mb-3">
                            <i class="fas fa-star me-2 text-warning"></i>
                            <strong>Juegos favoritos:</strong> ${data.favoriteGenres.join(", ")}
                        </div>
                        <div class="stat-item mb-3">
                            <i class="fas fa-history me-2 text-secondary"></i>
                            <strong>Último juego jugado:</strong> ${data.lastPlayedGame}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    `;

    statsContainer.innerHTML = statsHTML;
}

function mostrarGraficos(data) {
    // Gráfica de juegos más jugados
    const mostPlayedCtx = document.getElementById('mostPlayedGamesChart').getContext('2d');
    new Chart(mostPlayedCtx, {
        type: 'bar',
        data: {
            labels: data.mostPlayedGames.map(game => game.name),
            datasets: [{
                label: 'Horas jugadas',
                data: data.mostPlayedGames.map(game => game.playtime),
                backgroundColor: 'rgba(54, 162, 235, 0.5)',
                borderColor: 'rgba(54, 162, 235, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    // Gráfica de tiempo jugado por género
    const genreCtx = document.getElementById('timeByGenreChart').getContext('2d');
    new Chart(genreCtx, {
        type: 'pie',
        data: {
            labels: data.timeByGenre.map(genre => genre.name),
            datasets: [{
                data: data.timeByGenre.map(genre => genre.playtime),
                backgroundColor: [
                    'rgba(255, 99, 132, 0.5)',
                    'rgba(54, 162, 235, 0.5)',
                    'rgba(255, 206, 86, 0.5)',
                    'rgba(75, 192, 192, 0.5)',
                    'rgba(153, 102, 255, 0.5)'
                ]
            }]
        },
        options: {
            responsive: true
        }
    });

    // Gráfica de logros desbloqueados
    const achievementsCtx = document.getElementById('achievementsChart').getContext('2d');
    new Chart(achievementsCtx, {
        type: 'doughnut',
        data: {
            labels: ['Desbloqueados', 'Pendientes'],
            datasets: [{
                data: [data.totalAchievements, data.totalPossibleAchievements - data.totalAchievements],
                backgroundColor: [
                    'rgba(75, 192, 192, 0.5)',
                    'rgba(255, 99, 132, 0.5)'
                ]
            }]
        },
        options: {
            responsive: true
        }
    });
} 