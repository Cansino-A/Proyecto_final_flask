document.addEventListener("DOMContentLoaded", function() {
    console.log("✅ dashboard_riot.js cargado correctamente");

    const searchButton = document.getElementById("riot-search-button");
    const gameNameInput = document.getElementById("riot-gameName");
    const tagLineInput = document.getElementById("riot-tagLine");
    const resultsContainer = document.getElementById("riot-summoner-info");

    if (!searchButton || !gameNameInput || !tagLineInput || !resultsContainer) {
        console.error("❌ Error: Elementos no encontrados en el DOM.");
        return;
    }

    // Evento de búsqueda
    searchButton.addEventListener("click", function() {
        let gameName = gameNameInput.value.trim();
        let tagLine = tagLineInput.value.trim();

        if (!gameName || !tagLine) {
            alert("Por favor, ingresa el nombre y el tag del jugador.");
            return;
        }

        fetch(`/api/riot/summoner?gameName=${encodeURIComponent(gameName)}&tagLine=${encodeURIComponent(tagLine)}`)
            .then(response => response.json())
            .then(data => {
                console.log("Respuesta de la API:", data);  // Verifica la respuesta en la consola
                mostrarHistorial(data);
            })
            .catch(error => {
                console.error("❌ Error al buscar el jugador:", error);
            });
    });

    function mostrarHistorial(data) {
        if (data.error) {
            resultsContainer.innerHTML = `<div class="alert alert-danger">Error: ${data.error}</div>`;
            return;
        }
    
        let matchesHTML = `
            <div class="card shadow">
                <div class="card-body">
                    <h5 class="card-title">Últimas partidas</h5>
                    <div class="list-group">
        `;
    
        data.matches.forEach(matchId => {
            matchesHTML += `
                <a href="#" class="list-group-item list-group-item-action" onclick="verDetalles('${matchId}', '${data.puuid}')">
                    <div class="d-flex justify-content-between align-items-center">
                        <span>Partida: ${matchId}</span>
                        <i class="fas fa-chevron-right"></i>
                    </div>
                </a>
            `;
        });
    
        matchesHTML += `
                    </div>
                </div>
            </div>
        `;
    
        resultsContainer.innerHTML = matchesHTML;
    }
    
    // Variable global para el modal
    let matchModal = null;
    
    window.verDetalles = function(matchId, puuid) {
        // Eliminar el modal anterior si existe
        if (matchModal) {
            matchModal.dispose();  // Cerrar y eliminar el modal anterior
        }
    
        fetch(`/api/riot/match/${matchId}?puuid=${encodeURIComponent(puuid)}`)
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    alert(`Error: ${data.error}`);
                    return;
                }
    
                // Crear el contenido del modal
                const modalContent = `
                    <div class="modal-dialog modal-lg">
                        <div class="modal-content">
                            <div class="modal-header">
                                <h5 class="modal-title">Detalles de la partida</h5>
                                <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
                            </div>
                            <div class="modal-body">
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6>Información básica</h6>
                                        <p><strong>Campeón:</strong> ${data.champion}</p>
                                        <p><strong>KDA:</strong> ${data.kills}/${data.deaths}/${data.assists}</p>
                                        <p><strong>Resultado:</strong> ${data.win ? "Victoria 🏆" : "Derrota 😞"}</p>
                                        <p><strong>Duración:</strong> ${data.duration} minutos</p>
                                        <p><strong>Modo de juego:</strong> ${data.gameMode}</p>
                                    </div>
                                    <div class="col-md-6">
                                        <h6>Estadísticas avanzadas</h6>
                                        <p><strong>Daño total:</strong> ${data.totalDamageDealt}</p>
                                        <p><strong>Daño a campeones:</strong> ${data.totalDamageDealtToChampions}</p>
                                        <p><strong>Curaciones:</strong> ${data.totalHeal}</p>
                                        <p><strong>Oro total:</strong> ${data.goldEarned}</p>
                                        <p><strong>Minions eliminados:</strong> ${data.totalMinionsKilled}</p>
                                    </div>
                                </div>
                                <hr>
                                <div class="row">
                                    <div class="col-md-6">
                                        <h6>Objetos comprados</h6>
                                        <div class="d-flex flex-wrap">
                                            ${data.items.map(item => `
                                                <div class="me-2 mb-2">
                                                    <img src="https://ddragon.leagueoflegends.com/cdn/13.24.1/img/item/${item}.png" 
                                                         alt="Item ${item}" 
                                                         width="40" 
                                                         height="40"
                                                         onerror="this.src='https://via.placeholder.com/40';">
                                                </div>
                                            `).join("")}
                                        </div>
                                    </div>
                                    <div class="col-md-6">
                                        <h6>Hechizos de invocador</h6>
                                        <div class="d-flex">
                                            ${data.summonerSpells.map(spell => `
                                                <div class="me-2">
                                                    <img src="https://ddragon.leagueoflegends.com/cdn/13.24.1/img/spell/${spell}.png" 
                                                         alt="Spell ${spell}" 
                                                         width="40" 
                                                         height="40"
                                                         onerror="this.src='https://via.placeholder.com/40';">
                                                </div>
                                            `).join("")}
                                        </div>
                                    </div>
                                </div>
                                <hr>
                                <div class="row">
                                    <div class="col-md-12">
                                        <h6>Runas</h6>
                                        <div class="d-flex">
                                            ${data.runes.map(rune => `
                                                <div class="me-2">
                                                    <img src="https://ddragon.leagueoflegends.com/cdn/img/${rune.icon}" 
                                                         alt="Rune ${rune.name}" 
                                                         width="40" 
                                                         height="40"
                                                         onerror="this.src='https://via.placeholder.com/40';">
                                                    <small class="d-block text-center">${rune.name}</small>
                                                </div>
                                            `).join("")}
                                        </div>
                                    </div>
                                </div>
                            </div>
                            <div class="modal-footer">
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
});