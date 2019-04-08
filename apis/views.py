# -*- coding: utf-8 -*-

from rest_framework.views import APIView
from rest_framework import status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from  .serializers import *
from web.clases import *
import datetime
import requests

import rest_framework.permissions as drf_perm

import logging

class HelloView(APIView):
    permission_classes = (drf_perm.IsAuthenticated,)

    def get(self, request):
        content = {'message': 'Hello, ('+ request._user.first_name +')!'}
        return Response(content)


class VictoriusApi(APIView):
    def get(self, request):
        """*Devuelve la lista de funciones"""
        lista_funciones=[
            "/apis/lista/ :Muestra esta información (Metodo GET)",
            "/apis/actividades/ :Devuelve lista completa de todas las actividades (Metodo GET)",
            "/apis/actividades/userid/ :Devuelve las actividades donde el usuario esta afiliado (Metodo GET)",
            "/apis/actividades/useralias/ :Devuelve las actividades donde el usuario esta afiliado (Metodo GET)",
            "/apis/detalle-actividad/userId/ :Devuelve el detalle completo de la actividad (Metodo GET)",
            "/apis/detalle-actividad/useralias/ :Devuelve el detalle completo de la actividad (Metodo GET)",
            "/apis/esperas/userid/ :Devuelve las actividades donde el usuario esta en lista de espera (Metodo GET)",
            "/apis/esperas/useralias/ :Devuelve las actividades donde el usuario esta en lista de espera (Metodo GET)",
            "/apis/reservas/userid/ :Devuelve las actividades donde el usuario esta reservado (Metodo GET)",
            "/apis/reservas/useralias/ :Devuelve las actividades donde el usuario esta reservado (Metodo GET)",
            "/apis/profiles/ :*Devuelve lista completa de usuarios registrados (Metodo GET)",
            "/apis/profiles/userid/ :Devuelve el detalle completo del usuario (Metodo GET)",
            "/apis/profiles/useralias/ :Devuelve el detalle completo del usuario (Metodo GET)",
            "/apis/profiles/userId/ :Actualiza el campo de UserProfile (Metodo PUT) requiere {key:val} en body",
            "/apis/profiles/userlias/ :Actualiza el campo de UserProfile (Metodo PUT) requiere {key:val} en body",
        ]
        return Response({'mensaje':"Victorius API","funciones":lista_funciones})

class ProfilesApiView(APIView):
    def get(self, request):
        """*Devuelve lista completa de usuarios registrados"""
        profile = UserProfile.objects.all()
        data = UserShortProfileSerializer(profile, many=True).data
        return Response(data, status.HTTP_200_OK)


def get_profile(pk):
    try:
        pk = int(pk)
    except:
        pass
    if type(pk) is int:
        profile = get_object_or_404(UserProfile, pk=pk)
    elif type(pk) is str:
        profile = get_object_or_404(UserProfile, u_alias=pk)
    elif type(pk) is unicode:
        profile = get_object_or_404(UserProfile, u_alias=pk)
    else:
        profile = get_object_or_404(UserProfile, u_alias=pk)
    return profile

class ProfileDetailApiView(APIView):
    def get(self, request, pk):
        """*Devuelve el detalle completo del usuario (acepta userid o useralias)"""
        profile=get_profile(pk)
        data = UserProfileSerializer(profile).data
        return Response(data, status.HTTP_200_OK)

    def put(self, request,pk):
        '''
            *Actualiza el campo de UserProfile (acepta userid o useralias)
            /apis/profiles/id
            {'key':val}

        '''

        serializer = UserProfileSerializer(data=request.data)
        if serializer.is_valid():
            profile=UserProfile.objects.filter(pk=pk)
            profile.update(**serializer.initial_data)
        data = UserProfileSerializer(profile).data
        return Response(data, status.HTTP_200_OK)

class ActividadesTodasView(APIView):
    def get(self,request):
        """*Devuelve lista completa de actividades"""
        actividades = Actividad.objects.all().order_by('id')
        data = ActividadesSerializer(actividades, many=True).data
        for i in range(0,len(data)):
            imagen=data[i]['disciplinaImagen'].replace('..',host)
            data[i]['disciplinaImagen'] = 'https://'+imagen

        return Response(data, status.HTTP_200_OK)

