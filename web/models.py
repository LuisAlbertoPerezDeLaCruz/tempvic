# -*- coding: utf-8 -*-

from django.db import models
from django.conf import settings
from django.db.models import Count
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import signals
from django.core.validators import RegexValidator
from datetime import datetime, timedelta
from django.core.validators import MaxValueValidator, MinValueValidator
import os
import time
from unittest.util import _MAX_LENGTH
from django.contrib.postgres.fields import ArrayField

import logging

from numpy import unicode

log = logging.getLogger('vicLog')

class ProductoMarca(models.Model):
    p_nombre = models.CharField(max_length=100)
    p_precio = models.IntegerField()
    p_precio2 = models.IntegerField(default=0)
    p_precio3 = models.IntegerField(default=0)
    p_duracion_semanas = models.IntegerField()
    p_activo = models.BooleanField(default=True)
    p_historico = models.BooleanField(default=False)
    p_public = models.BooleanField(default=True)

    def __str__(self):
        return str(self.p_nombre)


class Marca(models.Model):
    CURRENCY_CHOICES = (
        ('$  ', '$'),
        ('Bs.', 'Bs.'),
        ('€  ', '€'),)
    TIPO_CUENTA_CHOICES=(
        ('N','Natural'),
        ('J','Juridica'),
    )
    m_nombre = models.CharField(max_length=200)
    m_alias = models.CharField(max_length=30)
    m_direccion = models.TextField(blank=True,null=True,default='')
    m_calle = models.TextField(default='',blank=True,null=True)
    m_urbanizacion = models.TextField(default='',blank=True,null=True)
    m_edificioCasa = models.TextField(default='',blank=True,null=True)
    m_ciudad = models.ForeignKey('Ciudad',blank=True,null=True,on_delete=models.CASCADE)
    m_municipio = models.ForeignKey('Zona',blank=True,null=True,on_delete=models.CASCADE)
    m_pais = models.ForeignKey('Pais',blank=True,null=True,on_delete=models.CASCADE)
    m_correo = models.EmailField(max_length=70, blank=True, default='victrois@gmail.com')
    m_telefono1 = models.CharField(max_length=30,default='',blank=True,null=True)
    m_telefono2 =  models.CharField(max_length=30,default='',blank=True,null=True)
    m_razon_social = models.CharField(max_length=150,default='',blank=True,null=True)
    m_doc_ident = models.CharField(max_length=30)
    m_descripcion = models.TextField(default='',blank=True,null=True)
    m_public = models.BooleanField(default=True)
    m_moneda = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='Bs.', )
    m_boletin = models.BooleanField(default=True)
    m_est_rrev = models.IntegerField(default=7)  # medido en dias
    m_est_irrev = models.IntegerField(default=120)  # medido en minutos
    m_planVictorius = models.ForeignKey('PlanVictorius', default='Core',on_delete=models.CASCADE)
    m_instructoresContratados = models.IntegerField(default=1)
    m_redSocial_Facebook = models.CharField(max_length=100,blank=True,null=True, default='')
    m_redSocial_Twitter = models.CharField(max_length=100,blank=True,null=True, default='')
    m_redSocial_Instagram = models.CharField(max_length=100,blank=True,null=True, default='')
    m_created_at = models.DateTimeField(default=datetime.now, blank=True)
    m_iniciales = models.CharField(max_length=3,blank=True,null=True, default='')
    m_porcentaje_aviso_cupos_restantes=models.IntegerField(default=80)
    m_permite_referenciados=models.BooleanField(default=False)
    m_tipoCuenta= models.CharField(max_length=1, choices=TIPO_CUENTA_CHOICES, default='J',)
    m_displinafav1 = models.ForeignKey('Disciplina', related_name='mfav1', blank=True, null=True, default=None,on_delete=models.CASCADE)
    m_displinafav2 = models.ForeignKey('Disciplina', related_name='mfav2', blank=True, null=True, default=None,on_delete=models.CASCADE)
    m_displinafav3 = models.ForeignKey('Disciplina', related_name='mfav3', blank=True, null=True, default=None,on_delete=models.CASCADE)

    def _get_full_dir(self):
        "Devuelve la direccion completa."
        if self.m_ciudad:
            ciudad=self.m_ciudad
        else:
            ciudad=''
        if self.m_municipio:
            municipio=self.m_municipio
        else:
            municipio=''
        if self.m_pais:
            pais=self.m_pais
        else:
            pais=''
        dir=''
        if self.m_calle:
           dir+=self.m_calle + ' '
        if self.m_edificioCasa:
            dir+=self.m_edificioCasa + ' '
        if self.m_urbanizacion:
            dir += self.m_urbanizacion + ', '
        if self.m_municipio:
            dir+=self.m_municipio.z_municipio + ', '
        if self.m_ciudad:
            dir+=self.m_ciudad.c_nombre + ', '
        if self.m_pais:
            dir+=self.m_pais.p_nombre + ' '

        return dir

        # return '%s %s, %s, %s, %s, %s' % (
        # self.m_calle, self.m_edificioCasa, self.m_urbanizacion, self.m_municipio, self.m_ciudad, self.m_pais)

    full_dir = property(_get_full_dir)

    def __str__(self):
        return str(self.m_nombre)

    def _get_ruta_avatar(self):
        "Devuelve la ruta de la carpeta de imagenes"
        if settings.AMBIENTE=='DESARROLLO':
            url = settings.MEDIA_URL+'avatars'
        else:
            url = '/static'+settings.MEDIA_URL+'avatars'
        temp = '%s/%s.png' % (url, self.m_alias)
        return temp

    full_ruta_avatar = property(_get_ruta_avatar)

