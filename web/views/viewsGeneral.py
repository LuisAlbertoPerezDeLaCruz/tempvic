# -*- coding: utf-8 -*-
#######################
# viewsGeneral.py #
#######################

from web.crons import *
from web.templatetags.filtrosEspeciales import *
from calendar import monthrange
from datetime import datetime
from django.contrib import auth
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.mail import send_mail
from django.db.models import Sum
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib import messages
import random
import string
import json
from random import randint
from django.http import JsonResponse
import numpy as np
from web.decorators import user_is_legal
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from PIL import Image
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from django.db import transaction
from accounts.views import manejarSesion

tipo = 0

import logging
log = logging.getLogger('vicLog')

def validate_refpago(request):
    tipoIn = ['Transferencia', 'Deposito', 'POS', 'VPOS', 'Cheque', 'Efectivo', 'Por_Cobrar', 'BECA'].index(
        request.GET.get('tipo'))
    refpago = request.GET.get('refpago', None)
    marcaId = request.GET.get('marcaId', None)
    existeEnCualquierMedio = Pago.objects.filter(p_marca_id=marcaId, p_referencia__iexact=refpago).exists()
    existeEnEsteMedio = False
    diferencia = 0
    if Pago.objects.filter(p_marca_id=marcaId, p_referencia__iexact=refpago, p_medio=tipoIn).exists():
        existeEnEsteMedio = True
        pagos = Pago.objects.filter(p_marca_id=marcaId, p_referencia__iexact=refpago, p_medio=tipo).order_by(
            '-p_referencia_uso')
        pago = pagos[0]
        diferencia = pago.p_diferencia
    data = {
        'existeEnEsteMedio': existeEnEsteMedio,
        'existeEnCualquierMedio': existeEnCualquierMedio,
        'diferencia': diferencia
    }
    return JsonResponse(data)


def cambiarmarca(request, pk):
    request.session['marca'] = pk
    manejarSesion(request, pk, True)

    return redirect("/" + request.session['marca'] + "/dashboard")


def getmes(i):
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre",
             "Noviembre", "Diciembre"]
    return meses[i]

def contactos(request):
    return render(request, "contactos.html")

def updateajax(request):
    user = User.objects.get(username=(request.POST['username']))
    user.first_name = (request.POST['primerNombre'])
    user.last_name = (request.POST['primerApellido'])
    user.set_password(request.POST['passwordIn'])
    user.is_active = True
    user.save()
    profile = UserProfile.objects.get(u_user=user)
    profile.u_secondname = (request.POST['segundoNombre'])
    profile.u_secondlastname = (request.POST['segundoApellido'])
    profile.u_telefono = request.POST['telefono']
    profile.u_calle = request.POST['calle']
    profile.u_urbanizacion = request.POST['urbanizacion']
    profile.u_ciudad = Ciudad.objects.get(c_nombre=request.POST['ciudad'])
    profile.u_municipio = Zona.objects.get(z_municipio=request.POST['municipio'])
    profile.u_pais = Pais.objects.get(p_nombre=request.POST['pais'])
    profile.u_edificioCasa = request.POST['edificioCasa']
    profile.u_direccion = "Edf. " + request.POST['edificioCasa'] + ", Cll/Av." + request.POST['calle'] + " - Urb." + \
                          request.POST['urbanizacion']
    profile.u_alias = (request.POST['alias'])
    profile.u_fecha_nac = (request.POST['fechaNacimiento'])
    profile.u_displinafav1 = Disciplina.objects.get(d_nombre=(request.POST['dic1']))
    profile.u_displinafav2 = Disciplina.objects.get(d_nombre=(request.POST['dic2']))
    profile.save()
    token = Token.objects.get(u_user=user)
    token.u_data = True
    token.save()
    disciplinas = Disciplina.objects.all()
    marcas_publicas = Marca.objects.filter(m_public=True).order_by('m_nombre')
    messages.success(request, 'usuario activado exitosamente.')
    log.info('usuario activado :' + request.user.username)
    return redirect("/")


def crearactualizarcuentaajax(request, pka):
    id = (request.POST['idCuenta'])
    cno = (request.POST['bancoCuent'])
    cnu = (request.POST['numCuenta'])
    if (id == u'-1'):
        ce = (request.POST['estatusCuent']) == u'1'
        try:
            Cuenta.objects.create(c_marca=Marca.objects.get(m_alias=pka), c_status=ce, c_banco=cno, c_numero_cuenta=cnu)
            messages.success(request, 'Cuenta creada exitosamente.')
        except:
            messages.error(request, 'Cuenta no fue creada. Se produjo un error.')
    else:
        ce = (request.POST['estatusCuent'])
        try:
            Cuenta.objects.filter(id=str(id)).update(c_status=ce, c_banco=cno, c_numero_cuenta=cnu)
            messages.success(request, 'Cuenta actualizada exitosamente.')
        except:
            messages.error(request, 'Cuenta no fue actualizada. Se produjo un error.')
    data = ""
    return redirect(request.META['HTTP_REFERER'])


def crearactualizarsalaajax(request, pka):
    id = (request.POST['idSala'])
    n = (request.POST['nameSala'])
    c = (request.POST['capSala'])
    d = (request.POST['dicSala'])
    esReferenciado = False
    if 'idReferenciado' in request.POST:
        if request.POST['idReferenciado'] == 'on':
            esReferenciado = True
    if (id == '-1'):
        try:
            Salon.objects.create(s_marca=Marca.objects.get(m_alias=pka), s_nombre=n, s_capacidad=c,
                                 s_referenciado=esReferenciado,
                                 s_disciplina=Disciplina.objects.get(d_nombre=d))
            messages.success(request, 'Sala creada exitosamente.')
        except:
            messages.error(request, 'Sala no fue creada. Se produjo un error.')
    else:
        try:
            Salon.objects.filter(id=str(id)).update(s_nombre=n, s_capacidad=c, s_referenciado=esReferenciado,
                                                    s_disciplina=Disciplina.objects.get(d_nombre=d))
            messages.success(request, 'Sala actualizada exitosamente.')
        except:
            messages.error(request, 'Sala no fue actualizada. Se produjo un error.')
    data = ""
    return redirect(request.META['HTTP_REFERER'])


def forgotajax(request):
    print('entre en forgotajax')
    c = (request.GET['correo'])
    raw_password = User.objects.make_random_password(8,
                                                     'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ01234567890')
    user = User.objects.get(username=c)
    user.set_password(raw_password)
    try:
        user.save()
        send_mail('Victorius - recordatorio de password',
                  'Buen dia enviamos este correo puesto que usted solicito por nuestro portal, la reincorporacion de su Password \n\n Usuario: ' + c + '\nPassword: ' + raw_password + "\n\n Una vez acceda en el sistema con esta clave podra cambiarla",
                  'register@victorius.io', [c], fail_silently=False, )
        notificacion = "La contraseña ha sido enviado a su correo"
        messages.success(request, 'La contraseña ha sido enviado a su correo.')
    except:
        notificacion = "Hubo un error enviando el correo"
        messages.error(request, 'Hubo un error enviando el correo')
    return HttpResponse(json.dumps(notificacion), content_type='application/json')





def centros(request):
    pk = request.user.profile.u_alias
    vs = manejarSesion(request, pk, False)
    marcasPublicas = Marca.objects.filter().values('m_alias').order_by('m_nombre')
    aPM = []
    i = -1
    idx = -1
    for marcaPublica in marcasPublicas:
        pm = PerfilMarca(marcaPublica['m_alias'])
        i += 1
        if pm.marcaDuenoAlias == pk:
            aPM.append(pm)
            idx = i
            break
    # Ahora lleno la lista excluyendo la marca propietaria si es que existe
    i = -1
    for marcaPublica in marcasPublicas:
        i += 1
        if i != idx:
            pm = PerfilMarca(marcaPublica['m_alias'])
            aPM.append(pm)
    perfilAtleta=PerfilAtleta(pk)
    return render(request, 'centros.html', {
        'vs': vs,
        'centros': aPM,
        'dummy': randint(0, 10000),
        'relaciones': Relacion.objects.filter(r_user=request.user, r_estado='A'),
        'perfilAtleta':perfilAtleta,
    })


def instructores(request):
    return render(request, 'instructores.html', {})


@login_required(login_url='/requerirLogon')
def acerca_de(request):
    return render(request, 'index.html', {})


@login_required(login_url='/requerirLogon')
def calendarioajax(request, pk):
    perfil = UserProfile.objects.get(u_user=request.user)
    avance = int(request.GET['input'])
    ano = int(request.GET['ano'])
    mes = int(request.GET['mes'])
    dia = int(request.GET['dia'])
    ini_sem_ant = datetime(year=ano, month=mes, day=dia)
    ini_sem_ant = ini_sem_ant.replace(hour=0, minute=0, second=0)
    if (avance == 1):
        ini_sem = ini_sem_ant + timedelta(days=7)
    elif (avance == -1):
        ini_sem = ini_sem_ant - timedelta(days=7)
    elif (avance == 0):
        hoy = datetime.today()
        ini_sem = hoy - timedelta(days=hoy.weekday())
        ini_sem = ini_sem.replace(hour=0, minute=0, second=0)
    elif (avance == 2):
        ini_sem = ini_sem_ant
    fin_sem = ini_sem + timedelta(days=7)
    sem = []
    if perfil.u_marca:
        marcas = Dueno.objects.filter(d_user=request.user)
        actual = Marca.objects.get(m_alias=pk)
        actividades_semana = []
        confirmados_semana = []
        reservas_semana = []
        enespera_semana = []
        cuposenespera_semana = []
        entrenadores = []
        for i in range(0, 8):
            sem.append((ini_sem + timedelta(days=i)).day)
            act = Actividad.objects.filter(ac_marca=actual, ac_fecha__range=(
                ini_sem + timedelta(days=i), ini_sem + timedelta(days=i, hours=23))).order_by('ac_hora_ini')
            e = []
            acuser = []
            for a in act:
                acuser = a.ac_instructor
                e.append([a.ac_instructor.u_alias, a.ac_instructor.u_user.pk])
            entrenadores.append(e)
            actividades_semana.append(serializers.serialize('json', act))
            confirmados_semana.append(Actividad.objects.filter(ac_marca=actual, ac_fecha__range=(
                ini_sem + timedelta(days=i), ini_sem + timedelta(days=i, hours=23))).aggregate(
                sum_cupos=Coalesce(Sum('ac_cupos_reservados'), 0)))
            reservas_semana.append(Actividad.objects.filter(ac_marca=actual, ac_fecha__range=(
                ini_sem + timedelta(days=i), ini_sem + timedelta(days=i, hours=23))).aggregate(
                sum_cupos=Coalesce(Sum('ac_cap_max'), 0)))
            enespera_semana.append(Actividad.objects.filter(ac_marca=actual, ac_fecha__range=(
                ini_sem + timedelta(days=i), ini_sem + timedelta(days=i, hours=23))).aggregate(
                sum_cupos=Coalesce(Sum('ac_cupos_en_espera'), 0)))
            cuposenespera_semana.append(Actividad.objects.filter(ac_marca=actual, ac_fecha__range=(
                ini_sem + timedelta(days=i), ini_sem + timedelta(days=i, hours=23))).aggregate(
                sum_cupos=Coalesce(Sum('ac_cap_max_espera'), 0)))
        data1 = [ini_sem.day, ini_sem.month, ini_sem.year]
        data2 = [fin_sem.day, fin_sem.month, fin_sem.year]
        data3 = sem
        data4 = (json.dumps({'a_s': actividades_semana}))
        data5 = (json.dumps({'c_s': confirmados_semana}))
        data6 = (json.dumps({'r_s': reservas_semana}))
        data7 = (json.dumps({'s_s': enespera_semana}))
        data8 = (json.dumps({'e_s': cuposenespera_semana}))
        return HttpResponse(json.dumps([data1, data2, data3, data4, data5, data6, data7, data8, entrenadores]),
                            content_type='application/json')
    else:
        actividades_semana = []
        confirmados_semana = []
        reservas_semana = []
        enespera_semana = []
        entrenadores = []
        cuposenespera_semana = []
        disciplinas = Disciplina.objects.all()
        for i in range(0, 8):
            sem.append((ini_sem + timedelta(days=i)).day)
            p = Participantes.objects.values_list('pa_actividad', flat=True).filter(pa_usuario=request.user,
                                                                                    pa_actividad__ac_fecha__range=(
                                                                                        ini_sem + timedelta(days=i),
                                                                                        ini_sem + timedelta(days=i,
                                                                                                            hours=23)), )
            e = Espera.objects.values_list('es_actividad', flat=True).filter(es_usuario=request.user,
                                                                             es_actividad__ac_fecha__range=(
                                                                                 ini_sem + timedelta(days=i),
                                                                                 ini_sem + timedelta(days=i,
                                                                                                     hours=23)), )
            pq = Actividad.objects.filter(pk__in=p)
            eq = Actividad.objects.filter(pk__in=e)
            if perfil.u_entrenador:
                q = Actividad.objects.filter(ac_instructor=perfil, ac_fecha__range=(
                    ini_sem + timedelta(days=i), ini_sem + timedelta(days=i, hours=23)))
                acthoy = (q | pq | eq).order_by('ac_hora_ini')
            else:
                acthoy = (pq | eq).order_by('ac_hora_ini')
            e = []
            acuser = []
            for a in acthoy:
                acuser = a.ac_instructor
                e.append([a.ac_instructor.u_alias, a.ac_instructor.u_user.pk, a.ac_marca.m_nombre])
            entrenadores.append(e)
            est = []
            for x in acthoy:
                if x in pq:
                    est.append([1, Participantes.objects.get(pa_actividad=x, pa_usuario=request.user).pa_num_cupo])
                elif x in eq:
                    est.append([2, Espera.objects.get(es_actividad=x, es_usuario=request.user).es_num_cupo])
                else:
                    est.append([0])
            actividades_semana.append([serializers.serialize('json', acthoy), est])
            confirmados_semana.append(Actividad.objects.filter(ac_instructor=perfil, ac_fecha__range=(
                ini_sem + timedelta(days=i), ini_sem + timedelta(days=i, hours=23))).aggregate(
                sum_cupos=Coalesce(Sum('ac_cupos_reservados'), 0)))
            reservas_semana.append(Actividad.objects.filter(ac_instructor=perfil, ac_fecha__range=(
                ini_sem + timedelta(days=i), ini_sem + timedelta(days=i, hours=23))).aggregate(
                sum_cupos=Coalesce(Sum('ac_cap_max'), 0)))
            enespera_semana.append(Actividad.objects.filter(ac_instructor=perfil, ac_fecha__range=(
                ini_sem + timedelta(days=i), ini_sem + timedelta(days=i, hours=23))).aggregate(
                sum_cupos=Coalesce(Sum('ac_cupos_en_espera'), 0)))
            cuposenespera_semana.append(Actividad.objects.filter(ac_instructor=perfil, ac_fecha__range=(
                ini_sem + timedelta(days=i), ini_sem + timedelta(days=i, hours=23))).aggregate(
                sum_cupos=Coalesce(Sum('ac_cap_max_espera'), 0)))
        data1 = [ini_sem.day, ini_sem.month, ini_sem.year]
        data2 = [fin_sem.day, fin_sem.month, fin_sem.year]
        data3 = sem
        data4 = (json.dumps({'a_s': actividades_semana}))
        data5 = (json.dumps({'c_s': confirmados_semana}))
        data6 = (json.dumps({'r_s': reservas_semana}))
        data7 = (json.dumps({'s_s': enespera_semana}))
        data8 = (json.dumps({'e_s': cuposenespera_semana}))
        return HttpResponse(json.dumps([data1, data2, data3, data4, data5, data6, data7, data8, entrenadores]),
                            content_type='application/json')


def reservarajax(request, pk):
    vs = manejarSesion(request, request.user.profile.u_alias, False)
    p = int(request.GET['idactividad'])
    actividad = Actividad.objects.get(id=p)
    ids = Relacion.objects.values_list('r_user', flat=True).filter(r_marca=actividad.ac_marca, r_estado='A')
    if actividad.ac_instructor:
        perfiles = UserProfile.objects.filter(u_user__pk__in=set(ids)).exclude(
            pk=actividad.ac_instructor.pk).order_by('u_user__first_name', 'u_user__last_name', 'u_user__id')
    else:
        perfiles = UserProfile.objects.filter(u_user__pk__in=set(ids)).order_by('u_user__first_name', 'u_user__last_name', 'u_user__id')
    aPa = []
    try:
        for perfil in perfiles:
            pa = PerfilAtleta(perfil.u_alias)
            try:
                vicsafe = VicSafe(pa.atletaId, vs.marcaEnUsoId, vs)
                planIdParaReservar = vicsafe.puedeReservarActividad(actividad.id, vs)
            except Exception as ex:
                continue
            aPa.append(pa.armarJsonAtletaFast(actividad.ac_marca.m_alias, actividad.id, planIdParaReservar))
    except Exception as ex:
        pass

    ra = PerfilActividad(actividad.id).resumenActividadJson()

    ra['actividadFecha'] = fechaCortaPlus(ra['actividadFecha'])
    ra['actividadHoraInicio'] = ra['actividadHoraInicio'].strftime('%H:%M %P')

    return HttpResponse(json.dumps([aPa, ra]), content_type='application/json')


@login_required(login_url='/requerirLogon')
def cancelarajax(request, pk):
    user = request.user

    # Recibo los parametros de entrada
    atletaId = int(request.GET['usuario'])
    actividadId = int(request.GET['actividad'])

    vs = manejarSesion(request, user.profile.u_alias, False)
    marcaId = Actividad.objects.get(id=actividadId).ac_marca.id

    # Creo el objeto VicSafe
    vicsafe = VicSafe(atletaId, marcaId, vs)

    pa = PerfilActividad(actividadId)

    try:
        with transaction.atomic():
            if pa.atletaReservado(atletaId):
                strReturn = vicsafe.registrar_cancelar_reserva(actividadId)
                if strReturn == 'ok':
                    if vs.tipoSesion == vs.ATLETA:
                        log.info('cancelo actividad id #' + str(actividadId) + ' :' + request.user.username)
                    else:
                        log.info('cancelo actividad id #' + str(actividadId) + ' al atletaId# ' + str(vicsafe.atletaId) + ' :' + request.user.username)
                    mensaje = " ha cancelado la reserva."
                    if pa.actividadEspera > 0:
                        esperas = pa.actividadEsperas()
                        for atletaElegido in esperas:
                            if atletaElegido['participantePuesto'] == 1:
                                atletaElegidoId = atletaElegido['participanteUserId']
                                vicsafeAtletaElegido = VicSafe(atletaElegidoId, marcaId, vs)
                                vicsafeAtletaElegido.promover_desde_lista_espera(actividadId)
                                if strReturn == 'ok':
                                    mensaje = mensaje  # dejo el mensaje que traia
                                    mn = ManejoNotificaciones()
                                    mf = ManejoFechas()

                                    # Notificacion al atleta
                                    texto = {}
                                    texto['actividad'] = pa.actividadNombre
                                    texto['fechaHora'] = mf.fechaCorta(pa.actividadFecha) + ' ' + mf.horaCivil(
                                        pa.actividadHoraInicio)
                                    texto['instructor'] = pa.actividadNombreInstructor
                                    texto['mensaje'] = 'Has sido reservado'
                                    mn.marca_informa_atleta(User.objects.get(id=atletaElegidoId), pa.actividadMarca,
                                                            texto, 'RL')

                                else:
                                    mensaje = strReturn
                else:
                    mensaje = strReturn
            elif pa.atletaEnListaEspera(atletaId):
                strReturn = vicsafe.registrar_cancelar_lista_espera(actividadId)
                if strReturn == 'ok':
                    mensaje = " ha salido de la lista de espera."
                else:
                    mensaje = strReturn
            else:
                mensaje = 'no se encuentra en reserva ni en lista de espera'
    except:
        mensaje = 'Found Error. Executed Rollback'
        messages.error(request, mensaje)
        return HttpResponse(json.dumps([vicsafe.userAlias, mensaje , -1]), content_type='application/json')

    return HttpResponse(json.dumps([vicsafe.userAlias, mensaje]), content_type='application/json')