class ActividadesAfiliacionView(APIView):
    permission_classes = (drf_perm.IsAuthenticated,)
    # log = logging.getLogger('vicLog')
    # tempLog = []
    def get(self, request):
        # self.tempLog.append('entre en ActividadesAfiliacionView(), --> ' + str(datetime.datetime.now().minute) + ':' + str(
        #     datetime.datetime.now().second))
        pk = request._user.pk
        """*Devuelve lista de actividades donde el usuario esta afiliado"""
        if 'fecha' in request.POST:
            f = request.POST['fecha']
            try:
                fecha = datetime.datetime.strptime(f, "%d/%m/%Y").date()
            except:
                return Response('fecha invalida', status.HTTP_400_BAD_REQUEST)
        else:
            fecha = None

        profile = get_profile(pk)
        afiliaciones = Relacion.objects.filter(r_user=profile.u_user, r_estado='A').values_list('r_marca_id', flat=True)
        localidadesAfiliadas = []
        sinMunicipioNulo = True

        for marcaId in afiliaciones:
            pm = PerfilMarca(Marca.objects.get(pk=marcaId).m_alias)
            if pm.marcaLocalidad == '':
                sinMunicipioNulo = False
            localidadesAfiliadas.append(pm.marcaLocalidad)

        if 'centros' in request.POST:
            try:
                centros=request.POST['centros'].split(',')
                centros = [x.replace("'", "") for x in centros]
                centros = [int(x) for x in centros]
            except:
                return Response('Parametros invalidos', status.HTTP_400_BAD_REQUEST)
        else:
            centros = afiliaciones

        if 'localidades' in request.POST:
            localidades = request.POST['localidades'].split(',')
            localidades = [x.replace("'", "") for x in localidades]
        else:
            localidades = localidadesAfiliadas

        reservas=Participantes.objects.filter(pa_usuario=pk).values_list('pa_actividad_id',flat=True)
        esperas = Espera.objects.filter(es_usuario=pk).values_list('es_actividad_id', flat=True)

        if fecha:
             actividades = Actividad.objects.filter(ac_marca_id__in=centros, ac_estado__in=TipoEstatus().tipoTodasFuturas,ac_fecha=fecha).order_by('ac_fecha', 'ac_hora_ini')
        else:
            actividades = Actividad.objects.filter(ac_marca_id__in=centros,ac_estado__in=TipoEstatus().tipoTodasFuturas).order_by('ac_fecha','ac_hora_ini')

        # self.tempLog.append('entre en ActividadesSerializer(), --> ' + str(datetime.datetime.now().minute) + ':' + str(
        #     datetime.datetime.now().second))

        data = ActividadesSerializer(actividades, many=True).data

        # self.tempLog.append('sali de ActividadesSerializer(), --> ' + str(datetime.datetime.now().minute) + ':' + str(
        #     datetime.datetime.now().second))

        if settings.AMBIENTE == 'DESARROLLO':
            urlMarca = 'http://'+host+'/static/media/avatars/'
            urlMarcaPlaceHolder = 'http://' + host + '/static/media/avatars/marcaPlaceHolder.png'
            urlInstructorPlaceHolder = 'http://' + host + '/static/media/avatars/instructorPlaceHolder.png'
            urlInstructor = 'http://' + host + '/static/media/avatars/'
        else:
            urlMarca = 'https://'+host+'/static/media/avatars/'
            urlMarcaPlaceHolder = 'https://' + host + '/static/media/avatars/marcaPlaceHolder.png'
            urlInstructorPlaceHolder = 'https://' + host + '/static/media/avatars/instructorPlaceHolder.png'
            urlInstructor = 'https://' + host + '/static/media/avatars/'

        marcasImg = {}
        instructoresImg = {}

        for i in range(0, len(data)):
            imagen=data[i]['disciplinaImagen'].replace('..', host)
            data[i]['disciplinaImagen'] = 'https://'+imagen
            actividadId = data[i]['id']
            data[i]['atletaReservado'] = actividadId in reservas
            data[i]['atletaListEspera'] = actividadId in esperas

            if data[i]['marca_alias'] not in marcasImg:
                tempImg = urlMarca + data[i]['marca_alias']+'.png'
                r = requests.get(tempImg)
                if r.status_code == 200:
                    marcasImg[data[i]['marca_alias']] = tempImg
                else:
                   marcasImg[data[i]['marca_alias']] = urlMarcaPlaceHolder

            data[i]['marcaImagenUrl'] = marcasImg[data[i]['marca_alias']]

            if data[i]['instructorAlias'] not in instructoresImg:
                tempImg = urlInstructor + data[i]['instructorAlias'] + '.png'
                r = requests.get(tempImg)
                if r.status_code == 200:
                    instructoresImg[data[i]['instructorAlias']] = tempImg
                else:
                    instructoresImg[data[i]['instructorAlias']] = urlInstructorPlaceHolder

            data[i]['instructorImagenUrl'] = instructoresImg[data[i]['instructorAlias']]

            if data[i]['ac_estado'] in TipoEstatus().tipoTodas and \
                    data[i]['instructorAlias'] != profile.u_alias:
                data[i]['puedeReservar'] = True
            else:
                data[i]['puedeReservar'] = False
            data[i]['puedeReservar'] = False
            del data[i]['ac_estado']

        # self.tempLog.append('sali de ActividadesAfiliacionView(), --> ' + str(datetime.datetime.now().minute) + ':' + str(
        #     datetime.datetime.now().second))
        #
        # for item in self.tempLog:
        #     self.log.info(item)

        return Response(data, status.HTTP_200_OK)

