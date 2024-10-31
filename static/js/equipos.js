// static/js/equipos.js
document.addEventListener('DOMContentLoaded', function() {
    const posiciones = ['Base', 'Escolta', 'Alero', 'Ala-pívot', 'Pívot'];
    let equipoActual = {
        tipo: null,
        jugadores: []
    };

    // Manejador para los botones de tipo de equipo
    document.querySelectorAll('.tipo-equipo-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.tipo-equipo-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            equipoActual.tipo = this.dataset.tipo;
            mostrarSelectorPosiciones();
        });
    });

    function mostrarSelectorPosiciones() {
        const container = document.getElementById('posicionesContainer');
        container.innerHTML = '';
        
        posiciones.forEach(posicion => {
            const div = document.createElement('div');
            div.className = 'mb-3';
            div.innerHTML = `
                <h5>${posicion}</h5>
                <select class="form-select jugador-select" data-posicion="${posicion}">
                    <option value="">Seleccionar jugador</option>
                </select>
            `;
            container.appendChild(div);
            
            cargarJugadoresPorPosicion(posicion);
        });
    }

    async function cargarJugadoresPorPosicion(posicion) {
        try {
            const response = await fetch(`/api/jugadores_por_posicion/${posicion}`);
            const jugadores = await response.json();
            
            const select = document.querySelector(`select[data-posicion="${posicion}"]`);
            jugadores.forEach(jugador => {
                const option = document.createElement('option');
                option.value = jugador.id;
                option.textContent = `${jugador.nombre} (${jugador.equipo}) - PPP: ${jugador.puntos_por_partido}`;
                select.appendChild(option);
            });
            
            select.addEventListener('change', function() {
                actualizarEquipo(posicion, this.value);
            });
        } catch (error) {
            console.error('Error al cargar jugadores:', error);
        }
    }

    function actualizarEquipo(posicion, jugadorId) {
        const index = posiciones.indexOf(posicion);
        if (jugadorId) {
            equipoActual.jugadores[index] = jugadorId;
        } else {
            equipoActual.jugadores[index] = null;
        }
        
        // Habilitar botón de guardar si el equipo está completo
        const btnGuardar = document.getElementById('guardarEquipo');
        btnGuardar.disabled = !equipoCompleto();
    }

    function equipoCompleto() {
        return equipoActual.tipo && 
               equipoActual.jugadores.filter(j => j).length === 5;
    }

    document.getElementById('guardarEquipo')?.addEventListener('click', async function() {
        if (!equipoCompleto()) return;
        
        try {
            const response = await fetch('/api/crear_equipo', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    tipo: equipoActual.tipo,
                    jugadores: equipoActual.jugadores.filter(j => j)
                })
            });
            
            const result = await response.json();
            if (result.success) {
                alert('Equipo creado exitosamente');
                location.reload();
            } else {
                alert('Error al crear el equipo: ' + result.error);
            }
        } catch (error) {
            console.error('Error al guardar equipo:', error);
            alert('Error al crear el equipo');
        }
    });
});