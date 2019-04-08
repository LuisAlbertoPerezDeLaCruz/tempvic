# -*- coding: utf-8 -*-

from django import template
from datetime import datetime, timedelta
import locale
from django.utils.safestring import mark_safe
import re
from web.models import *
from web.clases import VicSafe,PerfilActividad,PerfilMarca, VicSession
from django_globals import globals

register = template.Library()

@register.simple_tag
def notificaciones_pendientes(vs):
    if vs.tipoSesion==vs.MARCA:
        np = str(Marca_Notificacion.objects.filter(mn_marca_id=vs.marcaEnUsoId, mn_estado='C').count())
    else:
        np = str(Usuario_Notificacion.objects.filter(un_usuario_id=vs.userId, un_estado='C').count())
    if np == '0':
       np = ''
    return np

@register.simple_tag
def current_time(format_string):
    return datetime.now().strftime(format_string)

@register.simple_tag
def perfil_de_marca(marcaAlias):
    pm=PerfilMarca(marcaAlias)
    return pm

@register.simple_tag
def marca_tiene_actividades_abiertas(marcaId):
    tiene=False
    actividades=Actividad.objects.filter(ac_marca_id=marcaId, ac_estado_id__in=['Abierta Reversible', 'Abierta Irreversible'])
    if actividades:
        tiene=True
    return tiene

@register.simple_tag
def soy_yo_mismo(atletaId):
    soyYoMismo=False
    vs = None
    if 'vs' in globals.request.session:
        vsJson = globals.request.session['vs']
        vs = VicSession(globals.request.user.username)
        vs.setear(vsJson)
    if vs.userId == atletaId:
        soyYoMismo=True
    return soyYoMismo

@register.simple_tag
def puede_reservar(actividadId,atletaId):
    vs = None
    if 'vs' in globals.request.session:
        vsJson = globals.request.session['vs']
        vs = VicSession(globals.request.user.username)
        vs.setear(vsJson)
    actividad=Actividad.objects.get(id=actividadId)
    actividadInstructor = actividad.ac_instructor
    marcaActividadId=actividad.ac_marca_id

    try:
        if vs.userAlias==actividadInstructor.u_alias:
            return False
        else:
            try:
                vicsafe = VicSafe(atletaId, marcaActividadId, None)
                resultado = vicsafe.puedeReservarActividad(actividadId, vs) is not None
                return resultado
            except:
                return False
    except:
        return False


@register.simple_tag
def esta_reservado(actividadId,atletaId):
    reservado = Participantes.objects.filter(pa_actividad_id=actividadId,pa_usuario_id=atletaId)
    espera =Espera.objects.filter(es_actividad_id=actividadId,es_usuario_id=atletaId)
    if reservado or espera:
        estaReservado=True
    else:
        estaReservado=False
    return estaReservado

@register.simple_tag
def atleta_asistio(actividadId,atletaId):
    participo = Participantes.objects.filter(pa_actividad_id=actividadId,pa_usuario_id=atletaId)
    if participo:
        if participo[0].pa_asistencia==True:
            return True
    return False

@register.simple_tag
def puesto_reserva(actividadId,atletaId):
    participacion = Participantes.objects.filter(pa_actividad_id=actividadId,pa_usuario_id=atletaId)
    if participacion:
       puestoReserva=participacion[0].pa_num_cupo
    else:
       puestoReserva = None
    return puestoReserva

@register.simple_tag
def puesto_espera(actividadId,atletaId):
    espera = Espera.objects.filter(es_actividad_id=actividadId,es_usuario_id=atletaId)
    if espera:
       puestoEspera=espera[0].es_num_cupo
    else:
       puestoEspera = None
    return puestoEspera

@register.simple_tag
def esta_en_espera(actividadId,atletaId):
    espera =Espera.objects.filter(es_actividad_id=actividadId,es_usuario_id=atletaId)
    if espera:
        estaEnEspera=True
    else:
        estaEnEspera=False
    return estaEnEspera

@register.simple_tag
def siguiendo_esta_marca(marcaId,atletaId):
    estaSiguiendo=False
    siguiendo = Relacion.objects.filter(r_user_id=atletaId,r_marca_id=marcaId,r_estado='A')
    if siguiendo:
        estaSiguiendo=True
    return estaSiguiendo

@register.simple_tag
def pendiente_con_esta_marca(marcaId,atletaId):
    estaPendiente=False
    pendiente = Relacion.objects.filter(r_user_id=atletaId,r_marca_id=marcaId,r_estado='P')
    if pendiente:
        estaPendiente=True
    return estaPendiente

@register.simple_tag
def instructor_en_esta_marca(marcaId,atletaId):
    esInstructor=False
    instructor = Relacion.objects.filter(r_user_id=atletaId,r_marca_id=marcaId,r_entrenador=True)
    if instructor:
       esInstructor=True
    return esInstructor

@register.simple_tag
def esAmigo(atletaReceptorId,atletaSolicitanteId):
    esAmigo=False
    amigos=Amistad.objects.filter(a_estado='A',a_receptor_id=atletaReceptorId,a_solicitante_id=atletaSolicitanteId)
    if amigos:
        esAmigo=True
    return esAmigo