class Pais(models.Model):
    p_nombre = models.CharField(primary_key=True, max_length=30)
    p_alias = models.CharField(max_length=30, default='')

    def __str__(self):
        return str(self.p_nombre)


class Ciudad(models.Model):
    c_pais = models.ForeignKey('Pais', default='Venezuela',on_delete=models.CASCADE)
    c_nombre = models.CharField(primary_key=True, max_length=30)

    def __str__(self):
        return str(self.c_nombre)


class Zona(models.Model):
    z_ciudad = models.ForeignKey('Ciudad',on_delete=models.CASCADE)
    z_municipio = models.CharField(primary_key=True, max_length=30)

    def __str__(self):
        return str(self.z_municipio)


class EstadoActividad(models.Model):

    ESTADOS_CHOICES = (
        ('Planifico', 'Planifico'),
        ('Abierta Reversible', 'Abierta Reversible'),
        ('Abierta Irreversible', 'Abierta Irreversible'),
        ('Activa', 'Activa'),
        ('Culminada', 'Culminada'),
        ('Cancelada', 'Cancelada'),
        ('En Conflicto', 'En Conflicto'),
    )

    ea_estado = models.CharField(max_length=20, primary_key=True, choices=ESTADOS_CHOICES, default='Planifico', )
    ea_imagen = models.CharField(max_length=100, default='', null=True, blank=True)

    def __str__(self):
        return unicode(self.ea_estado)


