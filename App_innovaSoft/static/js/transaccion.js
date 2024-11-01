//transaccion.js

// Función para agregar fila
$('#addRow').click(function() {
    $.ajax({
        url: '/obtener_catalogo_cuentas/',  // Ruta que devuelve los datos de CatalogoCuentas en formato JSON
        type: 'GET',
        dataType: 'json',
        success: function(data) {
            let options = '<option value="" disabled selected>Seleccione una cuenta</option>';
            data.forEach(function(cuenta) {
                options += `<option value="${cuenta.id}">${cuenta.nombre}</option>`;
            });

            let newRow = `<tr>
                            <td>
                                <select class="form-control" name="cuenta">
                                    ${options}
                                </select>
                            </td>
                            <td><input type="number" class="form-control debe" placeholder="Debe"></td>
                            <td><input type="number" class="form-control haber" placeholder="Haber"></td>
                            <td><button class="btn btn-danger btn-sm removeRow">Eliminar</button></td>
                          </tr>`;
            $('#dynamicTable tbody').append(newRow);
            calcularTotales(); // Actualiza los totales después de agregar una fila
        },
        error: function() {
            alert('Error al obtener el catálogo de cuentas');
        }
    });
});

// Evento para actualizar totales en tiempo real al cambiar los valores de "Debe" y "Haber"
$('#dynamicTable').on('input', '.debe, .haber', function() {
    calcularTotales();
});

// Función para calcular totales de "Debe" y "Haber"
function calcularTotales() {
    let totalDebe = 0;
    let totalHaber = 0;

    $('#dynamicTable tbody tr').each(function() {
        const debe = parseFloat($(this).find('.debe').val()) || 0;
        const haber = parseFloat($(this).find('.haber').val()) || 0;
        totalDebe += debe;
        totalHaber += haber;
    });

    $('#totalDebe').text(totalDebe.toFixed(2));
    $('#totalHaber').text(totalHaber.toFixed(2));
}

// Evento para eliminar fila
$('#dynamicTable').on('click', '.removeRow', function() {
    $(this).closest('tr').remove();
    calcularTotales(); // Recalcula los totales después de eliminar una fila
});




//guardar transaccion
// Inicializa un array para las transacciones
let transacciones = [];

// Guarda transacción
document.getElementById('guardar_transaccion').addEventListener('click', () => {
    transacciones = []; // Reinicia el array para evitar duplicados
    document.querySelectorAll('#dynamicTable tbody tr').forEach(row => {
        const idSubCuenta = row.querySelector('[name="cuenta"]').value;
        const idCuentaDetalle = row.querySelector('[name="cuentaDetalle"]').value;
        const debe = row.querySelector('.debe').value || 0;
        const haber = row.querySelector('.haber').value || 0;

        if (idSubCuenta && idCuentaDetalle) {
            transacciones.push({
                idSubCuenta: parseInt(idSubCuenta),
                idCuentaDetalle: parseInt(idCuentaDetalle),
                debe: parseFloat(debe),
                haber: parseFloat(haber)
            });
        } else {
            alert("Falta el id de SubCuenta o idCuentaDetalle en una de las filas.");
        }
    });

    // Enviar las transacciones al servidor
    if (transacciones.length > 0) {
        fetch('/guardar_transaccion/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCookie('csrftoken') // Obtener el token CSRF
            },
            body: JSON.stringify(transacciones)
        })
        .then(response => {
            if (response.ok) {
                alert("Transacciones guardadas exitosamente.");
                // Limpiar el formulario o hacer otras acciones
            } else {
                return response.json().then(data => { throw new Error(data.message); });
            }
        })
        .catch(error => {
            alert("Error al guardar transacciones: " + error.message);
        });
    }
});

// Función para obtener el token CSRF de las cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