@login_required(login_url='/requerirLogon')
def reservandoajax(request, pk):
    user = request.user

    # Recibo los parametros de entrada
    atletaId = int(request.GET['usuario'])
    actividadId = int(request.GET['actividad'])
    if 'cupo' in request.GET:
        cupo = int(request.GET['cupo'])
    else:
        cupo = 0

    vs = manejarSesion(request, user.profile.u_alias, False)
    marcaId = Actividad.objects.get(id=actividadId).ac_marca.id

    # Creo el objeto vicsafe
    vicsafe = VicSafe(atletaId, marcaId, vs)

    pa = PerfilActividad(actividadId)

    mensaje = ''
    strRetorno = ''

    try:
        with transaction.atomic():
            if pa.actividadReservados == pa.actividadCapacidadMaxima:
                if pa.actividadCapacidadEspera > 0:
                    strRetorno = vicsafe.registrar_lista_espera(actividadId)
                    if strRetorno == 'ok':
                        mensaje = " paso a lista de espera"
                    else:
                        mensaje = strRetorno
                else:
                    mensaje = " No existe lista de espera."
            else:
                strRetorno = vicsafe.registrar_reserva(actividadId, cupo)
                if strRetorno == 'ok':
                    if pa.actividadEsSerie:
                        oActividad = Actividad.objects.get(id=actividadId)
                        actualizaBaseEnSerie(oActividad)
                        oActividad.ac_serieId_originaria=oActividad.ac_actividadBaseSerieId
                        oActividad.ac_actividadBaseSerieId = actividadId
                        oActividad.ac_OpcionSerie = 'No'
                        oActividad.ac_repetirComo = ''
                        oActividad.ac_despd = 'No'
                        oActividad.ac_do = 1
                        oActividad.ac_enf = 'No'
                        oActividad.ac_fdesp = oActividad.ac_fecha
                        oActividad.save()

                    mensaje = " ha sido reservado"
                    if vs.tipoSesion == vs.ATLETA:
                        log.info('reservo actividad id #' + str(actividadId) + ' :' + request.user.username)
                    else:
                        log.info('reservo actividad id #' + str(actividadId) + ' al atletaId# ' + str(
                            vicsafe.atletaId) + ' :' + request.user.username)

                else:
                    mensaje = strRetorno

            if strRetorno == 'ok' and vs.tipoSesion == vs.MARCA:
                mn = ManejoNotificaciones()
                mf = ManejoFechas()
                texto = {}
                texto['actividad'] = pa.actividadNombre
                texto['fechaHora'] = mf.fechaCorta(pa.actividadFecha) + ' ' + mf.horaCivil(pa.actividadHoraInicio)
                texto['instructor'] = pa.actividadNombreInstructor
                texto['mensaje'] = mensaje
                mn.marca_informa_atleta(user, vs.marcaEnUso, texto, 'RR')
    except:
        mensaje = 'Found Error. Executed Rollback'
        messages.error(request, mensaje)
        return HttpResponse(json.dumps([vicsafe.userAlias, mensaje , -1]), content_type='application/json')
    return HttpResponse(json.dumps([vicsafe.userAlias, mensaje + '.', 1]), content_type='application/json')


@login_required(login_url='/requerirLogon')
def cuporeservandoajax(request, pk):
    u = int(request.GET['usuario'])
    a = int(request.GET['actividad'])
    c = int(request.GET['costo'])
    usuario = User.objects.get(pk=u)
    actividad = Actividad.objects.get(pk=a)
    saldo = Saldo.objects.get(s_user=usuario, s_marca=actividad.ac_marca)
    usuarioperfil = UserProfile.objects.get(u_user=usuario)
    ocupados = list(Participantes.objects.values_list('pa_num_cupo', flat=True).filter(pa_actividad=actividad))
    cupo = actividad.ac_cap_max
    return HttpResponse(json.dumps(
        [usuarioperfil.u_user.first_name + " " + usuarioperfil.u_user.last_name, usuarioperfil.u_alias, ocupados,
         cupo]), content_type='application/json')


@login_required(login_url='/requerirLogon')
def comprarajax(request, pk):
    marca = Marca.objects.get(m_alias=pk)
    actividadId = request.GET['actividadId']
    if actividadId != u'':
        pa = PerfilActividad(actividadId)
    else:
        pa = None
    perfil = UserProfile.objects.get(u_user=int(request.GET['usuario']))
    usuario = perfil.u_alias
    if pa:
        if pa.actividadProductosPermitidos:
            productos = Producto.objects.filter(id__in=(pa.actividadProductosPermitidos), p_marca=marca, p_activo=True).exclude(p_tipo=3)
        else:
            productos = Producto.objects.filter(p_marca=marca, p_activo=True).exclude(p_tipo=3)
    else:
        productos = Producto.objects.filter(p_marca=marca, p_activo=True).exclude(p_nombre='Referenciado')
    planes = serializers.serialize('json', productos)
    dueno = Dueno.objects.filter(d_user=request.user, d_marca=marca).exists()
    nombre = perfil.u_user.first_name + " " + perfil.u_user.last_name
    correo = perfil.u_user.email
    return HttpResponse(json.dumps([planes, usuario, dueno, nombre, correo]), content_type='application/json')


@login_required(login_url='/requerirLogon')
def comprar2ajax(request, pk):
    marca = Marca.objects.get(m_alias=pk)
    usuario = User.objects.get(pk=int(request.GET['usuario']))
    usuario = User.objects.get(pk=int(request.GET['planes']))
    planes = serializers.serialize('json', Producto.objects.filter(p_marca=marca).exclude(p_tipo=3))
    return HttpResponse(json.dumps([planes]), content_type='application/json')


@login_required(login_url='/requerirLogon')
def cuentasajax(request, pk):
    marca = Marca.objects.get(pk=pk)
    cuentas = serializers.serialize('json', Cuenta.objects.filter(c_marca=marca, c_status=1))
    return HttpResponse(json.dumps([cuentas]), content_type='application/json')


@login_required(login_url='/requerirLogon')
def pagoajax(request):
    try:
        with transaction.atomic():
            user = User.objects.get(username=request.user)
            vs = manejarSesion(request, user.profile.u_alias, False)
            marcaId = Marca.objects.get(pk=int(request.GET['marca'])).id
            atletaId = User.objects.get(pk=int(request.GET['pagador'])).id

            # Creo el objeto vicsafe
            vicsafe = VicSafe(atletaId, marcaId, vs)

            # Obtengo las variables (In) de entrada
            planParametrosJson = {}
            planParametrosJson['tipoIn'] = int(request.GET['tipo'])
            planParametrosJson['pagadorIn'] = User.objects.get(pk=int(request.GET['pagador']))
            planParametrosJson['productoIn'] = Producto.objects.get(pk=int(request.GET['plan']))
            planParametrosJson['montoIn'] = float(request.GET['monto'])/100
            planParametrosJson['precioIn'] = float(request.GET['precio'])
            planParametrosJson['dtoGeneralIn'] = float(request.GET['dtoGeneral'])
            planParametrosJson['dtoParticularIn'] = float(request.GET['dtoParticular'])
            fechaIn = request.GET['fecha']
            planParametrosJson['fechaIn'] = fechaIn[-4:] + '-' + fechaIn[3:-5] + '-' + fechaIn[:2]
            planParametrosJson['referenciaIn'] = request.GET['referencia']
            if planParametrosJson['referenciaIn'] == '':
                planParametrosJson['referenciaIn'] = '0'
            planParametrosJson['cuentaIn'] = request.GET['cuenta']

            if planParametrosJson['referenciaIn']=='0' and int(planParametrosJson['tipoIn'])<5:
                mensaje = 'Compra no pudo ser realizada - Falta la referencia.'
                planOutId = 0
                data = {
                    'mensaje': mensaje,
                    'planId': planOutId,
                }

                return JsonResponse(data)

            # Llamo al metodo de vicsafe para que gestione el pago del plan
            strRetorno = vicsafe.registrar_compra_plan(planParametrosJson)
            if strRetorno['mensaje'] == 'ok':
                mensaje = 'Compra de plan realizada con exito'
                planOutId = strRetorno['planOutId']
                plan = Planes.objects.get(id=planOutId)

                # Notificacion al atleta
                mn = ManejoNotificaciones()
                texto = {}
                texto['plan'] = plan.p_nombre
                texto['mensaje'] = 'Se ha registrado plan '
                mn.marca_informa_atleta(User.objects.get(id=atletaId), plan.p_marca, texto, 'RP')

                # Enviar Correo al Atleta
            else:
                mensaje = 'Compra no pudo ser realizada.' + strRetorno['mensaje']
                planOutId = 0

            data = {
                'mensaje': mensaje,
                'planId': planOutId,
            }

            return JsonResponse(data)
    except:
        mensaje = 'Found Error. Executed Rollback'
        planOutId = 0
        data = {
            'mensaje': mensaje,
            'planId': planOutId,
        }
        messages.error(request,mensaje)
        return JsonResponse(data)


@login_required(login_url='/requerirLogon')
def pagoPorCobrarAjax(request):
    TRANSFERENCIA = 0
    DEPOSITO = 1
    POS = 2
    VPOS = 3
    CHEQUE = 4
    EFECTIVO = 5
    POR_COBRAR = 6
    BECA = 7

    hoy = datetime.today()

    planIn = request.GET['plan']
    tipoIn = int(request.GET['tipo'])
    referenciaIn = request.GET['referencia']
    fechaIn = request.GET['fecha']
    fechaIn = fechaIn[-4:] + '-' + fechaIn[3:-5] + '-' + fechaIn[:2]

    if tipoIn in [TRANSFERENCIA, DEPOSITO, POS]:
        cuentaIn = Cuenta.objects.get(c_numero_cuenta=request.GET['cuenta'])
    else:
        referenciaIn = None
        cuentaIn = None
    statusIn = tipoIn in [VPOS, CHEQUE, POR_COBRAR]

    pagoOut = Pago.objects.get(p_plan_id=planIn)
    pagoOut.p_fecha_registro = hoy
    pagoOut.p_fecha_transaccion = fechaIn
    pagoOut.p_medio = tipoIn
    pagoOut.p_referencia = referenciaIn
    pagoOut.p_status = statusIn
    pagoOut.p_porcobrar = False
    if (cuentaIn is not None):
        pagoOut.p_cuenta_id = cuentaIn.pk
    else:
        pagoOut.p_cuenta_id = cuentaIn
    pass
    try:
        pagoOut.save()
        mensaje = "Pago realizado con exito"
    except Exception as e:
        mensaje = "Error:" + str(e)
        print(mensaje)

    data = {
        'mensaje': mensaje,
        'planId': planIn,
    }
    return JsonResponse(data)


def getplanajax(request):
    plan = Producto.objects.get(pk=int(request.GET['plan']))
    today = datetime.today()
    if plan.p_tipo == 3:
        vence = datetime(3000, today.month, today.day).strftime('%d/%m/%Y')
    else:
        vence = (datetime.today() + timedelta(days=plan.p_duracion_meses * 30)).strftime('%d/%m/%Y')
    d0 = today
    d1 = datetime.strptime(vence, '%d/%m/%Y')
    delta = d1 - d0
    descuentoIn = float(request.GET['descuento'])
    precioPlan = float(plan.p_precio)
    precioConDescuento = 0
    descuentoGeneral = 0
    descuentoParticular = 0
    if plan.p_descuento > 0:
        descuentoGeneral = float(plan.p_descuento) / 100 * precioPlan
        precioConDescuento = precioPlan - descuentoGeneral
    else:
        precioConDescuento = precioPlan
    if descuentoIn > 0:
        descuentoParticular = descuentoIn / 100 * precioConDescuento
        precioConDescuento -= descuentoParticular
    precioCredito = 0
    if plan.p_creditos > 0:
        precioCredito = plan.p_precio / plan.p_creditos
    else:
        precioCredito = 0
    return HttpResponse(json.dumps(
        [plan.p_nombre, plan.p_creditos, plan.p_precio, plan.p_moneda, precioCredito, vence,
         descuentoGeneral, descuentoParticular, precioConDescuento, plan.p_tipo]), content_type='application/json')


def getPlanPendientePorCobrarAjax(request):
    plan = Planes.objects.get(pk=int(request.GET['planId']))
    pago = Pago.objects.get(p_plan=plan)
    producto = Producto.objects.filter(p_nombre=plan.p_nombre)[0]
    vence = plan.p_fecha_caducidad.strftime('%d/%m/%Y')
    precioproducto = float(producto.p_precio)
    precioConDescuento = pago.p_monto
    descuentoGeneral = pago.p_dtoGeneral
    descuentoParticular = pago.p_dtoParticular
    try:
        return HttpResponse(json.dumps(
            [producto.p_nombre, producto.p_creditos, producto.p_precio, producto.p_moneda,
             producto.p_precio / producto.p_creditos, vence,
             descuentoGeneral, descuentoParticular, precioConDescuento]), content_type='application/json')
    except Exception as e:
        pass


@login_required(login_url='/requerirLogon')
def clasecancelarajax(request, pk):
    u = int(request.GET['usuario'])
    a = int(request.GET['actividad'])
    c = int(request.GET['costo'])
    usuario = User.objects.get(pk=u)
    actividad = Actividad.objects.get(pk=a)
    marcas = Dueno.objects.filter(d_user=request.user)
    try:
        r = Participantes.objects.get(pa_usuario=usuario, pa_actividad=actividad)
        if (actividad.ac_cupos_en_espera > 0):
            primero = Espera.objects.filter(es_actividad=actividad)[0]
            new = Participantes.objects.create(pa_usuario=primero.es_usuario, pa_actividad=actividad,
                                               pa_num_cupo=r.pa_num_cupo)
            primero.delete()
            actividad.ac_cupos_en_espera += -1
        else:
            actividad.ac_cupos_reservados += -1
        mensaje = " ha cancelado su reserva."
    except:
        r = Espera.objects.get(es_usuario=usuario, es_actividad=actividad)
        actividad.ac_cupos_en_espera += -1
        mensaje = " ha sido eliminado de la lista de espera."

    r.delete()
    saldo = Saldo.objects.get(s_user=usuario, s_marca=actividad.ac_marca)
    usuarioperfil = UserProfile.objects.get(u_user=usuario)
    saldo.s_saldo += c
    saldo.s_bloqueado += -c
    saldo.save()
    actividad.save()
    plan = Planes.objects.filter(p_usuario=u, p_marca=actividad.ac_marca, p_fecha_caducidad__gte=datetime.today())[0]
    plan.p_creditos_usados += -1
    plan.p_historico = False
    plan.save()
    return HttpResponse(json.dumps([usuarioperfil.u_alias, mensaje]), content_type='application/json')


def validarsalonajax(request):
    marca = Marca.objects.get(pk=request.GET['marca'])

    salones = Salon.objects.filter(s_marca=marca)

    entrenadores = UserProfile.objects.filter()

    return HttpResponse(
        json.dumps([serializers.serialize('json', salones), serializers.serialize('json', entrenadores)]),
        content_type='application/json')


def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)


@login_required(login_url='/requerirLogon')
def obtenerclaseajax(request):
    ac = Actividad.objects.get(pk=int(request.GET['actividad']))
    marca = ac.ac_marca
    actividad = serializers.serialize('json', [ac])
    entre = Relacion.objects.filter(r_marca=marca, r_estado="A", r_entrenador=True).values_list('r_user__pk', flat=True)
    entrenadores = UserProfile.objects.filter(u_user__pk__in=entre)
    nombres = []
    for e in entrenadores:
        nombres.append(e.u_user.get_full_name())
    return HttpResponse(json.dumps([actividad, serializers.serialize('json', entrenadores), nombres]),
                        content_type='application/json')


@login_required(login_url='/requerirLogon')
def obtenerserieajax(request):
    se = Serie.objects.filter(s_num_ser=int(request.GET['serie']))[0]
    ac = Actividad.objects.get(pk=int(request.GET['actividad']))
    actividad = serializers.serialize('json', [ac])
    serie = serializers.serialize('json', [se])
    return HttpResponse(json.dumps([actividad, serie]), content_type='application/json')


@login_required(login_url='/requerirLogon')
def marcarasistenciaajax(request):
    try:
        participante = Participantes.objects.get(pk=int(request.GET['asis']))
        participante.pa_asistencia = not participante.pa_asistencia
        participante.save()
        if (participante.pa_asistencia):
            r = 1
        else:
            r = 2
    except:
        r = -1
    # return redirect(request.META['HTTP_REFERER'])
    return HttpResponse(json.dumps([r, participante.pa_actividad.pk]), content_type='application/json')


# Este es el registro de usuario desde la marca
@login_required(login_url='/requerirLogon')
def registrarusuarioajax(request):
    nombre = (request.GET['nombre'])
    apellido = (request.GET['apellido'])
    correo = (request.GET['correo'])
    alias = (request.GET['alias'])
    if 'comoInstructor' in request.GET:
        comoInstructor = request.GET['comoInstructor']
        if comoInstructor == 'false':
            comoInstructor = False
        if comoInstructor == 'true':
            comoInstructor = True
    else:
        comoInstructor = False
    vs = manejarSesion(request, request.user.profile.u_alias, False)
    marca = vs.marcaEnUso
    codigoRetorno = '0'
    try:
        with transaction.atomic():
            if User.objects.filter(username__iexact=correo).exists():
                usuario = User.objects.filter(username__iexact=correo)
                if Relacion.objects.filter(r_user=usuario, r_marca=marca, r_estado='A').exists() == False:
                    codigoRetorno = '2'
                    Relacion.objects.create(r_user=usuario.get(), r_marca=marca, r_estado='A', r_entrenador=comoInstructor)
                    messages.success(request, 'Usuario ha sido incorporado a su marca exitosamente')
                    pm = PerfilMarca(marca.m_alias)
                    pa = PerfilAtleta(usuario.get().profile.u_alias)
                    if pm.marcaPermiteReferenciados:
                        setearPlanReferenciado(pa, pm)
            else:
                contra = User.objects.make_random_password()
                usuario = User.objects.create(username=correo, password=contra, first_name=nombre, last_name=apellido,
                                              email=correo,
                                              is_active=True)
                t = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(25))
                token = Token.objects.create(u_user=usuario, u_token=t)
                tel = request.GET['tel']
                perfil = UserProfile.objects.create(u_user=usuario, u_alias=alias, u_secondname='', u_secondlastname='',
                                                    u_telefono=tel, u_direccion='', u_displinafav1=None,
                                                    u_displinafav2_id=None, u_displinafav3_id=None, u_registrado=False)
                Relacion.objects.create(r_user=usuario, r_marca=marca, r_estado='A', r_entrenador=comoInstructor)
                if not Saldo.objects.filter(s_user=usuario, s_marca=marca):
                    Saldo.objects.create(s_user=usuario, s_marca=marca)
                pm = PerfilMarca(marca.m_alias)
                pa = PerfilAtleta(usuario.profile.u_alias)
                if pm.marcaPermiteReferenciados:
                    setearPlanReferenciado(pa, pm)
                codigoRetorno = '1'

                from django.template import loader
                message = 'Correo de Bienvenida'
                data = {
                    'token': token,
                    'enlace': "http://" + request.META['HTTP_HOST'] + "/token/" + token.u_token,
                    'nombres': nombre + ' ' + apellido,
                    'alias': alias,
                    'marcaNombre': marca.m_nombre,
                    'marcaDescripcion': marca.m_descripcion,
                    'activo': False,
                }
                html_message = loader.render_to_string(
                    'correoBienvenida.html',
                    data,
                )
                send_mail('Bienvenido a ' + marca.m_nombre + '. Completa tu registro para la auto-gestion.', message,
                          'register@victorius.io', [correo], fail_silently=True,
                          html_message=html_message)
                messages.success(request, 'Usuario creado. Favor completar el registro a traves del correo enviado')
    except Exception as ex:
        messages.error(request,'Found Error. Executed Rollback')

    return HttpResponse(json.dumps([codigoRetorno]), content_type='application/json')