class Actividad(models.Model):
    ESTADOS_CHOICES = (
        ('Planifico', 'Planifico'),
        ('Abierta Reversible', 'Abierta Reversible'),
        ('Abierta Irreversible', 'Abierta Irreversible'),
        ('Activa', 'Activa'),
        ('Culminada', 'Culminada'),
        ('Cancelada', 'Cancelada'),
        ('En Conflicto', 'En Conflicto')),
    tipoRepeticiones = (
        ('LM', 'Lunes, Miercoles y Viernes'),
        ('MJ', 'Martes y Jueves'),
        ('LV', 'Lunes a Viernes'),
        ('DI', 'Diario'),
        ('SM', 'Semanal'),)
    ac_nombre = models.CharField(max_length=200)
    ac_disciplina = models.ForeignKey('Disciplina',on_delete=models.CASCADE)
    ac_fecha = models.DateField()
    ac_estado = models.ForeignKey('EstadoActividad', default='', null=True, blank=True,on_delete=models.CASCADE)
    ac_hora_ini = models.TimeField()
    ac_hora_fin = models.TimeField()
    ac_salon = models.ForeignKey('Salon', default=0, null=True, blank=True,on_delete=models.CASCADE)
    ac_marca = models.ForeignKey('Marca',on_delete=models.CASCADE)
    ac_instructor = models.ForeignKey('UserProfile', default=0, null=True, blank=True,on_delete=models.CASCADE)
    ac_colaborador1 = models.IntegerField(default=0, null=True, blank=True)
    ac_colaborador2 = models.IntegerField(default=0, null=True, blank=True)
    ac_descripcion = models.TextField()
    ac_cap_min = models.IntegerField(default=0)
    ac_cap_max = models.IntegerField(default=100)
    ac_requisitos = models.TextField()
    ac_cupos_reservados = models.IntegerField(default=0)
    ac_cap_max_espera = models.IntegerField(default=100)
    ac_cupos_en_espera = models.IntegerField(default=0)
    ac_precio = models.FloatField(default=1)
    ac_bono = models.FloatField(default=0)
    ac_creditos = models.IntegerField(default=1)
    ac_intensidad = models.IntegerField(default=1)
    ac_instrucciones = models.TextField(default='')
    ac_actividadBaseSerieId = models.IntegerField(default=0, null=True, blank=True)
    ac_OpcionSerie = models.CharField(max_length=2, default='No', null=True, blank=True)
    ac_nunca = models.CharField(max_length=2, default='No', null=True, blank=True)
    ac_repetirComo = models.CharField(max_length=2, choices=tipoRepeticiones, default='No', null=True, blank=True)
    ac_patron_repeticion_semanal = models.CharField(max_length=14, default='', null=True, blank=True)
    ac_despd = models.CharField(max_length=2, default='No', null=True, blank=True)
    ac_do = models.IntegerField(default=0, null=True, blank=True)
    ac_enf = models.CharField(max_length=2, default='No', null=True, blank=True)
    ac_fdesp = models.DateField(default=datetime.now(), null=True, blank=True)
    ac_productos_permitidos = ArrayField(
        models.IntegerField(default={}),
        size=10,
        null=True,
    )
    ac_referenciado=models.BooleanField(default=False)
    ac_imagenes=ArrayField(
        models.CharField(max_length=200),
        blank=True,
        default=list,
    )
    ac_serieId_originaria=models.IntegerField(null=True, blank=True,default=0)
    def __str__(self):
        return unicode(self.ac_nombre + ', id=' + str(self.id))

    def _get_fechaConHora(self):
        "Devuelve el fecha con hora de la actividad"
        fechaHora = datetime(self.ac_fecha.year, self.ac_fecha.month, self.ac_fecha.day, self.ac_hora_ini.hour,
                             self.ac_hora_ini.minute)
        return fechaHora

    fechaHoraActividad = property(_get_fechaConHora)

    def _get_fechaEpoch(self):
        epoch = int(self.ac_fecha.strftime('%s'))
        return epoch

    fechaActividadEpoch = property(_get_fechaEpoch)

    def _get_hora_ini_Epoch(self):
        fechaHoraIni = datetime.combine(self.ac_fecha, self.ac_hora_ini)
        epoch = int(fechaHoraIni.strftime('%s'))
        return epoch

    horaIniActividadEpoch = property(_get_hora_ini_Epoch)

    def _get_hora_fin_Epoch(self):
        fechaHoraFin = datetime.combine(self.ac_fecha, self.ac_hora_fin)
        epoch = int(fechaHoraFin.strftime('%s'))
        return epoch

    horaFinActividadEpoch = property(_get_hora_fin_Epoch)

    def _get_Duracion(self):
        fechaHoraIni = datetime.combine(self.ac_fecha, self.ac_hora_ini)
        epochIni = int(fechaHoraIni.strftime('%s'))
        fechaHoraFin = datetime.combine(self.ac_fecha, self.ac_hora_fin)
        epochFin = int(fechaHoraFin.strftime('%s'))
        duracion = int((epochFin - epochIni) / 60)
        return duracion

    duracionActividadMinutos = property(_get_Duracion)


