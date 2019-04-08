//Notificaciones.js

var estado=''

function llamarFuncion(callback, fn) {
    callback(notificacionId,estado);
}

function aceptarSolicitudUsuario(marcaId, userId, notificacionId) {
    $.ajax({
        data: {
            'opcion': 1,
            'userId': userId,
            'marcaId': marcaId,
            'notificacionId': notificacionId,
            'disparador': 'atleta',
        },
        async: false,
        url: '/ajax/aceptarRechazarSolicitud',
        success: function (data) {
            estado=data.estado;
            alertVictorius('Solicitud de afiliación aceptada', 1);
        },
    });
}

function rechazarSolicitudUsuario(marcaId, userId, notificacionId) {
    $.ajax({
        data: {
            'opcion': 0,
            'userId': userId,
            'marcaId': marcaId,
            'notificacionId': notificacionId,
            'disparador': 'atleta',
        },
        async: false,
        url: '/ajax/aceptarRechazarSolicitud',
        success: function (data) {
            estado=data.estado;
            alertVictorius('Solicitud de afiliación eliminada', 1);
        },
    });
}

function aceptarInvitacionMarca(marcaId, userId, notificacionId) {
    $.ajax({
        data: {
            'opcion': 1,
            'userId': userId,
            'marcaId': marcaId,
            'notificacionId': notificacionId,
            'disparador': 'marca',
        },
        async: false,
        url: '/ajax/aceptarRechazarSolicitud',
        success: function (data) {
            estado=data.estado;
            alertVictorius('Invitación de afiliación aceptada', 1);
        },
    });
}

function rechazarInvitacionMarca(marcaId, userId, notificacionId) {
    $.ajax({
        data: {
            'opcion': 0,
            'userId': userId,
            'marcaId': marcaId,
            'notificacionId': notificacionId,
            'disparador': 'marca',
        },
        async: false,
        url: '/ajax/aceptarRechazarSolicitud',
        success: function (data) {
            estado=data.estado;
            alertVictorius('Solicitud de afiliación eliminada', 1);
        },
    });
}

function actualizar() {
    location.reload();
}

function modificarBotones(notificacionId,estado){
    $('#idAceptar-'+notificacionId).text(estado);
    $('#idAceptar-'+notificacionId).attr('disabled', true);
    $('#idAceptar-'+notificacionId).removeClass('btn-default btn-xs reservar-active');
    $('#idRechazar-'+notificacionId).hide();
}