@transaction.atomic
def agregarUsuarioExistenteAjax(request):
    marcaAlias = request.session['marca']
    userAlias = request.GET['alias']
    if request.GET['comoInstructor'] == 'true':
        comoInstructor = True
    else:
        comoInstructor = False
    marca = Marca.objects.get(m_alias=marcaAlias)
    profile = UserProfile.objects.get(u_alias=userAlias)
    usuario = profile.u_user

    mensaje = ''
    mn = ManejoNotificaciones()
    try:
        if Relacion.objects.filter(r_user=usuario, r_marca=marca, r_estado='P'):
            mensaje = 'Existe una invitación pendiente'
        else:
            Relacion.objects.create(r_user=usuario, r_marca=marca, r_estado='A', r_entrenador=comoInstructor)
            if not Saldo.objects.filter(s_user=usuario, s_marca=marca):
                Saldo.objects.create(s_user=usuario, s_marca=marca)
            mensaje = 'Invitación de afiliación registrada'
            mn.marca_invita_atleta_afiliacion(usuario, marca)
        messages.success(request, mensaje)
    except:
        mensaje = 'Hubo un error al realizar la operacion.'
        messages.error(request, mensaje)

    data = {'mensaje': mensaje}
    return JsonResponse(data)


@login_required(login_url='/requerirLogon')
@user_is_legal
def planes(request, pk):
    vs = manejarSesion(request, pk, False)
    if vs.tipoSesion == vs.MARCA:
        pm = PerfilMarca(vs.marcaEnUsoAlias)
    else:
        pm = PerfilMarca(pk)
    marcas_publicas = Marca.objects.filter(m_public=True).order_by('m_nombre')
    try:
        marcas = Dueno.objects.filter(d_user=request.user)
    except:
        marcas = 0
    actual = Marca.objects.get(m_alias=pk)
    perfil = UserProfile.objects.get(u_user=request.user)
    referenciado = Producto.objects.filter(p_marca=actual, p_tipo=3)
    productos = Producto.objects.filter(p_marca=actual).order_by('-p_creacion', '-p_activo', 'p_creditos').exclude(
        p_tipo=3)
    productosTodos = list(productos) + list(referenciado)
    if PerfilMarca(pk).marcaEsPublica or siguiendo_esta_marca(pm.marcaId, vs.userId):
        return render(request, 'planes.html',
                      {
                          'perfil': perfil,
                          'esmarca': True,
                          'marcas_publicas': marcas_publicas,
                          'marcas': marcas,
                          'marca_actual': actual,
                          'vs': vs,
                          'perfilMarca': pm,
                          'pk': pk,
                          'productos': productosTodos,
                      })
    else:
        return redirect(request.META['PATH_INFO'].replace('planes', ''))


@login_required(login_url='/requerirLogon')
@user_is_legal
def salas(request, pk):
    vs = manejarSesion(request, pk, False)
    pm = PerfilMarca(pk)

    return render(request, 'salas.html',
                  {
                      'perfilMarca': pm,
                      'vs': vs,
                  })


@login_required(login_url='/requerirLogon')
@user_is_legal
def cuentas(request, pk):
    vs = manejarSesion(request, pk, False)
    pm = PerfilMarca(pk)

    return render(request, 'cuentas.html',
                  {
                      'perfilMarca': pm,
                      'vs': vs,
                  })


@login_required(login_url='/requerirLogon')
@user_is_legal
def habilitarplanajax(request):
    pk = request.GET['pk']
    marcas = Dueno.objects.filter(d_user=request.user)
    valor = int(request.GET['valor'])
    try:
        plan = Producto.objects.get(pk=int(request.GET['id']))
        if plan.p_tipo == 3:
            pm = PerfilMarca(plan.p_marca.m_alias)
            if valor == 0:
                quiereTipoReferenciado = False
            if valor == 1:
                quiereTipoReferenciado = True
            revisarSeteoTipoReferenciado(pm, quiereTipoReferenciado)
        if valor == 0:
            plan.p_activo = False
            plan.save()
            resultado = 2
            messages.success(request, 'El plan ha sido inhabilitado')
        if valor == 1:
            plan.p_activo = True
            plan.save()
            resultado = 1
            messages.success(request, 'El plan ha sido deshabilitado')
    except:
        resultado = -1
        messages.error(request, 'Operacion de habilitar/deshabilitar produjo un error.')
    actual = Marca.objects.get(m_alias=pk)
    productos = Producto.objects.filter(p_marca=actual, p_activo=True)
    inactivos = Producto.objects.filter(p_marca=actual, p_activo=False)
    return HttpResponse(json.dumps(resultado), content_type='application/json')


@login_required(login_url='/requerirLogon')
def editarplanajax(request):
    pk = (request.GET['pk'])
    marcas = Dueno.objects.filter(d_user=request.user)
    creditos = 0
    creditos_mensual = 0
    if request.GET['tipoPlan'] == 'Por Creditos':
        tipoPlan = 0
        creditos = int(request.GET['credito'])
    elif request.GET['tipoPlan'] == 'Mensual Ilimitado':
        tipoPlan = 1
    elif request.GET['tipoPlan'] == 'Mensual Limitado':
        tipoPlan = 2
        creditos_mensual = int(request.GET['credito'])
    actual = Marca.objects.get(m_alias=pk)
    if int(request.GET['id']) == -1:
        try:
            plan = Producto.objects.create(p_nombre=request.GET['nombre'], p_precio=int(request.GET['precio']),
                                           p_precio2=int(request.GET['precio2']), p_precio3=int(request.GET['precio3']),
                                           p_creditos=creditos,
                                           p_creditos_mensual=creditos_mensual,
                                           p_duracion_meses=int(request.GET['vencimiento']),
                                           p_creacion=datetime.today(), p_descuento=int(request.GET['descuento']),
                                           p_tipo=tipoPlan,
                                           p_disciplinas=[],
                                           p_marca=actual)
            plan.save()
            resultado = 4
            messages.success(request, 'Plan creado exitosamente.')
        except:
            messages.error(request, 'Plan no fue creado. Se produjo un error.')
    else:
        if (int(request.GET['descuento']) <= 100):
            try:
                plan = Producto.objects.get(pk=int(request.GET['id']))
                plan.p_nombre = request.GET['nombre']
                plan.p_creditos = int(request.GET['credito'])
                plan.p_precio = int(request.GET['precio'])
                plan.p_precio2 = int(request.GET['precio2'])
                plan.p_precio3 = int(request.GET['precio3'])
                plan.p_descuento = int(request.GET['descuento'])
                plan.p_duracion_meses = int(request.GET['vencimiento'])
                plan.p_tipo = tipoPlan
                plan.save()
                resultado = 3
                messages.success(request, 'Plan actualizado exitosamente.')
            except:
                resultado = -1
                messages.error(request, 'Plan no fue actualizado. Se produjo un error.')
        else:
            resultado = -1
    productos = Producto.objects.filter(p_marca=actual, p_activo=True)
    inactivos = Producto.objects.filter(p_marca=actual, p_activo=False)
    return HttpResponse(json.dumps(resultado), content_type='application/json')


@login_required(login_url='/requerirLogon')
@user_is_legal
def perfilatleta(request, pk, pka):
    vs = manejarSesion(request, pka, pk == pka)
    try:
        modoInstructor = 'clase' in request.META['HTTP_REFERER']
        if not modoInstructor:
            try:
                modoInstructor = 'instructor' in request.path
            except:
                modoInstructor = False
    except:
        try:
            modoInstructor = 'instructor' in request.path
        except:
            modoInstructor = False

    perfilBasico = PerfilBasicoAtleta(pka, vs)
    if perfilBasico.atletaEsInstructor:
        perfil = PerfilInstructor(pka, vs)
        descripcionInstructor = perfil.profifeInstructor()
    else:
        perfil = PerfilAtleta(pka, vs)
        descripcionInstructor = ''
    marca_actual = None
    if vs.tipoSesion == vs.MARCA:
        marca_actual = vs.marcaEnUso

    estaEnMarcaActual=False
    for marca in perfil.atletaMarcas():
        if marca == marca_actual:
            estaEnMarcaActual = True
            break
    esInstructorEnMarcaActual=perfil.esInstructorEnMarca()

    puedeVer={}

    puedeVerActividadesAtleta=False
    puedeVerPlanesAtleta = False
    puedeVerActividadesInstructor=False
    puedeVerRemuneracionesInstructor=False
    puedeVerPerfilInstructor=False
    puedeVerPerfilAtleta=False

    if vs.tipoSesion == vs.ATLETA:
        if perfil.atletaAlias == vs.userAlias:
            puedeVerPerfilInstructor = True
            puedeVerActividadesInstructor = True
            puedeVerRemuneracionesInstructor = True
            puedeVerPerfilAtleta = True
            puedeVerActividadesAtleta = True
            puedeVerPlanesAtleta = True
        else:
            puedeVerPerfilInstructor = True
            puedeVerActividadesInstructor = True
            puedeVerRemuneracionesInstructor = False
    else:
        if estaEnMarcaActual:
           puedeVerPerfilAtleta = True
           puedeVerPlanesAtleta = True
           puedeVerActividadesAtleta = True
           if perfil.atletaEsInstructor and esInstructorEnMarcaActual:
              puedeVerPerfilInstructor = True
              puedeVerActividadesInstructor = True
              puedeVerRemuneracionesInstructor = True

    # if vs.tipoSesion==vs.ATLETA:
    #    if vs.userAlias != perfil.atletaAlias and modoInstructor:
    #        puedeVerPerfilInstructor=True
    #        puedeVerActividadesInstructor = True
    # else:
    #     if modoInstructor:
    #         puedeVerPerfilInstructor=True
    #         puedeVerActividadesInstructor = True
    #     else:
    #         puedeVerPerfilAtleta = True
    #         puedeVerPerfilInstructor = True
    #         puedeVerActividadesInstructor = True
    #         puedeVerRemuneracionesInstructor = True
    #         puedeVerPlanesAtleta = True
    #         puedeVerActividadesAtleta = True

    puedeVer['ActividadesAtleta']=puedeVerActividadesAtleta
    puedeVer['PlanesAtleta']=puedeVerPlanesAtleta
    puedeVer['ActividadesInstructor']=puedeVerActividadesInstructor
    puedeVer['RemuneracionesInstructor'] = puedeVerRemuneracionesInstructor
    puedeVer['PerfilAtleta'] = puedeVerPerfilAtleta
    puedeVer['PerfilInstructor'] = puedeVerPerfilInstructor

    if request.method == 'POST' and request.FILES['myAvatar']:


        # myAvatar = request.FILES['myAvatar']
        # fs = FileSystemStorage()
        # tempFileName='avatars/'+vs.userAlias+'.jpg'
        # if fs.exists(tempFileName):
        #     fs.delete(tempFileName)
        # filename = fs.save(tempFileName, myAvatar)
        # uploaded_file_url = fs.url(filename)



        myAvatar = request.FILES['myAvatar']
        im = Image.open(myAvatar)

        y=300
        x=300

        while True:
            size = (x, y)
            im.thumbnail(size)
            if im.height <=150 or im.width <=150:
                break
            y-=5
            x-=5
        from django.conf import settings
        mediaDir=settings.MEDIA_ROOT
        if settings.AMBIENTE=='DESARROLLO':
            imBase = Image.open(mediaDir+'/avatars/base.jpg')
            outputFile = mediaDir+'/avatars/' + vs.userAlias + '.png'
        else:
            imBase = Image.open(mediaDir+'/avatars/base.jpg')
            outputFile = mediaDir+'/avatars/' + vs.userAlias + '.png'

        image_copy = imBase.copy()

        y=(imBase.height-im.height)/2
        x=(imBase.width-im.width)/2

        position=(0,0)

        image_copy.paste(im, position)

        image_copy.save(outputFile)
        uploaded_file_url = outputFile

        # myAvatar = request.FILES['myAvatar']
        # fs = FileSystemStorage()
        # tempFileName = 'avatars/temp'
        # if fs.exists(tempFileName):
        #     fs.delete(tempFileName)
        # filename = fs.save(tempFileName, myAvatar)
        # outputFile = 'media/avatars/' + vs.userAlias + '.jpg'
        # im = Image.open('media/'+filename)
        # im.thumbnail(size)
        # im.save(outputFile)
        # uploaded_file_url = outputFile

        return render(request, 'perfil.html', {
            'perfil': perfil,
            'vs': vs,
            'hoy': datetime.now(),
            'dummy': randint(0, 10000),
            'marca_actual': marca_actual,
            'relaciones': Relacion.objects.filter(r_user=request.user, r_estado='A'),
            'modoInstructor': modoInstructor,
            'descripcionInstructor': descripcionInstructor,
            'puedeVer': puedeVer,
            'uploaded_file_url': uploaded_file_url
        })

    return render(request, 'perfil.html', {
        'perfil': perfil,
        'vs': vs,
        'hoy': datetime.now(),
        'dummy': randint(0, 10000),
        'marca_actual': marca_actual,
        'relaciones': Relacion.objects.filter(r_user=request.user, r_estado='A'),
        'modoInstructor': modoInstructor,
        'descripcionInstructor': descripcionInstructor,
        'puedeVer': puedeVer,
    })

def perfilActividadesAtleta(request, pk=None, pka=None):
    actividadesPorPagina=25

    marcaAlias=request.GET.get('marcaAlias','')

    if pka==None and pk is not None:
        pka=pk

    vs = manejarSesion(request, pka, pk == pka)

    pa = PerfilAtleta(pka, vs)

    if vs.tipoSesion==vs.MARCA:
        marcaAlias=vs.marcaEnUsoAlias

    actividadesVigentes=pa.actividadesVigentesEntreFechas(marcaAlias=marcaAlias,fitroEnSoloLasMias=True)
    actividadesNoVigentes=pa.actividadesNoVigentesEntreFechas(marcaAlias=marcaAlias,fitroEnSoloLasMias=True)

    #Pagineo para tabIzquierdo
    paginaIZQ = request.GET.get('paginaIZQ', 1)
    paginatorIZQ = Paginator(actividadesVigentes, actividadesPorPagina)
    try:
        actividadesIZQ = paginatorIZQ.page(paginaIZQ)
    except PageNotAnInteger:
        actividadesIZQ = paginatorIZQ.page(1)
    except EmptyPage:
        actividadesIZQ = paginatorIZQ.page(paginatorIZQ.num_pages)

        # Pagineo para tabDerecho
    paginaDER = request.GET.get('paginaDER', 1)
    paginatorDER = Paginator(actividadesNoVigentes, actividadesPorPagina)
    try:
        actividadesDER = paginatorDER.page(paginaDER)
    except PageNotAnInteger:
        actividadesDER = paginatorDER.page(1)
    except EmptyPage:
        actividadesDER = paginatorDER.page(paginatorDER.num_pages)

    numPagesIZQ=actividadesIZQ.paginator.num_pages
    numPagesDER=actividadesDER.paginator.num_pages

    if actividadesIZQ.paginator.count==0:
        numPagesIZQ=0

    if actividadesDER.paginator.count==0:
        numPagesDER=0

    if 'reset' in request.GET:
        reset = request.GET['reset']
    else:
        reset = False

    if paginaIZQ > 1 or paginaDER > 1 or reset:
        return render(request, 'calendario-atleta-table.html', {
            'vs': vs,
            'dummy': randint(0, 10000),
            'perfilAtleta': pa,
            'actividadesIZQ': actividadesIZQ,
            'actividadesDER': actividadesDER,
            'numPagesIZQ':numPagesIZQ,
            'numPagesDER': numPagesDER,
            'urlPagineo':'pagineo_perfil_actividades_atleta',
        })
    else:
        return render(request, 'perfil-actividades-atleta.html', {
            'vs': vs,
            'dummy': randint(0, 10000),
            'perfilAtleta': pa,
            'actividadesIZQ': actividadesIZQ,
            'actividadesDER': actividadesDER,
            'numPagesIZQ': numPagesIZQ,
            'numPagesDER': numPagesDER,
            'urlPagineo': 'pagineo_perfil_actividades_atleta',
        })

def carruselMisActividades(request, pk=None):
    vs = manejarSesion(request, pk, False)
    if vs==None:
       return redirect('logout')
    pa = PerfilAtleta(vs.userAlias, vs)

    actividades = pa.actividadesTodasEntreFechas(request)
    return render(request, 'calendario-atleta-carrusel-misActividades.html', {
        'vs': vs,
        'dummy': randint(0, 10000),
        'perfilAtleta': pa,
        'misActividadesTodas': actividades[1],
    })