class DetalleActividadView(APIView):
    permission_classes = (drf_perm.IsAuthenticated,)
    def get(self, request, id):
        """*Devuelve el detalle de la actividad"""
        actividad = Actividad.objects.filter(id=id)
        if actividad:
            pa=PerfilActividad(id)

        data = ActividadesDetailSerializer(actividad,many=True).data[0]

        if not 'localidad' in data:
            data['localidad']=''
        if not 'salaNombre' in data:
            data['salaNombre']=''

        if settings.AMBIENTE == 'DESARROLLO':
            http_='http://'
        else:
            http_ = 'https://'

        imagen = data['disciplinaImagen'].replace('..', host)
        data['disciplinaImagen'] = http_ + imagen

        # if 'userId' in request.POST:
        #     userId=request.POST['userId']
        #     profile = get_profile(userId)
        # else:
        #     profile=None

        userId=request._user.pk
        profile = get_profile(userId)

        try:
            urlMarcaImage = http_ + host + '/static/media/avatars/' + data['marca_alias'] + '.png'
            urlMarcaPlaceHolder = http_ + host + '/static/media/avatars/marcaPlaceHolder.png'
            r = requests.get(urlMarcaImage)
            if r.status_code == 200:
                data['marcaImagenUrl'] = urlMarcaImage
            else:
                data['marcaImagenUrl'] = urlMarcaPlaceHolder
        except:
            pass

        if not data['ac_imagenes']:
            data['ac_imagenes'] = [http_ + host + '/static/media/avatars/actividadPlaceHolder.png']
        else:
            imagenes = []
            for imagen in data['ac_imagenes']:
                imagenes.append(
                    http_ + host + '/static/media/avatars/' + imagen
                )
            data['ac_imagenes'] = imagenes

        if pa.actividadEsSerie:
            data['actividadRepiteComo']=pa.actividadRepetirComo
        elif pa.actividadSerieOriginaria >0 :
            pmOriginario=PerfilActividad(pa.actividadSerieOriginaria)
            data['actividadRepiteComo'] = pmOriginario.actividadRepetirComo

        instructorJSON={}
        profileInstructor=None
        if data['ac_instructor']:
            profileInstructor = get_profile(data['ac_instructor'])
            perfilInstructor=PerfilInstructor(profileInstructor.u_alias)
            instructorJSON['instructorNombre']=perfilInstructor.atletaNombreCompleto
            instructorDescripcion=perfilInstructor.instructorDescripcion
            instructorJSON['instructorDescripcion']=instructorDescripcion
            del data['ac_instructor']
            try:

                urlInstructorImage = http_ + host + '/static/media/avatars/' + perfilInstructor.atletaAlias + '.png'
                urlInstructorPlaceHolder = http_ + host + '/static/media/avatars/instructorPlaceHolder.png'

                r = requests.get(urlInstructorImage)
                if r.status_code == 200:
                    instructorJSON['instructorImagenUrl'] = urlInstructorImage
                else:
                    instructorJSON['instructorImagenUrl'] = urlInstructorPlaceHolder
            except:
                pass
            if perfilInstructor.atletaDisciplinas():
                instructorDisciplinas=[]
                instructorDisciplina={}
                for disciplina in perfilInstructor.atletaDisciplinas():
                    instructorDisciplina['disciplinaNombre']=disciplina['nombreDisciplina']
                    instructorDisciplina['disciplinaImagen'] = disciplina['imagenDisciplinaNormal'].replace('..', host)
                    if settings.AMBIENTE == 'DESARROLLO':
                        instructorDisciplina['disciplinaImagen'] = http_ + instructorDisciplina['disciplinaImagen']
                    else:
                        instructorDisciplina['disciplinaImagen'] = http_ + instructorDisciplina['disciplinaImagen']
                    instructorDisciplinas.append(instructorDisciplina)
                instructorJSON['instructorDiscplinas'] = instructorDisciplinas
        else:
            pass

        data['instructor']=instructorJSON

        if profile:
            estaReservado = Participantes.objects.filter(pa_usuario=profile.u_user, pa_actividad=actividad).exists()
            estaEnListaEspera = Espera.objects.filter(es_usuario=profile.u_user, es_actividad=actividad).exists()
            data['atletaReservado'] = estaReservado
            data['atletaListEspera'] = estaEnListaEspera

        cantidadParticipantes=pa.actividadReservados + pa.actividadEspera

        data['cantidadParticipantes'] = cantidadParticipantes

        cuposDisponibles = pa.actividadCapacidadMaxima - cantidadParticipantes
        aunHayChance = ((pa.actividadCapacidadMaxima + pa.actividadCapacidadEspera) - cantidadParticipantes) > 0

        if profileInstructor:
            if data['ac_estado'] in TipoEstatus().tipoTodas and \
                    profileInstructor.u_alias != profile.u_alias and aunHayChance:
                data['puedeReservar'] = True
            else:
                data['puedeReservar'] = False
        else:
            if data['ac_estado'] in TipoEstatus().tipoTodas:
                data['puedeReservar'] = True
            else:
                data['puedeReservar'] = False

        data['cuposDisponibles'] = cuposDisponibles

        data['participantesReservados']=pa.actividadParticipantes()

        data['participantesEnListaEspera']=pa.actividadEsperas()

        data['calorias']=7*data['duracionActividadMinutos']

        return Response(data, status.HTTP_200_OK)