class Serie(models.Model):
    tipos = (
        ('LM', 'Lunes, Miercoles y Viernes'),
        ('MJ', 'Martes y Jueves'),
        ('LV', 'Lunes a Viernes'),
        ('DI', 'Diario'),
        ('SM', 'Semanal'),)
    fin = (
        ('D', 'Terminar en la fecha'),
        ('R', 'Despues de'),)
    s_actividad = models.ForeignKey('Actividad', on_delete=models.CASCADE)
    s_num_ser = models.CharField(max_length=50)
    s_tipo = models.CharField(max_length=2, choices=tipos)
    s_cada = models.IntegerField(default=0)
    s_lunes = models.BooleanField(default=False)
    s_martes = models.BooleanField(default=False)
    s_miercoles = models.BooleanField(default=False)
    s_jueves = models.BooleanField(default=False)
    s_viernes = models.BooleanField(default=False)
    s_sabado = models.BooleanField(default=False)
    s_domingo = models.BooleanField(default=False)
    s_empieza = models.DateField(default=datetime.now())
    s_termina = models.CharField(max_length=1, choices=fin)
    s_termina_date = models.DateField(default=datetime.now())
    s_termina_int = models.IntegerField(default=20)

    def __str__(self):
        return str(self.s_num_ser + " - " + str(self.s_actividad))


class Ayudante(models.Model):
    ay_actividad = models.ForeignKey('Actividad', on_delete=models.CASCADE)
    ay_entrenador = models.ForeignKey('auth.User',on_delete=models.CASCADE)

    def __str__(self):
        return str(self.ay_entrenador)


class Participantes(models.Model):
    pa_actividad = models.ForeignKey('Actividad', on_delete=models.CASCADE)
    pa_usuario = models.ForeignKey('auth.User',on_delete=models.CASCADE)
    pa_num_cupo = models.IntegerField()
    pa_asistencia = models.BooleanField(default=False)
    pa_cobrado = models.BooleanField(default=False)
    pa_plan = models.ForeignKey('Planes',on_delete=models.CASCADE)

    class Meta:
        unique_together = ["pa_actividad", "pa_usuario"]

    def __str__(self):
        return str(self.pa_actividad.ac_nombre + " - " + self.pa_usuario.username)


class Espera(models.Model):
    es_actividad = models.ForeignKey('Actividad', on_delete=models.CASCADE)
    es_usuario = models.ForeignKey('auth.User',on_delete=models.CASCADE)
    es_num_cupo = models.IntegerField()
    es_plan = models.ForeignKey('Planes',on_delete=models.CASCADE)

    class Meta:
        unique_together = ["es_actividad", "es_usuario"]

    def __str__(self):
        return str(self.es_actividad.ac_nombre + " - " + self.es_usuario.username)


class Disciplina(models.Model):
    d_nombre = models.CharField(max_length=100)
    d_imagen = models.CharField(max_length=100, default='', null=True, blank=True)
    d_imagen_negra = models.CharField(max_length=100, default='', null=True, blank=True)

    def __str__(self):
        return str(self.d_nombre)


class Salon(models.Model):
    s_nombre = models.CharField(max_length=100)
    s_capacidad = models.IntegerField()
    s_marca = models.ForeignKey('Marca', default=0,on_delete=models.CASCADE)
    s_disciplina = models.ForeignKey('Disciplina', default=0, null=True, blank=True,on_delete=models.CASCADE)
    s_overflow = models.IntegerField(default=0)
    s_referenciado=models.BooleanField(default=False)

    def __str__(self):
        return str(self.s_nombre.encode('utf-8'))