def perfilActividadesAtletaPerfil(request, pk=None, pka=None):
    import operator
    actividadesPorPagina=25

    marcaAlias=request.GET.get('marcaAlias','')
    if marcaAlias == 'None':
        marcaAlias=None
    if not pka:
        pka=request.GET.get('pka',None)
    if pka==None and pk is not None:
        pka=pk

    vs = manejarSesion(request, pka, pk == pka)

    #----------------------------------------->

    perfilBasico = PerfilBasicoAtleta(pka, vs)
    if perfilBasico.atletaEsInstructor:
        perfil = PerfilInstructor(pka, vs)
        descripcionInstructor = perfil.profifeInstructor()
        actividadesPorImpartir = perfil.actividadesPorImpartir(marcaAlias)
        actividadesYaImpartidas = perfil.actividadesYaImpartidas(marcaAlias)
        diasUltimaImpartida = perfil.diasUltimaImpartida()
    else:
        perfil = PerfilAtleta(pka, vs)
        descripcionInstructor = ''
        actividadesPorImpartir = []
        actividadesYaImpartidas = []
        diasUltimaImpartida=-1

    #----------------------------------------->

    pa = PerfilAtleta(pka, vs)

    if vs.tipoSesion==vs.MARCA:
        marcaAlias=vs.marcaEnUsoAlias

    actividadesVigentes=pa.actividadesVigentesEntreFechas(marcaAlias=marcaAlias,fitroEnSoloLasMias=True)
    actividadesPorImpartir_=[]
    for actividad in actividadesPorImpartir:
        actividadesPorImpartir_.append(PerfilActividad(actividad['actividadId']))
    actividadesVigentes.extend(actividadesPorImpartir_)
    actividadesVigentes=sorted(actividadesVigentes,key=lambda k: k.actividadHoraInicio)
    actividadesVigentes=sorted(actividadesVigentes,key=lambda k: k.actividadFecha)

    actividadesNoVigentes=pa.actividadesNoVigentesEntreFechas(marcaAlias=marcaAlias,fitroEnSoloLasMias=True)
    actividadesYaImpartidas_=[]
    for actividad in actividadesYaImpartidas:
        actividadesYaImpartidas_.append(PerfilActividad(actividad['actividadId']))
    actividadesNoVigentes.extend(actividadesYaImpartidas_)
    actividadesNoVigentes=sorted(actividadesNoVigentes,key=lambda k: k.actividadHoraInicio)
    actividadesNoVigentes=sorted(actividadesNoVigentes,key=lambda k: k.actividadFecha)

    #Pagineo para tabIzquierdolap
    paginaIZQ = request.GET.get('paginaIZQ', 1)
    paginatorIZQ = Paginator(actividadesVigentes, actividadesPorPagina)
    try:
        actividadesIZQ = paginatorIZQ.page(paginaIZQ)
    except PageNotAnInteger:
        actividadesIZQ = paginatorIZQ.page(1)
    except EmptyPage:
        actividadesIZQ = paginatorIZQ.page(paginatorIZQ.num_pages)

        # Pagineo para tabDerecho
    paginaDER = request.GET.get('paginaDER', 1)
    paginatorDER = Paginator(actividadesNoVigentes, actividadesPorPagina)
    try:
        actividadesDER = paginatorDER.page(paginaDER)
    except PageNotAnInteger:
        actividadesDER = paginatorDER.page(1)
    except EmptyPage:
        actividadesDER = paginatorDER.page(paginatorDER.num_pages)

    numPagesIZQ=actividadesIZQ.paginator.num_pages
    numPagesDER=actividadesDER.paginator.num_pages

    if actividadesIZQ.paginator.count==0:
        numPagesIZQ=0

    if actividadesDER.paginator.count==0:
        numPagesDER=0

    if 'reset' in request.GET:
        reset = request.GET['reset']
    else:
        reset = False

    if paginaIZQ > 1 or paginaDER > 1 or reset:
        return render(request, 'calendario-atleta-table.html', {
            'vs': vs,
            'dummy': randint(0, 10000),
            'perfilAtleta': pa,
            'actividadesIZQ': actividadesIZQ,
            'actividadesDER': actividadesDER,
            'numPagesIZQ':numPagesIZQ,
            'numPagesDER': numPagesDER,
            'urlPagineo':'pagineo_perfil_actividades_atleta_perfil',
        })
    else:
        return render(request, 'perfil-actividades-atleta-perfil.html', {
            'vs': vs,
            'dummy': randint(0, 10000),
            'perfilAtleta': pa,
            'actividadesIZQ': actividadesIZQ,
            'actividadesDER': actividadesDER,
            'numPagesIZQ': numPagesIZQ,
            'numPagesDER': numPagesDER,
            'urlPagineo': 'pagineo_perfil_actividades_atleta_perfil',
        })

def perfilActividadesMarca(request, pk=None):
    actividadesPorPagina=25
    vs = manejarSesion(request, pk, False)
    numPages=1
    try:
        pm = PerfilMarca(vs.marcaEnUsoAlias)
    except:
        try:
            pm = PerfilMarca(request.GET['pk'])
        except:
            return redirect('logout')
    actividades = pm.actividadesTodasEntreFechas(request)

    #Pagineo para tab Unico
    pagina = request.GET.get('pagina', 1)
    paginator = Paginator(actividades, actividadesPorPagina)

    if 'reset' in request.GET:
        reset=request.GET['reset']
    else:
        reset=False

    try:
        actividadesTodas = paginator.page(pagina)
    except PageNotAnInteger:
        actividadesTodas = paginator.page(1)
    except EmptyPage:
        actividadesTodas = paginator.page(paginator.num_pages)
    numPages=actividadesTodas.paginator.num_pages
    if actividadesTodas.paginator.count==0:
        numPages=0

    if pagina>1 or reset:
        return render(request, 'calendario-marca-table.html', {
            'vs':vs,
            'perfilMarca':pm,
            'iniciales': pm.marcaIniciales,
            'status': TipoEstatus().tipoTodasPlus,
            'disciplinas': Disciplina.objects.filter(),
            'numPages': numPages,
            'actividadesTodas': actividadesTodas,
            'urlPagineo': 'perfil-actividades-marca',
        })
    else:
        return render(request, 'perfil-actividades-marca.html', {
            'vs':vs,
            'perfilMarca':pm,
            'iniciales': pm.marcaIniciales,
            'status': TipoEstatus().tipoTodasPlus,
            'disciplinas': Disciplina.objects.filter(),
            'numPages': numPages,
            'actividadesTodas': actividadesTodas,
            'urlPagineo': 'perfil-actividades-marca',
        })

def perfilActividadesMarcaPorAtleta(request, pk=None):
    actividadesPorPagina=25
    vs = manejarSesion(request, pk, False)

    pka=vs.userAlias
    pa = PerfilAtleta(pka, vs)

    numPages=1

    marcaAlias=request.GET['pk']

    try:
        pm = PerfilMarca(marcaAlias)
    except:
        return redirect('logout')

    actividades = pm.actividadesTodasEntreFechas(request)

    #Pagineo para tab Unico
    pagina = request.GET.get('pagina', 1)
    paginator = Paginator(actividades, actividadesPorPagina)

    if 'reset' in request.GET:
        reset=request.GET['reset']
    else:
        reset=False

    try:
        actividadesTodas = paginator.page(pagina)
    except PageNotAnInteger:
        actividadesTodas = paginator.page(1)
    except EmptyPage:
        actividadesTodas = paginator.page(paginator.num_pages)
    numPages=actividadesTodas.paginator.num_pages
    if actividadesTodas.paginator.count==0:
        numPages=0

    if pagina>1 or reset:
        return render(request, 'calendario-atleta-table.html', {
            'vs':vs,
            'perfilMarca':pm,
            'perfilAtleta': pa,
            'iniciales': pm.marcaIniciales,
            'status': TipoEstatus().tipoTodasPlus,
            'disciplinas': Disciplina.objects.filter(),
            'numPages': numPages,
            'numPagesIZQ': numPages,
            'numPagesDER': numPages,
            'actividadesIZQ': actividadesTodas,
            'urlPagineo': 'perfil-actividades-marca-por-atleta',
        })
    else:
        return render(request, 'perfil-actividades-marca-por-atleta.html', {
            'vs':vs,
            'perfilMarca':pm,
            'perfilAtleta': pa,
            'iniciales': pm.marcaIniciales,
            'status': TipoEstatus().tipoTodasPlus,
            'disciplinas': Disciplina.objects.filter(),
            'numPages': numPages,
            'numPagesIZQ': numPages,
            'numPagesDER': numPages,
            'actividadesIZQ': actividadesTodas,
            'urlPagineo': 'perfil-actividades-marca-por-atleta',
        })


@login_required(login_url='/requerirLogon')
@user_is_legal
def perfilPlanesAtleta(request, pk, pka):
    vs = manejarSesion(request, pka, pk == pka)
    try:
        modoInstructor = 'clase' in request.META['HTTP_REFERER']
    except:
        modoInstructor = False
    try:
        marcaAlias = request.GET['marcaAlias']
    except:
        marcaAlias = None
    perfilBasico = PerfilBasicoAtleta(pka, vs)
    if perfilBasico.atletaEsInstructor:
        perfil = PerfilInstructor(pka, vs)
        descripcionInstructor = perfil.profifeInstructor()
    else:
        perfil = PerfilAtleta(pka, vs)
        descripcionInstructor = ''
    marca_actual = None
    if vs.tipoSesion == vs.MARCA:
        marca_actual = vs.marcaEnUso
    planesActivosPagos = perfil.planesActivosPagos(marcaAlias)
    planesHistoricos = perfil.planesHistoricos(marcaAlias)
    return render(request, 'perfil-planes-atleta.html', {
        'perfil': perfil,
        'vs': vs,
        'hoy': datetime.now(),
        'dummy': randint(0, 10000),
        'marca_actual': marca_actual,
        'relaciones': Relacion.objects.filter(r_user=request.user, r_estado='A'),
        'modoInstructor': modoInstructor,
        'descripcionInstructor': descripcionInstructor,
        'planesActivosPagos': planesActivosPagos,
        'planesHistoricos': planesHistoricos,
    })

@login_required(login_url='/requerirLogon')
@user_is_legal
def perfilPlanesAtletaPerfil(request, pk=None, pka=None):

    if not pka:
        pka=request.GET.get('pka',None)
    if pka==None and pk is not None:
        pka=pk

    vs = manejarSesion(request, pka, pk == pka)

    try:
        modoInstructor = 'clase' in request.META['HTTP_REFERER']
    except:
        modoInstructor = False
    try:
        marcaAlias = request.GET['marcaAlias']
    except:
        marcaAlias = None
    perfilBasico = PerfilBasicoAtleta(pka, vs)
    if perfilBasico.atletaEsInstructor:
        perfil = PerfilInstructor(pka, vs)
        descripcionInstructor = perfil.profifeInstructor()
    else:
        perfil = PerfilAtleta(pka, vs)
        descripcionInstructor = ''
    marca_actual = None
    if vs.tipoSesion == vs.MARCA:
        marca_actual = vs.marcaEnUso
    planesActivosPagos = perfil.planesActivosPagos(marcaAlias)
    planesHistoricos = perfil.planesHistoricos(marcaAlias)

    return render(request, 'perfil-planes-atleta-perfil.html', {
        'perfil': perfil,
        'vs': vs,
        'hoy': datetime.now(),
        'dummy': randint(0, 10000),
        'marca_actual': marca_actual,
        'relaciones': Relacion.objects.filter(r_user=request.user, r_estado='A'),
        'modoInstructor': modoInstructor,
        'descripcionInstructor': descripcionInstructor,
        'planesActivosPagos': planesActivosPagos,
        'planesHistoricos': planesHistoricos,
    })

def table_body_planes_atleta(request):
    pk = request.GET['pk']
    pka = pk
    vs = manejarSesion(request, pka, pk == pka)
    try:
        modoInstructor = 'clase' in request.META['HTTP_REFERER']
    except:
        modoInstructor = False
    try:
        marcaAlias = request.GET['marcaAlias']
    except:
        marcaAlias = None
    perfilBasico = PerfilBasicoAtleta(pka, vs)
    if perfilBasico.atletaEsInstructor:
        perfil = PerfilInstructor(pka, vs)
        descripcionInstructor = perfil.profifeInstructor()
    else:
        perfil = PerfilAtleta(pka, vs)
        descripcionInstructor = ''
    marca_actual = None
    if vs.tipoSesion == vs.MARCA:
        marca_actual = vs.marcaEnUso
    planesActivosPagos = perfil.planesActivosPagos(marcaAlias)
    planesHistoricos = perfil.planesHistoricos(marcaAlias)
    return render(request, 'table_body_planes_atleta.html', {
        'perfil': perfil,
        'vs': vs,
        'hoy': datetime.now(),
        'dummy': randint(0, 10000),
        'marca_actual': marca_actual,
        'relaciones': Relacion.objects.filter(r_user=request.user, r_estado='A'),
        'modoInstructor': modoInstructor,
        'descripcionInstructor': descripcionInstructor,
        'planesActivosPagos': planesActivosPagos,
        'planesHistoricos': planesHistoricos,
    })


def perfilAtletaMarca(request, pk, pka):
    vs = manejarSesion(request, pka, pk == pka)
    try:
        modoInstructor = 'clase' in request.META['HTTP_REFERER']
    except:
        modoInstructor = False
    perfilBasico = PerfilBasicoAtleta(pka, vs)
    if perfilBasico.atletaEsInstructor:
        perfil = PerfilInstructor(pka, vs)
        descripcionInstructor = perfil.profifeInstructor()
    else:
        perfil = PerfilAtleta(pka, vs)
        descripcionInstructor = ''
    marca_actual = None
    if vs.tipoSesion == vs.MARCA:
        marca_actual = vs.marcaEnUso
    return render(request, 'perfil-atleta-marca.html', {
        'perfil': perfil,
        'vs': vs,
        'hoy': datetime.now(),
        'dummy': randint(0, 10000),
        'marca_actual': marca_actual,
        'relaciones': Relacion.objects.filter(r_user=request.user, r_estado='A'),
        'modoInstructor': modoInstructor,
        'descripcionInstructor': descripcionInstructor,
    })


@login_required(login_url='/requerirLogon')
@user_is_legal
def perfilAfiliacionesAtleta(request, pk, pka):
    vs = manejarSesion(request, pka, pk == pka)
    try:
        modoInstructor = 'clase' in request.META['HTTP_REFERER']
    except:
        modoInstructor = False
    perfilBasico = PerfilBasicoAtleta(pka, vs)
    if perfilBasico.atletaEsInstructor:
        perfil = PerfilInstructor(pka, vs)
        descripcionInstructor = perfil.profifeInstructor()
    else:
        perfil = PerfilAtleta(pka, vs)
        descripcionInstructor = ''
    marca_actual = None
    if vs.tipoSesion == vs.MARCA:
        marca_actual = vs.marcaEnUso

    marcasPublicas = Marca.objects.filter().values('m_alias').order_by('m_nombre')
    aPM = []
    i = -1
    idx = -1
    for marcaPublica in marcasPublicas:
        pm = PerfilMarca(marcaPublica['m_alias'])
        i += 1
        if pm.marcaDuenoAlias == pk:
            aPM.append(pm)
            idx = i
            break
    # Ahora lleno la lista excluyendo la marca propietaria si es que existe
    i = -1
    for marcaPublica in marcasPublicas:
        i += 1
        if i != idx:
            pm = PerfilMarca(marcaPublica['m_alias'])
            aPM.append(pm)

    return render(request, 'perfil-afiliaciones-atleta.html', {
        'perfil': perfil,
        'vs': vs,
        'hoy': datetime.now(),
        'dummy': randint(0, 10000),
        'marca_actual': marca_actual,
        'relaciones': Relacion.objects.filter(r_user=request.user, r_estado='A'),
        'modoInstructor': modoInstructor,
        'descripcionInstructor': descripcionInstructor,
        'centros': aPM,
    })


def perfilActividadesInstructor(request, pk=None, pka=None):
    actividadesPorPagina=25
    esElMismo=False
    marcaAlias=request.GET.get('marcaAlias',None)
    if pka==None and pk is not None:
        pka=pk

    vs = manejarSesion(request, pka, False)

    if vs.tipoSesion==vs.MARCA:
        marcaAlias=vs.marcaEnUsoAlias


    perfilBasico = PerfilBasicoAtleta(pka, vs)
    if perfilBasico.atletaEsInstructor:
        perfil = PerfilInstructor(pka, vs)
        descripcionInstructor = perfil.profifeInstructor()
    else:
        perfil = PerfilAtleta(pka, vs)
        descripcionInstructor = ''

    esElMismo=perfil.atletaAlias==vs.userAlias

    actividadesPorImpartir=perfil.actividadesPorImpartir(marcaAlias)
    actividadesYaImpartidas=perfil.actividadesYaImpartidas(marcaAlias)

    #Pagineo para tabIzquierdo
    paginaIZQ = request.GET.get('paginaIZQ', 1)
    paginatorIZQ = Paginator(actividadesPorImpartir, actividadesPorPagina)
    try:
        actividadesIZQ = paginatorIZQ.page(paginaIZQ)
    except PageNotAnInteger:
        actividadesIZQ = paginatorIZQ.page(1)
    except EmptyPage:
        actividadesIZQ = paginatorIZQ.page(paginatorIZQ.num_pages)

    # Pagineo para tabDerecho
    paginaDER = request.GET.get('paginaDER', 1)
    paginatorDER = Paginator(actividadesYaImpartidas, actividadesPorPagina)
    try:
        actividadesDER = paginatorDER.page(paginaDER)
    except PageNotAnInteger:
        actividadesDER = paginatorDER.page(1)
    except EmptyPage:
        actividadesDER = paginatorDER.page(paginatorDER.num_pages)

    numPagesIZQ=actividadesIZQ.paginator.num_pages
    numPagesDER=actividadesDER.paginator.num_pages

    if actividadesIZQ.paginator.count==0:
        numPagesIZQ=0

    if actividadesDER.paginator.count==0:
        numPagesDER=0

    if 'reset' in request.GET:
        reset = request.GET['reset']
    else:
        reset = False

    diasUltimaImpartida=perfil.diasUltimaImpartida()

    if paginaIZQ > 1 or paginaDER > 1 or reset:
        return render(request, 'calendario-instructor-table.html', {
            'vs': vs,
            'dummy': randint(0, 10000),
            'perfilAtleta': perfil,
            'actividadesIZQ': actividadesIZQ,
            'actividadesDER': actividadesDER,
            'numPagesIZQ':numPagesIZQ,
            'numPagesDER': numPagesDER,
            'urlPagineo': 'pagineo_perfil_actividades_instructor',
            'diasUltimaImpartida':diasUltimaImpartida,
            'esElMismo':esElMismo,
        })
    else:
        return render(request, 'perfil-actividades-instructor.html', {
            'vs': vs,
            'dummy': randint(0, 10000),
            'perfilAtleta': perfil,
            'actividadesIZQ': actividadesIZQ,
            'actividadesDER': actividadesDER,
            'numPagesIZQ': numPagesIZQ,
            'numPagesDER': numPagesDER,
            'urlPagineo': 'pagineo_perfil_actividades_instructor',
            'diasUltimaImpartida': diasUltimaImpartida,
            'esElMismo': esElMismo,
        })