class ActividadesReservadasView(APIView):
    def get(self, request, pk):
        """*Devuelve lista de actividades reservadas por el usuario"""
        profile=get_profile(pk)
        reservas=Participantes.objects.filter(pa_usuario=profile.u_user).values_list('pa_actividad_id',flat=True)

        actividades = Actividad.objects.filter(id__in=reservas).order_by('id')
        data = ActividadesSerializer(actividades,many=True).data
        for i in range(0,len(data)):
            imagen=data[i]['disciplinaImagen'].replace('..',host)
            data[i]['disciplinaImagen']='https://'+imagen
        return Response(data, status.HTTP_200_OK)

class ActividadesEnEsperaView(APIView):
    def get(self, request, pk):
        """*Devuelve lista de actividades en lsta de espera del usuario"""
        profile=get_profile(pk)

        esperas=Espera.objects.filter(es_usuario=profile.u_user).values_list('es_actividad_id',flat=True)

        actividades = Actividad.objects.filter(id__in=esperas).order_by('id')
        data = ActividadesSerializer(actividades,many=True).data
        for i in range(0,len(data)):
            imagen=data[i]['disciplinaImagen'].replace('..',host)
            data[i]['disciplinaImagen']='https://'+imagen
        return Response(data, status.HTTP_200_OK)

