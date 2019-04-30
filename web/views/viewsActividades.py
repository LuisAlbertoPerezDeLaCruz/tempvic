# -*- coding: utf-8 -*-
#######################
# viewsActividades.py #
#######################

from web.crons import *
from web.clases import *
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
import json
from accounts.views import manejarSesion

from django.http import JsonResponse
from web.templatetags.filtrosEspeciales import *
from django.core import serializers
from web.views.viewsGeneral import actualizaBaseEnSerie

from django.db import transaction
from django.contrib import messages


@login_required(login_url='/requerirLogon')
def validate_salon(request):
    try:
        salonIdIn = int(request.GET.get('salonId', None))
    except:
        salonIdIn = None
    try:
        capacidad = Salon.objects.get(id=salonIdIn).s_capacidad
        overflow = Salon.objects.get(id=salonIdIn).s_overflow
    except:
        capacidad = 0
        overflow = 0
    data = {
        'capacidad': capacidad,
        'overflow': overflow,
    }
    return JsonResponse(data)


@login_required(login_url='/requerirLogon')
def obtenerActividadAjax(request):
    actividadIn = request.GET['actividad']
    actividad = Actividad.objects.get(id=int(actividadIn))
    disciplina = serializers.serialize('json', [Disciplina.objects.get(id=actividad.ac_disciplina_id)])
    if actividad.ac_instructor_id == 0 or actividad.ac_instructor_id == None:
        instructor = 0
    else:
        instructor = serializers.serialize('json', [UserProfile.objects.get(id=actividad.ac_instructor_id)])
    if actividad.ac_salon_id == 0 or actividad.ac_salon_id == None:
        salon = 0
    else:
        salon = serializers.serialize('json', [Salon.objects.get(id=actividad.ac_salon_id)])
    marca = serializers.serialize('json', [Marca.objects.get(id=actividad.ac_marca_id)])

    if (actividad.ac_OpcionSerie == 'Si'):
        ultimaActividadSerie = serializers.serialize('json', [
            Actividad.objects.filter(ac_actividadBaseSerieId=actividad.ac_actividadBaseSerieId).order_by('-ac_fecha')[
            :1].get()])
    else:
        ultimaActividadSerie = serializers.serialize('json', [Actividad.objects.get(id=int(actividadIn))])

    if (actividad.ac_OpcionSerie == 'Si'):
        cantidadEnSerie=Actividad.objects.filter(ac_actividadBaseSerieId=actividad.ac_actividadBaseSerieId,id__gte=actividad.id).count()
    else:
        cantidadEnSerie=1

    instructoresReservados = []
    salonesReservados = []

    if Participantes.objects.filter(pa_actividad_id=actividad.id):

        actividadId=actividad.id
        fecha=actividad.ac_fecha
        hora_iniIn=actividad.ac_hora_ini
        hora_finIn=actividad.ac_hora_fin
        marca_in=actividad.ac_marca

        actividadesSolapadas1 = Actividad.objects.filter(
            ac_marca=marca_in,
            ac_fecha=fecha,
            ac_estado_id__in=TipoEstatus().tipoTodas,
            ac_hora_ini__lte=hora_iniIn, ac_hora_fin__gt=hora_iniIn
        ).exclude(id=actividadId)

        actividadesSolapadas2 = Actividad.objects.filter(
            ac_marca=marca_in,
            ac_fecha=fecha,
            ac_estado_id__in=TipoEstatus().tipoTodas,
            ac_hora_ini__lt=hora_finIn, ac_hora_fin__gte=hora_finIn
        ).exclude(id=actividadId)

        actividadesSolapadas3 = Actividad.objects.filter(
            ac_marca=marca_in,
            ac_fecha=fecha,
            ac_estado_id__in=TipoEstatus().tipoTodas,
            ac_hora_ini__gte=hora_iniIn, ac_hora_fin__lte=hora_finIn
        ).exclude(id=actividadId)

        actividadesSolapadas=actividadesSolapadas1|actividadesSolapadas2|actividadesSolapadas3

        for actividadSolapada in actividadesSolapadas:
            instructoresReservados.append(actividadSolapada.ac_instructor.id)
            salonesReservados.append(actividadSolapada.ac_salon_id)

    actividad = serializers.serialize('json', [Actividad.objects.get(id=int(actividadIn))])

    return HttpResponse(json.dumps([actividad, ultimaActividadSerie, disciplina,instructor, salon, marca, cantidadEnSerie, instructoresReservados, salonesReservados]),content_type='application/json')


@login_required(login_url='/requerirLogon')
def obtenerActividadRecargaAjax(request):
    actividadId = request.GET['actividadId']
    pa = PerfilActividad(actividadId)
    pm = PerfilMarca(pa.actividadAliasMarca)
    productosPermitidos = []
    if pa.actividadProductosPermitidos:
        productos = Producto.objects.filter(p_marca_id=pm.marcaId, p_activo=True,
                                            id__in=pa.actividadProductosPermitidos)
    else:
        productos = Producto.objects.filter(p_marca_id=pm.marcaId, p_activo=True)
    for producto in productos:
        productosPermitidos.append({'nombre': producto.p_nombre, 'precio': bolivares(producto.p_precio),
                                    'descuento': formatoPorcentaje(producto.p_descuento),
                                    'creditos': producto.p_creditos,
                                    'vencimiento': producto.p_duracion_meses})

    return HttpResponse(json.dumps([pm.marcaNombre, pm.marcaRazonSocial, pm.marcaRif, pm.marcaCuentasBancarias,
                                    productosPermitidos, pm.marcaTelefono1, pm.marcaTelefono2, pm.marcaCorreo]),
                        content_type='application/json')


