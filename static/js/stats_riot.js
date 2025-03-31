document.addEventListener("DOMContentLoaded", function() {
    const statsContainer = document.getElementById("riot-summoner-stats");
    const resultsContainer = document.getElementById("riot-summoner-info");
    const warningContainer = document.querySelector(".riot-warning");

    if (!statsContainer || !resultsContainer) {
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

    resultsContainer.innerHTML = `
        <div class="card shadow mb-4">
            <div class="card-body text-center">
                <div class="spinner-border text-primary" role="status">
                    <span class="visually-hidden">Cargando...</span>
                </div>
                <p class="mt-2">Cargando partidas...</p>
            </div>
        </div>
    `;

    // Obtener las estadísticas del usuario
    fetch('/api/riot/user-stats')
        .then(response => {
            if (!response.ok) {
                return response.json().then(err => {
                    throw new Error(err.error || "Error al obtener estadísticas");
                });
            }
            return response.json();
        })
        .then(data => {
            if (data.error && data.error !== "No tienes una cuenta de Riot vinculada. Por favor, vincula tu cuenta en tu perfil.") {
                statsContainer.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-circle"></i> Error al cargar las estadísticas: ${data.error}
                    </div>
                `;
                return;
            }

            if (warningContainer) {
                warningContainer.style.display = 'none';
            }
            mostrarEstadisticasGenerales(data.puuid);
            mostrarHistorial(data);
        })
        .catch(error => {
            console.error("❌ Error al obtener estadísticas:", error);
            if (error.message !== "No tienes una cuenta de Riot vinculada. Por favor, vincula tu cuenta en tu perfil.") {
                statsContainer.innerHTML = `
                    <div class="alert alert-danger">
                        <i class="fas fa-exclamation-circle"></i> Error al cargar las estadísticas: ${error.message}
                    </div>
                `;
            }
        });
});

function mostrarEstadisticasGenerales(puuid) {
    const statsContainer = document.getElementById("riot-summoner-stats");
    if (!statsContainer) {
        console.error("❌ No se encontró el contenedor 'riot-summoner-stats'.");
        return;
    }

    fetch(`/api/riot/summoner-info?puuid=${encodeURIComponent(puuid)}`)
        .then(response => {
            if (!response.ok) {
                throw new Error("Error al obtener información del invocador.");
            }
            return response.json();
        })
        .then(data => {
            if (data.error) {
                console.error("Error al obtener información del invocador:", data.error);
                return;
            }

            // Diccionario para traducir los rangos
            const tierTranslation = {
                "IRON": "Hierro",
                "BRONZE": "Bronce",
                "SILVER": "Plata",
                "GOLD": "Oro",
                "PLATINUM": "Platino",
                "DIAMOND": "Diamante",
                "MASTER": "Maestro",
                "GRANDMASTER": "Gran Maestro",
                "CHALLENGER": "Retador"
            };

            // Calcular estadísticas generales
            let totalWins = 0;
            let totalLosses = 0;
            let globalWinRate = 0;
            let totalGamesPlayed = 0;
            let bestRank = "No clasificado";

            if (Array.isArray(data.rankedInfo)) {
                data.rankedInfo.forEach(queue => {
                    totalWins += queue.wins;
                    totalLosses += queue.losses;
                });

                totalGamesPlayed = totalWins + totalLosses;
                globalWinRate = totalGamesPlayed > 0 ? ((totalWins / totalGamesPlayed) * 100).toFixed(2) : 0;

                // Obtener el mejor rango
                bestRank = data.rankedInfo.reduce((best, queue) => {
                    const tierOrder = ["IRON", "BRONZE", "SILVER", "GOLD", "PLATINUM", "DIAMOND", "MASTER", "GRANDMASTER", "CHALLENGER"];
                    const currentTierIndex = tierOrder.indexOf(queue.tier.toUpperCase());
                    const bestTierIndex = tierOrder.indexOf(best.tier.toUpperCase());
                    return currentTierIndex > bestTierIndex ? queue : best;
                }, { tier: "IRON", rank: "IV" });

                bestRank = `${tierTranslation[bestRank.tier]} ${bestRank.rank}`;
            }

            // Formatear la información de clasificación
            let rankedInfoHTML = "No clasificado";
            if (Array.isArray(data.rankedInfo)) {
                rankedInfoHTML = data.rankedInfo.map(queue => {
                    const tier = queue.tier.toUpperCase();
                    const rank = queue.rank;
                    const translatedTier = tierTranslation[tier] || tier;
                    const winRate = ((queue.wins / (queue.wins + queue.losses)) * 100).toFixed(2);

                    // Convertir el rango a un formato compatible con los nombres de tus imágenes
                    const rankNumber = rank === "I" ? 1 : rank === "II" ? 2 : rank === "III" ? 3 : 4;

                    // URL del icono de rango (usando las imágenes locales)
                    const rankIconUrl = `/static/images/ranks/${tier}_${rankNumber}.webp`;

                    return `
                        <div class="mb-3">
                            <div class="d-flex align-items-center">
                                <img src="${rankIconUrl}" width="50" class="me-3" alt="${translatedTier} ${rank}" onerror="this.onerror=null; this.src='/static/images/ranks/default.webp';">
                                <div>
                                    <strong>${queue.queueType === "RANKED_SOLO_5x5" ? "Solo/Duo" : "Flexible"}:</strong>
                                    ${translatedTier} ${rank} (${queue.leaguePoints} LP)
                                    <br>
                                    <small>${queue.wins} victorias / ${queue.losses} derrotas (${winRate}% de victorias)</small>
                                </div>
                            </div>
                        </div>
                    `;
                }).join("");
            }

            const summonerInfoHTML = `
                <div class="card shadow mb-4">
                    <div class="card-body">
                        <h5 class="card-title">Estadísticas Generales</h5>
                        <div class="row">
                            <div class="col-md-12">
                                <p><strong>Clasificación:</strong></p>
                                ${rankedInfoHTML}
                                <p><strong>Win Rate Global:</strong> ${globalWinRate}%</p>
                                <p><strong>Partidas Jugadas:</strong> ${totalGamesPlayed}</p>
                                <p><strong>Mejor Rango Alcanzado:</strong> ${bestRank}</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;

            // Insertar el HTML en el contenedor de estadísticas
            statsContainer.innerHTML = summonerInfoHTML;
        })
        .catch(error => {
            console.error("❌ Error al obtener estadísticas generales:", error);
            statsContainer.innerHTML = `
                <div class="alert alert-danger">
                    ${error.message}
                </div>
            `;
        });
}

function mostrarHistorial(data) {
    const resultsContainer = document.getElementById("riot-summoner-info");
    if (!resultsContainer) {
        console.error("❌ No se encontró el contenedor 'riot-summoner-info'.");
        return;
    }

    if (data.error) {
        resultsContainer.innerHTML = `<div class="alert alert-danger">Error: ${data.error}</div>`;
        return;
    }

    let matchesHTML = `
        <div class="card shadow mb-4">
            <div class="card-body">
                <h3 class="card-title mb-4">Últimas partidas</h3>
                <div class="row row-cols-1 g-4">
    `;

    let loadedMatches = 0;
    const totalMatches = data.matches.length;
    let matchesData = [];

    data.matches.forEach(matchId => {
        fetch(`/api/riot/match/${matchId}?puuid=${encodeURIComponent(data.puuid)}`)
            .then(response => {
                if (!response.ok) {
                    return response.json().then(err => {
                        throw new Error(err.error || "Error al cargar la partida");
                    });
                }
                return response.json();
            })
            .then(matchDetails => {
                if (matchDetails.error) {
                    matchesData.push({
                        error: matchDetails.error,
                        timestamp: 0
                    });
                } else {
                    matchesData.push({
                        ...matchDetails,
                        timestamp: matchDetails.gameStartTimestamp
                    });
                }

                loadedMatches++;
                if (loadedMatches === totalMatches) {
                    // Ordenar las partidas por fecha (más recientes primero)
                    matchesData.sort((a, b) => b.timestamp - a.timestamp);

                    // Generar el HTML con las partidas ordenadas
                    matchesData.forEach((match, index) => {
                        if (match.error) {
                            matchesHTML += `
                                <div class="col">
                                    <div class="card">
                                        <div class="card-body">
                                            <p class="card-text text-danger">Error al cargar la partida: ${match.error}</p>
                                        </div>
                                    </div>
                                </div>
                            `;
                        } else {
                            const winClass = match.win ? "border-start border-5 border-primary" : "border-start border-5 border-danger";
                            const resultText = match.win ? "Victoria 🏆" : "Derrota 😞";
                            const gameMode = match.gameMode;
                            const currentMatchId = data.matches[index];

                            matchesHTML += `
                            <div class="col">
                                <div class="card h-100 ${winClass} match-card" style="border-radius: 10px; transition: transform 0.2s, box-shadow 0.2s; cursor: pointer;" 
                                    onclick="verDetalles('${currentMatchId}', '${data.puuid}')">
                                    <div class="card-body d-flex flex-column justify-content-between p-3">
                                        <div class="d-flex align-items-center">
                                            <img src="${match.champion_image}" width="80" class="me-3 rounded" onerror="this.src='/static/images/default_champion.png'">
                                            <div>
                                                <h5 class="card-title mb-1" style="font-size: 1.4rem;">${match.champion}</h5>
                                                <p class="card-text mb-1" style="font-size: 1.2rem;"><strong>KDA:</strong> ${match.kills}/${match.deaths}/${match.assists}</p>
                                                <p class="card-text mb-1" style="font-size: 1.2rem;">${resultText}</p>
                                            </div>
                                        </div>
                                        <div class="text-end">
                                            <p class="card-text mb-1" style="font-size: 1rem;">${new Date(match.timestamp).toLocaleString()}</p>
                                            <p class="card-text mb-1" style="font-size: 1rem;"><strong>Modo:</strong> ${gameMode}</p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                            `;
                        }
                    });

                    // Actualizar el contenido del contenedor
                    resultsContainer.innerHTML = matchesHTML + `</div></div></div>`;

                    // Añadir efecto hover a las tarjetas de partidas
                    const matchCards = document.querySelectorAll(".match-card");
                    matchCards.forEach(card => {
                        card.addEventListener("mouseenter", () => {
                            card.style.transform = "scale(1.02)";
                            card.style.boxShadow = "0 4px 8px rgba(0, 0, 0, 0.2)";
                        });
                        card.addEventListener("mouseleave", () => {
                            card.style.transform = "scale(1)";
                            card.style.boxShadow = "0 2px 4px rgba(0, 0, 0, 0.1)";
                        });
                    });
                }
            })
            .catch(error => {
                console.error("❌ Error al obtener detalles de la partida:", error);
                loadedMatches++;
                if (loadedMatches === totalMatches) {
                    resultsContainer.innerHTML = matchesHTML + `</div></div></div>`;
                }
            });
    });
}

// Variable global para el modal
let matchModal = null;
    
// Función para abrir el modal de detalles de la partida
window.verDetalles = function(matchId, puuid) {
    // Eliminar el modal anterior si existe
    if (matchModal) {
        matchModal.dispose();
    }

    fetch(`/api/riot/match/${matchId}?puuid=${encodeURIComponent(puuid)}`)
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                alert(`Error: ${data.error}`);
                return;
            }

            const winClass = data.win ? "bg-primary text-white" : "bg-danger text-white";
            const resultText = data.win ? "Victoria 🏆" : "Derrota 😞";

            const modalContent = `
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header ${winClass}">
                            <h5 class="modal-title">Detalles de la partida</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                        </div>
                        <div class="modal-body bg-dark text-white">
                            <div class="row">
                                <div class="col-md-6">
                                    <h6>Información básica</h6>
                                    <div class="text-center mb-3">
                                        <img src="${data.champion_image}" width="100" class="rounded mb-2">
                                        <h5>${data.champion} (Nivel ${data.championLevel})</h5>
                                    </div>
                                    <p><strong>Resultado:</strong> ${resultText}</p>
                                    <p><strong>KDA:</strong> ${data.kills}/${data.deaths}/${data.assists}</p>
                                    <p><strong>Duración:</strong> ${data.duration} minutos</p>
                                    <p><strong>Modo de juego:</strong> ${data.gameMode}</p>
                                </div>
                                <div class="col-md-6">
                                    <h6>Estadísticas avanzadas</h6>
                                    <ul class="list-group bg-dark">
                                        <li class="list-group-item bg-dark text-white"><strong>Daño total:</strong> ${data.totalDamageDealt}</li>
                                        <li class="list-group-item bg-dark text-white"><strong>Daño a campeones:</strong> ${data.totalDamageDealtToChampions}</li>
                                        <li class="list-group-item bg-dark text-white"><strong>Curaciones:</strong> ${data.totalHeal}</li>
                                        <li class="list-group-item bg-dark text-white"><strong>Oro total:</strong> ${data.goldEarned}</li>
                                        <li class="list-group-item bg-dark text-white"><strong>Minions eliminados:</strong> ${data.totalMinionsKilled}</li>
                                        <li class="list-group-item bg-dark text-white"><strong>Wards colocados:</strong> ${data.wardsPlaced}</li>
                                        <li class="list-group-item bg-dark text-white"><strong>Wards destruidos:</strong> ${data.wardsKilled}</li>
                                        <li class="list-group-item bg-dark text-white"><strong>Dragones asesinados:</strong> ${data.dragonsKilled}</li>
                                        <li class="list-group-item bg-dark text-white"><strong>Barones asesinados:</strong> ${data.baronsKilled}</li>
                                    </ul>
                                </div>
                            </div>
                        </div>
                        <div class="modal-footer bg-dark">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cerrar</button>
                        </div>
                    </div>
                </div>
            `;

            // Crear el modal
            const modalElement = document.createElement("div");
            modalElement.classList.add("modal", "fade");
            modalElement.innerHTML = modalContent;
            document.body.appendChild(modalElement);

            // Inicializar el modal
            matchModal = new bootstrap.Modal(modalElement);
            matchModal.show();

            // Eliminar el modal cuando se cierre
            modalElement.addEventListener("hidden.bs.modal", () => {
                modalElement.remove();
            });
        })
        .catch(error => {
            console.error("❌ Error al obtener detalles de la partida:", error);
        });
}; 