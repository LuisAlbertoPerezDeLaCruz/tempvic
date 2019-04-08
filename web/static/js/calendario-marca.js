// calendario-marca.js

//Variables Globales
var pagina = 1;
var numPages=1;
var resultado = '';
var marcaAlias='';

$(document).ready(function () {

    $('.vic-load').hide();

    $(".searchString").keyup(function (e) {
        if (e.which == 13) {
            clear_form_search();
        }
    });

    settingsDelFiltro();

    $('.vic-list-detallado').click(function () {
        vic_list_detallado();
    });

    $('.vic-list-simple').click(function () {
        vic_list_simple();
    });

    $('.accionPagineo').click(function () {
        pagina++;
        actualizar(pagina);
    });
});

function vic_list_detallado() {


    $('.vic-div-list-simple').show(100);


    $('.vic-list-detallado').parent().parent().removeClass('disabled');
    $('.vic-list-simple').parent().parent().addClass('disabled');

    $('.vic-list-detallado-col').show(100);
    $('.vic-list-simple-col').hide(100);


}

function vic_list_simple() {

    $('.vic-div-list-simple').hide(100);

    $('.vic-list-detallado').parent().parent().addClass('disabled');
    $('.vic-list-simple').parent().parent().removeClass('disabled');

    $('.vic-list-detallado-col').hide(100);
    $('.vic-list-simple-col').show(100);

}

function settingsDelFiltro() {

    $(".vic-calendar-filter-close").click(function () {
        $(".vic-filtro").hide(100);
    });

    $(".vic-calendar-filter-open").click(function () {
        $(".vic-filtro").show(100);
    });

    $(".disciplina").change(function () {
        $('.searchString').val('');
    });

    $(".localidad").change(function () {
        $('.searchString').val('');
    });

    $(".instructor").change(function () {
        $('.searchString').val('');
    });

    $(".marcaAlias").change(function () {
    });

    $('.fechaInicioCalendar').datetimepicker({
        icons: {
            time: 'fas fa-clock',
            date: 'fas fa-calendar-alt',
            up: 'fa fa-chevron-up',
            down: 'fa fa-chevron-down',
            previous: 'fa fa-chevron-left',
            next: 'fa fa-chevron-right',
            today: 'glyphicon glyphicon-screenshot',
            clear: 'fa fa-trash',
            close: 'fa fa-times'
        },
        useCurrent: false,
        ignoreReadonly: true,
        locale: 'es',
        format: 'DD/MM/YYYY',
    }).on("dp.change", function (e) {
        $('.fechaFinalizacionCalendar').val();
    });

    $('.fechaFinalizacionCalendar').datetimepicker({
        //defaultDate: myDate.setDate(myDate.getDate()),
        icons: {
            time: 'fas fa-clock',
            date: 'fas fa-calendar-alt',
            up: 'fa fa-chevron-up',
            down: 'fa fa-chevron-down',
            previous: 'fa fa-chevron-left',
            next: 'fa fa-chevron-right',
            today: 'glyphicon glyphicon-screenshot',
            clear: 'fa fa-trash',
            close: 'fa fa-times'
        },
        useCurrent: false,
        ignoreReadonly: true,
        locale: 'es',
        format: 'DD/MM/YYYY',
    }).on("dp.change", function (e) {
        if (!(fechaFinalizacion2 == $('.fechaFinalizacionCalendar').val())) {
            $('.fechaSelect').html('');
        }
        fechaFinalizacion2 = '';
    });

    function clear_form_search() {

        $('.disciplina').val('');
        $('.localidad').val('');
        $('.instructor').val('');

    }

}

function showModalMarca() {

    $(".filtroCalendarioMarca").find(".modal-title").html(' <span class="	color: #393939;	font-family: Roboto;	font-size: 16px;	font-weight: bold;	line-height: 17px;">Buscar' + '<span>');
    $(".filtroCalendarioMarca").modal();

}