def perfilActividadesInstructorPerfil(request, pk=None, pka=None):

    if not pka:
        pka=request.GET.get('pka',None)
    if pka==None and pk is not None:
        pka=pk

    vs = manejarSesion(request, pka, pk == pka)


    actividadesPorPagina=25
    esElMismo=False
    marcaAlias=request.GET.get('marcaAlias',None)
    if pka==None and pk is not None:
        pka=pk

    vs = manejarSesion(request, pka, False)

    if vs.tipoSesion==vs.MARCA:
        marcaAlias=vs.marcaEnUsoAlias

    perfilBasico = PerfilBasicoAtleta(pka, vs)
    if perfilBasico.atletaEsInstructor:
        perfil = PerfilInstructor(pka, vs)
        descripcionInstructor = perfil.profifeInstructor()
        actividadesPorImpartir = perfil.actividadesPorImpartir(marcaAlias)
        actividadesYaImpartidas = perfil.actividadesYaImpartidas(marcaAlias)
        diasUltimaImpartida = perfil.diasUltimaImpartida()
    else:
        perfil = PerfilAtleta(pka, vs)
        descripcionInstructor = ''
        actividadesPorImpartir = []
        actividadesYaImpartidas = []
        diasUltimaImpartida=-1

    esElMismo=perfil.atletaAlias==vs.userAlias

    #Pagineo para tabIzquierdo
    paginaIZQ = request.GET.get('paginaIZQ', 1)
    paginatorIZQ = Paginator(actividadesPorImpartir, actividadesPorPagina)
    try:
        actividadesIZQ = paginatorIZQ.page(paginaIZQ)
    except PageNotAnInteger:
        actividadesIZQ = paginatorIZQ.page(1)
    except EmptyPage:
        actividadesIZQ = paginatorIZQ.page(paginatorIZQ.num_pages)

    # Pagineo para tabDerecho
    paginaDER = request.GET.get('paginaDER', 1)
    paginatorDER = Paginator(actividadesYaImpartidas, actividadesPorPagina)
    try:
        actividadesDER = paginatorDER.page(paginaDER)
    except PageNotAnInteger:
        actividadesDER = paginatorDER.page(1)
    except EmptyPage:
        actividadesDER = paginatorDER.page(paginatorDER.num_pages)

    numPagesIZQ=actividadesIZQ.paginator.num_pages
    numPagesDER=actividadesDER.paginator.num_pages

    if actividadesIZQ.paginator.count==0:
        numPagesIZQ=0

    if actividadesDER.paginator.count==0:
        numPagesDER=0

    if 'reset' in request.GET:
        reset = request.GET['reset']
    else:
        reset = False

    if paginaIZQ > 1 or paginaDER > 1 or reset:
        return render(request, 'calendario-instructor-table.html', {
            'vs': vs,
            'dummy': randint(0, 10000),
            'perfilAtleta': perfil,
            'actividadesIZQ': actividadesIZQ,
            'actividadesDER': actividadesDER,
            'numPagesIZQ':numPagesIZQ,
            'numPagesDER': numPagesDER,
            'urlPagineo': 'pagineo_perfil_actividades_instructor_perfil',
            'diasUltimaImpartida':diasUltimaImpartida,
            'esElMismo':esElMismo,
        })
    else:
        return render(request, 'perfil-actividades-instructor-perfil.html', {
            'vs': vs,
            'dummy': randint(0, 10000),
            'perfilAtleta': perfil,
            'actividadesIZQ': actividadesIZQ,
            'actividadesDER': actividadesDER,
            'numPagesIZQ': numPagesIZQ,
            'numPagesDER': numPagesDER,
            'urlPagineo': 'pagineo_perfil_actividades_instructor_perfil',
            'diasUltimaImpartida': diasUltimaImpartida,
            'esElMismo': esElMismo,
        })

def table_body_perfil_instructor(request):
    marcaAlias = request.GET['marcaAlias']

    if 'pk2' in request.GET:
        pk = request.GET['pk2']
        vs = manejarSesion(request, pk, False)
        patl = PerfilAtleta(pk, vs)
    else:
        vs = manejarSesion(request, request.user.profile.u_alias, False)
        pk = request.session['vs']['userAlias']
        patl = PerfilAtleta(pk, vs)

    if marcaAlias:
        actividades = Actividad.objects.filter(
            ac_marca__m_alias=marcaAlias,
            ac_instructor__u_alias=pk,
            ac_fecha__lte=datetime.today(),
            ac_fecha__gte=datetime.today() - timedelta(days=6)).order_by('-ac_fecha').values('id')
    else:
        actividades = Actividad.objects.filter(
            ac_instructor__u_alias=pk,
            ac_fecha__lte=datetime.today(),
            ac_fecha__gte=datetime.today() - timedelta(days=6)).order_by('-ac_fecha').values('id')
    aAct = []
    for actividad in actividades:
        actJson = PerfilActividad(actividad['id']).resumenActividadJson()
        aAct.append(actJson)
    actividadesYaImpartidas = aAct

    if marcaAlias:
        actividades = Actividad.objects.filter(
            ac_marca__m_alias=marcaAlias,
            ac_instructor__u_alias=pk,
            ac_fecha__gt=datetime.today()).order_by('ac_fecha')[0:20].values('id')
    else:
        actividades = Actividad.objects.filter(
            ac_instructor__u_alias=pk,
            ac_fecha__gt=datetime.today()).order_by('ac_fecha')[0:20].values('id')
    aAct = []
    for actividad in actividades:
        actJson = PerfilActividad(actividad['id']).resumenActividadJson()
        aAct.append(actJson)
    actividadesPorImpartir=aAct

    return render(request, 'table_body_perfil_instructor.html', {
        'actividadesYaImpartidas': actividadesYaImpartidas,
        'actividadesPorImpartir': actividadesPorImpartir,
        'perfilAtleta': patl,
        'vs': vs,
    })


@login_required(login_url='/requerirLogon')
@user_is_legal
def perfilRemuneracionesInstructorPerfil(request, pk=None, pka=None):
    if not pka:
        pka=request.GET.get('pka',None)
    if pka==None and pk is not None:
        pka=pk

    vs = manejarSesion(request, pka, pk == pka)
    try:
        modoInstructor = 'clase' in request.META['HTTP_REFERER']
    except:
        modoInstructor = False
    perfilBasico = PerfilBasicoAtleta(pka, vs)
    if perfilBasico.atletaEsInstructor:
        perfil = PerfilInstructor(pka, vs)
        descripcionInstructor = perfil.profifeInstructor()
    else:
        perfil = PerfilAtleta(pka, vs)
        descripcionInstructor = ''
    marca_actual = None
    if vs.tipoSesion == vs.MARCA:
        marca_actual = vs.marcaEnUso
    return render(request, 'perfil-remuneraciones-instructor-perfil.html', {
        'perfil': perfil,
        'vs': vs,
        'hoy': datetime.now(),
        'dummy': randint(0, 10000),
        'marca_actual': marca_actual,
        'relaciones': Relacion.objects.filter(r_user=request.user, r_estado='A'),
        'modoInstructor': modoInstructor,
        'ingresosPorPercibir': perfil.ingresosPorPercibir(),
        'ingresosYaPercibidos':perfil.ingresosYaPercibidos(),
        'descripcionInstructor': descripcionInstructor,
    })

@login_required(login_url='/requerirLogon')
@user_is_legal
def perfilRemuneracionesInstructor(request, pk, pka):
    vs = manejarSesion(request, pka, pk == pka)
    try:
        modoInstructor = 'clase' in request.META['HTTP_REFERER']
    except:
        modoInstructor = False
    perfilBasico = PerfilBasicoAtleta(pka, vs)
    if perfilBasico.atletaEsInstructor:
        perfil = PerfilInstructor(pka, vs)
        descripcionInstructor = perfil.profifeInstructor()
    else:
        perfil = PerfilAtleta(pka, vs)
        descripcionInstructor = ''
    marca_actual = None
    if vs.tipoSesion == vs.MARCA:
        marca_actual = vs.marcaEnUso
    log.info('Saliendo de perfilRemuneracionesInstructor')
    return render(request, 'perfil-remuneraciones-instructor.html', {
        'perfil': perfil,
        'vs': vs,
        'hoy': datetime.now(),
        'dummy': randint(0, 10000),
        'marca_actual': marca_actual,
        'relaciones': Relacion.objects.filter(r_user=request.user, r_estado='A'),
        'modoInstructor': modoInstructor,
        'ingresosPorPercibir': perfil.ingresosPorPercibir(),
        'ingresosYaPercibidos':perfil.ingresosYaPercibidos(),
        'descripcionInstructor': descripcionInstructor,
    })

@login_required(login_url='/requerirLogon')
@user_is_legal
def table_body_remuneraciones_instructor(request):
    pka=request.GET['pk']
    marcaAlias=None
    if 'marcaAlias' in request.GET:
        marcaAlias=request.GET['marcaAlias']
    vs = manejarSesion(request, pka, False)
    perfilBasico = PerfilBasicoAtleta(pka, vs)
    if perfilBasico.atletaEsInstructor:
        perfil = PerfilInstructor(pka, vs)
        descripcionInstructor = perfil.profifeInstructor()
    else:
        perfil = PerfilAtleta(pka, vs)
        descripcionInstructor = ''
    return render(request, 'table_body_remuneraciones_instructor.html', {
        'perfil': perfil,
        'vs': vs,
        'hoy': datetime.now(),
        'dummy': randint(0, 10000),
        'relaciones': Relacion.objects.filter(r_user=request.user, r_estado='A'),
        'modoInstructor': True,
        'ingresosPorPercibir': perfil.ingresosPorPercibir(marcaAlias),
        'ingresosYaPercibidos': perfil.ingresosYaPercibidos(marcaAlias),
        'descripcionInstructor': descripcionInstructor,
    })

def centeredCrop(img, new_height, new_width):
    width = np.size(img, 1)
    height = np.size(img, 0)

    left = np.ceil((width - new_width) / 2.)
    top = np.ceil((height - new_height) / 2.)
    right = np.floor((width + new_width) / 2.)
    bottom = np.floor((height + new_height) / 2.)
    # cImg = img[top:bottom, left:right]
    cImg = img.crop((left, top, right, bottom))
    return cImg


@login_required(login_url='/requerirLogon')
def planesatleta(request, pk, pka):
    vs = manejarSesion(request, pk, False)
    usuario_a_consultar = UserProfile.objects.get(u_alias=pka)
    esmarca = usuario_a_consultar.u_marca
    try:
        marca_actual = Marca.objects.get(m_alias=pk)
    except:
        marca_actual = None
        usuario_a_consultar = UserProfile.objects.get(u_user=request.user)
    marcas = Dueno.objects.filter(d_user=request.user)
    planes = Planes.objects.filter(p_usuario=usuario_a_consultar.u_user)
    pagos = []
    estados = []
    for p in planes:
        pag = Pago.objects.get(p_plan=p)
        pagos.append(pag)
        if pag.p_medio == 1:
            estados.append("Transferencia")
        elif pag.p_medio == 2:
            estados.append("Deposito")
        elif pag.p_medio == 3:
            estados.append("POS")
        elif pag.p_medio == 4:
            estados.append("VPOS")
        elif pag.p_medio == 5:
            estados.append("Cheque")
        elif pag.p_medio == 6:
            estados.append("Efectivo")
        else:
            estados.append("Por Cobrar")

    return render(request, 'planes-atleta.html', {
        'perfil': UserProfile.objects.get(u_user=request.user),
        'perfilusuario': usuario_a_consultar,
        'marca_actual': marca_actual,
        'vs': vs,
        'user': usuario_a_consultar.u_user,
        'relaciones': Relacion.objects.filter(r_user=request.user, r_estado='A'),
        'marcas': marcas,
        'esmarca': esmarca,
        'planes': zip(planes, pagos, estados),
    })


@login_required(login_url='/requerirLogon')
def historial(request, pk, id, pkb):
    vs = manejarSesion(request, pk, False)
    ide = int(id)
    marca_actual = Marca.objects.get(m_alias=pkb)
    marcas = Dueno.objects.filter(d_user=request.user)
    marcasids = marcas.values_list('d_marca', flat=True)
    actividades = Actividad.objects.filter(ac_marca__in=marcasids)
    user = User.objects.get(pk=pk)
    perfil = UserProfile.objects.get(u_user=pk)
    marca = Marca.objects.get(m_alias=pkb)
    if int(id) == 1:
        mostrar = Participantes.objects.filter(pa_usuario=user, pa_actividad__in=actividades,
                                               pa_actividad__ac_fecha__lte=datetime.today()).order_by(
            '-pa_actividad__ac_fecha')
    if int(id) == 2:
        mostrar = Espera.objects.filter(es_usuario=user, es_actividad__in=actividades)
    if int(id) == 3:
        mostrar = Actividad.objects.filter(ac_instructor=perfil, ac_marca__in=marcasids,
                                           ac_fecha__gt=datetime.today()).exclude(
            ac_estado__ea_estado__in=['Culminada', 'Activa']).order_by('ac_fecha')
    if int(id) == 4:
        mostrar = Actividad.objects.filter(ac_instructor=perfil, ac_marca__in=marcasids,
                                           ac_estado__ea_estado__in=['Culminada', 'Activa'],
                                           ac_fecha__lte=datetime.today()).order_by('ac_fecha')
    if int(id) > 4:
        mostrar = Participantes.objects.filter(pa_usuario=user, pa_actividad__ac_marca=marcas[int(id) - 5].d_marca,
                                               pa_actividad__ac_fecha__gt=datetime.today()).order_by(
            '-pa_actividad__ac_fecha')
        marca = marcas[int(id) - 5]
        pk = marca.id
    if int(id) in [1, 2, 5]:
        return render(request, 'historial-clases-atleta.html', {
            'perfil': UserProfile.objects.get(u_user=request.user),
            'perfilusuario': perfil,
            'marca_actual': marca_actual,
            'vs': vs,
            'user': user,
            'mostrar': mostrar,
            'marca': marca,
            'ide': ide,
            'esmarca': True,
            'marcas': marcas,
        })
    else:
        return render(request, 'clases-instruidas.html', {
            'perfil': UserProfile.objects.get(u_user=request.user),
            'perfilusuario': perfil,
            'marca_actual': marca_actual,
            'vs': vs,
            'user': user,
            'mostrar': mostrar,
            'marca': marca,
            'ide': ide,
            'esmarca': True,
            'marcas': marcas,
        })


@login_required(login_url='/requerirLogon')
def consumoplan(request, pk, pka):
    vs = manejarSesion(request, pk, False)
    id = pka
    marcas = Dueno.objects.filter(d_user=request.user)
    marcasids = marcas.values_list('d_marca', flat=True)
    actividades = Actividad.objects.filter(ac_marca__in=marcasids)
    marca = Marca.objects.get(m_alias=pk)
    plan = Planes.objects.get(pk=id)
    consumos = Participantes.objects.filter(pa_plan=plan)
    return render(request, 'consumoplan.html', {
        'usuario': plan.p_usuario,
        'perfil': UserProfile.objects.get(u_user=plan.p_usuario),
        'plan': plan,
        'marca_actual': marca,
        'vs': vs,
        'consumos': consumos,
        'marcas': marcas,
    })


@login_required(login_url='/requerirLogon')
@user_is_legal
def atletascentro(request, pk):
    vs = manejarSesion(request, pk, False)
    perfil = UserProfile.objects.get(u_user=request.user)
    try:
        entrenadores = request.GET['entrenadores']
    except:
        entrenadores = 'n'
    marcas = Dueno.objects.filter(d_user=request.user)
    marcasids = marcas.values_list('d_marca', flat=True)
    try:
        marca_actual = Marca.objects.get(m_alias=pk)
    except:
        marca_actual = Marca.objects.get(m_alias=vs.marcaEnUsoAlias)
    fecha = datetime.today()
    if fecha.day >= 1 and fecha.day <= 15:
        primero = fecha.replace(day=1)
        ultimo = fecha.replace(day=15)
    else:
        primero = fecha.replace(day=16)
        ultimo = fecha.replace(day=monthrange(fecha.year, fecha.month)[1])
    if entrenadores == 's':
        relacionconmarca = Relacion.objects.filter(r_marca=marca_actual, r_estado="A", r_entrenador=True)
    else:
        relacionconmarca = Relacion.objects.filter(r_marca=marca_actual, r_estado="A")
    relacion = relacionconmarca.values_list('r_user', flat=True)
    users = UserProfile.objects.filter(u_user__pk__in=relacion).order_by('u_user__first_name', 'u_user__last_name')
    urelacion = []
    for u in users:
        try:
            saldo = Saldo.objects.filter(s_user__pk=u.u_user_id, s_marca=marca_actual)[0]

            planes = Planes.objects.filter(p_usuario=u.u_user, p_historico=False, p_marca__m_alias=marca_actual.m_alias)
            plan = planes[0]

            varios = planes.count() > 1
        except:
            plan = 0
            varios = False
            saldo = None

        if entrenadores == 's':
            pagos = Actividad.objects.filter(ac_instructor=u, ac_estado__ea_estado='Culminada', ac_fecha__lte=ultimo,
                                             ac_fecha__gte=primero)
            total_hoy = pagos.aggregate(Sum('ac_precio'))

            clasesimpartidas = Actividad.objects.filter(ac_instructor=u, ac_marca__in=marcasids,
                                                        ac_estado__ea_estado__in=['Culminada', 'Activa'],
                                                        ac_fecha__lte=datetime.today()).count()
            clasesporimpartir = Actividad.objects.filter(ac_instructor=u, ac_marca__in=marcasids,
                                                         ac_fecha__gt=datetime.today()).exclude(
                ac_estado__ea_estado__in=['Culminada', 'Activa', 'Cancelada']).count()

            urelacion.append(
                [u, Relacion.objects.get(r_marca=marca_actual, r_user=u.u_user).r_entrenador, plan, total_hoy,
                 clasesimpartidas, clasesporimpartir, saldo])
        else:
            urelacion.append(
                [u, Relacion.objects.get(r_marca=marca_actual, r_user=u.u_user).r_entrenador, plan, varios, saldo])
    return render(request, 'clientes-detail.html', {
        'marcas': marcas,
        'valor': pk,
        'marca_actual': marca_actual,
        'vs': vs,
        'perfil': perfil,
        'esmarca': True,
        'users': urelacion,
        'relacionconmarca': relacionconmarca,
        'pk': pk,
        'instructores': entrenadores,
        'dummy': randint(0, 10000),
    })


def atletasentrenadores(request, pk):
    vs = manejarSesion(request, pk, False)
    marca_actual = Marca.objects.get(m_alias=pk)
    relacionconmarca = Relacion.objects.filter(r_marca=marca_actual, r_estado="A", r_entrenador=True)
    relacion = relacionconmarca.values_list('r_user', flat=True)
    users = UserProfile.objects.filter(u_user__pk__in=relacion)
    urelacion = []
    fecha = datetime.today()
    if fecha.day >= 1 and fecha.day <= 15:
        primero = fecha.replace(day=1)
        ultimo = fecha.replace(day=15)
    else:
        primero = fecha.replace(day=16)
        ultimo = fecha.replace(day=monthrange(fecha.year, fecha.month)[1])
    for u in users:
        pagos = Actividad.objects.filter(ac_instructor=u, ac_estado="Culminada", ac_fecha__lte=ultimo,
                                         ac_fecha__gte=primero)
        total_hoy = pagos.aggregate(Sum('ac_precio'))
        urelacion.append([u, Relacion.objects.get(r_marca=marca_actual, r_user=u.u_user).r_entrenador, total_hoy])

    return render(request, 'clientes-detail.html', {
        'marca_actual': marca_actual,
        'vs': vs,
        'users': urelacion,
        'esmarca': True,
        'relacionconmarca': relacionconmarca,
        'pk': pk,
        'entrenadores': 's',
    })