class Producto(models.Model):
    CURRENCY_CHOICES = (
        ('$  ', '$'),
        ('Bs.', 'Bs.'),
        ('€  ', '€'),)
    TIPO_PRODUCTO_CHOICES = (
        (0, 'POR CREDITOS'),
        (1, 'MENSUAL ILIMITADO'),
        (2, 'MENSUAL LIMITADO'),
        (3, 'REFERENCIADO'),
    )
    p_nombre = models.CharField(max_length=100)
    p_descripcion = models.TextField(default='')
    p_precio = models.IntegerField(null=True,default=0)
    p_precio2 = models.IntegerField(null=True,default=0)
    p_precio3 = models.IntegerField(null=True,default=0)
    p_creditos = models.IntegerField()
    p_moneda = models.CharField(max_length=3, choices=CURRENCY_CHOICES, default='Bs.', )
    p_duracion_meses = models.IntegerField()
    p_creacion = models.DateTimeField(auto_now_add=True, blank=True)
    p_activo = models.BooleanField(default=True)
    p_historico = models.BooleanField(default=False)
    p_descuento = models.IntegerField(null=True,default=0,validators=[MaxValueValidator(100), MinValueValidator(0)])
    p_marca = models.ForeignKey('Marca',on_delete=models.CASCADE)
    p_tipo = models.IntegerField(default=0, choices=TIPO_PRODUCTO_CHOICES)
    p_disciplinas = ArrayField(
        models.IntegerField(default={}),
        size=10,
        null=True,
    )
    p_creditos_mensual= models.IntegerField(default=0)


class Planes(models.Model):
    p_creditos_usados = models.IntegerField(default=0)
    p_creditos_totales = models.IntegerField()
    p_fecha_obtencion = models.DateTimeField()
    p_fecha_caducidad = models.DateTimeField()
    p_tipo = models.IntegerField(default=0)
    p_historico = models.BooleanField(default=False)
    p_marca = models.ForeignKey('Marca',on_delete=models.CASCADE)
    p_usuario = models.ForeignKey('auth.User',on_delete=models.CASCADE)
    p_nombre = models.CharField(max_length=100, default="")
    p_producto = models.ForeignKey('Producto', null=True,on_delete=models.CASCADE)
    p_creditos_totales_plan_mensual= models.IntegerField(default=0)
    p_creditos_usados_plan_mensual= models.IntegerField(default=0)
    def __str__(self):
        return str(self.p_usuario.username) + " - " + str(self.p_creditos_usados) + " / " + str(
            self.p_creditos_totales) + "  \t  -->" + str(self.p_fecha_caducidad)


class UserProfile(models.Model):
    GENERO_CHOICES = (
        ('0', 'Sin Indicar'),
        ('1', 'Masculino'),
        ('2', 'Femenino'),)
    u_user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name="profile")
    u_secondname = models.CharField(max_length=30)
    u_secondlastname = models.CharField(max_length=30)
    u_telefono = models.CharField(max_length=30,default='',blank=True,null=True)
    u_alias = models.CharField(max_length=100)
    u_direccion = models.TextField(null=True, blank=True, default = '')
    u_calle = models.TextField(null=True, blank=True, default = '')
    u_urbanizacion = models.TextField(null=True, blank=True, default = '')
    u_edificioCasa = models.TextField(null=True, blank=True, default = '')
    u_ciudad = models.ForeignKey('Ciudad', null=True, blank=True, default = None,on_delete=models.CASCADE)
    u_municipio = models.ForeignKey('Zona', null=True, blank=True, default = None,on_delete=models.CASCADE)
    u_pais = models.ForeignKey('Pais', null=True, blank=True, default = None,on_delete=models.CASCADE)
    u_fecha_nac = models.DateField(default=datetime.now, blank=True)
    u_entrenador = models.BooleanField(default=False)
    u_marca = models.BooleanField(default=False)
    u_displinafav1 = models.ForeignKey('Disciplina', related_name='fav1', blank=True, null=True, default=0,on_delete=models.CASCADE)
    u_displinafav2 = models.ForeignKey('Disciplina', related_name='fav2', blank=True, null=True, default=0,on_delete=models.CASCADE)
    u_displinafav3 = models.ForeignKey('Disciplina', related_name='fav3', blank=True, null=True, default=0,on_delete=models.CASCADE)
    u_objetivos = models.TextField(default='')
    u_created_at = models.DateTimeField(default=datetime.now, blank=True)
    u_ultima_sesion_tipo = models.IntegerField(default=0, null=True)
    u_ultima_marca_en_uso = models.IntegerField(default=0, null=True)
    u_iniciales = models.CharField(max_length=3, default='')
    u_entrenador_profile=models.TextField(null=True,blank=True,default='')
    u_genero = models.CharField(choices=GENERO_CHOICES,max_length=1,default='0')
    u_public = models.BooleanField(default=True)
    u_registrado = models.BooleanField(default=True)
    u_puede_registrar_marca=models.BooleanField(default=False)
    u_cantidad_marcas_permitidas=models.IntegerField(default=1)

    def _get_full_dir(self):
        "Devuelve la direccion completa."

        try:
            temp = '%s %s, %s, %s, %s, %s' % (
            self.u_calle, self.u_edificioCasa, self.u_urbanizacion, self.u_municipio, self.u_ciudad, self.u_pais)
        except:
            temp = '%s %s, %s' % (
                self.u_calle, self.u_edificioCasa, self.u_urbanizacion)
        return temp

    def _get_full_name(self):
        "Devuelve el nombre completo"
        temp= '%s %s' % (self.u_user.first_name,self.u_user.last_name)
        return temp

    full_name = property(_get_full_name)
    full_dir = property(_get_full_dir)

    def __str__(self):
        return str(self.u_user)

    def get_User(self, Users):
        if Users == None:
            return None
        else:
            up = []
            for User in Users:
                up.append(UserProfile.objects.get(u_user__pk=User))
            return up

    def _get_ruta_avatar(self):
        "Devuelve la ruta de la carpeta de imagenes"
        if settings.AMBIENTE=='DESARROLLO':
            url = settings.MEDIA_URL+'avatars'
        else:
            url = '/static'+settings.MEDIA_URL+'avatars'
        temp = '%s/%s.png' % (url, self.u_alias)
        #log.info('full_ruta_avatar:'+temp)
        return temp

    full_ruta_avatar = property(_get_ruta_avatar)


