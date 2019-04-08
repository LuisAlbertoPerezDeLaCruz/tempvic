// calendario-atleta.js

//Variables Globales
var IZQ = 1;
var DER = 2;
var EXT = 3;
var marcaAlias = '';
var tabActual = IZQ;
var paginaIZQ = 1;
var paginaDER = 1;
var paginaEXT = 1;
var numPagesIZQ = 1;
var numPagesDER = 1;
var resultado = '';
var urlIZQ='';
var urlDER='';
var pka=''

$(document).ready(function () {

    $('.vic-load').hide();

    $(".searchString").keyup(function (e) {
        if (e.which == 13) {
            clear_form_search();
        }
    });

    settingsDelFiltro();
    settingDelCarrusel();
    settingsTabs();
    settingDelCarrusel();

    $('.accionPagineoIZQ').click(function () {
        actualizar(1);
    });

    $('.accionPagineoDER').click(function () {
        actualizar(1);
    });

    $('.tabIzquierdo').click();

});

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

function settingDelCarrusel() {
    $('.customCarruselAtleta').owlCarousel({
        loop: false,
        center: false,
        dots: false,
        margin: 5,
        responsiveClass: true,
        animateOut: 'fadeOut',
        nav: false,
        autoWidth: false,
        rewind: true,
        responsive: {
            0: {
                items: 4,
                dots: false
            },
            600: {
                items: 6,
                dots: false
            }
        }
    });
}


function setCarruserActividades() {
    $('.customCarruserActividades').owlCarousel({
        loop: false,
        center: false,
        dots: false,
        margin: 5,
        responsiveClass: true,
        animateOut: 'fadeOut',
        nav: false,
        autoWidth: false,
        rewind: true,
        responsive: {
            0: {
                items: 4,
                dots: false
            },
            600: {
                items: 6,
                dots: false
            }
        }
    });
}

function settingsTabs() {

    $('.tabIzquierdo').click(function () {
        $('.tabDerecho').removeClass('active');
        $('.tabExtra').removeClass('active');
        $('.tabIzquierdo').addClass('active');
        $('#idDivContenidoDER').hide();
        $('.seccionPaginaDer').hide();
        $('#idDivContenidoIZQ').show();
        $('.seccionPaginaIzq').show();
        $('#idDivContenidoEXT').hide();
        $('.seccionPaginaExt').hide();
        if (paginaIZQ < numPagesIZQ) {
            $('.accionPagineoIZQ').show();
        }
        $('.accionPagineoDER').hide();
        tabActual = IZQ;
        $('.soloDER').hide();
        $('.soloIZQ').show();
    });

    $('.tabDerecho').click(function () {
        $('.tabIzquierdo').removeClass('active');
        $('.tabExtra').removeClass('active');
        $('.tabDerecho').addClass('active');
        $('#idDivContenidoIZQ').hide();
        $('.seccionPaginaIzq').hide();
        $('#idDivContenidoDER').show();
        $('.seccionPaginaDer').show();
        $('#idDivContenidoEXT').hide();
        $('.seccionPaginaExt').hide();
        if (paginaDER < numPagesDER) {
            $('.accionPagineoDER').show();
        }
        $('.accionPagineoIZQ').hide();
        tabActual = DER;
        $('.soloIZQ').hide();
        $('.soloDER').show();
    });

    $('.tabExtra').click(function () {
        $('.tabIzquierdo').removeClass('active');
        $('.tabDerecho').removeClass('active');
        $('.tabExtra').addClass('active')
        $('#idDivContenidoIZQ').hide();
        $('#idDivContenidoDER').hide();
        $('#idDivContenidoEXT').show();
        tabActual = EXT;
    });

}

function seleccionCirculoMarca(marcaAlias) {
    $('.vic-circle-calendar-carrusel').removeClass('selected');
    $('.vic-circle-calendar-carrusel-lap').removeClass('selected');
    $('.vic-circle-calendar-carrusel-65').removeClass('selected');
    if (marcaAlias == '') {
        $('#idDiv_Todos').addClass('selected');
        $('.idDiv_Todos').addClass('selected');
        $('.marcaAlias').val('');
    }
    else {
        $('#idDiv_' + marcaAlias).addClass('selected');
        $('.idDiv_' + marcaAlias).addClass('selected');
        $('.marcaAlias').val(marcaAlias);
    }
    inicializar();
}

function showModalAtleta() {

    $(".filtroCalendarioAtleta").find(".modal-title").html(' <span class="	color: #393939;	font-family: Roboto;	font-size: 16px;	font-weight: bold;	line-height: 17px;">Buscar' + '<span>');
    $(".filtroCalendarioAtleta").modal();

}

function actualizar(incremento) {
    if (typeof incremento=='undefined')
        incremento=0
    if (incremento==0){
        inicializar();
        return false;
    }
    if (tabActual == IZQ) {
        paginaIZQ+=incremento;
        actualizarIZQ(paginaIZQ, paginaDER);
    }
    else if (tabActual == DER) {
        paginaDER+=incremento;
        actualizarDER(paginaIZQ, paginaDER);
    }
    else {
        paginaEXT++;
    }
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
    parametros += '&searchString=' + searchString;
    parametros = parametros.split(' ').join('+');

    return parametros;

}