@login_required(login_url='/requerirLogon')
def estadoentrenadorajax(request, pk):
    estado = int(request.GET['estado'])
    marca_actual = Marca.objects.get(m_alias=pk)
    relacion = Relacion.objects.get(r_user=int(request.GET['usuario']), r_marca=marca_actual)
    perfil = UserProfile.objects.get(u_user=int(request.GET['usuario']))
    perfil.u_entrenador = True
    try:
        perfil.save()
        relacion.r_entrenador = estado == 2
        relacion.save()
        resultado = estado
        if estado == 2:
            messages.success(request, 'El usuario @' + perfil.u_alias + ' ha sido autorizado como entrenador')
        else:
            messages.success(request, 'El usuario @' + perfil.u_alias + ' ha sido desautorizado como entrenador')
    except:
        resultado = -1
        messages.error(request, 'La autorizacion/desautorizacion del usuario produjo un error')
    return HttpResponse(json.dumps(resultado), content_type='application/json')


@login_required(login_url='/requerirLogon')
@user_is_legal
def estadodecuenta(request, pk):
    vs = manejarSesion(request, pk, False)
    pm = PerfilMarca(pk)
    hoy = datetime.now()
    mes = hoy.month
    anno = hoy.year
    return render(request, 'edo-cuenta.html', {
        'pm': pm,
        'vs': vs,
        'mesCalendar': mes,
        'annoCalendar': anno,
        'tiposDeStatus': Pago.STATUS_CHOICES,
        'mediosDePago': Pago.MEDIO_CHOICES,
        'comenzando': True,
    })


def activarDesactivarCuentaAjax(request):
    cuentaId = request.GET['cuentaId']
    opcion = request.GET['opcion']
    cuenta = Cuenta.objects.get(id=cuentaId)
    if opcion == '0':
        cuenta.c_status = False
    else:
        cuenta.c_status = True
    try:
        cuenta.save()
        resultado = 1
    except:
        resultado = -1
    return HttpResponse(json.dumps(resultado), content_type='application/json')


def table_body_estado_cuenta(request):
    mes = int(request.GET['mes'])
    anno = int(request.GET['anno'])
    searchString = request.GET['searchString']
    idStatus = request.GET['idStatus']
    idMedio = request.GET['idMedio']
    idPlan = request.GET['idPlan']
    pk = request.GET['pk']
    vs = manejarSesion(request, pk, False)

    criteria = {}
    criteria['searchString'] = searchString
    criteria['idStatus'] = idStatus
    criteria['idMedio'] = idMedio
    criteria['idPlan'] = idPlan

    pm = PerfilMarca(pk)
    resultado = pm.marcaPagosMensuales(mes, anno, criteria)
    pagos = resultado[0]
    totales = resultado[1]

    mf = ManejoFechas()
    fechaLiteral = mf.mesLiteral(mes) + ' ' + str(anno)

    return render(request, 'table_body_estado_cuenta.html', {
        'mesCalendar': None,
        'annoCalendar': None,
        'pagos': pagos,
        'totales': totales,
        'fechaLiteral': fechaLiteral,
    })


@login_required(login_url='/requerirLogon')
def cambiarStatusPago(request):
    pagoId = int(request.GET['pago'])
    opcion = int(request.GET['opcion'])
    try:
        pago = Pago.objects.get(id=pagoId)
        pago.p_status = opcion
        if pago.p_status == 1:
            pago.p_fecha_Conciliacion = datetime.now()
        pago.save()
        resultado = 'ok'
    except:
        resultado = 'error'
    return HttpResponse(json.dumps(resultado), content_type='application/json')


@login_required(login_url='/requerirLogon')
def mostrarpagoajax(request):
    pk = int(request.GET['pago'])
    pago = Pago.objects.get(pk=pk)
    return HttpResponse(json.dumps([pago.p_pagador.pk, pago.p_producto.pk]), content_type='application/json')


@login_required(login_url='/requerirLogon')
def mostrarPagoPendientePorCobrarAjax(request):
    pk = int(request.GET['pagoId'])
    pago = Pago.objects.get(pk=pk)
    return HttpResponse(json.dumps([pago.p_pagador.pk, pago.p_plan.pk]), content_type='application/json')


@login_required(login_url='/requerirLogon')
def registromarca(request, pka=None, method='POST'):
    pk = request.user.profile.u_alias
    vs = manejarSesion(request, pk, False)
    perfil = UserProfile.objects.get(u_user=request.user)
    pa = PerfilAtleta(pk)
    if request.method == 'POST':
        post = request.POST
        if post.get('idEditando') == 'True':
            editando = True
        else:
            editando = False
        try:
            if editando:
                marca = Marca.objects.get(id=vs.marcaEnUsoId)
                pm = PerfilMarca(vs.marcaEnUsoAlias)
            else:
                marca = Marca()
            esReferenciado = False
            if 'idReferenciado' in request.POST:
                if request.POST['idReferenciado'] == u'on':
                    esReferenciado = True
            tipoDeCuenta = ''
            if 'idTipoDeCuenta' in request.POST:
                if request.POST['idTipoDeCuenta'] == '1':
                    tipoDeCuenta = 'N'
                else:
                    tipoDeCuenta = 'J'
            marca.m_displinafav1 = Disciplina.objects.get(id=post.get('idDisciplina1'))
            marca.m_displinafav2 = Disciplina.objects.get(id=post.get('idDisciplina2'))
            marca.m_displinafav3 = Disciplina.objects.get(id=post.get('idDisciplina3'))
            marca.m_tipoCuenta = tipoDeCuenta
            marca.m_permite_referenciados = esReferenciado
            marca.m_correo = post.get('idCorreo')
            marca.m_nombre = post.get('idMarcaNombre')
            marca.m_razon_social = post.get('idRazonSocial')
            marca.m_alias = post.get('idAlias')
            marca.m_iniciales = post.get('idIniciales')
            marca.m_iniciales = marca.m_iniciales.upper()
            if tipoDeCuenta == 'N':
                marca.m_doc_ident = post.get('idCedula')
            else:
                marca.m_doc_ident = post.get('idRif')
                marca.m_razon_social = post.get('idRazonSocial')
            marca.m_telefono1 = post.get('idTelefonoPrimario')
            marca.m_telefono2 = post.get('idTelefonoSecundario')
            marca.m_calle = post.get('idAvenidaCalle')
            marca.m_urbanizacion = post.get('idUrbanizacion')
            marca.m_edificioCasa = post.get('idEdificioCasa')
            if post.get('idCiudad') == '':
                marca.m_ciudad_id = None
                marca.m_municipio_id = None
                marca.m_pais_id = None
            else:
                marca.m_ciudad_id = post.get('idCiudad')
                marca.m_municipio_id = post.get('idMunicipio')
                marca.m_pais_id = post.get('idPais')

            if post.get('idPublicoPrivado') == u'on':
                marca.m_public = True
            else:
                marca.m_public = False

            marca.m_est_rrev = post.get('idTiempoReversible')
            marca.m_est_irrev = post.get('idTiempoIreversible')

            marca.m_redSocial_Facebook = post.get('idFacebook')
            marca.m_redSocial_Instagram = post.get('idInstagram')
            marca.m_redSocial_Twitter = post.get('idTwitter')

            marca.m_descripcion = post.get('idDescripcion')
            marca.m_planVictorius_id = 'Core'
            marca.m_boletin = True

            marca.save()

            marcaCreada = Marca.objects.get(m_alias=post.get('idAlias'))

            if not editando:

                dueno = Dueno()
                dueno.d_marca = marcaCreada
                dueno.d_user = request.user
                dueno.save()

                relacion = Relacion()
                relacion.r_user = request.user
                relacion.r_marca = marcaCreada
                relacion.r_estado = 'A'
                relacion.save()

                saldo = Saldo()
                saldo.s_user = request.user
                saldo.s_marca = marcaCreada
                saldo.s_bloqueado = 0
                saldo.s_saldo = 0
                saldo.save()

                perfil.u_marca = True
                perfil.save()

                if esReferenciado:
                    Producto.objects.create(p_nombre='Referenciado', p_marca_id=marcaCreada.id, p_duracion_meses=999,
                                            p_precio=0, p_descuento=0, p_creditos=0, p_tipo=3, p_disciplinas=[])
                    pm = PerfilMarca(marcaCreada.m_alias)
                    setearPlanReferenciado(pa, pm)
                messages.success(request, 'Marca ' + marcaCreada.m_alias + ' fue creada')

            else:

                revisarSeteoTipoReferenciado(pm, esReferenciado)
                messages.success(request, 'Marca ' + marcaCreada.m_alias + ' fue actualizada')


        except Exception as e:
            messages.error(request, 'Marca no fue creada. Error:' + e.message)
    else:
        return render(request, "registroMarca.html",
                      {'ciudad': Ciudad.objects.all(),
                       'municipio': Zona.objects.all(),
                       'usuario': request.user,
                       'pais': Pais.objects.all,
                       'disciplinas': Disciplina.objects.all(),
                       'planVictorius': PlanVictorius.objects.all,
                       'vs': vs,
                       'perfilAtleta': pa,
                       })

    vs = manejarSesion(request, marca.m_alias, True)
    request.session['marca'] = marca.m_alias
    return redirect("/" + marca.m_alias + "/dashboard")


@login_required(login_url='/requerirLogon')
@user_is_legal
def confmarca(request, pka):
    pk = request.user.profile.u_alias
    vs = manejarSesion(request, pk, False)
    pm = PerfilMarca(vs.marcaEnUsoAlias)
    pais = Pais.objects.all()
    ciudad = Ciudad.objects.all()
    municipio = Zona.objects.all()
    return render(request, 'registroMarca.html', {
        'pais': pais,
        'ciudad': ciudad,
        'municipio': municipio,
        'vs': vs,
        'perfilMarca': pm,
        'disciplinas': Disciplina.objects.all(),
        'editando': True,
    })


@login_required(login_url='/requerirLogon')
def actualizarConfigMarca(request, pka):
    nombre = request.POST['nombreComercial']
    razonSocial = request.POST['razonSocial']
    rif = request.POST['rif']
    descripcion = request.POST['descripcion']
    calle = request.POST['calle']
    urbanizacion = request.POST['urbanizacion']
    ciudad = request.POST['ciudad']
    municipio = request.POST['municipio']
    pais = request.POST['pais']
    edificioCasa = request.POST['edificioCasa']
    tiempoReversible = request.POST['tiempoReversible']
    tiempoIrreversible = request.POST['tiempoIrreversible']
    planContratado = request.POST['planContratado']
    instructoresContratados = request.POST['instructoresContratados']
    pm = PerfilMarca(pka)
    quiereTipoReferenciado = False
    if 'esReferenciado' in request.POST:
        if request.POST['esReferenciado'] == u'on':
            quiereTipoReferenciado = True
    publica = request.POST.get('publica', False)
    if publica == u'on':
        publica = True
    try:
        revisarSeteoTipoReferenciado(pm, quiereTipoReferenciado)
        Marca.objects.filter(m_alias=pka).update(m_nombre=nombre, m_razon_social=razonSocial, m_doc_ident=rif,
                                                 m_descripcion=descripcion, m_calle=calle, m_urbanizacion=urbanizacion,
                                                 m_edificioCasa=edificioCasa,
                                                 m_ciudad=ciudad, m_municipio=municipio, m_pais=pais,
                                                 m_est_rrev=tiempoReversible, m_est_irrev=tiempoIrreversible,
                                                 m_planVictorius=planContratado,
                                                 m_instructoresContratados=instructoresContratados,
                                                 m_public=publica,
                                                 m_permite_referenciados=quiereTipoReferenciado, )
        messages.success(request, 'Marca actualizada exitosamente.')
    except:
        messages.error(request, 'Marca no fue actualizada. Se produjo un error.')

    return redirect(request.META['HTTP_REFERER'])


def revisarSeteoTipoReferenciado(pm, quiereTipoReferenciado):
    if quiereTipoReferenciado and pm.marcaProductoTipoReferenciado:
        # Aqui no se hace nada, es referenciado y quiere seguir asi
        pass
    elif quiereTipoReferenciado and not pm.marcaProductoTipoReferenciado:
        # Hay marcar tipoReferenciado en tabla Marca, no es referenciado y quiere serlo
        Marca.objects.filter(m_alias=pm.marcaAlias).update(m_permite_referenciados=True)
        # Hay que incluir el producto refernciado a la marca si es que no existe
        # de un seteo previo (pudo haber sido que dejo de ser referenciado y ahora quiere serlo).
        pm = PerfilMarca(pm.marcaAlias)
        if not Producto.objects.filter(p_nombre='Referenciado', p_marca_id=pm.marcaId):
            Producto.objects.create(p_nombre='Referenciado', p_marca_id=pm.marcaId, p_duracion_meses=999,
                                    p_precio=0, p_descuento=0, p_creditos=0, p_tipo=3, p_disciplinas=[])
        else:
            # En este caso tuvo anteriormente un producto referenciado y esta activandolo
            pm.marcaProductoTipoReferenciado.p_activo = True
            pm.marcaProductoTipoReferenciado.save()

        # Hay que incluirle el producto referenciado y los planes a sus atletas si no los tienen
        for atleta in pm.marcaAtletas():
            pa = PerfilAtleta(atleta['aliasatleta'])
            setearPlanReferenciado(pa, pm)
    elif not quiereTipoReferenciado and pm.marcaProductoTipoReferenciado:
        # Hay desmarcar tipoReferenciado en tabla Marca
        productoReferenciado = pm.marcaProductoTipoReferenciado
        productoReferenciado.p_activo = False
        productoReferenciado.save()
        Marca.objects.filter(m_alias=pm.marcaAlias).update(m_permite_referenciados=False)
    return


@login_required(login_url='/requerirLogon')
@user_is_legal
def confatleta(request, pka):
    pk = request.user.profile.u_alias
    vs = manejarSesion(request, pk, False)
    usuario = vs.user
    perfil = UserProfile.objects.get(u_alias=vs.userAlias)
    try:
        telefono = perfil.u_telefono
    except:
        telefono = None
    paises = Pais.objects.all()
    ciudades = Ciudad.objects.all()
    municipios = Zona.objects.all()
    marcasPublicas = Marca.objects.filter(m_public=True)
    marcasSeguidas = Relacion.objects.filter(r_user_id=usuario.id).values_list('r_marca_id__m_nombre', flat=True)
    marcas = Dueno.objects.filter(d_user=request.user)
    try:
        dic1 = Disciplina.objects.get(pk=perfil.u_displinafav1_id).d_nombre
    except:
        dic1 = ''
    try:
        dic2 = Disciplina.objects.get(pk=perfil.u_displinafav2_id).d_nombre
    except:
        dic2 = ''
    try:
        dic3 = Disciplina.objects.get(pk=perfil.u_displinafav3_id).d_nombre
    except:
        dic3 = ''
    disciplinas = Disciplina.objects.all()
    return render(request, 'config-atleta.html', {
        'usuario': usuario,
        'perfil': perfil,
        'telefono': telefono,
        'fechaNac': str(perfil.u_fecha_nac),
        'fechaNacFormatoSP': str(perfil.u_fecha_nac.year) + '-' + '%02d' % (
            perfil.u_fecha_nac.month,) + '-' + '%02d' % (perfil.u_fecha_nac.day,),
        'dic1': str(dic1),
        'dic2': dic2,
        'dic3': dic3,
        'marcasPublicas': marcasPublicas,
        'marcasSeguidas': marcasSeguidas,
        'esmarca': False,
        'paises': paises,
        'ciudades': ciudades,
        'disciplinas': disciplinas,
        'municipios': municipios,
        'marcas': marcas,
        'vs': vs,
        'token': False,
    })


def actualizarConfigAtleta(request, pka):
    conToken = False
    cambioEnUser = False
    if 'token' in request.META['HTTP_REFERER']:
        k = request.META['HTTP_REFERER'].rfind("/")
        token = Token.objects.get(u_token=request.META['HTTP_REFERER'][k + 1:])
        user = token.u_user
        token.delete()
        user.is_active = True
        conToken = True
    else:
        user = request.user
    if user.username != request.POST['correo']:
        user.username = request.POST['correo']
        cambioEnUser = True
    if user.first_name != request.POST['primerNombre']:
        user.first_name = request.POST['primerNombre']
        cambioEnUser = True
    if user.last_name != request.POST['primerApellido']:
        user.last_name = request.POST['primerApellido']
        cambioEnUser = True

    try:
        if request.POST['passwordIn'] != u'':
            user.set_password(request.POST['passwordIn'])
            user.is_active = True
            cambioEnUser = True
    except:
        pass

    perfil = UserProfile.objects.get(u_user=user)
    perfil.u_alias = request.POST['u-alias']
    perfil.u_secondname = (request.POST['segundoNombre'])
    perfil.u_secondlastname = (request.POST['segundoApellido'])
    perfil.u_telefono = request.POST['telefono']
    perfil.u_calle = request.POST['calle']
    perfil.u_urbanizacion = request.POST['urbanizacion']

    try:
        perfil.u_ciudad = Ciudad.objects.get(request.POST['ciudad'])
        perfil.u_municipio = Zona.objects.get(request.POST['municipio'])
        perfil.u_pais = Pais.objects.get(request.POST['pais'])
    except:
        perfil.u_ciudad = None
        perfil.u_municipio = None
        perfil.u_pais = None

    perfil.u_edificioCasa = request.POST['edificioCasa']
    perfil.u_direccion = "Edf. " + request.POST['edificioCasa'] + ", Cll/Av." + request.POST['calle'] + " - Urb." + \
                         request.POST['urbanizacion']

    try:
        perfil.u_fecha_nac = datetime.strptime(request.POST['fechaNacimiento'], '%Y-%m-%d')
    except:
        pass

    perfil.u_genero = request.POST['genero']
    try:
        perfil.u_displinafav1 = Disciplina.objects.get(id=(request.POST['dic1']))
        perfil.u_displinafav2 = Disciplina.objects.get(id=(request.POST['dic2']))
        perfil.u_displinafav3 = Disciplina.objects.get(id=(request.POST['dic3']))
    except:
        pass
    perfil.u_objetivos = (request.POST['objetivos'])
    try:
        if request.POST['publica'] == 'on':
            perfil.u_public = True
    except:
        perfil.u_public = False

    try:
        if cambioEnUser:
            user.save()
        perfil.u_registrado = True
        perfil.save()
        messages.success(request, 'Atleta actualizado exitosamente.')
    except Exception as e:
        messages.error(request, 'Atleta no fue actualizado. Se produjo un error.')

    if conToken:
        return redirect("/")
    else:
        return redirect(request.META['HTTP_REFERER'])


@login_required(login_url='/requerirLogon')
@user_is_legal
def perfilmarca(request, pk):

    vs = manejarSesion(request, pk, False)
    pm = PerfilMarca(pk)

    productosActivos = []
    productos = Producto.objects.filter(p_marca_id=pm.marcaId, p_activo=True).exclude(p_tipo=3)
    for producto in productos:
        log.info('producto:'+ producto.p_nombre)
        productosActivos.append({
             'id': producto.id,
             'nombre': producto.p_nombre,
             'precio': bolivares(producto.p_precio),
             'descuento': formatoPorcentaje(producto.p_descuento),
             'creditos': producto.p_creditos,
             'vencimiento': producto.p_duracion_meses,
        })
    log.info('Estoy saliendo de perfilmarca')
    return render(request, 'centro-detail.html', {
        'vs': vs,
        'pm': pm,
        'perfilMarca': pm,
        'relaciones': Relacion.objects.filter(r_user=vs.userId, r_estado='A'),
        'disciplinas': Disciplina.objects.filter(),
        'productosActivos': productosActivos,
    })