class Relacion(models.Model):
    SOLICITUDES_CHOICES = (
        ('A', 'Aprobada'),
        ('R', 'Rechazada'),
        ('P', 'Pendiente'),)
    r_user = models.ForeignKey('auth.User',on_delete=models.CASCADE)
    r_marca = models.ForeignKey('Marca',on_delete=models.CASCADE)
    r_estado = models.CharField(max_length=1, choices=SOLICITUDES_CHOICES, default='P', )
    r_entrenador = models.BooleanField(default=False)

    def __str__(self):
        return str(self.r_marca)


class Amistad(models.Model):
    SOLICITUDES_CHOICES = (
        ('A', 'Aprobada'),
        ('R', 'Rechazada'),
        ('P', 'Pendiente'),)
    a_solicitante = models.ForeignKey('auth.User', related_name='Solicitante',on_delete=models.CASCADE)
    a_receptor = models.ForeignKey('auth.User', related_name='Receptor',on_delete=models.CASCADE)
    a_estado = models.CharField(max_length=1, choices=SOLICITUDES_CHOICES, default='P', )

    def __str__(self):
        return str(self.a_solicitante) + " - " + str(self.a_receptor)


class Dueno(models.Model):
    d_user = models.ForeignKey('auth.User',on_delete=models.CASCADE)
    d_marca = models.ForeignKey('Marca',on_delete=models.CASCADE)

    def __str__(self):
        return str(self.d_user) + " " + str(self.d_marca)


class Saldo(models.Model):
    s_user = models.ForeignKey('auth.User',on_delete=models.CASCADE)
    s_marca = models.ForeignKey('Marca',on_delete=models.CASCADE)
    s_saldo = models.IntegerField(default=0)
    s_bloqueado = models.IntegerField(default=0)

    class Meta:
        unique_together = ("s_user", "s_marca")

    def __str__(self):
        return str(self.s_user) + " " + str(self.s_marca)