@login_required(login_url='/requerirLogon')
def tabRecarga(request):
    actividadId = request.GET['actividadId']
    pa = PerfilActividad(actividadId)
    pm = PerfilMarca(pa.actividadAliasMarca)
    productosPermitidos = []
    if pa.actividadProductosPermitidos:
        productos = Producto.objects.filter(p_marca_id=pm.marcaId, p_activo=True,
                                            id__in=pa.actividadProductosPermitidos).exclude(p_tipo=3)
    else:
        productos = Producto.objects.filter(p_marca_id=pm.marcaId, p_activo=True).exclude(p_tipo=3)
    for producto in productos:
        productosPermitidos.append({'nombre': producto.p_nombre, 'precio': bolivares(producto.p_precio),
                                    'descuento': formatoPorcentaje(producto.p_descuento),
                                    'creditos': producto.p_creditos,
                                    'vencimiento': producto.p_duracion_meses,
                                    'id':producto.id,
                                    })
    return render(request, 'tabRecarga.html', {
        'perfilMarca': pm,
        'perfilActividad': pa,
        'productosPermitidos': productosPermitidos,
        'correoUsuario': request.user.username,
    })


@login_required(login_url='/requerirLogon')
def tabPlanesCentros(request):
    marcaId = request.GET['marcaId']
    marca = Marca.objects.get(id=marcaId)
    pm = PerfilMarca(marca.m_alias)
    productosPermitidos = []
    productos = Producto.objects.filter(p_marca_id=pm.marcaId, p_activo=True).exclude(p_tipo=3)
    for producto in productos:
        productosPermitidos.append({'nombre': producto.p_nombre, 'precio': bolivares(producto.p_precio),
                                    'descuento': formatoPorcentaje(producto.p_descuento),
                                    'creditos': producto.p_creditos,
                                    'vencimiento': producto.p_duracion_meses,
                                    'id':producto.id,
                                    })
    return render(request, 'tabRecarga.html', {
        'perfilMarca': pm,
        'productosPermitidos': productosPermitidos,
    })


@login_required(login_url='/requerirLogon')
def clasedetail(request, pk, pka):
    actividad=Actividad.objects.get(id=pka)
    vs = manejarSesion(request, pk, False)
    pa = PerfilActividad(pka)
    ids = Relacion.objects.values_list('r_user__pk', flat=True).filter(r_marca__m_alias=pa.actividadAliasMarca,
                                                                       r_entrenador=True)
    instructores = UserProfile.objects.filter(u_user__pk__in=set(ids))
    perfilMarca = PerfilMarca(pa.actividadAliasMarca)

    if pa.actividadEstado=='En Conflicto':
        tupleConflictos=encuentraConflictosEnActividad(actividad)
        conflictos=preparaDiccionarioDeConflictos(actividad,tupleConflictos[0],tupleConflictos[1],tupleConflictos[2],tupleConflictos[3])
    else:
        conflictos=None

    return render(request, 'clase-detail.html', {
        'perfilActividad': pa,
        'disciplinas': Disciplina.objects.all(),
        'salones': Salon.objects.filter(s_marca__m_alias=pa.actividadAliasMarca),
        'instructores': instructores,
        'vs': vs,
        'perfilMarca': perfilMarca,
        'conflictos':conflictos,
    })