function actualizarIZQ(paginaIZQ, paginaDER) {
    divPagina = '<div class="seccionPaginaIzq seccionPaginaIzq_' + paginaIZQ + '" ></div>';
    $('.seccionPagina').append(divPagina);
    seccionCarga = 'seccionPaginaIzq_' + paginaIZQ;
    $('.vic-load').show();
    parametros = setValuesfiltro();
    parametros += '&paginaIZQ=' + paginaIZQ;
    parametros += '&paginaDER=' + paginaDER;
    parametros += '&pka=' +pka

    $('.' + seccionCarga).load(urlIZQ + parametros, function () {
        $('.vic-load').hide();
        $('.tabIzquierdo').click();
        if (paginaIZQ >= numPagesIZQ)
            $('.accionPagineoIZQ').hide();
        $('.vic-load').hide();
    });
}

function actualizarDER(paginaIZQ, paginaDER) {
    divPagina = '<div class="seccionPaginaDer seccionPaginaDer_' + paginaDER + '" ></div>';
    $('.seccionPagina').append(divPagina);
    seccionCarga = 'seccionPaginaDer_' + paginaDER;
    $('.vic-load').show();
    parametros = setValuesfiltro();
    parametros += '&paginaIZQ=' + paginaIZQ;
    parametros += '&paginaDER=' + paginaDER;
    parametros += '&pka=' +pka
    $('.' + seccionCarga).load(urlDER + parametros, function () {
        $('.vic-load').hide();
        $('.tabDerecho').click();
        if (paginaDER >= numPagesDER)
            $('.accionPagineoDER').hide();
        $('.vic-load').hide();
    });
}

function resetearCentrosEnCarrusel() {
    marcaAlias = '';
    if (getBrowserWidth()=='xs' || getBrowserWidth()=='sm')
        $("#idMarcaAliasModal").each(function (index) {
            if ($(this).val()) {
                marcaAlias = $(this).val();
                return false;
            }
        });
    else
        $("#idMarcaAlias").each(function (index) {
            if ($(this).val()) {
                marcaAlias = $(this).val();
                return false;
            }
        });
    $('.vic-circle-calendar-carrusel').removeClass('selected');
    if (marcaAlias == '') {
        $('#idDiv_Todos').addClass('selected');
        $('.marcaAlias').val('');
    }
    else {
        $('#idDiv_' + marcaAlias).addClass('selected');
        $('.marcaAlias').val(marcaAlias);
    }
}

function inicializar() {
    $('.accionPagineoIZQ').hide();
    $('.accionPagineoDER').hide();
    $('.mensajesAtleta').hide();
    $('.resultado_div').hide();
    $('.seccionPagina').remove();
    div = '<div class="seccionPagina" ></div>'
    $('.seccionPrincipal').append(div);
    seccionCarga = 'seccionPagina'
    $('.vic-load').show();
    parametros = setValuesfiltro();
    parametros += '&reset=True';
    $('.' + seccionCarga).load(urlIZQ + parametros, function () {
        $('.vic-load').hide();
        if (tabActual==IZQ)
            $('.tabIzquierdo').click();
        else
            $('.tabDerecho').click();
        paginaIZQ = 1;
        paginaDER = 1;
        if (paginaIZQ >= numPagesIZQ)
            $('.accionPagineoIZQ').hide();
        if (paginaDER >= numPagesDER)
            $('.accionPagineoDER').hide();
        if (resultado != '') {
            $(".resultado").html(resultado);
            $('.resultado_div').show();
        } else {
            $('.resultado_div').hide();
        }
        if (numPagesIZQ == 0) {
            $('.sinActividades').show();
        } else {
            $('.sinActividades').hide();
        }
        $('.mensajesAtleta').show();
        $('.vic-load').hide();
    });

    $('.sectionCarruselMisActividades').load('carrusel-mis-actividades', function () {

    });

    $('.filtroCalendarioAtleta').modal('hide');
}

function reservarUsuario(usuario, actividad, costo) {
    reservarActualizar(actualizar, usuario, actividad, costo)}

function cancelarUsuario(usuario, actividad, costo) {
    //cancelarActualizar(actualizar, usuario, actividad, costo)
    eliminarreserva(usuario, actividad, 'reserva');
}

function cancelarListaUsuario(usuario, actividad, costo) {
    //cancelarActualizar(actualizar, usuario, actividad, costo)
    eliminarreserva(usuario, actividad, 'lista de espera');
}

var getBrowserWidth = function(){
    if(window.innerWidth < 768){
        // Extra Small Device
        return "xs";
    } else if(window.innerWidth < 991){
        // Small Device
        return "sm"
    } else if(window.innerWidth < 1199){
        // Medium Device
        return "md"
    } else {
        // Large Device
        return "lg"
    }
};

function prepararLLamadoTabProximas(fecha1, fecha2, hora, tiempoFaltante) {
    var strDias = 'día'
    var strFaltan = 'Falta'
    if (tiempoFaltante > 1) {
        strDias += 's.'
        strFaltan += 'n'
    }
    else {
        strDias += '.'
    }

    $('#idDivFechaTabProximas_1').html(fecha1);
    $('#idDivFechaTabProximas_2').html(fecha2 + ' a las ' + hora + '.');
    if (tiempoFaltante > 0)
        $('#idDivTiempoFaltanteTabProximas').html('(' + strFaltan + ' ' + tiempoFaltante + ' ' + strDias + ')');
    changeTabs('proximas');
}