class Cancelar(APIView):
    def post(self,request):
        mensaje = 'ok'

        if 'id' in request.POST and 'pk' in request.POST:
            try:
                actividadId=int(request.POST['id'])
                userId = int(request.POST['pk'])
                if User.objects.filter(pk=userId).exists() and Actividad.objects.filter(pk=actividadId).exists():
                    pass
                else:
                    mensaje = 'parametros invalidos'
            except:
                mensaje = 'parametros invalidos'
        else:
            mensaje='parametros invalidos'

        perfilActividad=PerfilActividad(actividadId)
        atletaAlias=User.objects.get(pk=userId).profile.u_alias
        perfilAtleta=PerfilAtleta(atletaAlias)
        marcaId = perfilActividad.actividadMarcaId
        vicsafe = VicSafe(perfilAtleta.atletaId, marcaId, None)

        if Participantes.objects.filter(pa_actividad=actividadId,pa_usuario=userId).exists():
            mensaje=vicsafe.registrar_cancelar_reserva(perfilActividad.actividadId)
        elif Espera.objects.filter(es_actividad=actividadId,es_usuario=userId).exists():
            mensaje = vicsafe.registrar_cancelar_lista_espera(perfilActividad.actividadId)
        else:
            mensaje = 'no registrado o en espera'

        if mensaje=='ok':
            return Response(mensaje, status.HTTP_200_OK)
        else:
            return Response(mensaje, status.HTTP_400_BAD_REQUEST)

class Reservar(APIView):
    def post(self,request):
        mensaje = 'ok'
        if 'actividadId' in request.POST and 'userId' in request.POST:
            try:
                actividadId=int(request.POST['actividadId'])
                userId = int(request.POST['userId'])
                if User.objects.filter(pk=userId).exists() and Actividad.objects.filter(pk=actividadId).exists():
                    pass
                else:
                    mensaje = 'parametros invalidos'
            except:
                mensaje = 'parametros invalidos'
        else:
            mensaje='parametros invalidos'

        planId=0
        try:
            if 'planId' in request.POST:
                planId=int(request.POST['planId'])
        except:
            planId=0
            
        cupo=0
        try:
            if 'cupo' in request.POST:
                cupo=int(request.POST['cupo'])
        except:
            cupo=0

        perfilActividad=PerfilActividad(actividadId)
        atletaAlias=User.objects.get(pk=userId).profile.u_alias
        perfilAtleta=PerfilAtleta(atletaAlias)
        if puede_reservar(perfilActividad,perfilAtleta):
            mensaje=reservarUsuario(perfilActividad, perfilAtleta,cupo,planId)
        else:
            mensaje='atleta no puede reservar'
        if mensaje=='ok':
            return Response(mensaje, status.HTTP_200_OK)
        else:
            return Response(mensaje, status.HTTP_400_BAD_REQUEST)

def reservarUsuario(perfilActividad,perfilAtleta,cupo,planId):
    atletaId=perfilAtleta.atletaId
    actividadId=perfilActividad.actividadId
    vs=VicSession(perfilAtleta.atletaCorreo)
    marcaId=perfilActividad.actividadMarcaId
    vicsafe = VicSafe(perfilAtleta.atletaId, marcaId, None)

    mensaje=''

    if perfilActividad.actividadReservados == perfilActividad.actividadCapacidadMaxima:
        if perfilActividad.actividadCapacidadEspera > 0:
            strRetorno = vicsafe.registrar_lista_espera(actividadId, planId)
            if strRetorno == 'ok':
                mensaje = " paso a lista de espera"
            else:
                mensaje = strRetorno
        else:
            mensaje = " No existe lista de espera."
    else:
        strRetorno = vicsafe.registrar_reserva(actividadId, cupo, planId)
        if strRetorno == 'ok':
            if perfilActividad.actividadEsSerie:
                oActividad = Actividad.objects.get(id=actividadId)
                oActividad.ac_serieId_originaria = oActividad.ac_actividadBaseSerieId
                actualizaBaseEnSerie(oActividad)
                oActividad.ac_actividadBaseSerieId = actividadId
                oActividad.ac_OpcionSerie = 'No'
                oActividad.ac_repetirComo = ''
                oActividad.ac_despd = 'No'
                oActividad.ac_do = 1
                oActividad.ac_enf = 'No'
                oActividad.ac_fdesp = oActividad.ac_fecha
                oActividad.save()
    
            mensaje = " ha sido reservado"
        else:
            mensaje = strRetorno

    return mensaje