@login_required(login_url='/requerirLogon')
def crearActividadAjax(request):
    diasTipoSMIn=''
    fechaIn = request.GET['fecha']
    fechaCheck=datetime.strptime(fechaIn, "%d/%m/%Y").date()
    #horaCheck = datetime.strptime(request.GET['hora_ini'], "%I:%M %p").time()
    #fechaHoraCheck=datetime.combine(fechaCheck,horaCheck)
    horaCheck = datetime.strptime('11:30 PM', "%I:%M %p").time()
    fechaHoraCheck = datetime.combine(fechaCheck, horaCheck)
    if fechaHoraCheck < datetime.today():
        mensaje = "Acción no realizada fecha menor que fecha actual."
        print(mensaje)
        opcion = -99
        return HttpResponse(json.dumps([opcion, 0, {}]), content_type='application/json')
    serieIn = request.GET['serie']
    actividadId=request.GET['actividadId']

    marcaIn = request.GET['marca']
    pm = PerfilMarca(Marca.objects.get(id=marcaIn).m_alias)

    actividadBaseSerieId = int(request.GET['ac_actividadBaseSerieId'])
    productosPermitidosIn = str(request.GET['productosPermitidos']).split(",")
    productosPermitidos = []

    if 'planReferenciado' in request.GET:
        planReferenciadoIn=request.GET['planReferenciado']
    else:
        planReferenciadoIn=None

    if planReferenciadoIn==u'1':
        productosPermitidos.append(pm.marcaProductoTipoReferenciado.id)

    for productoPermitido in productosPermitidosIn:
        if int(productoPermitido) > 0:
            productosPermitidos.append(int(productoPermitido))
    try:
        with transaction.atomic():
            if actividadBaseSerieId > 0:
                actividadVieja = Actividad.objects.get(pk=actividadId)
                diasTipoSMIn = actividadVieja.ac_patron_repeticion_semanal
                diasTipoSMIn = diasTipoSMIn.replace('S,','SABADO,').replace('L,','LUNES,').replace('M,','MARTES,').replace('X,','MIERCOLES,')
                diasTipoSMIn = diasTipoSMIn.replace('J,','JUEVES,').replace('V,','VIERNES,').replace('D,','DOMINGO,')
                if (serieIn == 'No'):
                    updateActividad = True
                    actividadBaseSerieId = actividadVieja.id
                    ultimaFechaSerie = None
                else:
                    updateActividad = False
                    ultimaFechaSerie = \
                        Actividad.objects.filter(ac_actividadBaseSerieId=int(actividadBaseSerieId)).order_by('-ac_fecha')[
                            0].ac_fecha
                    eliminarActividades(fechaIn, actividadBaseSerieId)
            else:
                updateActividad = False
                ultimaFechaSerie = None

            hora_iniIn = request.GET['hora_ini']
            hora_finIn = request.GET['hora_fin']
            instructorIn = request.GET['instructor']
            marcaCorreo = Marca.objects.get(id=int(request.GET['marca'])).m_correo
            if (instructorIn == '-1' or instructorIn == ''):
                instructorIn = 0
            else:
                instructorIn = int(request.GET['instructor'])
            colaborador1In = request.GET['colaborador1']
            if (colaborador1In == '-1' or colaborador1In == ''):
                colaborador1In = 0
            else:
                colaborador1In = int(colaborador1In)
            colaborador2In = request.GET['colaborador2']
            if (colaborador2In == '-1' or colaborador2In == ''):
                colaborador2In = 0
            else:
                colaborador2In = int(colaborador2In)
            disciplinaIn = request.GET['disciplina']
            descripcionIn = request.GET['descripcion']
            nombreIn = request.GET['nombre']
            minIn = request.GET['min']
            if minIn == u'-1' or minIn == u'':
                minIn = 0
            maxIn = request.GET['max']
            if maxIn == u'-1' or maxIn == u'':
                maxIn = 0
            esperaIn = request.GET['espera']
            if esperaIn == u'-1' or esperaIn == u'':
                esperaIn = 0
            dificultadIn = request.GET['dificultad']
            instruccionesIn = request.GET['instrucciones']
            salaIn = request.GET['sala']
            if (salaIn == u'-1' or salaIn == ''):
                salaIn = 0
                maxIn = 0
                minIn = 0
                esperaIn = 0
            inversionIn = request.GET['inversion']
            if inversionIn == u'':
                inversionIn = u'0'
            inversionIn=inversionIn.replace('.','').replace(',','.')

            costoIn = request.GET['costo']

            bonificacionIn = request.GET['bonificacion']
            if (bonificacionIn == u''):
                bonificacionIn = '0'
            bonificacionIn = bonificacionIn.replace('.', '').replace(',', '.')
            repetirComoIn = request.GET['repetirComo']
            if not diasTipoSMIn:
                diasTipoSMIn=request.GET['diasTipoSM']
            if diasTipoSMIn:
                diasTipoSM=diasTipoSMIn.split(',')
                diasTipoSM = [x for x in diasTipoSM if x != '']
            else:
                diasTipoSM=None
            nuncaIn = request.GET['nunca']
            if nuncaIn == u'1':
                nuncaIn = 'Si'
            else:
                nuncaIn = 'No'
            doIn = request.GET['do']
            if doIn == '':
                doIn = '0'
            despdIn = request.GET['despd']
            if despdIn == u'1':
                despdIn = 'Si'
            else:
                despdIn = 'No'
            fdespIn = request.GET['fdesp']

            if repetirComoIn:
                if fdespIn or doIn !='0':
                    pass
                else:
                    opcion = 7
                    return HttpResponse(json.dumps([opcion, 0, {}]),content_type='application/json')

            if pm.marcaProductoTipoReferenciado:
                if pm.marcaProductoTipoReferenciado.id in productosPermitidos:
                    actividadReferenciada = True
                else:
                    actividadReferenciada = False
            else:
                actividadReferenciada = False
            enfIn = request.GET['enf']
            if enfIn == u'1':
                enfIn = 'Si'
            else:
                enfIn = 'No'
            if fdespIn:
                enfIn = 'Si'
            fechas = determinarFechas(fechaIn, serieIn, nuncaIn, doIn, despdIn, fdespIn, repetirComoIn,diasTipoSM)
            conflictosSalas = []
            conflictosInstructores = []
            conflictosColaborador1 = []
            conflictosColaborador2 = []

            padreSerie = False
            padreSerieId = 0

            hayConflictos = False

            for fecha in fechas:

                if ultimaFechaSerie:
                    if fecha > ultimaFechaSerie:
                        continue
                if updateActividad:
                    oActividad = actividadVieja
                    diasTipoSMIn=''
                    repetirComoIn=''
                    oActividad.ac_patron_repeticion_semanal=diasTipoSMIn
                    padreSerie = True
                    padreSerieId = actividadBaseSerieId
                else:
                    oActividad = Actividad()
                    oActividad.ac_patron_repeticion_semanal = diasTipoSMIn.replace('SABADO','S,').replace('DOMINGO','D,')
                    oActividad.ac_patron_repeticion_semanal = oActividad.ac_patron_repeticion_semanal.replace('LUNES', 'L,').replace('MARTES', 'M,')
                    oActividad.ac_patron_repeticion_semanal = oActividad.ac_patron_repeticion_semanal.replace('MIERCOLES', 'X,').replace('JUEVES', 'J,')
                    oActividad.ac_patron_repeticion_semanal = oActividad.ac_patron_repeticion_semanal.replace('VIERNES', 'V,').replace(',,',',')

                oActividad.ac_nombre = nombreIn
                oActividad.ac_productos_permitidos = productosPermitidos
                oActividad.ac_fecha = fecha
                oActividad.ac_estado = EstadoActividad.objects.get(ea_estado='Planifico')
                oActividad.ac_hora_ini = datetime.strptime(hora_iniIn, "%I:%M %p").time()
                oActividad.ac_hora_fin = datetime.strptime(hora_finIn, "%I:%M %p").time()
                if (oActividad.ac_fecha == datetime.now().date()):
                    if (oActividad.ac_hora_ini < datetime.now().time()):
                        oActividad = None
                        opcion = 5
                        continue
                oActividad.ac_descripcion = descripcionIn
                oActividad.ac_cap_max = int(maxIn)
                oActividad.ac_cap_min = int(minIn)
                oActividad.ac_cap_max_espera = int(esperaIn)
                oActividad.ac_precio = float(inversionIn)
                oActividad.ac_creditos = int(costoIn)
                oActividad.ac_disciplina_id = int(disciplinaIn)
                oActividad.ac_actividadBaseSerieId = padreSerieId
                if not updateActividad:
                    oActividad.ac_OpcionSerie = serieIn
                oActividad.ac_nunca = nuncaIn
                oActividad.ac_repetirComo = repetirComoIn
                oActividad.ac_despd = despdIn
                oActividad.ac_do = int(doIn)
                oActividad.ac_enf = enfIn
                if type(fdespIn) is unicode:
                    if (fdespIn == u''):
                        oActividad.ac_fdesp = fecha
                    else:
                        try:
                            fdespIn = datetime.strptime(fdespIn, "%d/%m/%Y").date()
                        except:
                            fdespIn = datetime.strptime(fdespIn, "%Y-%m-%d").date()
                        oActividad.ac_fdesp = fdespIn
                else:
                    oActividad.ac_fdesp = fdespIn

                if updateActividad:
                    actualizaBaseEnSerie(actividadVieja)
                    oActividad.ac_actividadBaseSerieId = actividadBaseSerieId
                    oActividad.ac_OpcionSerie = 'No'
                    oActividad.ac_repetirComo = ''
                    oActividad.ac_despd = 'No'
                    oActividad.ac_do = 1
                    oActividad.ac_enf = 'No'
                    oActividad.ac_fdesp = oActividad.ac_fecha

                oActividad.ac_instructor_id = instructorIn
                oActividad.ac_colaborador1 = int(colaborador1In)
                oActividad.ac_colaborador2 = int(colaborador1In)
                oActividad.ac_salon_id = int(salaIn)

                oActividad.ac_marca_id = int(marcaIn)
                oActividad.ac_bono = float(bonificacionIn)
                oActividad.ac_intensidad = int(dificultadIn)
                oActividad.ac_instrucciones = instruccionesIn
                if oActividad.ac_salon_id == 0:
                    oActividad.ac_salon_id = None
                if oActividad.ac_instructor_id == 0:
                    oActividad.ac_instructor_id = None

                oActividad.ac_referenciado = actividadReferenciada

                huboCambios = False

                if updateActividad:
                    fieldsNuevos = oActividad.__dict__
                    fieldsViejos = Actividad.objects.get(pk=actividadId).__dict__
                    for field,value in fieldsViejos.items():
                        if 'ac_' in field:
                            if fieldsNuevos[field]!=value:
                                if 'ac_estado' not in field:
                                    huboCambios=True
                                    break

                try:

                    if huboCambios or not updateActividad:
                        oActividad.save()

                        if (salaIn != 0):
                            conflictoSala = determinarConflictosSalas(salaIn, fecha, hora_iniIn, hora_finIn, oActividad.id)
                            if conflictoSala:
                                conflictosSalas+=conflictoSala
                        else:
                            conflictoSala=None

                        if (instructorIn != 0):
                            conflictoInstructor = determinarConflictosInstructores(instructorIn, fecha, hora_iniIn, hora_finIn, oActividad.id)
                            if conflictoInstructor:
                                conflictosInstructores+=conflictoInstructor
                        else:
                            conflictoInstructor=None

                        if (colaborador1In != 0):
                            conflictoColaborador1 = determinarConflictosColaborador1(colaborador1In, fecha, hora_iniIn, hora_finIn, oActividad.id)
                            if conflictoColaborador1:
                                conflictosColaborador1+=conflictoColaborador1
                        else:
                            conflictoColaborador1=None

                        if (colaborador2In != 0):
                            conflictoColaborador2 = determinarConflictosColaborador2(colaborador2In, fecha, hora_iniIn, hora_finIn, oActividad.id)
                            if conflictoColaborador2:
                                conflictosColaborador2+=conflictoColaborador2
                        else:
                            conflictoColaborador2=None

                        # Por ahora ignoramos conflictos con colaboradores
                        conflictoColaborador1 = None
                        conflictoColaborador2 = None

                        if (conflictoSala or conflictoInstructor or conflictoColaborador1 or conflictoColaborador2):
                            oActividad.ac_estado = EstadoActividad.objects.get(ea_estado='En Conflicto')
                            hayConflictos = True


                        if padreSerie == False:
                            padreSerieId = Actividad.objects.filter().order_by('-id')[0].id
                            padreSerie = True

                        oActividad.ac_actividadBaseSerieId = padreSerieId
                        oActividad.save()

                        # Notificacion al atleta
                        mn=ManejoNotificaciones()
                        mf=ManejoFechas()
                        pa=PerfilActividad(oActividad.id)
                        for atleta in pa.actividadParticipantes():
                            texto = {}
                            texto['actividad'] = pa.actividadNombre
                            texto['fechaHora'] = mf.fechaCorta(pa.actividadFecha) + ' ' + mf.horaCivil(pa.actividadHoraInicio)
                            texto['instructor'] = pa.actividadNombreInstructor
                            texto['mensaje'] = 'ha sido modificada'
                            mn.marca_informa_atleta(User.objects.get(id=atleta['participanteUserId']), pa.actividadMarca, texto,
                                                    'MA')

                    else:
                        opcion=6
                        return HttpResponse(json.dumps([opcion, oActividad.ac_actividadBaseSerieId, []]),
                                            content_type='application/json')

                except Exception as e:
                    mensaje = "Actividad no pudo ser modificada. Error:" + str(e)
                    print(mensaje)
                    opcion = -1

            if updateActividad:
                if hayConflictos:
                    if (actividadBaseSerieId == 0):
                        opcion = 2
                    else:
                        opcion = 4
                else:
                    if (actividadBaseSerieId == 0):
                        opcion = 1
                    else:
                        opcion = 3
            else:
                if hayConflictos:
                    if (actividadBaseSerieId == 0):
                        opcion = 2
                    else:
                        opcion = 4
                else:
                    if (actividadBaseSerieId == 0):
                        opcion = 1
                    else:
                        opcion = 3

            update_activities()

            try:
                nombreSala = Salon.objects.get(id=int(salaIn)).s_nombre
            except:
                nombreSala = 'Sin Asignar'

            try:
                nombreInstructor = User.objects.get(
                    id=UserProfile.objects.get(id=int(instructorIn)).u_user_id).first_name + ' ' + User.objects.get(
                    id=UserProfile.objects.get(id=int(instructorIn)).u_user_id).last_name
            except:
                nombreInstructor = 'Sin Asignar'

            try:
                nombreColaborador1 = User.objects.get(
                    id=UserProfile.objects.get(id=int(colaborador1In)).u_user_id).first_name + ' ' + User.objects.get(
                    id=UserProfile.objects.get(id=int(colaborador1In)).u_user_id).last_name
            except:
                nombreColaborador1 = 'Sin Asignar'

            try:
                nombreColaborador2 = User.objects.get(
                    id=UserProfile.objects.get(id=int(colaborador2In)).u_user_id).first_name + ' ' + User.objects.get(
                    id=UserProfile.objects.get(id=int(colaborador2In)).u_user_id).last_name
            except:
                nombreColaborador2 = 'Sin Asignar'

            conflictos = []
            if conflictosSalas:
                for fecha, horas, actividad, localizador in conflictosSalas:
                    conflicto = {}
                    conflicto['tipo'] = 'Sala ' + nombreSala + ' ocupada en actividad ' + actividad
                    conflicto['fecha'] = '{0}/{1}/{2}'.format(fecha.day, fecha.month, fecha.year)
                    conflicto['horas'] = horas
                    conflicto['localizador'] = localizador
                    conflictos.append(conflicto)
            if conflictosInstructores:
                for fecha, horas, actividad, localizador in conflictosInstructores:
                    conflicto = {}
                    conflicto['tipo'] = 'Instructor ' + nombreInstructor + ' previamente asignado a ' + actividad
                    conflicto['fecha'] = '{0}/{1}/{2}'.format(fecha.day, fecha.month, fecha.year)
                    conflicto['horas'] = horas
                    conflicto['localizador'] = localizador
                    conflictos.append(conflicto)
            if conflictosColaborador1:
                for fecha, horas, actividad, localizador in conflictosColaborador1:
                    conflicto = {}
                    conflicto['tipo'] = 'Colaborador ' + nombreColaborador1 + ' previamente asignado a ' + actividad
                    conflicto['fecha'] = '{0}/{1}/{2}'.format(fecha.day, fecha.month, fecha.year)
                    conflicto['horas'] = horas
                    conflicto['localizador'] = localizador
                    conflictos.append(conflicto)
            if conflictosColaborador2:
                for fecha, horas, actividad, localizador in conflictosColaborador2:
                    conflicto = {}
                    conflicto['tipo'] = 'Colaborador ' + nombreColaborador2 + ' previamente asignado a ' + actividad
                    conflicto['fecha'] = '{0}/{1}/{2}'.format(fecha.day, fecha.month, fecha.year)
                    conflicto['horas'] = horas
                    conflicto['localizador'] = localizador
                    conflictos.append(conflicto)

            try:
                return HttpResponse(json.dumps([opcion, oActividad.ac_actividadBaseSerieId, conflictos]),
                                    content_type='application/json')
            except:
                return HttpResponse(json.dumps([opcion, 0]), content_type='application/json')
    except Exception as ex:
        messages.error(request,'Found Error. Executed Rollback')
        return HttpResponse(json.dumps([-1,-1]), content_type='application/json')


