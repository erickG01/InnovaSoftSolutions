// transacciones.js

// Abre el modal de edición/agregar transacción
function openEditModal(id, fecha, cuentaId, debe, haber) {
    document.getElementById('transaccionId').value = id || '';
    document.getElementById('fecha').value = fecha || '';
    document.getElementById('cuentaSelectModal').value = cuentaId || '';
    document.getElementById('debe').value = debe || '';
    document.getElementById('haber').value = haber || '';
    $('#agregarTransaccionModal').modal('show');
}

// Función para guardar o editar la transacción
function guardarTransaccion() {
    const id = document.getElementById('transaccionId').value;
    const cuenta = document.getElementById('cuentaSelectModal').value;
    const fecha = document.getElementById('fecha').value;
    const debe = document.getElementById('debe').value;
    const haber = document.getElementById('haber').value;

    const url = id ? `/editar_transaccion/${id}/` : `/agregar_transaccion/`;
    const method = id ? 'PUT' : 'POST';

    fetch(url, {
        method: method,
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': '{{ csrf_token }}'
        },
        body: JSON.stringify({ cuenta, fecha, debe, haber })
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            location.reload();
        } else {
            alert('Error al guardar la transacción');
        }
    })
    .catch(error => console.error('Error:', error));
}

// Función para eliminar una transacción
function eliminarTransaccion(id) {
    if (confirm('¿Estás seguro de que deseas eliminar esta transacción?')) {
        fetch(`/eliminar_transaccion/${id}/`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}'
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            } else {
                alert('Error al eliminar la transacción');
            }
        })
        .catch(error => console.error('Error:', error));
    }
}