def puede_reservar(perfilActividad,perfilAtleta):

    actividadInstructor = perfilActividad.actividadInstructorAlias
    marcaId=perfilActividad.actividadMarcaId
    vs=VicSession(perfilAtleta.atletaCorreo)
    try:
        if perfilAtleta.atletaAlias==perfilActividad.actividadInstructorAlias:
            return False
        else:
            try:
                vicsafe = VicSafe(perfilAtleta.atletaId, marcaId, None)
                resultado = vicsafe.puedeReservarActividad(perfilActividad.actividadId) is not None
                return resultado
            except Exception as ex:
                return False
    except:
        return False

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

class CentrosPublicosView(APIView):
    def get(self,request):
        """*Devuelve lista completa de los centros publicos"""
        centros=Marca.objects.filter(m_public=True)
        data=[]
        for centro in centros:
            pm=PerfilMarca(centro.m_alias)
            data.append(
                {'marcaId': pm.marcaId,
                 'marcaNombre': pm.marcaNombre,
                 'marcaAlias': pm.marcaAlias,
                 'marcaIniciales': pm.marcaIniciales,
                 'marcaLocalidad': pm.marcaLocalidad,
                }
            )
        return Response(data, status.HTTP_200_OK)

class CentrosAfiliacionView(APIView):
    def get(self, request, pk):
        """*Devuelve lista de centros donde el usuario esta afiliado"""
        profile=get_profile(pk)
        afiliaciones=Relacion.objects.filter(r_user=profile.u_user,r_estado='A').values_list('r_marca_id',flat=True)
        centros=Marca.objects.filter(m_public=True,id__in=afiliaciones)
        data=[]
        for centro in centros:
            pm=PerfilMarca(centro.m_alias)
            data.append(
                {'marcaId': pm.marcaId,
                 'marcaNombre': pm.marcaNombre,
                 'marcaAlias': pm.marcaAlias,
                 'marcaIniciales': pm.marcaIniciales,
                 'marcaLocalidad': pm.marcaLocalidad,
                }
            )

        return Response(data, status.HTTP_200_OK)


class LocalidadesView(APIView):
    def get(self,request):
        """*Devuelve lista completa de los centros publicos"""
        centros=Marca.objects.filter(m_public=True)
        data=[]
        for centro in centros:
            pm=PerfilMarca(centro.m_alias)
            if pm.marcaLocalidad:
                data.append(
                    {'localidad':pm.marcaLocalidad}
                )
        return Response(data, status.HTTP_200_OK)

class LocalidadesAfiliacionView(APIView):
    def get(self, request, pk):
        """*Devuelve lista de centros donde el usuario esta afiliado"""
        profile=get_profile(pk)
        afiliaciones=Relacion.objects.filter(r_user=profile.u_user,r_estado='A').values_list('r_marca_id',flat=True)
        centros=Marca.objects.filter(m_public=True,id__in=afiliaciones)
        data=[]
        for centro in centros:
            pm=PerfilMarca(centro.m_alias)
            if pm.marcaLocalidad:
                data.append(
                    {'localidad':pm.marcaLocalidad}
                )

        return Response(data, status.HTTP_200_OK)