@login_required(login_url='/requerirLogon')
def eliminarActividadAjax(request):
    fechaActividadIn = request.GET['fechaActividad']
    fecha = datetime.strptime(fechaActividadIn, "%Y-%m-%d").date()
    elimTipoIn = request.GET['elimTipo']
    actividadId = int(request.GET['actividadId'])
    actividad = Actividad.objects.get(id=actividadId);
    actividadBaseSerieId = actividad.ac_actividadBaseSerieId

    try:
        with transaction.atomic():
            if elimTipoIn == 'Serie':
                Actividad.objects.filter(ac_actividadBaseSerieId=int(actividadBaseSerieId), ac_fecha__gte=fecha).delete()
                opcion = 2
            else:
                Actividad.objects.filter(id=actividadId).delete()
                opcion = 1
    except:
        messages.error(request,'Found Error. Executed Rollback')
        opcion = -1
    return HttpResponse(json.dumps([opcion]), content_type='application/json')

@login_required(login_url='/requerirLogon')
def reactivarActividadAjax(request):
    actividadId = int(request.GET['actividad'])
    actividad = Actividad.objects.get(id=actividadId)
    actividad.ac_estado = EstadoActividad.objects.get(ea_estado='Planifico')
    try:
        actividad.save()
        update_activities()
        opcion=1
    except:
        opcion=2
    return HttpResponse(json.dumps([opcion]), content_type='application/json')

