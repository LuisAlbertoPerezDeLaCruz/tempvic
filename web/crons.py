# -*- coding: utf-8 -*-
#######################
# crons.py #
#######################

from .models import *
from datetime import datetime
from .clases import *


def update_activities():
    #arregloBD()
    revisarActividadesConflictivas()
    hoy = datetime.today()
    sietedias = hoy + timedelta(days=7)
    haceUnMes = hoy - timedelta(days=30)
    actividades = Actividad.objects.filter(ac_fecha__gte=haceUnMes, ac_fecha__lte=sietedias)
    for a in actividades:
        actualizar_cupos(a)
        irreversible = hoy + timedelta(minutes=a.ac_marca.m_est_irrev)
        reversible = hoy + timedelta(days=a.ac_marca.m_est_rrev)
        ini = datetime.combine(a.ac_fecha, a.ac_hora_ini)
        fin = datetime.combine(a.ac_fecha, a.ac_hora_fin)

        if a.ac_estado.ea_estado not in ['Cancelada','En Conflicto']:
            if ini > reversible:
                a.ac_estado = EstadoActividad.objects.get(ea_estado='Planifico')
            elif ini > irreversible and ini <= reversible:
                a.ac_estado = EstadoActividad.objects.get(ea_estado='Abierta Reversible')
            elif ini > hoy and ini <= irreversible:
                a.ac_estado = EstadoActividad.objects.get(ea_estado='Abierta Irreversible')
            elif ini <= hoy and fin > hoy:
                a.ac_estado = EstadoActividad.objects.get(ea_estado='Activa')
                cobrar(a)
            else:
                a.ac_estado = EstadoActividad.objects.get(ea_estado='Culminada')
                cobrar(a)
            a.save()
    return

def revisarActividadesConflictivas():
    from .views.viewsActividades import encuentraConflictosEnActividad
    mf=ManejoFechas()
    mn=ManejoNotificaciones()
    hoy = datetime.today()
    actividadesConflictivas=Actividad.objects.filter(ac_estado='En Conflicto',ac_fecha__gte=hoy.date())
    for actividad in actividadesConflictivas:
        ini = datetime.combine(actividad.ac_fecha, actividad.ac_hora_ini)
        if ini > hoy:
            conflictos=encuentraConflictosEnActividad(actividad)
            if conflictos:
                if not conflictos[0] and not conflictos[1]:
                    actividad.ac_estado=EstadoActividad.objects.get(ea_estado='Planifico')
                    actividad.save()
                    # Notificacion a la marca
                    texto = {}
                    texto['actividad'] = actividad.ac_nombre
                    texto['fechaHora'] = mf.fechaCorta(actividad.ac_fecha) + ' ' + mf.horaCivil(actividad.ac_hora_ini)
                    texto['instructor'] = actividad.ac_instructor.u_user.first_name + ' ' + actividad.ac_instructor.u_user.last_name
                    texto['mensaje'] = 'ha dejado de estar en conflicto'
                    dueno=Dueno.objects.get(d_marca=actividad.ac_marca)
                    mn.marca_informa_marca(dueno.d_user, actividad.ac_marca, texto, 'CE')

    return
def arregloBD():
    from .views.viewsGeneral import setearPlanReferenciado
    listaDuenos=Dueno.objects.filter()
    for dueno in listaDuenos:
        marca=Marca.objects.get(id=dueno.d_marca_id)
        if marca.m_permite_referenciados:
            planReferenciado=Planes.objects.filter(p_marca_id=marca.id,p_usuario_id=dueno.d_user.id,p_tipo=3)
            if planReferenciado:
                pass
            else:
                pa=PerfilAtleta(dueno.d_user.profile.u_alias)
                pm=PerfilMarca(marca.m_alias)
                setearPlanReferenciado(pa,pm)
    return

def actualizar_cupos(actividad):
    participantes=Participantes.objects.filter(pa_actividad_id=actividad.id).count()
    esperas=Espera.objects.filter(es_actividad_id=actividad.id).count()
    if actividad.ac_cupos_reservados != participantes or actividad.ac_cupos_en_espera != esperas :
        actividad.ac_cupos_reservados = participantes
        actividad.ac_cupos_en_espera = esperas
        actividad.save()

def actualizar_planes_tokens():
    caducarplanes()
    borrartokens()

def cobrar(actividad):
    participantes = Participantes.objects.filter(pa_actividad=actividad)
    for p in participantes:
        p.pa_cobrado = True
        p.save()
    espera = Espera.objects.filter(es_actividad=actividad)
    for e in espera:
        pa=PerfilActividad(actividad.id)
        atletaId=e.es_usuario.id
        marcaId=pa.actividadMarca.id
        vicsafe=VicSafe(atletaId,marcaId,None)
        pa=PerfilActividad(actividad.id)
        strReturn=vicsafe.registrar_reintegro_por_no_participacion(pa)

def caducarplanes():
    planes = Planes.objects.filter(p_historico=False)
    for plan in planes:
        if plan.p_fecha_caducidad < datetime.today() or \
                (plan.p_creditos_usados >= plan.p_creditos_totales and plan.p_tipo==0) or \
                (plan.p_creditos_usados >= plan.p_creditos_totales and plan.p_tipo == 2):
            marcaId=plan.p_marca_id
            atletaId=plan.p_usuario_id
            planId=plan.id
            vicsafe=VicSafe(atletaId,marcaId,None)
            strReturn=vicsafe.registrar_desactivacion_plan(planId)
            if strReturn=='ok':
                if plan.p_fecha_caducidad < datetime.today():
                    # Notificacion al atleta
                    mn = ManejoNotificaciones()
                    texto = {}
                    texto['plan'] = plan.p_nombre
                    texto['mensaje'] = 'alcanzo fecha de vencimiento'
                    mn.marca_informa_atleta(User.objects.get(id=atletaId), plan.p_marca, texto, 'VP')
                else:
                    # Notificacion al atleta
                    mn = ManejoNotificaciones()
                    texto = {}
                    texto['plan'] = plan.p_nombre
                    texto['mensaje'] = 'esta agotado'
                    mn.marca_informa_atleta(User.objects.get(id=atletaId), plan.p_marca, texto, 'VP')


def borrartokens():
    tokens = Token.objects.filter(u_data=True)
    for t in tokens:
        t.delete()

