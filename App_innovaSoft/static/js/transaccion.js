// transaccion.js
$(document).ready(function() {
    let rowCount = 1; // Contador de filas

    // Función para calcular totales
    function calcularTotales() {
        let totalDebe = 0;
        let totalHaber = 0;

        // Sumar los valores de cada columna "Debe" y "Haber"
        $('.debe').each(function() {
            let debe = parseFloat($(this).val()) || 0;
            totalDebe += debe;
        });
        $('.haber').each(function() {
            let haber = parseFloat($(this).val()) || 0;
            totalHaber += haber;
        });

        // Mostrar los totales en la fila de total
        $('#totalDebe').text(totalDebe.toFixed(2));
        $('#totalHaber').text(totalHaber.toFixed(2));
    }

     // Función para guardar las transacciones al hacer clic en el botón "Guardar"
     $('#guardarTransacciones').click(function() {
        let transacciones = [];

        $('#dynamicTable tbody tr').each(function() {
            let numeroCuenta = $(this).find('.numero-cuenta').val();
            let nombreCuenta = $(this).find('.numero-cuenta').val(); // Ajusta esto si tienes otro campo para el nombre
            let debe = $(this).find('.debe').val();
            let haber = $(this).find('.haber').val();

            // Añade cada transacción a la lista
            transacciones.push({
                'numeroCuenta': numeroCuenta,
                'nombreCuenta': nombreCuenta,
                'debe': debe,
                'haber': haber
            });
        });

        // Enviar los datos al servidor
        $.ajax({
            url: '/guardar_transacciones/',
            method: 'POST',
            data: {
                'transacciones': JSON.stringify(transacciones),
                'csrfmiddlewaretoken': $('input[name=csrfmiddlewaretoken]').val()
            },
            success: function(response) {
                alert("Transacciones guardadas exitosamente en el Libro Mayor.");
            },
            error: function() {
                alert("Hubo un error al guardar las transacciones.");
            }
        });
    });
});


     // Función para agregar fila
    $('#addRow').click(function() {
        rowCount++;
        let newRow = `<tr>
                        <td><select class="form-control" id="cuentaSelect" name="cuenta">
                    <option value="" disabled selected>Seleccione una cuenta</option>
                    {% for cuenta in CatalogoCuentas %}
                        <option value="{{ cuenta.id }}">{{ cuenta.nombre }}</option>
                    {% endfor %}
                </select></td>
                        <td><input type="text" class="form-control numero-cuenta" placeholder="Nombre de Cuenta" readonly></td>
                        <td><input type="number" class="form-control debe" placeholder="Debe"></td>            <td><input type="number" class="form-control haber" placeholder="Haber"></td>
                        <td><button class="btn btn-danger btn-sm removeRow">Eliminar</button></td>
                      </tr>`;
        $('#dynamicTable tbody').append(newRow);
        calcularTotales();
    });

    // Función para eliminar fila
    $(document).on('click', '.removeRow', function() {
        $(this).closest('tr').remove();
        calcularTotales();
    });

    // Calcular totales cuando se cambia el valor de "Debe" o "Haber"
    $(document).on('input', '.debe, .haber', function() {
        calcularTotales();
    });

    // Calcular totales inicialmente
    calcularTotales();