@login_required(login_url='/requerirLogon')
def suspenderActividadAjax(request):
    pk = request.user.profile.u_alias
    vs = manejarSesion(request, pk, False)
    actividadId = int(request.GET['actividad'])
    pa = PerfilActividad(actividadId)
    todoOk = True
    mn = ManejoNotificaciones()
    mf = ManejoFechas()
    for atleta in pa.actividadEsperas():
        vicsafe = VicSafe(atleta['participanteUserId'], vs.marcaEnUsoId, vs)
        strReturn = vicsafe.registrar_reintegro_por_suspension(pa)
        if strReturn != 'ok':
            todoOk = False
        else:
            # Notificacion al atleta
            texto={}
            texto['actividad']=pa.actividadNombre
            texto['fechaHora']=mf.fechaCorta(pa.actividadFecha)+ ' ' + mf.horaCivil(pa.actividadHoraInicio)
            texto['instructor']=pa.actividadNombreInstructor
            texto['mensaje']='ha sido suspendida'
            mn.marca_informa_atleta(User.objects.get(id=atleta['participanteUserId']),pa.actividadMarca,texto,'CA')
    for atleta in pa.actividadParticipantes():
        vicsafe = VicSafe(atleta['participanteUserId'], vs.marcaEnUsoId, vs)
        strReturn = vicsafe.registrar_reintegro_por_suspension(pa)
        if strReturn != 'ok':
            todoOk = False
        else:
            # Notificacion al atleta
            texto={}
            texto['actividad']=pa.actividadNombre
            texto['fechaHora']=mf.fechaCorta(pa.actividadFecha)+ ' ' + mf.horaCivil(pa.actividadHoraInicio)
            texto['instructor']=pa.actividadNombreInstructor
            texto['mensaje']='ha sido suspendida'
            mn.marca_informa_atleta(User.objects.get(id=atleta['participanteUserId']),pa.actividadMarca,texto,'CA')

    actividad = Actividad.objects.get(id=actividadId)
    actividad.ac_estado = EstadoActividad.objects.get(ea_estado='Cancelada')
    actividad.save()
    pa=PerfilActividad(actividadId)
    if pa.actividadEsSerie:
        oActividad = Actividad.objects.get(id=actividadId)
        actualizaBaseEnSerie(oActividad)
        oActividad.ac_actividadBaseSerieId = actividadId
        oActividad.ac_OpcionSerie = 'No'
        oActividad.ac_repetirComo = ''
        oActividad.ac_despd = 'No'
        oActividad.ac_do = 1
        oActividad.ac_enf = 'No'
        oActividad.ac_fdesp = oActividad.ac_fecha
        oActividad.save()
    if todoOk:
        opcion = 1
        # Notificacion al instructor
        texto = {}
        texto['actividad'] = actividad.ac_nombre
        texto['fechaHora'] = mf.fechaCorta(actividad.ac_fecha) + ' ' + mf.horaCivil(actividad.ac_hora_ini)
        texto['instructor'] = actividad.ac_instructor.u_user.first_name + ' ' + actividad.ac_instructor.u_user.last_name
        texto['mensaje'] = 'ha sido suspendida'
        instructor = actividad.ac_instructor.u_user
        mn.marca_informa_atleta(instructor, actividad.ac_marca, texto, 'CA')

        # Notificacion a la marca
        texto = {}
        texto['actividad'] = actividad.ac_nombre
        texto['fechaHora'] = mf.fechaCorta(actividad.ac_fecha) + ' ' + mf.horaCivil(actividad.ac_hora_ini)
        texto['instructor'] = actividad.ac_instructor.u_user.first_name + ' ' + actividad.ac_instructor.u_user.last_name
        texto['mensaje'] = 'ha sido suspendida'
        dueno=Dueno.objects.get(d_marca=actividad.ac_marca)
        mn.marca_informa_marca(dueno.d_user, actividad.ac_marca, texto, 'CA')

    else:
        opcion = 2
    return HttpResponse(json.dumps([opcion]), content_type='application/json')