@register.simple_tag
def tieneAmigosEnActividad(atletaId,actividadId):
    tieneAmigos=False
    participantes=Participantes.objects.filter(pa_actividad_id=actividadId)
    for participante in participantes:
        if esAmigo(participante.pa_usuario_id,atletaId):
            tieneAmigos=True
            break
    return tieneAmigos

def multiply(value, arg):
    return value*arg

def telefono(telefonoIn):
    telefonoIn=re.sub("[^0-9]", "", telefonoIn)
    if telefonoIn[0:2]=='58':
        telefonoIn=telefonoIn[2:]
    if len(telefonoIn)==11:
        area=telefonoIn[0:4]
        tel=telefonoIn[4:]
    elif len(telefonoIn)==10:
        area = '0'+telefonoIn[0:3]
        tel = telefonoIn[3:]
    else:
        area=''
        tel = telefonoIn[:]
    telefonoFormateado=''
    telefonoFormateado+='+58'+' ('+area+') '+tel[0:3]+'-'+tel[3:]
    return telefonoFormateado

def fechaLarga(fechaIn): # Solo un argumento.
    fechaFormateada=''
    if not fechaIn:
        return fechaFormateada
    dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado','domingo']
    meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre',
             'noviembre', 'diciembre']
    if fechaIn=='ahora':
        fechaIn=datetime.now()
    if type(fechaIn).__name__=='date' or type(fechaIn).__name__=='datetime':
        fecha=fechaIn
    else:
        fecha=datetime.strptime(fechaIn, "%I:%M %p").time()
    d=fecha.weekday()
    fechaFormateada=dias[d]+', '
    fechaFormateada+=str(fecha.day)+' de '
    fechaFormateada += meses[fecha.month-1] + ' de '
    fechaFormateada += str(fecha.year)
    return fechaFormateada

def fechaMedioLarga(fechaIn): # Solo un argumento.
    fechaFormateada=''
    if not fechaIn:
        return fechaFormateada
    dias = ['lun', 'mar', 'mié', 'jue', 'vie', 'sab','dom']
    meses = ['ene', 'feb', 'mar', 'abr', 'may', 'jun', 'jul', 'ago', 'sep', 'oct',
             'nov', 'dic']
    if fechaIn=='ahora':
        fechaIn=datetime.now()
    if type(fechaIn).__name__=='date' or type(fechaIn).__name__=='datetime':
        fecha=fechaIn
    else:
        fecha=datetime.strptime(fechaIn, "%I:%M %p").time()
    d=fecha.weekday()
    fechaFormateada = dias[d].capitalize() + ', '
    fechaFormateada+=str(fecha.day)+' '
    fechaFormateada += meses[fecha.month-1].capitalize() + ' '
    fechaFormateada += str(fecha.year)
    return fechaFormateada

def fechaNormal(fechaIn): # Solo un argumento.
    fechaFormateada=''
    if not fechaIn:
        return fechaFormateada
    meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre',
             'noviembre', 'diciembre']
    if fechaIn=='ahora':
        fechaIn=datetime.now()
    if type(fechaIn).__name__=='date' or type(fechaIn).__name__=='datetime':
        fecha=fechaIn
    else:
        fecha=datetime.strptime(fechaIn, "%I:%M %p").time()
    d=fecha.weekday()
    fechaFormateada+=str(fecha.day)+' de '
    fechaFormateada += meses[fecha.month-1] + ' de '
    fechaFormateada += str(fecha.year)
    return fechaFormateada

def fechaEspecial(fechaIn): # Solo un argumento.
    hoy=datetime.now().date()
    fechaFormateada=''
    if not fechaIn:
        return fechaFormateada
    dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado','domingo']
    meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre',
             'noviembre', 'diciembre']
    if fechaIn=='ahora':
        fechaIn=datetime.now()
    if type(fechaIn).__name__=='date' or type(fechaIn).__name__=='datetime':
        fecha=fechaIn
    else:
        fecha=datetime.strptime(fechaIn, "%I:%M %p").time()
    d=fecha.weekday()
    dia = dias[d]
    if fecha == hoy:
        fechaFormateada = 'hoy'
    elif fecha == hoy + timedelta(days=1):
        fechaFormateada = 'mañana'
    elif fecha == hoy - timedelta(days=1):
        fechaFormateada = 'ayer'
    elif fecha.month==hoy.month and fecha.year==hoy.year:
        fechaFormateada=dia +' '+ str(fecha.day)
    elif fecha.year==hoy.year:
        fechaFormateada += str(fecha.day) + ' de '
        fechaFormateada += meses[fecha.month - 1]
    else:
        fechaFormateada+=str(fecha.day)+' de '
        fechaFormateada += meses[fecha.month-1] + ' de '
        fechaFormateada += str(fecha.year)
    return fechaFormateada