function setValuesfiltro() {
    resultado = '';

    var parametros = '';

    var fechaInicio = "";
    var fechaFinalizacion = "";
    var disciplina = "";
    var localidad = "";
    var instructor = "";
    var marcaAlias = "";
    var searchString = "";
    var status = "";

    $(".fechaInicio").each(function (index) {
        if ($(this).val()) {
            fechaInicio = $(this).val();
        }
    });


    $(".fechaFinalizacion").each(function (index) {
        if ($(this).val()) {
            fechaFinalizacion = $(this).val();
        }
    });

    if (fechaInicio != '' && fechaFinalizacion != '') {
        if (resultado != '') {
            resultado = resultado + ', ';
        }
        resultado += fechaInicio + ' al ' + fechaFinalizacion;

    }

    $(".searchString").each(function (index) {
        if ($(this).val()) {
            searchString = $(this).val();

            if (resultado != '') {
                resultado = resultado + ', ';
            }
            resultado += $(this).val();
        }
    });

    $(".marcaAlias").each(function (index) {
        if ($(this).val()) {
            marcaAlias = $(this).val();

            if (resultado != '') {
                resultado = resultado + ', ';
            }

            resultado += $(this).val();
            return false;
        }
    });


    $(".disciplina").each(function (index) {
        if ($(this).val()) {
            disciplina = $(this).val();
            if (resultado != '') {
                resultado = resultado + ', ';
            }
            resultado += $(this).val();

        }
    });


    $(".instructor").each(function (index) {
        if ($(this).val()) {
            instructor = $(this).val();
            if (resultado != '') {
                resultado = resultado + ', ';
            }
            resultado += $(this).val();
        }
    });


    $(".localidad").each(function (index) {
        if ($(this).val()) {
            localidad = $(this).val();
            if (resultado != '') {
                resultado = resultado + ', ';
            }
            resultado += $(this).val();
        }
    });


    $(".status").each(function (index) {
        if ($(this).val()) {
            status = $(this).val();
        }
    });

    var parametros = '';

    parametros += '?fechaInicio=' + fechaInicio;
    parametros += '&fechaFinalizacion=' + fechaFinalizacion;
    parametros += '&disciplina=' + disciplina;
    parametros += '&localidad=' + localidad;
    parametros += '&instructor=' + instructor;
    parametros += '&marcaAlias=' + marcaAlias;
    parametros += '&status=' + status;
    parametros += '&searchString=' + searchString;
    parametros = parametros.split(' ').join('+');

    return parametros;

}

function actualizar(pagina) {
/*    if (pagina >= numPages) {
        $('.accionPagineo').hide();
        return;
    }*/
    divPagina = '<div class="seccionPagina seccionPagina_' + pagina + '" ></div>';
    $('.seccionPrincipal').append(divPagina);
    seccionCarga = 'seccionPagina_' + pagina;
    $('.vic-load').show();
    parametros = setValuesfiltro();
    parametros += '&pagina=' + pagina;
    parametros += '&pk=' + marcaAlias;
    $('.' + seccionCarga).load(urlIZQ + parametros, function () {
        $('.vic-load').hide();
        if (pagina >= numPages)
            $('.accionPagineo').hide();
    });

}

function inicializar() {
    $('.resultado_div').hide();
    $('.seccionPagina').remove();
    div = '<div class="seccionPagina" ></div>'
    $('.seccionPrincipal').append(div);
    seccionCarga = 'seccionPagina'
    $('.vic-load').show();
    parametros = setValuesfiltro();
    parametros += '&reset=True';
    urlIZQ='calendario-marca'
    $('.' + seccionCarga).load(urlIZQ + parametros, function () {
        $('.vic-load').hide();
        pagina = 1;
        if (pagina >= numPages)
            $('.accionPagineo').hide();
        else
            $('.accionPagineo').show();
        if (resultado != '') {
            $(".resultado").html(resultado);
            $('.resultado_div').show();
        } else {
            $('.resultado_div').hide();
        }
    })
    $('.filtroCalendarioMarca').modal('hide');
}