def eliminarActividades(fechaIn, actividadBaseSerieId):
    fecha = datetime.strptime(fechaIn, "%d/%m/%Y").date()
    Actividad.objects.filter(ac_actividadBaseSerieId=int(actividadBaseSerieId), ac_fecha__gte=fecha).delete()
    return


def determinarFechas(fechaIn, serieIn, nuncaIn, doIn, despdIn, fdespIn, repetirComoIn,diasTipoSM):
    # Constantes
    LUNES = 0
    MARTES = 1
    MIERCOLES = 2
    JUEVES = 3
    VIERNES = 4
    SABADO = 5
    DOMINGO = 6

    fechaIn = datetime.strptime(fechaIn, "%d/%m/%Y").date()

    fecha = fechaIn
    fechaEnd = fechaIn
    if (type(fdespIn) is unicode):
        if (fdespIn != u''):
            try:
                fdespIn = datetime.strptime(fdespIn, "%d/%m/%Y").date()
            except:
                fdespIn = datetime.strptime(fdespIn, "%Y-%m-%d").date()

    fechas = []
    dias = []

    if (doIn != ''):
        doIn = int(doIn)
    else:
        doIn = 0

    if (repetirComoIn == u'DI'):
        dias = [LUNES, MARTES, MIERCOLES, JUEVES, VIERNES, SABADO, DOMINGO]
    elif (repetirComoIn == u'LM'):
        dias = [LUNES, MIERCOLES, VIERNES]
    elif (repetirComoIn == u'MJ'):
        dias = [MARTES, JUEVES]
    elif (repetirComoIn == u'LV'):
        dias = [LUNES, MARTES, MIERCOLES, JUEVES, VIERNES]
    elif (repetirComoIn == u'SM'):
        dias=[]
        if 'LUNES' in diasTipoSM:
            dias.append(LUNES)
        if 'MARTES' in diasTipoSM:
            dias.append(MARTES)
        if 'MIERCOLES' in diasTipoSM:
            dias.append(MIERCOLES)
        if 'JUEVES' in diasTipoSM:
            dias.append(JUEVES)
        if 'VIERNES' in diasTipoSM:
            dias.append(VIERNES)
        if 'SABADO' in diasTipoSM:
            dias.append(SABADO)
        if 'DOMINGO' in diasTipoSM:
            dias.append(DOMINGO)
    else:
        dias.append(fechaIn.weekday())

    if (serieIn == u'No'):
        fechas.append(fechaIn)
    else:
        if (nuncaIn == u'1'):
            fechaEnd = fechaIn + timedelta(weeks=52)
        elif (doIn > 0):
            if (repetirComoIn == u'ME'):
                fechaEnd = fechaIn + timedelta(months=doIn)
            else:
                fechaEnd = fechaIn + timedelta(weeks=doIn) - timedelta(days=1)
        else:
            fechaEnd = fdespIn

        while fecha <= fechaEnd:
            if (fecha.weekday() in dias):
                fechas.append(fecha)
            fecha += timedelta(days=1)

    return fechas

def encuentraConflictosEnActividad(actividad):
    mf=ManejoFechas()
    fecha=str(actividad.ac_fecha)
    hora_iniIn=mf.horaCivil(actividad.ac_hora_ini)
    hora_finIn=mf.horaCivil(actividad.ac_hora_fin)
    salaIn=actividad.ac_salon_id
    instructorIn=actividad.ac_instructor_id
    colaborador1In=actividad.ac_colaborador1
    colaborador2In=actividad.ac_colaborador2

    conflictosSalas = []
    conflictosInstructores = []
    conflictosColaborador1 = []
    conflictosColaborador2 = []

    if (salaIn > 0):
        conflictoSala = determinarConflictosSalas(salaIn, fecha, hora_iniIn, hora_finIn, actividad.id)
        if conflictoSala:
            conflictosSalas += conflictoSala
    else:
        conflictoSala = None

    if (instructorIn > 0):
        conflictoInstructor = determinarConflictosInstructores(instructorIn, fecha, hora_iniIn, hora_finIn,
                                                               actividad.id)
        if conflictoInstructor:
            conflictosInstructores += conflictoInstructor
    else:
        conflictoInstructor = None

    if (colaborador1In > 0):
        conflictoColaborador1 = determinarConflictosColaborador1(colaborador1In, fecha, hora_iniIn, hora_finIn,
                                                                 actividad.id)
        if conflictoColaborador1:
            conflictosColaborador1 += conflictoColaborador1
    else:
        conflictoColaborador1 = None

    if (colaborador2In > 0):
        conflictoColaborador2 = determinarConflictosColaborador2(colaborador2In, fecha, hora_iniIn, hora_finIn,
                                                                 actividad.id)
        if conflictoColaborador2:
            conflictosColaborador2 += conflictoColaborador2
    else:
        conflictoColaborador2 = None

    return (conflictoSala,conflictoInstructor,conflictoColaborador1,conflictoColaborador2)

