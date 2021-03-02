$("#tipoUsuario").change(function() {
    if ($(this).val() == "visitante") {
      $('#areaDiv').show();
      $('#areaVisitada').attr('required', '');
      $('#areaVisitada').attr('data-error', 'This field is required.');
      $('#descripcionDiv').show();
      $('#descripcion').attr('required', '');
      $('#descripcion').attr('data-error', 'This field is required.');
    } else {
      $('#areaDiv').hide();
      $('#areaVisitada').removeAttr('required');
      $('#areaVisitada').removeAttr('data-error');
      $('#descripcionDiv').hide();
      $('#descripcion').removeAttr('required');
      $('#descripcion').removeAttr('data-error');
    }
  });
  $("#tipoUsuario").trigger("change");