def fechaCorta(fechaIn):
    fechaFormateada=''
    if not fechaIn:
        return fechaFormateada
    if type(fechaIn).__name__=='date' or type(fechaIn).__name__=='datetime':
        fecha=fechaIn
    else:
        fecha=datetime.strptime(fechaIn, "%I:%M %p").time()
    fechaFormateada=str(fecha.day)+'/'+str(fecha.month)+'/'+str(fecha.year)
    return fechaFormateada

def fechaCortaConHora(fechaIn):
    fechaFormateada=''
    if not fechaIn:
        return fechaFormateada
    fecha=fechaIn
    fechaFormateada = str(fecha.day) + '/' + str(fecha.month) + '/' + str(fecha.year)
    fechaFormateada += ' '
    fechaFormateada += horaCivil(fechaIn.time())
    return fechaFormateada

def horaCivil(horaIn):
    if type(horaIn).__name__=='time' or type(horaIn).__name__=='datetime.time':
        hora=horaIn
    else:
        hora=datetime.strptime(horaIn,"%I:%M %p").time()
    horaFormateada=hora.strftime("%I:%M %P")
    return horaFormateada

def tiempo(tiempoIn):
    if type(tiempoIn).__name__=='time' or type(tiempoIn).__name__=='datetime.time':
        tiempo=tiempoIn
    else:
        tiempo=datetime.strptime(tiempoIn,"%I:%M").time()
    tiempoFormateado=tiempo.strftime("%I:%M")
    return tiempoFormateado

def porcentajeValor(valorIn,baseIn): #Dos argumentos
    valor=float(valorIn)
    base=float(baseIn)
    try:
        porcentaje=round(valor/base*100,1)
    except:
        porcentaje=0
    return porcentaje

def mesLiteral(fechaIn):
    mes=''
    dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado','domingo']
    meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre',
             'noviembre', 'diciembre']
    if fechaIn=='ahora':
        fechaIn=datetime.now()
    if type(fechaIn).__name__=='date' or type(fechaIn).__name__=='datetime':
        fecha=fechaIn
    else:
        fecha=datetime.strptime(fechaIn, "%I:%M %p").time()
    mes=meses[fecha.month-1]
    return mes

def bolivares(valor):
    locale.setlocale(locale.LC_ALL, 'es_VE.utf8')
    try:
        valor=float(valor)
    except:
        valor=0
    valorFormateado = locale.format("%.0f", valor, grouping=True)
    #valorFormateado += ' Bs.'
    return valorFormateado

def fechaCortaPlus(fechaIn):
    dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
    if type(fechaIn).__name__=='date':
        fecha=fechaIn
    elif type(fechaIn).__name__=='datetime':
        fecha=fechaIn.date()
    else:
        fecha=datetime.strptime(fechaIn, "%I:%M %p").date()
    fechaFormateada=str(fecha.day)+'/'+str(fecha.month)+'/'+str(fecha.year)
    try:
        if fecha==datetime.now().date():
            fechaFormateada='Hoy'
        elif fecha==datetime.now().date() + timedelta(days=1):
            fechaFormateada='Manana'
        elif fecha==datetime.now().date() - timedelta(days=1):
            fechaFormateada='Ayer'
        else:
            dia = dias[fecha.weekday()][:3].capitalize()
            fechaFormateada=dia+', '+str(fecha.day)+' de '+ fechaIn.strftime('%B')[:3].capitalize()
    except:
        a=1
    return fechaFormateada

@register.filter(name='getkey')
def getkey(value, arg):
    return value[arg]

@register.simple_tag
def actualizar_variable(value):
    """Allows to update existing variable in template"""
    return value

def tupleToString(value):
    value = ''.join(value[0])
    return value

def tipoMedioPago(value):
    tipoIn = ['Transferencia', 'Deposito', 'POS', 'VPOS', 'Cheque', 'Efectivo', 'Por_Cobrar', 'BECA'][value]
    return tipoIn

def formatoPorcentaje(value):
    value=round(value)
    if value-int(value)>0:
        return locale.format("%.1f", value, grouping=True) + '%'
    else:
        return locale.format("%.0f", value, grouping=True) + '%'

def nbsp(value):
    return mark_safe("&nbsp;".join(value.split(' ')))

register.filter('update_variable', actualizar_variable)
register.filter('fechaLarga', fechaLarga)
register.filter('fechaMedioLarga', fechaMedioLarga)
register.filter('fechaCorta', fechaCorta)
register.filter('fechaCortaConHora', fechaCortaConHora)
register.filter('fechaNormal', fechaNormal)
register.filter('fechaEspecial', fechaEspecial)
register.filter('horaCivil', horaCivil)
register.filter('porcentajeValor', porcentajeValor)
register.filter('mesLiteral',mesLiteral)
register.filter('bolivares',bolivares)
register.filter('fechaCortaPlus', fechaCortaPlus)
register.filter('tupleToString', tupleToString)
register.filter('tipoMedioPago', tipoMedioPago)
register.filter('formatoPorcentaje', formatoPorcentaje)
register.filter('nbsp', nbsp)
register.filter('telefono', telefono)
register.filter('tiempo', tiempo)
register.filter('multiply',multiply)