@login_required(login_url='/requerirLogon')
def solicitudusuarioajax(request):
    opcion = int(request.GET['opcion'])
    usuario = User.objects.get(pk=int(request.GET['usuario']))
    marca = Marca.objects.get(pk=int(request.GET['marca']))
    mensaje = ''
    mn = ManejoNotificaciones()
    try:
        with transaction.atomic():
            if opcion == 1:
                if Relacion.objects.filter(r_user=usuario, r_marca=marca, r_estado='P'):
                    mensaje = 'Existe una invitación de seguimiento pendiente'
                else:
                    Relacion.objects.create(r_user=usuario, r_marca=marca, r_estado='P')
                    mensaje = 'Solicitud de seguimineto registrada'
                    mn.atleta_solicita_afiliacion(usuario, marca)
            elif opcion == 0:
                r = Relacion.objects.get(r_user=usuario, r_marca=marca)
                if r.r_estado == 'P':
                    mn.eliminarNotificacionAtletaMarca(marca.id, usuario.id, 'SA')
                    mn.eliminarNotificacionMarcaAtleta(marca.id, usuario.id, 'IA')
                    r.delete()
                    mensaje = 'Eliminacion de solicitud realizada'
                else:
                    r.delete()
                    mensaje = 'Eliminacion de seguimiento realizada'
            messages.success(request, mensaje)
    except:
        mensaje = 'Hubo un error al realizar la operacion.'
        messages.error(request, 'Found Error. Executed Rollback')

    return HttpResponse(json.dumps(mensaje), content_type='application/json')


def setearPlanReferenciado(pa, pm):
    if Planes.objects.filter(p_marca_id=pm.marcaId, p_usuario_id=pa.atletaId,
                             p_producto_id=pm.marcaProductoTipoReferenciado.id):
        return
    hoy = datetime.today()
    # Primero creo el plan
    planOut = Planes()
    planOut.p_nombre = 'Referenciado'
    planOut.p_creditos_totales = 0
    planOut.p_fecha_obtencion = hoy
    planOut.p_fecha_caducidad = datetime(3000, hoy.month, hoy.day).strftime('%Y-%m-%d')
    planOut.p_tipo = 3
    planOut.p_marca_id = pm.marcaId
    planOut.p_usuario_id = pa.atletaId
    planOut.p_producto_id = pm.marcaProductoTipoReferenciado.id
    planOut.save()

    # Generacion del codigo interno
    nro = Pago.objects.filter(p_marca=pm.marcaId).count() + 1
    fechaIn = hoy.strftime('%Y-%m-%d')
    codigoInterno = str(pm.marcaId) + '-' + fechaIn + '-' + str(nro)

    # Segundo creo el pago
    pagoOut = Pago()
    pagoOut.p_medio = 0
    pagoOut.p_pagador_id = pa.atletaId
    pagoOut.p_marca_id = pm.marcaId
    pagoOut.p_plan = planOut
    pagoOut.p_producto_id = planOut.p_producto_id
    pagoOut.p_fecha_registro = hoy
    pagoOut.p_fecha_transaccion = fechaIn
    pagoOut.p_medio = 0
    pagoOut.p_monto = 0
    pagoOut.p_precio = 0
    pagoOut.p_dtoGeneral = 0
    pagoOut.p_dtoParticular = 0
    pagoOut.p_diferencia = 0
    pagoOut.p_status = False
    pagoOut.p_porcobrar = False
    pagoOut.p_codigoInterno = codigoInterno
    pagoOut.save()

    return


@login_required(login_url='/requerirLogon')
def pagospendientes(request, pk, pka):
    vs = manejarSesion(request, pk, False)
    perfil = UserProfile.objects.get(u_user=request.user)
    aperfil = UserProfile.objects.get(u_alias=pka)
    user = aperfil.u_user

    try:
        fecha = datetime.strptime(request.GET['fecha'], '%Y-%m-%d')
        esultimo = False
        if fecha.day >= 1 and fecha.day <= 15:
            fecha = fecha.replace(day=1)
            ultimo = fecha.replace(day=15)
            primero = fecha.replace(day=1)
        else:
            fecha = fecha.replace(day=16)
            ultimo = fecha.replace(day=monthrange(fecha.year, fecha.month)[1])
            primero = fecha.replace(day=1)
    except:
        fecha = datetime.today()
        esultimo = True
        if fecha.day >= 1 and fecha.day <= 15:
            ultimo = fecha
            primero = fecha.replace(day=1)
            if not fecha.day == datetime.today().day:
                ultimo = fecha.replace(day=15)
        else:
            ultimo = fecha
            primero = fecha.replace(day=16)
            if not fecha.day == datetime.today().day:
                ultimo = fecha.replace(day=monthrange(fecha.year, fecha.month)[1])
    marcas = Dueno.objects.filter(d_user=request.user)
    marcasids = marcas.values_list('d_marca', flat=True)
    marca_actual = Marca.objects.get(m_alias=pk)
    mesesprevios = []
    totalesprevios = []
    pagos = Actividad.objects.filter(ac_instructor=aperfil, ac_estado="Culminada", ac_fecha__lte=ultimo,
                                     ac_fecha__gte=primero)
    total_hoy = pagos.aggregate(Sum('ac_creditos'))
    hoy = primero
    creditos = (Actividad.objects.filter(ac_instructor=aperfil, ac_fecha__lte=ultimo,
                                         ac_estado__ea_estado__in=['Culminada', 'Activa'],
                                         ac_fecha__gte=primero).aggregate(Sum('ac_precio')))['ac_precio__sum']
    bonos = (Actividad.objects.filter(ac_instructor=aperfil, ac_fecha__lte=ultimo,
                                      ac_estado__ea_estado__in=['Culminada', 'Activa'],
                                      ac_fecha__gte=primero).aggregate(Sum('ac_bono')))['ac_bono__sum']
    if creditos == None:
        creditos = 0
    if bonos == None:
        bonos = 0
    mostrar = []
    for x in range(0, 6):
        creditos = (Actividad.objects.filter(ac_instructor=aperfil, ac_fecha__lte=ultimo,
                                             ac_estado__ea_estado__in=['Culminada', 'Activa'],
                                             ac_fecha__gte=primero).aggregate(Sum('ac_precio')))['ac_precio__sum']
        bonos = (Actividad.objects.filter(ac_instructor=aperfil, ac_fecha__lte=ultimo,
                                          ac_estado__ea_estado__in=['Culminada', 'Activa'],
                                          ac_fecha__gte=primero).aggregate(Sum('ac_bono')))['ac_bono__sum']
        if creditos == None:
            creditos = 0
        if bonos == None:
            bonos = 0
        mesesprevios.append([primero, ultimo, creditos + bonos])
        totalesprevios.append([creditos, bonos, creditos + bonos])
        hoy = primero
        mostrar.append(Actividad.objects.filter(ac_instructor=aperfil, ac_fecha__gte=primero, ac_fecha__lte=ultimo,
                                                ac_estado="Culminada"))
        hoy = hoy - timedelta(days=10)
        if hoy.day >= 1 and hoy.day <= 15:
            primero = hoy.replace(day=1)
            ultimo = hoy.replace(day=15)
        else:
            primero = hoy.replace(day=16)
            ultimo = hoy.replace(day=monthrange(hoy.year, hoy.month)[1])
    if fecha.day >= 1 and fecha.day <= 15:
        primero = fecha.replace(day=1)
        ultimo = fecha.replace(day=15)
    else:
        primero = fecha.replace(day=16)
        ultimo = fecha.replace(day=monthrange(fecha.year, fecha.month)[1])
    marcasids = marcas.values_list('d_marca', flat=True)
    actividades = Actividad.objects.filter(ac_marca__in=marcasids)
    return render(request, 'pagos-pendientes.html', {
        'aperfil': aperfil,
        'esmarca': perfil.u_marca,
        'perfil': perfil,
        'user': user,
        'mostrar': mostrar,
        'marca_actual': marca_actual,
        'vs': vs,
        'esultimo': esultimo,
        'marcas': marcas,
        'fecha': fecha,
        'mesesprevios': mesesprevios,
        'totalesprevios': totalesprevios,
        'total_hoy': total_hoy,
        'pagos': pagos,
        'pk': pk,
        'pka': pka,
    })


@login_required(login_url='/requerirLogon')
@user_is_legal
def consumos(request, pk):
    vs = manejarSesion(request, pk, False)
    perfil = UserProfile.objects.get(u_user=request.user)
    try:
        hoy = datetime.strptime(request.GET['fecha'], '%Y-%m-%d')
    except:
        hoy = datetime.today()
    try:
        actual = Marca.objects.get(m_alias=pk)
        m = True
    except:
        m = False
    fechaActual = datetime.today()
    fechaActual = fechaActual.replace(hour=0, minute=0, second=0, microsecond=0)
    hoy = hoy.replace(hour=0, minute=0, second=0, microsecond=0)
    dia_hoy = hoy.day
    dia_sem = hoy.weekday()
    if fechaActual == hoy:
        ini_sem = (hoy - timedelta(days=5))
        sem_pas = ini_sem
        fin_sem = ini_sem + timedelta(days=6)
    else:
        ini_sem = (hoy - timedelta(days=3))
        sem_pas = ini_sem
        fin_sem = ini_sem + timedelta(days=6)

    sem = []
    sem_date = []
    participantes = []
    tespera = 0
    marcas = Dueno.objects.filter(d_user=request.user)

    participo = []
    perfiles = []
    tcreditos = []
    indice = 5
    for x in range(0, 6):
        fecha = (ini_sem + timedelta(days=x))
        fecha = fecha.replace(hour=0, minute=0, second=0, microsecond=0)
        if fecha == fechaActual:
            indice = x
        sem.append(fecha.day)
        sem_date.append(fecha)
        participantes.append(Participantes.objects.filter(pa_actividad__ac_marca=actual,
                                                          pa_actividad__ac_fecha=fecha).count())
        parti = Participantes.objects.filter(pa_actividad__ac_marca=actual,
                                             pa_actividad__ac_fecha=fecha)
        per = []
        creditos = 0
        for p in parti:
            per.append(UserProfile.objects.get(u_user=p.pa_usuario))
            creditos += p.pa_actividad.ac_creditos
        participo.append(zip(parti, per))
        perfiles.append(per)
        tcreditos.append(creditos)
        esta = ini_sem < datetime.today() and fin_sem > datetime.today()

    return render(request, 'consumos.html',
                  {'marcas': marcas,
                   'sem_date': zip(participantes, sem_date, participo, perfiles, tcreditos),
                   'marca_actual': actual,
                   'vs': vs,
                   'perfil': perfil,
                   'pk': pk,
                   'esultimo': esta,
                   'hoy': hoy,
                   'sem_pas': sem_pas,
                   'fin_sem': fin_sem,
                   'creditos': creditos,
                   'esmarca': True,
                   'dia_sem': ["Lun", "Mar", "Mie", "Jue", "Vie", "Sab", "Dom"][hoy.weekday()],
                   'indice': indice,
                   'participantes': participantes,
                   })


@login_required(login_url='/requerirLogon')
def cambiarcontraajax(request):
    u = int(request.GET['user'])
    try:
        if (request.user.pk == u):
            user = User.objects.get(pk=u)
            user.set_password(request.GET['password'])
            user.save()
            resultado = 1
        else:
            resultado = 2
    except:
        resultado = 0
    return HttpResponse(json.dumps(resultado), content_type='application/json')


@login_required(login_url='/requerirLogon')
def calendario(request, pk, pka):
    vs = manejarSesion(request, pk, False)
    update_activities()
    ahora = datetime.now()
    relaciones = Relacion.objects.filter(r_user=request.user, r_estado='A')
    try:
        hoy = datetime.strptime(request.GET['fecha'], '%Y-%m-%d')
    except:
        hoy = datetime.today()
    relacion = Relacion.objects.values_list('r_marca', flat=True).filter(r_estado="A", r_user=request.user)
    mare = Marca.objects.filter(pk__in=relacion)
    marcas_publicas = Marca.objects.filter(m_public=True).order_by('m_nombre') | mare
    perfil = UserProfile.objects.get(u_user=request.user)
    hoy = hoy.replace(hour=0, minute=0, second=0)
    dia_hoy = hoy.day
    dia_sem = hoy.weekday()
    ini_sem = (hoy - timedelta(days=hoy.weekday()))
    pasada = ini_sem - timedelta(days=7)
    fin_sem = ini_sem + timedelta(days=7)
    sem = []
    sem_date = []
    for x in range(0, 8):
        sem.append((ini_sem + timedelta(days=x)).day)
        sem_date.append(ini_sem + timedelta(days=x))
    marcas = Dueno.objects.filter(d_user=request.user)
    actual = Marca.objects.get(m_alias=pka)
    nombre = actual.m_nombre
    actividades_semana = []
    confirmados_semana = []
    reservas_semana = []
    enespera_semana = []
    cuposenespera_semana = []
    cuentas = []
    disciplinas = Disciplina.objects.all()
    ids = Relacion.objects.values_list('r_user__pk', flat=True).filter(r_marca=actual, r_entrenador=True)
    instructores = User.objects.filter(pk__in=set(ids))
    salones = Salon.objects.filter(s_marca=actual)
    try:
        saldo = Saldo.objects.get(s_marca=actual, s_user=request.user).s_saldo
    except:
        saldo = None
    for i in range(0, 8):
        p = Participantes.objects.values_list('pa_actividad', flat=True).filter(pa_usuario=request.user,
                                                                                pa_actividad__ac_fecha__range=(
                                                                                    ini_sem + timedelta(days=i),
                                                                                    ini_sem + timedelta(days=i,
                                                                                                        hours=23)), )
        e = Espera.objects.values_list('es_actividad', flat=True).filter(es_usuario=request.user,
                                                                         es_actividad__ac_fecha__range=(
                                                                             ini_sem + timedelta(days=i),
                                                                             ini_sem + timedelta(days=i, hours=23)), )
        pq = Actividad.objects.filter(pk__in=p)
        eq = Actividad.objects.filter(pk__in=e)
        cuentas.append(pq.count() + eq.count())
        acthoy = Actividad.objects.filter(ac_marca=actual, ac_fecha__range=(
            ini_sem + timedelta(days=i), ini_sem + timedelta(days=i, hours=23))).order_by('ac_hora_ini')
        est = []
        for x in acthoy:
            if x.ac_fecha >= datetime.now().date():
                if x in pq:
                    est.append([1, Participantes.objects.get(pa_actividad=x, pa_usuario=request.user).pa_num_cupo])
                elif x in eq:
                    est.append([2, Espera.objects.get(es_actividad=x, es_usuario=request.user).es_num_cupo])
                else:
                    est.append([0, 0])
            else:
                if x in pq:
                    est.append([3, Participantes.objects.get(pa_actividad=x, pa_usuario=request.user).pa_num_cupo])
                elif x in eq:
                    est.append([3, Espera.objects.get(es_actividad=x, es_usuario=request.user).es_num_cupo])
                else:
                    est.append([3, 0])
        actividades_semana.append(zip(acthoy, est))
        cuentas.append(acthoy.count())
        confirmados_semana.append(Actividad.objects.filter(ac_marca=actual, ac_fecha__range=(
            ini_sem + timedelta(days=i), ini_sem + timedelta(days=i, hours=23))).aggregate(
            sum_cupos=Coalesce(Sum('ac_cupos_reservados'), 0)))
        reservas_semana.append(Actividad.objects.filter(ac_marca=actual, ac_fecha__range=(
            ini_sem + timedelta(days=i), ini_sem + timedelta(days=i, hours=23))).aggregate(
            sum_cupos=Coalesce(Sum('ac_cap_max'), 0)))
        enespera_semana.append(Actividad.objects.filter(ac_marca=actual, ac_fecha__range=(
            ini_sem + timedelta(days=i), ini_sem + timedelta(days=i, hours=23))).aggregate(
            sum_cupos=Coalesce(Sum('ac_cupos_en_espera'), 0)))
        cuposenespera_semana.append(Actividad.objects.filter(ac_marca=actual, ac_fecha__range=(
            ini_sem + timedelta(days=i), ini_sem + timedelta(days=i, hours=23))).aggregate(
            sum_cupos=Coalesce(Sum('ac_cap_max_espera'), 0)))
        maximo = max(cuentas)
        nombressem = []
        nom = ["Lunes", "Martes", "Miercoles", "Jueves", "Viernes", "Sabado", "Domingo", "Lunes"]
        for i in range(0, 8):
            nombressem.append(nom[i] + " " + str(sem[i]))
        minimo = list(map((lambda x: range(maximo - x)), cuentas))

    return render(request, 'mi-calendario2.html', {
        'dia_hoy': str(dia_hoy),
        'ini_sem': str(ini_sem.day),
        'inicio_sem': ini_sem,
        'mes': getmes(ini_sem.month - 1),
        'fin_de_sem': fin_sem,
        'fin_sem': str(fin_sem.day),
        'dia_sem': dia_sem,
        'ahora': ahora,
        'sem': zip(sem, sem_date),
        'pasada': pasada,
        'pk': pk,
        'nombre': nombre,
        'relaciones': relaciones,
        'saldo': saldo,
        'perfil': perfil,
        'marcas_publicas': marcas_publicas,
        'sem_date': sem_date,
        'hoy': datetime.today(),
        'maximo': maximo,
        'marcas': marcas,
        'salones': salones,
        'marca_actual': actual,
        'vs': vs,
        'actividades_semana': zip(actividades_semana, minimo, sem_date),
        'confirmados_semana': confirmados_semana,
        'reservas_semana': reservas_semana,
        'enespera_semana': enespera_semana,
        'cuposenespera_semana': cuposenespera_semana,
        'disciplinas': disciplinas,
        'instructores': instructores,
    })


def instructordetail(request, pk, pka, pkb):
    perfil = UserProfile.objects.get(u_user=request.user)
    entrenador = UserProfile.objects.get(u_alias=pka)
    marca = Marca.objects.get(m_alias=pkb)
    relaciones = Relacion.objects.filter(r_user=entrenador.u_user, r_entrenador=True)
    clasesimpartidas = Actividad.objects.filter(ac_instructor=entrenador, ac_marca=marca,
                                                ac_fecha__lte=datetime.today())[0:4]
    clasesporimpartir = Actividad.objects.filter(ac_instructor=entrenador, ac_marca=marca,
                                                 ac_fecha__gt=datetime.today())[0:4]
    return render(request, 'instructor-detail.html', {
        'perfil': perfil,
        'entrenador': entrenador,
        'relaciones': relaciones,
        'marca': marca,
        'clasesimpartidas': clasesimpartidas,
        'clasesporimpartir': clasesporimpartir, })


def activacionporcorreo(request, pk):
    t = Token.objects.get(u_token="p-" + pk)
    usuario = t.u_user
    usuario.is_active = True
    usuario.save()
    t.delete()
    #messages.success(request, "Su usuario ha sido activado por favor inicie sesión", extra_tags='sticky')
    usuario = t.u_user
    auth.login(request, usuario)
    perfil = UserProfile.objects.get(u_user=usuario)
    if perfil.u_marca:
        actual = Dueno.objects.filter(d_user__username=usuario.username)[0]
        request.session['marca'] = actual.d_marca.m_alias
        return redirect('/' + actual.d_marca.m_alias + "/dashboard")
    else:
        return redirect("/" + perfil.u_alias + "/dashboard")
    return redirect("/")


