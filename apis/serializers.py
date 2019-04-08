# -*- coding: utf-8 -*-

from rest_framework import serializers
from web.models import *
from django.conf import settings

host=settings.DATABASES['default']['HOST']
host=settings.PUBLIC_HOST_IP

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'

class UserProfileSerializer(serializers.ModelSerializer):
    u_user=UserSerializer(many=False, read_only=True, required=False)
    u_alias=serializers.CharField(required=False)
    u_secondname=serializers.CharField(required=False)
    u_secondlastname=serializers.CharField(required=False)
    class Meta:
        model = UserProfile
        fields = '__all__'

class UserShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id','username','first_name','last_name')

class UserShortProfileSerializer(serializers.ModelSerializer):
    u_user = UserShortSerializer(many=False, read_only=True, required=False)
    class Meta:
        model = UserProfile
        fields = ('id', 'u_user', 'u_alias',)


class ActividadesSerializer(serializers.ModelSerializer):
    marca_nombre = serializers.ReadOnlyField(source='ac_marca.m_nombre')
    marca_alias = serializers.ReadOnlyField(source='ac_marca.m_alias')
    instructorAlias = serializers.ReadOnlyField(source='ac_instructor.u_alias')
    instructorNombre = serializers.ReadOnlyField(source='ac_instructor.full_name')
    disciplinaNombre = serializers.ReadOnlyField(source='ac_disciplina.d_nombre')
    disciplinaImagen = serializers.ReadOnlyField(source='ac_disciplina.d_imagen')
    salaNombre = serializers.ReadOnlyField(source='ac_salon.s_nombre')
    localidad=serializers.ReadOnlyField(source='ac_marca.m_municipio.z_municipio')
    class Meta:
        model = Actividad
        fields = (
            'id',
            'ac_nombre',
            'ac_fecha',
            'fechaActividadEpoch',
            'horaIniActividadEpoch',
            'horaFinActividadEpoch',
            'duracionActividadMinutos',
            'ac_hora_ini',
            'ac_hora_fin',
            'ac_estado',
            'ac_marca_id',
            'marca_nombre',
            'marca_alias',
            'salaNombre',
            'ac_instructor',
            'instructorAlias',
            'instructorNombre',
            'ac_disciplina',
            'disciplinaNombre',
            'disciplinaImagen',
            'localidad',
        )

class ActividadesDetailSerializer(serializers.ModelSerializer):
    marca_nombre = serializers.ReadOnlyField(source='ac_marca.m_nombre')
    marca_alias = serializers.ReadOnlyField(source='ac_marca.m_alias')
    disciplinaNombre = serializers.ReadOnlyField(source='ac_disciplina.d_nombre')
    disciplinaImagen = serializers.ReadOnlyField(source='ac_disciplina.d_imagen')
    salaNombre = serializers.ReadOnlyField(source='ac_salon.s_nombre')
    localidad=serializers.ReadOnlyField(source='ac_marca.m_municipio.z_municipio')
    class Meta:
        model = Actividad
        fields = (
            'id',
            'ac_nombre',
            'ac_fecha',
            'fechaActividadEpoch',
            'horaIniActividadEpoch',
            'horaFinActividadEpoch',
            'duracionActividadMinutos',
            'ac_hora_ini',
            'ac_hora_fin',
            'ac_descripcion',
            'ac_instrucciones',
            'ac_estado',
            'ac_marca_id',
            'marca_nombre',
            'marca_alias',
            'salaNombre',
            'ac_instructor',
            'ac_disciplina',
            'disciplinaNombre',
            'disciplinaImagen',
            'ac_referenciado',
            'localidad',
            'ac_imagenes',
        )