def preparaDiccionarioDeConflictos(actividad,conflictosSalas,conflictosInstructores,conflictosColaborador1,conflictosColaborador2):
    pa=PerfilActividad(actividad.id)
    nombreSala=pa.actividadNombre
    nombreInstructor=pa.actividadNombreInstructor
    nombreColaborador1=pa.actividadNombreAyudante1
    nombreColaborador2=pa.actividadNombreAyudante2
    conflictos = []
    if conflictosSalas:
        for fecha, horas, actividad, localizador in conflictosSalas:
            conflicto = {}
            conflicto['tipo'] = 'Sala ' + nombreSala + ' ocupada en actividad ' + actividad
            conflicto['fecha'] = '{0}/{1}/{2}'.format(fecha.day, fecha.month, fecha.year)
            conflicto['horas'] = horas
            conflicto['localizador'] = localizador
            conflictos.append(conflicto)
    if conflictosInstructores:
        for fecha, horas, actividad, localizador in conflictosInstructores:
            conflicto = {}
            conflicto['tipo'] = 'Instructor ' + nombreInstructor + ' previamente asignado a ' + actividad
            conflicto['fecha'] = '{0}/{1}/{2}'.format(fecha.day, fecha.month, fecha.year)
            conflicto['horas'] = horas
            conflicto['localizador'] = localizador
            conflictos.append(conflicto)
    if conflictosColaborador1:
        for fecha, horas, actividad, localizador in conflictosColaborador1:
            conflicto = {}
            conflicto['tipo'] = 'Colaborador ' + nombreColaborador1 + ' previamente asignado a ' + actividad
            conflicto['fecha'] = '{0}/{1}/{2}'.format(fecha.day, fecha.month, fecha.year)
            conflicto['horas'] = horas
            conflicto['localizador'] = localizador
            conflictos.append(conflicto)
    if conflictosColaborador2:
        for fecha, horas, actividad, localizador in conflictosColaborador2:
            conflicto = {}
            conflicto['tipo'] = 'Colaborador ' + nombreColaborador2 + ' previamente asignado a ' + actividad
            conflicto['fecha'] = '{0}/{1}/{2}'.format(fecha.day, fecha.month, fecha.year)
            conflicto['horas'] = horas
            conflicto['localizador'] = localizador
            conflictos.append(conflicto)

    return conflictos


def determinarConflictosSalas(salaIn, fecha, hora_iniIn, hora_finIn, actividadId):
    hora_iniIn = datetime.strptime(hora_iniIn, "%I:%M %p").time()
    hora_finIn = datetime.strptime(hora_finIn, "%I:%M %p").time()
    fechaEnConflicto = None
    actividadEnConflicto = None
    horaEnConflicto = None
    localizadorEnConflicto = None

    actividadesConflictivas1 = Actividad.objects.filter(
        ac_fecha=fecha, ac_salon_id=int(salaIn),
        ac_estado_id__in=TipoEstatus().tipoTodasMasCulminada,
        ac_hora_ini__lte=hora_iniIn, ac_hora_fin__gt=hora_iniIn
    ).exclude(id=actividadId)

    actividadesConflictivas2 = Actividad.objects.filter(
        ac_fecha=fecha, ac_salon_id=int(salaIn),
        ac_estado_id__in=TipoEstatus().tipoTodasMasCulminada,
        ac_hora_ini__lt=hora_finIn, ac_hora_fin__gte=hora_finIn
    ).exclude(id=actividadId)

    actividadesConflictivas3 = Actividad.objects.filter(
        ac_fecha=fecha, ac_salon_id=int(salaIn),
        ac_estado_id__in=TipoEstatus().tipoTodasMasCulminada,
        ac_hora_ini__gte=hora_iniIn, ac_hora_fin__lte=hora_finIn
    ).exclude(id=actividadId)

    actividadesConflictivas=actividadesConflictivas1|actividadesConflictivas2|actividadesConflictivas3

    conflictos=[]

    if actividadesConflictivas:
        for actividad in actividadesConflictivas:
            fechaEnConflicto = actividad.ac_fecha
            actividadEnConflicto = actividad.ac_nombre
            horaEnConflicto = '{0} - {1}'.format(horaCivil(hora_iniIn), horaCivil(hora_finIn))
            perfilActividad = PerfilActividad(actividad.id)
            localizadorEnConflicto = perfilActividad.actividadLocalizador
            conflictos.append((fechaEnConflicto, horaEnConflicto, actividadEnConflicto, localizadorEnConflicto))

    return conflictos


def determinarConflictosInstructores(instructor, fecha, hora_iniIn, hora_finIn, actividadId):
    hora_iniIn = datetime.strptime(hora_iniIn, "%I:%M %p").time()
    hora_finIn = datetime.strptime(hora_finIn, "%I:%M %p").time()
    fechaEnConflicto = None
    actividadEnConflicto = None
    horaEnConflicto = None
    localizadorEnConflicto = None

    actividadesConflictivas1 = Actividad.objects.filter(
        ac_fecha=fecha, ac_instructor_id=int(instructor),
        ac_estado_id__in=TipoEstatus().tipoTodasMasCulminada,
        ac_hora_ini__lte=hora_iniIn, ac_hora_fin__gt=hora_iniIn
    ).exclude(id=actividadId)

    actividadesConflictivas2 = Actividad.objects.filter(
        ac_fecha=fecha, ac_instructor_id=int(instructor),
        ac_estado_id__in=TipoEstatus().tipoTodasMasCulminada,
        ac_hora_ini__lt=hora_finIn, ac_hora_fin__gte=hora_finIn
    ).exclude(id=actividadId)

    actividadesConflictivas3 = Actividad.objects.filter(
        ac_fecha=fecha, ac_instructor_id=int(instructor),
        ac_estado_id__in=TipoEstatus().tipoTodasMasCulminada,
        ac_hora_ini__gte=hora_iniIn, ac_hora_fin__lte=hora_finIn
    ).exclude(id=actividadId)

    actividadesConflictivas=actividadesConflictivas1|actividadesConflictivas2|actividadesConflictivas3

    conflictos=[]

    if actividadesConflictivas:
        for actividad in actividadesConflictivas:
            fechaEnConflicto = actividad.ac_fecha
            actividadEnConflicto = actividad.ac_nombre
            horaEnConflicto = '{0} - {1}'.format(horaCivil(hora_iniIn), horaCivil(hora_finIn))
            perfilActividad = PerfilActividad(actividad.id)
            localizadorEnConflicto = perfilActividad.actividadLocalizador
            conflictos.append((fechaEnConflicto, horaEnConflicto, actividadEnConflicto, localizadorEnConflicto))

    return conflictos


