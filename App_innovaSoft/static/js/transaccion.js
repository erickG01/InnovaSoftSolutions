$(document).ready(function() {
    // Evento para agregar una nueva fila
    $('#addRow').click(function(e) {
        e.preventDefault();
        
        // Clonar la última fila de la tabla y restablecer los valores
        let newRow = $('#dynamicTable tbody tr:first').clone();
        newRow.find('input').val(''); // Limpiar campos de entrada
        newRow.find('select').val(''); // Limpiar select
        $('#dynamicTable tbody').append(newRow); // Añadir la nueva fila al final de la tabla
    });

    // Evento para eliminar la fila actual
    $(document).on('click', '.removeRow', function(e) {
        e.preventDefault();
        if ($('#dynamicTable tbody tr').length > 1) {
            $(this).closest('tr').remove();
        } else {
            alert('Debe haber al menos una fila.');
        }
    });
});