class Pago(models.Model):
    MEDIO_CHOICES=(
        (0,'TRANSFERENCIA'),
        (1,'DEPOSITO'),
        (2,'POS'),
        (3,'VPOS'),
        (4,'CHEQUE'),
        (5,'EFECTIVO'),
        (6,'POR_COBRAR'),
        (7,'BECA'),
    )
    STATUS_CHOICES=(
        (0,'Por Conciliar'),
        (1, 'Conciliado'),
        (2,'No Conciliado'),
        (3,'Pendiente de Pago'),
    )
    p_pagador = models.ForeignKey('auth.User',on_delete=models.CASCADE)
    p_marca = models.ForeignKey('Marca',on_delete=models.CASCADE)
    p_plan = models.ForeignKey('Planes',on_delete=models.CASCADE)
    p_producto = models.ForeignKey('Producto',on_delete=models.CASCADE)
    p_fecha_registro = models.DateTimeField(default=datetime.now, blank=True)
    p_fecha_transaccion = models.DateTimeField(default=datetime.now, blank=True)
    p_fecha_Conciliacion = models.DateTimeField(default=datetime.now, blank=True)
    p_medio = models.IntegerField(choices=MEDIO_CHOICES,default=0)
    p_status = models.IntegerField(choices=STATUS_CHOICES,default=0)
    p_referencia = models.BigIntegerField(null=True)
    p_referencia_uso = models.BigIntegerField(default=0)
    p_monto = models.FloatField()
    p_precio = models.FloatField(default=0)
    p_dtoGeneral = models.FloatField(default=0)
    p_dtoParticular = models.FloatField(default=0)
    p_diferencia = models.FloatField(default=0)
    p_cuenta = models.ForeignKey('Cuenta', null=True, blank=True, on_delete=models.CASCADE)
    p_porcobrar = models.BooleanField(default=True)
    p_codigoInterno = models.CharField(max_length=20, default='')

    def __str__(self):
        return str(self.id) + " - " + str(self.p_pagador.username)


class Cuenta(models.Model):
    c_marca = models.ForeignKey('Marca',on_delete=models.CASCADE)
    c_status = models.BooleanField()
    c_banco = models.CharField(max_length=50)
    c_numero_cuenta = models.CharField(max_length=20)

    def __str__(self):
        return str(self.c_banco) + " - " + str(self.c_marca.m_nombre)


class ProfileImage(models.Model):
    image = models.FileField(upload_to='profile/%Y/%m/%d')


class Token(models.Model):
    u_user = models.OneToOneField('auth.User', on_delete=models.CASCADE, related_name="token")
    u_token = models.CharField(max_length=100)
    u_data = models.BooleanField(default=False)


class PlanVictorius(models.Model):
    p_nombrePlan = models.CharField(primary_key=True, max_length=30)

    def __str__(self):
        return str(self.p_nombrePlan)

class TransactionLog(models.Model):
    OPCIONES_CHOICES = (
        ('RA', 'Reserva de Actividad'),
        ('CR', 'Cancelacion de Reserva'),
        ('EE', 'Entrada en Lista de Espera'),
        ('SE', 'Salida de Lista de Espera'),
        ('PE', 'Promocion desde Lista de Espera'),
        ('SA', 'Suspension de Actividad',),
        ('CP', 'Compra de Plan'),
        ('RS', 'Reintegro Por Suspension'),
        ('RX', 'Reintegro Por No Participacion'),
        ('IP', 'Inactivacion de Plan'),)
    tl_fecha = models.DateTimeField(auto_now_add=True, blank=True)
    tl_usuario = models.ForeignKey('auth.User',on_delete=models.CASCADE)
    tl_marca = models.ForeignKey('Marca',on_delete=models.CASCADE)
    tl_accion = models.CharField(max_length=2, choices=OPCIONES_CHOICES)
    tl_descripcion = models.CharField(max_length=50)
    tl_usuarioEjecutor = models.CharField(max_length=50, null=True)
    tl_actividad = models.ForeignKey('Actividad', default=None, null=True,on_delete=models.CASCADE)
    tl_creditos = models.IntegerField(default=0)
    tl_plan_accionado = models.ForeignKey('Planes', default=None, null=True,on_delete=models.CASCADE)