def determinarConflictosColaborador1(colaborador1, fecha, hora_iniIn, hora_finIn, actividadId):
    hora_iniIn = datetime.strptime(hora_iniIn, "%I:%M %p").time()
    hora_finIn = datetime.strptime(hora_finIn, "%I:%M %p").time()
    fechaEnConflicto = None
    actividadEnConflicto = None
    horaEnConflicto = None
    localizadorEnConflicto = None

    actividadesConflictivas1 = Actividad.objects.filter(
        ac_fecha=fecha, ac_colaborador1_id=int(colaborador1),
        ac_estado_id__in=TipoEstatus().tipoTodasMasCulminada,
        ac_hora_ini__lte=hora_iniIn, ac_hora_fin__gt=hora_iniIn
    ).exclude(id=actividadId)

    actividadesConflictivas2 = Actividad.objects.filter(
        ac_fecha=fecha, ac_colaborador1_id=int(colaborador1),
        ac_estado_id__in=TipoEstatus().tipoTodasMasCulminada,
        ac_hora_ini__lt=hora_finIn, ac_hora_fin__gte=hora_finIn
    ).exclude(id=actividadId)

    actividadesConflictivas3 = Actividad.objects.filter(
        ac_fecha=fecha, ac_colaborador1_id=int(colaborador1),
        ac_estado_id__in=TipoEstatus().tipoTodasMasCulminada,
        ac_hora_ini__gte=hora_iniIn, ac_hora_fin__lte=hora_finIn
    ).exclude(id=actividadId)

    actividadesConflictivas=actividadesConflictivas1|actividadesConflictivas2|actividadesConflictivas3

    conflictos=[]

    if actividadesConflictivas:
        for actividad in actividadesConflictivas:
            fechaEnConflicto = actividad.ac_fecha
            actividadEnConflicto = actividad.ac_nombre
            horaEnConflicto = '{0} - {1}'.format(horaCivil(hora_iniIn), horaCivil(hora_finIn))
            perfilActividad = PerfilActividad(actividad.id)
            localizadorEnConflicto = perfilActividad.actividadLocalizador
            conflictos.append((fechaEnConflicto, horaEnConflicto, actividadEnConflicto, localizadorEnConflicto))

    return conflictos


def determinarConflictosColaborador2(colaborador2, fecha, hora_iniIn, hora_finIn, actividadId):
    hora_iniIn = datetime.strptime(hora_iniIn, "%I:%M %p").time()
    hora_finIn = datetime.strptime(hora_finIn, "%I:%M %p").time()
    fechaEnConflicto = None
    actividadEnConflicto = None
    horaEnConflicto = None
    localizadorEnConflicto = None

    actividadesConflictivas1 = Actividad.objects.filter(
        ac_fecha=fecha, ac_colaborador2_id=int(colaborador2),
        ac_estado_id__in=TipoEstatus().tipoTodasMasCulminada,
        ac_hora_ini__lte=hora_iniIn, ac_hora_fin__gt=hora_iniIn
    ).exclude(id=actividadId)

    actividadesConflictivas2 = Actividad.objects.filter(
        ac_fecha=fecha, ac_colaborador2_id=int(colaborador2),
        ac_estado_id__in=TipoEstatus().tipoTodasMasCulminada,
        ac_hora_ini__lt=hora_finIn, ac_hora_fin__gte=hora_finIn
    ).exclude(id=actividadId)

    actividadesConflictivas3 = Actividad.objects.filter(
        ac_fecha=fecha, ac_colaborador2_id=int(colaborador2),
        ac_estado_id__in=TipoEstatus().tipoTodasMasCulminada,
        ac_hora_ini__gte=hora_iniIn, ac_hora_fin__lte=hora_finIn
    ).exclude(id=actividadId)

    actividadesConflictivas = actividadesConflictivas1 | actividadesConflictivas2 | actividadesConflictivas3

    conflictos = []

    if actividadesConflictivas:
        for actividad in actividadesConflictivas:
            fechaEnConflicto = actividad.ac_fecha
            actividadEnConflicto = actividad.ac_nombre
            horaEnConflicto = '{0} - {1}'.format(horaCivil(hora_iniIn), horaCivil(hora_finIn))
            perfilActividad = PerfilActividad(actividad.id)
            localizadorEnConflicto = perfilActividad.actividadLocalizador
            conflictos.append((fechaEnConflicto, horaEnConflicto, actividadEnConflicto, localizadorEnConflicto))

    return conflictos

def enviarCorreoConflictosActividades(marcaCorreo, conflictosSalas, conflictosInstructores, conflictosColaborador1,
                                      conflictosColaborador2):
    mailto = marcaCorreo
    cuerpoCorreo = ""
    if (conflictosSalas):
        cuerpoCorreo += "Conflictos con la Sala (fechas)\n"
        for fecha in conflictosSalas:
            cuerpoCorreo += '\n'
            cuerpoCorreo += str(fecha)
    cuerpoCorreo += '\n'
    if (conflictosInstructores):
        cuerpoCorreo += "Conflictos con el Instructor (fechas)\n"
        for fecha in conflictosInstructores:
            cuerpoCorreo += '\n'
            cuerpoCorreo += str(fecha)
    cuerpoCorreo += '\n'
    if (conflictosColaborador1):
        cuerpoCorreo += "Conflictos con el primer Colaborador (fechas)\n"
        for fecha in conflictosColaborador1:
            cuerpoCorreo += '\n'
            cuerpoCorreo += str(fecha)
    cuerpoCorreo += '\n'
    if (conflictosColaborador2):
        cuerpoCorreo += "Conflictos con el segundo Colaborador (fechas)\n"
        for fecha in conflictosColaborador2:
            cuerpoCorreo += '\n'
            cuerpoCorreo += str(fecha)
    cuerpoCorreo += '---------------\n'
    send_mail('Error al agregar Actividad en Victorius', cuerpoCorreo, 'register@victorius.io', [mailto],
              fail_silently=False, )
    return