class PlanesAtletaView(APIView):
    def get(self, request, pk):
        mn=ManejoFechas()
        """*Devuelve lista de planes activos del usuario, acepta actividad como parametro"""
        planDesc={}
        planDesc[0] = 'POR CREDITOS'
        planDesc[1] = 'MENSUAL ILIMITADO'
        planDesc[2] = 'MENSUAL LIMITADO'
        planDesc[3] = 'REFERENCIADO'
        data=[]
        if 'actividad' in request.POST:
            actividadId=request.POST['actividad']
            try:
                actividad=Actividad.objects.get(pk=actividadId)
            except:
                return Response('parametros invalidos', status.HTTP_400_BAD_REQUEST)
        else:
            actividad=None

        profile=get_profile(pk)

        if actividad:
            if actividad.ac_productos_permitidos:
                planUsuarios = Planes.objects.filter(p_usuario=profile.u_user,p_historico=False,p_producto_id__in=actividad.ac_productos_permitidos).order_by('p_marca_id')
            else:
                planUsuarios = Planes.objects.filter(p_usuario=profile.u_user, p_historico=False).order_by('p_marca_id')
        else:
            planUsuarios = Planes.objects.filter(p_usuario=profile.u_user,p_historico=False).order_by('p_marca_id')

        for plan in planUsuarios:
            creditosDisponibles=(plan.p_creditos_totales_plan_mensual - plan.p_creditos_usados_plan_mensual)
            if creditosDisponibles==-1:
                creditosDisponibles='no aplica'
            data.append({
                'planId':plan.id,
                'planNombre': plan.p_nombre,
                'planMarcaId': plan.p_marca_id,
                'planMarcaNombre': plan.p_marca.m_nombre,
                'planFechaCaducidad': mn.date2dateStr(plan.p_fecha_caducidad),
                'planTipoId': plan.p_tipo,
                'planTipoDescripcion': planDesc[plan.p_tipo],
                'planCreditosDisponibles': creditosDisponibles,
                'planProductoId': plan.p_producto_id,
                'planProductoNombre': plan.p_producto.p_nombre,
            })

        return Response(data, status.HTTP_200_OK)

class ProductosActividadView(APIView):
    def get(self, request, pk):
        """*Devuelve lista de productos aceptados por la actividad"""
        productoDesc={}
        productoDesc[0] = 'POR CREDITOS'
        productoDesc[1] = 'MENSUAL ILIMITADO'
        productoDesc[2] = 'MENSUAL LIMITADO'
        productoDesc[3] = 'REFERENCIADO'
        data=[]
        try:
            actividad=Actividad.objects.get(id=pk)
        except:
            return Response('parametros invalidos', status.HTTP_400_BAD_REQUEST)

        if actividad.ac_productos_permitidos:
            productos = Producto.objects.filter(p_historico=False,p_marca_id=actividad.ac_marca_id,p_producto_id__in=actividad.ac_productos_permitidos)
        else:
            productos = Producto.objects.filter(p_historico=False,p_marca_id=actividad.ac_marca_id)

        for producto in productos:
             data.append({
                'productoId':producto.pk,
                'productoNombre': producto.p_nombre,
                'productoTipoId': producto.p_tipo,
                'productoTipoDescripcion': productoDesc[producto.p_tipo],
                'productoPrecio': producto.p_precio,
                'productoCreditos': producto.p_creditos,
             })

        return Response(data, status.HTTP_200_OK)

class PinNotificacionesAtletaView(APIView):
    permission_classes = (drf_perm.IsAuthenticated,)
    def get(self, request):
        pk=request._user.pk
        """*Devuelve un boolean si hay o no notificaciones pendientes del atleta"""
        np = Usuario_Notificacion.objects.filter(un_usuario_id=pk, un_estado='C').count()
        data={}
        data['np']=np
        return Response(data, status.HTTP_200_OK)

class NotificacionesPendientesAtletaView(APIView):
    permission_classes = (drf_perm.IsAuthenticated,)
    def get(self, request):
        pk=request._user.pk
        """*Devuelve un boolean si hay o no notificaciones pendientes del atleta"""
        pendientes = ('C',)
        recientes = ('A', 'V',)
        mn = ManejoNotificaciones()
        listaNotificacionesPendientes = mn.listaNotificacionesAtleta(pk, pendientes)
        data=[]
        for notificacionPendiente in listaNotificacionesPendientes:
            notificacion={}
            notificacion['id']=notificacionPendiente['notificacionId']
            notificacion['text']=notificacionPendiente['textoNotificacion']
            notificacion['acciones']=notificacionPendiente['acciones']
            notificacion['descripcion'] = notificacionPendiente['descripcion']
            notificacion['tiempoEmitida'] = notificacionPendiente['tiempoEmitida']
            data.append(notificacion)
        return Response(data, status.HTTP_200_OK)
    