class TipoNotificacion(models.Model):
    TIPO_CHOICES = (
        ('IA', 'Invitacion Afiliacion'),
        ('SA', 'Solicitud Afiliacion'),
        ('CA','Cancelacion Actividad'),
        ('RL', 'Reservado desde Lista de espera'),
        ('MI','Marca Informa a Atleta'),
        ('AI', 'Atleta Informa a Marca'),
        ('AA', 'Atleta Informa a Atleta'),
        ('RP', 'Registro de Plan'),
        ('VP', 'Vencimiento de Plan'),
        ('RR', 'Registro de Reservación'),
        ('BM', 'Broadcast Marca'),
    )
    tn_tipo=models.CharField(max_length=2, choices=TIPO_CHOICES)
    tn_descripcion=models.CharField(max_length=255)
    tn_requiere_accion=models.BooleanField()
    tn_texto_base=models.CharField(max_length=255)


class Notificacion(models.Model):
    ESTADO_CHOICES = (
        ('P', 'Pendiente'),
        ('V', ''),
        ('G','Gestionada'),
    )
    nt_tipo=models.ForeignKey('TipoNotificacion',on_delete=models.CASCADE)
    nt_fecha=models.DateTimeField(auto_now_add=True)
    nt_texto=models.CharField(max_length=255)


class AccionesNotificacion(models.Model):
    an_tipo_notificacion=models.ForeignKey('TipoNotificacion',on_delete=models.CASCADE)
    an_ruta_funciones=models.CharField(max_length=255)
    an_funcion_aceptar=models.CharField(max_length=255)
    an_funcion_rechazar=models.CharField(max_length=255)
    an_callback_aceptar=models.CharField(max_length=255)
    an_callback_rechazar=models.CharField(max_length=255)


class Usuario_Notificacion(models.Model):
    ESTADO_CHOICES = (
        ('C','Creada'),
        ('A', 'Aceptada'),
        ('R', 'Rechazada'),
        ('V', ''),
    )
    un_usuario=  models.ForeignKey('auth.User',on_delete=models.CASCADE)
    un_marca = models.ForeignKey('Marca', blank=True, null=True,on_delete=models.CASCADE)
    un_amigo = models.ForeignKey('Userprofile', blank=True, null=True,on_delete=models.CASCADE)
    un_notificacion=models.ForeignKey('Notificacion',on_delete=models.CASCADE)
    un_estado=models.CharField(max_length=2, choices=ESTADO_CHOICES)
    un_parametros=models.CharField(max_length=255, blank=True, null=True)


class Marca_Notificacion(models.Model):
    ESTADO_CHOICES = (
        ('C','Creada'),
        ('A', 'Aceptada'),
        ('R', 'Rechazada'),
        ('V', ''),
    )
    mn_usuario=  models.ForeignKey('auth.User', blank=True, null=True,on_delete=models.CASCADE)
    mn_marca = models.ForeignKey('Marca',on_delete=models.CASCADE)
    mn_notificacion=models.ForeignKey('Notificacion',on_delete=models.CASCADE)
    mn_estado=models.CharField(max_length=2, choices=ESTADO_CHOICES)
    mn_parametros=models.CharField(max_length=255, blank=True, null=True)


class Prospect(models.Model):
    TIPO_CHOICES = (
        ('M','Marca'),
        ('A', 'Atleta'),
    )
    pr_created_at = models.DateTimeField(default=datetime.now, blank=True)
    pr_tipo = models.CharField(max_length=1,blank=True, choices=TIPO_CHOICES,default='')
    pr_nombre = models.CharField(max_length=30, blank=True, default='')
    pr_apellido = models.CharField(max_length=30, blank=True, default='')
    pr_correo = models.EmailField(max_length=70, blank=True, default='')
    pr_aspiraciones = models.TextField(blank=True,null=True,default='')
    pr_centros_frecuentados = models.TextField(blank=True,null=True,default='')
    pr_ubicacion_negocio = models.TextField(blank=True,null=True,default='')
    pr_nombre_negocio = models.CharField(max_length=30, blank=True, default='')
    pr_descripcion_negocio = models.TextField(blank=True, null=True, default='')
    def __str__(self):
        return str(self.pr_correo)
