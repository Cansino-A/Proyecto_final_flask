

document.addEventListener("DOMContentLoaded", function() {
    // Función flash para mostrar notificaciones por encima de los modales
    function flash(message, type) {
        const notificationContainer = document.getElementById("notification");
        if (!notificationContainer) {
            console.error("No se encontró el contenedor de notificaciones (#notification)");
            return;
        }
        // Crear la alerta con z-index alto
        const alertDiv = document.createElement("div");
        alertDiv.className = `alert alert-${type} alert-dismissible fade show d-flex align-items-center`;
        alertDiv.style.minWidth = "300px";
        alertDiv.style.marginBottom = "10px";
        alertDiv.style.paddingRight = "2.5rem";
        alertDiv.style.zIndex = "9999"; // Aparece por encima de los modales
        alertDiv.innerHTML = `
            <span style="flex-grow: 1; margin-right: 1rem;">${message}</span>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close" style="margin-left: auto;"></button>
        `;
        notificationContainer.appendChild(alertDiv);

        // Cerrar automáticamente la alerta tras 4 segundos
        setTimeout(() => {
            alertDiv.classList.remove("show");
            alertDiv.classList.add("fade");
            setTimeout(() => alertDiv.remove(), 150);
        }, 4000);
    }

    // Inicializar tooltips en el perfil
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.forEach(function(tooltipTriggerEl) {
        new bootstrap.Tooltip(tooltipTriggerEl);
    });

    /*******************************************************
     * 1. Cambiar el nombre de usuario
     *******************************************************/
    const saveUsernameBtn = document.getElementById("saveUsernameButton");
    if (saveUsernameBtn) {
        saveUsernameBtn.addEventListener("click", function() {
            const newUsername = document.getElementById("usernameInput").value;
            fetch("/update_username", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ username: newUsername })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Cerrar el modal (opcional, pues recargaremos la página)
                    bootstrap.Modal.getInstance(document.getElementById('editUsernameModal')).hide();
                    // Mostrar aviso flash y recargar la página tras un breve retraso
                    flash("Nombre de usuario actualizado correctamente.", "success");
                    setTimeout(() => location.reload(), 500);
                } else {
                    flash("Error al actualizar el nombre de usuario: " + data.error, "danger");
                }
            })
            .catch(error => {
                console.error("Error:", error);
                flash("Error al actualizar el nombre de usuario.", "danger");
            });
        });
    }

    /*******************************************************
     * 2. Cambiar el ID de Steam
     *******************************************************/
    const saveSteamIdBtn = document.getElementById("saveSteamIdButton");
    if (saveSteamIdBtn) {
        saveSteamIdBtn.addEventListener("click", function() {
            const newSteamId = document.getElementById("steamIdInput").value;
            fetch("/link_steam", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ steam_id: newSteamId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Cerrar el modal
                    bootstrap.Modal.getInstance(document.getElementById('editSteamIdModal')).hide();

                    // Actualizar el Steam ID en el perfil sin recargar la página
                    const steamIdDisplay = document.getElementById("steamIdDisplay");
                    if (steamIdDisplay) {
                        steamIdDisplay.textContent = newSteamId;
                    }

                    // Obtener el nombre de Steam y actualizarlo
                    fetch(`/api/get_steam_name?steam_id=${newSteamId}`)
                        .then(response => response.json())
                        .then(data => {
                            const steamNameDisplay = document.getElementById("steamNameDisplay");
                            if (steamNameDisplay && data.steam_name) {
                                steamNameDisplay.textContent = data.steam_name;
                            }
                        })
                        .catch(error => {
                            console.error("Error obteniendo el nombre de Steam:", error);
                        });

                    // Mostrar la barra de carga y continuar con la descarga...
                    const progressBarContainer = document.getElementById("progress-bar-container");
                    const progressBar = document.getElementById("progress-bar");
                    const progressMessage = document.getElementById("progress-message");

                    if (progressBarContainer && progressBar && progressMessage) {
                        progressBarContainer.style.display = "block";
                        progressBar.style.width = "0%";
                        progressBar.textContent = "0%";
                        progressMessage.textContent = "Cargando juegos... (0%)";
                    }

                    // Iniciar la verificación del estado de descarga
                    const downloadCheckInterval = setInterval(() => {
                        fetch("/api/check_download_status")
                            .then(response => response.json())
                            .then(data => {
                                if (!data.download_complete) {
                                    // Actualizar la barra de progreso
                                    progressBar.style.width = `${data.progress}%`;
                                    progressBar.textContent = `${data.progress}%`;
                                    progressMessage.textContent = `Cargando juegos... (${data.progress}%)`;
                                } else {
                                    // Ocultar la barra de progreso cuando la descarga esté completa
                                    progressBarContainer.style.display = "none";
                                    clearInterval(downloadCheckInterval);

                                    // Recargar la página para mostrar los nuevos juegos
                                    location.reload();
                                }
                            })
                            .catch(error => {
                                console.error("Error verificando estado de descarga:", error);
                            });
                    }, 2000); // Verificar cada 2 segundos

                    // Mostrar mensaje de éxito
                    flash("Steam ID actualizado correctamente. Descargando juegos y logros...", "success");
                } else {
                    flash("Error al actualizar el ID de Steam: " + data.error, "danger");
                }
            })
            .catch(error => {
                console.error("Error:", error);
                flash("Error al actualizar el ID de Steam.", "danger");
            });
        });
    }

    /*******************************************************
     * 3. Cambiar información de Riot
     *******************************************************/
    const saveRiotInfoBtn = document.getElementById("saveRiotInfoButton");
    if (saveRiotInfoBtn) {
        saveRiotInfoBtn.addEventListener("click", function() {
            const newSummonerName = document.getElementById("summonerNameInput").value;
            const newRiotTag = document.getElementById("riotTagInput").value;

            fetch("/update_riot_info", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ summoner_name: newSummonerName, riot_tag: newRiotTag })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    // Recargar la página para mostrar los cambios
                    location.reload();
                } else {
                    alert("Error al actualizar la información de Riot: " + data.error);
                }
            })
            .catch(error => {
                console.error("Error:", error);
                alert("Error al actualizar la información de Riot.");
            });
        });
    }

    /*******************************************************
     * 4. Cambiar la contraseña
     *******************************************************/
    const savePasswordBtn = document.getElementById("savePasswordButton");
    if (savePasswordBtn) {
        savePasswordBtn.addEventListener("click", function() {
            const currentPassword = document.getElementById("currentPasswordInput").value;
            const newPassword = document.getElementById("newPasswordInput").value;
            const confirmNewPassword = document.getElementById("confirmNewPasswordInput").value;

            if (newPassword !== confirmNewPassword) {
                flash("Las nuevas contraseñas no coinciden", "danger");
                return;
            }

            fetch("/update_password", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    current_password: currentPassword,
                    new_password: newPassword,
                    confirm_new_password: confirmNewPassword
                })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    const passwordModal = bootstrap.Modal.getInstance(document.getElementById('changePasswordModal'));
                    if (passwordModal) passwordModal.hide();
                    flash("Contraseña cambiada correctamente.", "success");

                    // Limpiar los campos del formulario de contraseña
                    document.getElementById("currentPasswordInput").value = "";
                    document.getElementById("newPasswordInput").value = "";
                    document.getElementById("confirmNewPasswordInput").value = "";

                    setTimeout(() => location.reload(), 500);
                } else {
                    flash("Error al cambiar la contraseña: " + data.error, "danger");
                }
            })
            .catch(error => {
                console.error("Error:", error);
                flash("Error al cambiar la contraseña.", "danger");
            });
        });
    }

    /*******************************************************
     * 5. Cambiar el icono de perfil
     *******************************************************/
    window.changeProfileIcon = function(icon_id) {
        fetch("/change_profile_icon", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ icon_id: parseInt(icon_id) })
        })
        .then(response => {
            if (!response.ok) throw new Error("Error en la respuesta del servidor");
            return response.json();
        })
        .then(data => {
            if (data.success) {
                bootstrap.Modal.getInstance(document.getElementById('changeProfileIconModal')).hide();
                flash("Icono de perfil actualizado correctamente.", "success");
                setTimeout(() => location.reload(), 500);
            } else {
                flash("Error: " + data.error, "danger");
            }
        })
        .catch(error => {
            console.error("Error al cambiar el icono:", error);
            flash("Error al cambiar el icono. Revisa la consola para más detalles.", "danger");
        });
    };
});