def reenviarcorreo(request):
    user = User.objects.get(username=request.GET['user'])
    try:
        token = Token.objects.get(u_user=user)
    except:
        t = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(25))
        token = Token.objects.create(u_user=user, u_token=t)
    enlace = "http://" + request.META['HTTP_HOST'] + "/token/" + token.u_token
    send_mail('Registro en Victorius',
              user.first_name + ' ' + user.last_name + ', gracias por registrarse en Victorius \n Usuario:' + user.username + "\nPara activar su cuenta entre en el siguiente enlace: " + enlace + "\n\n",
              'register@victorius.io', [user.username], fail_silently=False, )

    return HttpResponse(json.dumps("Le enviamos un correo confirmelo para iniciar sesión"),
                        content_type='application/json')


def requerirLogon(request):
    return render(request, "logon.html")


def getReciboPagoInfo(request):
    planIdIn = request.GET['planId']
    plan = Planes.objects.get(id=planIdIn)
    pago = Pago.objects.get(p_plan_id=planIdIn)
    centro = pago.p_marca.m_nombre
    perfilPagador = UserProfile.objects.get(u_user_id=pago.p_pagador_id)
    nombre = pago.p_pagador.first_name + ' ' + pago.p_pagador.last_name
    alias = perfilPagador.u_alias
    envioCorreo = False
    tiempoEmitido = datetime.now() - pago.p_fecha_registro
    if tiempoEmitido.total_seconds() < 5:
        envioCorreo = True
    fecha = fechaCorta(pago.p_fecha_registro)
    total = bolivares(pago.p_monto - pago.p_diferencia)
    numeroRecibo = pago.p_codigoInterno
    medioPago = tipoMedioPago(pago.p_medio)
    planHeaderDescuento = 'descuento '
    if pago.p_dtoGeneral > 0:
        planHeaderDescuento += formatoPorcentaje(porcentajeValor(pago.p_dtoGeneral, pago.p_precio))
        if pago.p_dtoParticular > 0:
            planHeaderDescuento += ' + ' + formatoPorcentaje(porcentajeValor(pago.p_dtoParticular, pago.p_precio))
    else:
        if pago.p_dtoParticular > 0:
            planHeaderDescuento += formatoPorcentaje(porcentajeValor(pago.p_dtoParticular, pago.p_precio))
    try:
        banco = pago.p_cuenta.c_banco
        referencia = pago.p_referencia
    except:
        banco = ''
        referencia = ''
    data = {
        'centro': centro,
        'nombre': nombre,
        'alias': alias,
        'fecha': fecha,
        'total': total,
        'numeroRecibo': numeroRecibo,
        'medioPago': medioPago,
        'banco': banco,
        'referencia': referencia,
        'planNombre': plan.p_nombre,
        'planCreditos': plan.p_creditos_totales,
        'planFechaVencimiento': fechaCorta(plan.p_fecha_caducidad),
        'planPrecio': bolivares(pago.p_precio),
        'planHeaderDescuento': planHeaderDescuento,
        'planDescuento': bolivares(pago.p_dtoGeneral + pago.p_dtoParticular)
    }
    from django.template import loader

    html_message = loader.render_to_string(
        'correoReciboDePago.html',
        data,
    )
    message = 'Recibo de Pago'
    if envioCorreo:
        send_mail('Recibo de Pago', message, 'register@victorius.io', [pago.p_pagador.email], fail_silently=True,
                  html_message=html_message)
    return JsonResponse(data)


def enviarCorreoIntencionCompra(request):
    from django.template import loader

    correoUsuario = request.user.username
    producto = Producto.objects.get(id=request.GET['productoId'])
    pm = PerfilMarca(producto.p_marca.m_alias)
    cuentas = pm.marcaCuentasBancarias
    data = {
        'nombres': request.user.first_name + ' ' + request.user.last_name,
        'productoNombre': producto.p_nombre,
        'productoPrecio': producto.p_precio,
        'marcaNombre': pm.marcaNombre,
        'marcaAlias': pm.marcaAlias,
        'marcaCuentas': cuentas,
        'marcaRazonSocial': pm.marcaRazonSocial,
        'marcaRIF': pm.marcaRif,
        'marcaCorreo': pm.marcaCorreo,
        'marcaTelefono': pm.marcaTelefono1,
    }
    message = 'Realiza el pago de tu plan ' + producto.p_nombre + ' en ' + pm.marcaNombre
    html_message = loader.render_to_string(
        'correoIntencionCompra.html',
        data,
    )
    send_mail('Realiza el pago de tu plan', message, 'register@victorius.io', [correoUsuario], fail_silently=True,
              html_message=html_message)
    return JsonResponse(data)


def correoBienvenida(request):
    from django.template import loader
    message = 'Correo de Bienvenida'
    data = {}
    html_message = loader.render_to_string(
        'correoBienvenida.html',
        data,
    )
    send_mail('Recibo de Pago', message, 'register@victorius.io', ['juan@hazling.com'], fail_silently=True,
              html_message=html_message)
    return redirect(request.META['HTTP_REFERER'])


def eliminarUsuario(request):
    usuarioId = request.GET['usuarioId']
    user = User.objects.get(id=usuarioId)
    mensaje = ''
    marca = request.session['marca']
    try:
        if Relacion.objects.filter(r_user_id=user.id).count() == 1:
            user.delete()
            mensaje = 'Usuario eliminado exitosamente'
        else:
            mensaje = 'Usuario removido exitosamente'
            Relacion.objects.filter(r_user=user, r_marca__m_alias=marca).delete()
        messages.success(request, mensaje)
    except Exception as e:
        mensaje = 'Usuario no pudo ser eliminado. Se produjo error:' + e.message
        print(mensaje)
        messages.error(request, mensaje)
    return HttpResponse(json.dumps(mensaje), content_type='application/json')

@login_required(login_url='/requerirLogon')
@user_is_legal
def configuracionGeneral(request, pka=None, method='POST'):
    vs = manejarSesion(request, pka, False)
    return render(request, 'configMenu.html', {
        'vs': vs,
    })


@login_required(login_url='/requerirLogon')
@user_is_legal
def gestionarPlanes(request, pka=None, pkb=None, method='POST'):
    vs = manejarSesion(request, pka, False)
    editando = False
    cuentaNueva = False
    if request.method == 'POST':
        post = request.POST
        if post.get('idEditando') == 'True':
            editando = True
        if editando:
            producto = Producto.objects.get(id=post.get('idPlan'))
        else:
            producto = Producto()
            producto.p_marca_id = vs.marcaEnUsoId
            cuentaNueva = True
        producto.p_nombre = post.get('idNombrePlan')

        producto.p_precio = int(float(post.get('idPrecio').replace('.', '').replace(',', '.')))

        if post.get('idDescuentoGeneral'):
            producto.p_descuento = int(post.get('idDescuentoGeneral'))

        if post.get('idDescuentoEspecial1'):
            producto.p_precio2 = int(post.get('idDescuentoEspecial1'))

        if post.get('idDescuentoEspecial2'):
            producto.p_precio3 = int(post.get('idDescuentoEspecial2'))

        producto.p_creditos = post.get('idCreditos')
        producto.p_duracion_meses = post.get('idVencimiento')
        producto.p_descripcion = post.get('idDescripcionPlan')
        if post.get('idTipoPlan') == 'PC':
            producto.p_tipo = 0
        elif post.get('idTipoPlan') == 'MI':
            producto.p_tipo = 1
            producto.p_creditos = 0
        elif post.get('idTipoPlan') == 'ML':
            producto.p_tipo = 2
        producto.save()
    else:
        if 'prd' in request.GET:
            productoId = request.GET['prd']
            producto = Producto.objects.get(id=productoId)
            idPlan = producto.id
            nombrePlan = producto.p_nombre
            descripcionPlan = producto.p_descripcion
            precio = producto.p_precio
            descuentoEspecial1 = producto.p_precio2
            descuentoEspecial2 = producto.p_precio3
            creditos = producto.p_creditos
            vencimiento = producto.p_duracion_meses
            descuentoGeneral = producto.p_descuento
            if producto.p_tipo == 0:
                tipoPlan = 'PC'
            elif producto.p_tipo == 1:
                tipoPlan = 'MI'
            elif producto.p_tipo == 2:
                tipoPlan = 'ML'
            return render(request, 'gestionarPlanes.html', {
                'idPlan': idPlan,
                'nombrePlan': nombrePlan,
                'descripcionPlan': descripcionPlan,
                'precio': precio,
                'descuentoEspecial1': descuentoEspecial1,
                'descuentoEspecial2': descuentoEspecial2,
                'creditos': creditos,
                'vencimiento': vencimiento,
                'descuentoGeneral': descuentoGeneral,
                'tipoPlan': tipoPlan,
                'vs': vs,
                'editando': True,
            })
    if editando or cuentaNueva:
        return redirect('/' + pka + '/' + 'planes')
    else:
        return render(request, 'gestionarPlanes.html', {'editando': False, 'vs': vs})


@login_required(login_url='/requerirLogon')
@user_is_legal
def gestionarCuentas(request, pka=None, method='POST'):
    vs = manejarSesion(request, pka, False)
    editando = False
    cuentaNueva = False
    pm = PerfilMarca(pka)
    statusLiteral = 'ACTIVA'
    if request.method == 'POST':
        post = request.POST
        if post.get('idEditando') == 'True':
            editando = True
        if editando:
            cuenta = Cuenta.objects.get(id=post.get('idCuenta'))
            idCambioStatus = False
            if post.get('idCambioStatus') == 'on':
                idCambioStatus = True
            statusActual = cuenta.c_status
            if idCambioStatus:
                cuenta.c_status = not statusActual
        else:
            cuenta = Cuenta()
            cuenta.c_marca_id = vs.marcaEnUsoId
            cuenta.c_status = True
            cuentaNueva = True

        cuenta.c_banco = post.get('idBanco')
        cuenta.c_numero_cuenta = post.get('idNumero')

        cuenta.save()

    else:
        if 'cta' in request.GET:
            cuentaId = request.GET['cta']
            cuenta = Cuenta.objects.get(id=cuentaId)
            banco = cuenta.c_banco
            numero = cuenta.c_numero_cuenta
            status = cuenta.c_status
            if not status:
                statusLiteral = 'INACTIVA'

            return render(request, 'gestionarCuentas.html', {
                'cuentaId': cuentaId,
                'banco': banco,
                'numero': numero,
                'status': status,
                'editando': True,
                'pm': pm,
                'statusLiteral': statusLiteral,
                'vs': vs,
            })
    if editando or cuentaNueva:
        return redirect('/' + pka + '/' + 'cuentas')
    else:
        return render(request, 'gestionarCuentas.html', {
            'editando': False,
            'pm': pm,
            'vs': vs,
        })


@login_required(login_url='/requerirLogon')
@user_is_legal
def gestionarSalas(request, pka=None, method='POST'):
    vs = manejarSesion(request, pka, False)
    editando = False
    salaNueva = False
    pm = PerfilMarca(pka)

    if request.method == 'POST':
        post = request.POST
        if post.get('idEditando') == 'True':
            editando = True
        if editando:
            sala = Salon.objects.get(id=post.get('idSala'))
        else:
            sala = Salon()
            sala.c_marca_id = vs.marcaEnUsoId
            salaNueva = True

        sala.s_nombre = post.get('idNombre')
        sala.s_capacidad = post.get('idCapacidad')
        sala.s_marca_id = vs.marcaEnUsoId
        sala.s_overflow = 0
        sala.s_disciplina = None
        if post.get('idReferenciado') == 'on':
            referenciado = True
        else:
            referenciado = False
        sala.s_referenciado = referenciado
        sala.save()

    else:
        if 'sla' in request.GET:
            salaId = request.GET['sla']
            sala = Salon.objects.get(id=salaId)
            nombre = sala.s_nombre
            capacidad = sala.s_capacidad
            overflow = sala.s_overflow
            referenciado = sala.s_referenciado

            return render(request, 'gestionarSalas.html', {
                'salaId': salaId,
                'nombre': nombre,
                'capacidad': capacidad,
                'overflow': overflow,
                'referenciado': referenciado,
                'editando': True,
                'vs': vs,
                'pm': pm,
            })
    if editando or salaNueva:
        return redirect('/' + pka + '/' + 'salas')
    else:
        return render(request, 'gestionarSalas.html', {
            'editando': False,
            'pm': pm,
            'vs': vs,
        })


@login_required(login_url='/requerirLogon')
def notificacionesAjax(request, pk):
    vs = manejarSesion(request, pk, False)
    mn = ManejoNotificaciones()

    pendientes = ('C',)
    recientes = ('A', 'V',)

    if vs.tipoSesion == vs.ATLETA:
        perfil=PerfilAtleta(vs.userAlias)
        notificacionesAtleta = Usuario_Notificacion.objects.filter(un_estado__in=recientes, un_usuario_id=vs.userId)
        if notificacionesAtleta:
            listaNotificacionesRecientes = mn.listaNotificacionesAtleta(vs.userId, recientes)
        else:
            listaNotificacionesRecientes = None
    else:
        perfil=PerfilMarca(vs.marcaEnUsoAlias)
        notificacionesMarca = Marca_Notificacion.objects.filter(mn_estado__in=recientes, mn_marca_id=vs.marcaEnUsoId)
        if notificacionesMarca:
            listaNotificacionesRecientes = mn.listaNotificacionesMarca(vs.marcaEnUsoId, recientes)
        else:
            listaNotificacionesRecientes = None

    if vs.tipoSesion == vs.ATLETA:
        notificacionesAtleta = Usuario_Notificacion.objects.filter(un_estado__in=pendientes, un_usuario_id=vs.userId)
        if notificacionesAtleta:
            listaNotificacionesPendientes = mn.listaNotificacionesAtleta(vs.userId, pendientes)
        else:
            listaNotificacionesPendientes = None
    else:
        notificacionesMarca = Marca_Notificacion.objects.filter(mn_estado__in=pendientes, mn_marca_id=vs.marcaEnUsoId)
        if notificacionesMarca:
            listaNotificacionesPendientes = mn.listaNotificacionesMarca(vs.marcaEnUsoId, pendientes)
        else:
            listaNotificacionesPendientes = None

    return render(request, 'notificaciones.html', {
        'notificacionesPendientes': listaNotificacionesPendientes,
        'notificacionesRecientes': listaNotificacionesRecientes,
        'vs': vs,
        'perfil':perfil,
    })


def aceptarRechazarSolicitudAjax(request):
    disparador = request.GET['disparador']
    opcion = request.GET['opcion']
    pk = request.user.profile.u_alias
    notificacionId = request.GET['notificacionId']
    marcaId = request.GET['marcaId']
    vs = manejarSesion(request, pk, False)
    if vs.tipoSesion == vs.MARCA:
        marcaAlias = vs.marcaEnUsoAlias
    else:
        marcaAlias = Marca.objects.get(id=marcaId).m_alias
    profile = UserProfile.objects.get(u_user_id=request.GET['userId'])
    userAlias = profile.u_alias
    pm = PerfilMarca(marcaAlias)
    pa = PerfilAtleta(userAlias)
    userId = profile.u_user_id
    notificacion = Notificacion.objects.get(id=notificacionId)
    mn = ManejoNotificaciones()
    mensaje = ''
    estado = 'Nada'
    try:
        relacion = Relacion.objects.get(r_marca_id=marcaId, r_user_id=userId)
        if (opcion == u'1'):
            if pm.marcaPermiteReferenciados:
                setearPlanReferenciado(pa, pm)
            relacion.r_estado = 'A'
            relacion.save()
            if not Saldo.objects.filter(s_user=profile.u_user, s_marca_id=marcaId):
                Saldo.objects.create(s_user=profile.u_user, s_marca_id=marcaId)

            if disparador == 'atleta':
                mn.marca_acepta_atleta(notificacion.id)

            if disparador == 'marca':
                mn.atleta_acepta_marca(notificacion.id)

            mensaje = 'aceptacion de solicitud realizada'
            estado = 'Aceptada'
        else:

            if disparador == 'atleta':
                mn.marca_rechaza_atleta(notificacion.id)

            if disparador == 'marca':
                mn.atleta_rechaza_marca(notificacion.id)

            relacion.delete()

            mensaje = 'eliminación de solicitud realizada'
            estado = 'Eliminada'

    except Exception as e:
        print('Error:' + e.message)
        mensaje = 'Se produjo un error, La accion no pudo ser ejecutada'
        messages.error(request, mensaje)

    data = {'estado': estado}
    return JsonResponse(data)


def actualizaBaseEnSerie(actividad):
    # Chequeo si la actividad es es cabeza de serie (solo si es cabeza de serie)
    if actividad.ac_OpcionSerie == 'Si' and actividad.ac_actividadBaseSerieId == actividad.id:
        try:
            proxBaseSerie = Actividad.objects.filter(id__gt=actividad.id).order_by('id')[0].id
            cantRemanenteSerie = Actividad.objects.filter(id__gt=actividad.id).order_by('id').count()
        except:
            proxBaseSerie = None
            cantRemanenteSerie = 0
    else:
        proxBaseSerie = None

    actividadBaseSerieId = actividad.id

    if proxBaseSerie:
        # Esto solo tiene lugar si esta actualizando la base de una serie de forma simple
        if cantRemanenteSerie > 1:
            # Si hay actividades en la serie le cambio la base ya que la base vieja se convirtio en actividad simple
            Actividad.objects.filter(ac_actividadBaseSerieId=actividad.ac_actividadBaseSerieId,
                                     id__gt=actividad.id).update(ac_actividadBaseSerieId=proxBaseSerie)
        else:
            # Si solo queda una actividad en la serie la convierto en actividad simple
            Actividad.objects.filter(ac_actividadBaseSerieId=actividad.ac_actividadBaseSerieId,
                                     id__gt=actividad.id) \
                .update(ac_actividadBaseSerieId=proxBaseSerie,
                        ac_OpcionSerie='No',
                        ac_repetirComo='',
                        ac_despd='No',
                        ac_do=1,
                        ac_enf='No',
                        ac_fdesp=actividad.ac_fecha)

    return


def password_reset_complete(request,
                            template_name='registration/password_reset_complete.html',
                            current_app=None, extra_context=None):
    from django.shortcuts import resolve_url
    from django.template.response import TemplateResponse
    context = {
        'login_url': resolve_url(settings.LOGIN_URL),
        'title': ('Password reset complete'),
    }
    if extra_context is not None:
        context.update(extra_context)

    if current_app is not None:
        request.current_app = current_app

    return TemplateResponse(request, template_name, context)

def subirAvatar(request,pk):
    if request.method == 'POST' and request.FILES['myAvatar']:
        myAvatar = request.FILES['myAvatar']
        fs = FileSystemStorage()
        filename = fs.save(myAvatar.name, myAvatar)
        uploaded_file_url = fs.url(filename)
        return render(request, 'perfil.html', {
            'uploaded_file_url': uploaded_file_url
        })
    return render(request, 'perfil.html')