class NotificacionesRecientesAtletaView(APIView):
    permission_classes = (drf_perm.IsAuthenticated,)
    def get(self, request):
        pk=request._user.pk
        """*Devuelve un boolean si hay o no notificaciones recientes del atleta"""
        pendientes = ('C',)
        recientes = ('A', 'V',)
        mn = ManejoNotificaciones()
        listaNotificacionesRecientes = mn.listaNotificacionesAtleta(pk, recientes)
        data=[]
        for notificacionPendiente in listaNotificacionesRecientes:
            notificacion={}
            notificacion['id']=notificacionPendiente['notificacionId']
            notificacion['text']=notificacionPendiente['textoNotificacion']
            notificacion['descripcion'] = notificacionPendiente['descripcion']
            notificacion['tiempoEmitida'] = notificacionPendiente['tiempoEmitida']
            data.append(notificacion)
        return Response(data, status.HTTP_200_OK)


class AccionNotificacionAtletaView(APIView):
    permission_classes = (drf_perm.IsAuthenticated,)

    def get(self, request):
        userId=request._user.pk
        id=request.POST.get('id',None)
        aceptar = request.POST.get('aceptar',False)
        if aceptar in ('1','True','true'):
            aceptar=True
        else:
            aceptar=False
        rechazar = request.POST.get('rechazar',False)
        if rechazar in ('1','True','true'):
            rechazar=True
        else:
            rechazar=False
            
        if id and (aceptar ^ rechazar):
            notificacion = Notificacion.objects.filter(pk=id)
        else:
            return Response('parametros invalidos', status.HTTP_400_BAD_REQUEST)

        pendientes = ('C',)
        mn = ManejoNotificaciones()

        if notificacion:
            notificacion=notificacion[0]
            usuario_Notificacion = Usuario_Notificacion.objects.filter(un_notificacion_id=id)

            if usuario_Notificacion:
               usuario_Notificacion=usuario_Notificacion[0]

               if usuario_Notificacion.un_estado not in pendientes:
                    return Response({'texto':'notificacion ya ha sido procesada anteriormente'}, status.HTTP_400_BAD_REQUEST)
               else:
                    if usuario_Notificacion.un_notificacion.nt_tipo.tn_tipo == 'IA':
                        pm=PerfilMarca(usuario_Notificacion.un_marca.m_alias)
                        user=User.objects.get(pk=userId)
                        pa=PerfilAtleta(user.profile.u_alias)
                        marcaId=pm.marcaId

                        try:
                            relacion = Relacion.objects.get(r_marca_id=marcaId, r_user_id=userId)
                            if aceptar:
                                if pm.marcaPermiteReferenciados:
                                    self.setearPlanReferenciado(pa, pm)
                                relacion.r_estado = 'A'
                                relacion.save()
                                if not Saldo.objects.filter(s_user=user, s_marca_id=marcaId):
                                    Saldo.objects.create(s_user=user, s_marca_id=marcaId)
                                mn.atleta_acepta_marca(notificacion.id)
                                mensaje = 'aceptacion de solicitud realizada'
                            else:
                                mn.atleta_rechaza_marca(notificacion.id)
                                relacion.delete()
                                mensaje = 'eliminación de solicitud realizada'
                        except Exception as e:
                            mensaje = 'Se produjo un error, La accion no pudo ser ejecutada'
                            return Response({'texto': mensaje}, status.HTTP_500_INTERNAL_SERVER_ERROR)

                    else:
                        return Response({'texto':'tipo de notificacion no contemplado'}, status.HTTP_400_BAD_REQUEST)
            else:
               return Response({'texto':'notificacion id invalido'}, status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'texto':'notificacion id invalido'}, status.HTTP_400_BAD_REQUEST)

        data={'texto':mensaje}

        return Response(data, status.HTTP_200_OK)

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