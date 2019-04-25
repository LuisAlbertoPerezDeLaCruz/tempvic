# -*- coding: utf-8 -*-
#######################
# clases.py #
#######################

from web.models import *
from datetime import datetime, date, time
from django.db.models import Sum
from django.db.models.functions import TruncMonth
import math
import locale

def getmes(i):
    meses = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre",
             "Noviembre", "Diciembre"]
    return meses[i]

class TipoEstatus:
    def __init__(self):
        self.tipoVigente = ['Abierta Reversible', 'Abierta Irreversible']
        self.tipoVigenteConCanceladas = ['Abierta Reversible', 'Abierta Irreversible','Cancelada']
        self.tipoVigenteConCanceladasYConflictivas = ['Abierta Reversible', 'Abierta Irreversible','Cancelada','En Conflicto']
        self.tipoNoVigente = ['Culminada', 'Activa']
        self.tipoTodas = ['Abierta Reversible', 'Abierta Irreversible','Planifico']
        self.tipoTodasMasCulminada = ['Abierta Reversible', 'Abierta Irreversible', 'Planifico','Culminada']
        self.tipoTodasPlus = ['Abierta Reversible', 'Abierta Irreversible', 'Planifico', 'Cancelada','En Conflicto','Culminada', 'Activa']
        self.tipoTodasFuturas = ['Abierta Reversible', 'Abierta Irreversible', 'Planifico', 'Activa']
class VicSession:
    """Manejo de sesiones de Victorius"""

    ATLETA = 1
    MARCA = 2
    INSTRUCTOR = 3

    def __init__(self, userIn):
        self.user = None
        self.userFirstName = None
        self.userLastName = None
        self.userAlias = None
        self.tipoSesion = None
        self.userId = None
        self.marcasPropietarias = []
        self.marcaEnUso = None
        self.marcaEnUsoId = None
        self.marcaEnUsoAlias = None
        self.marcaEnUsoNombre = None
        self.marcaEnUsoMunicipio = None
        self.marcaEnUsoMoneda = None
        self.marcaNotificacionesPendientes=None
        self.perfil = None
        self.marcasRelacionadas = []
        self.cantidadMarcas=None

        userList = User.objects.filter(username=userIn)
        self.cantidadMarcas = Marca.objects.count()
        if userList:
            self.user = userList[0]
            self.perfil = perfil = UserProfile.objects.get(u_user=self.user)
            self.userFirstName = self.user.first_name
            self.userLastName = self.user.last_name
            self.userId = self.user.id
            self.tipoSesion = VicSession.ATLETA
            self.userAlias = perfil.u_alias
            duenoList = Dueno.objects.filter(d_user=self.user).values_list('d_marca')
            if duenoList:
                for itemDueno in duenoList:
                    self.marcasPropietarias.append(Marca.objects.get(id=itemDueno[0]))

            relacionesList = Relacion.objects.filter(r_user=self.user)
            if relacionesList:
                for itemRelacion in relacionesList:
                    marca = Marca.objects.get(id=itemRelacion.r_marca.id)
                    self.marcasRelacionadas.append(marca.m_alias)

            if perfil.u_ultima_sesion_tipo:
                self.tipoSesion = perfil.u_ultima_sesion_tipo
                if self.tipoSesion == VicSession.MARCA:
                    self.marcaEnUso = Marca.objects.get(id=perfil.u_ultima_marca_en_uso)

                    try:
                        self.marcaEnUsoMunicipio = self.marcaEnUso.m_municipio.z_municipio
                    except:
                        self.marcaEnUsoMunicipio=''

                    VicSession.cambiarTipoSesion(self, self.marcaEnUso.m_alias)
                else:
                    self.marcaEnUso = None
                    VicSession.cambiarTipoSesion(self, self.userAlias)
            else:
                if duenoList:
                    self.tipoSesion = VicSession.MARCA
                    self.marcaEnUso = self.marcasPropietarias[0]
                    VicSession.cambiarTipoSesion(self, self.marcaEnUso.m_alias)
                else:
                    self.tipoSesion = VicSession.ATLETA
                    self.marcaEnUso = None
                    VicSession.cambiarTipoSesion(self, self.userAlias)
        else:
            pass

    def cambiarTipoSesion(self, aliasIn):
        if aliasIn == self.perfil.u_alias:
            self.tipoSesion = VicSession.ATLETA
            self.marcaEnUso = None
            self.perfil.u_ultima_marca_en_uso = None
            self.perfil.u_ultima_sesion_tipo = VicSession.ATLETA
            self.perfil.save()
        else:
            for marca in self.marcasPropietarias:
                if marca.m_alias == aliasIn:
                    self.tipoSesion = VicSession.MARCA
                    self.marcaEnUso = marca
                    self.marcaEnUsoId = marca.id
                    self.marcaEnUsoAlias = marca.m_alias
                    self.marcaEnUsoNombre = marca.m_nombre
                    self.marcaEnUsoMoneda = marca.m_moneda
                    self.perfil.u_ultima_marca_en_uso = self.marcaEnUso.id
                    self.perfil.u_ultima_sesion_tipo = self.tipoSesion
                    self.perfil.save()
        return

    def getJason(self):
        try:
            marcasPropietarias = []
            for marca in self.marcasPropietarias:
                marcasPropietarias.append([marca.m_alias, marca.m_nombre])
            marcaEnUsoAlias = None
            marcaEnUsoNombre = None
            if self.marcaEnUso:
                marcaEnUsoAlias = self.marcaEnUso.m_alias
                marcaEnUsoNombre = self.marcaEnUso.m_nombre
            json = {
                'ATLETA': VicSession.ATLETA,
                'MARCA': VicSession.MARCA,
                'userName': self.user.username,
                'userAlias': self.userAlias,
                'userFirstName': self.userFirstName,
                'userLastName': self.userLastName,
                'tipoSesion': self.tipoSesion,
                'marcaEnUsoAlias': marcaEnUsoAlias,
                'marcaEnUsoNombre': marcaEnUsoNombre,
                'marcasPropietarias': marcasPropietarias,
                'marcasRelacionadas': self.marcasRelacionadas,
                'cantidadMarcas': self.cantidadMarcas,
            }
        except:
            from django.shortcuts import redirect
            return redirect('logout')
        return json

    def setear(self, vsJson):
        self.tipoSesion = vsJson['tipoSesion']
        if vsJson['marcaEnUsoAlias']:
            self.marcaEnUso = Marca.objects.get(m_alias=vsJson['marcaEnUsoAlias'])
        else:
            self.marcaEnUso
        return

class PerfilMarca:
    """Facilita el despliegue de informacion en template del perfil de la marca"""

    def __init__(self, marcaIn):
        self.marcaId = None
        self.marcaAlias = marcaIn
        self.marcaNombre = None
        self.marcaDireccionCompleta = None
        self.marcaCalleAvenida=None
        self.marcaEdificioCasa=None
        self.marcaUrbanizacion=None
        self.marcaMunicipio=None
        self.marcaCiudad=None
        self.marcaPais=None
        self.marcaLocalidad=None
        self.marcaTelefono1 = None
        self.marcaTelefono2 = None
        self.marcaIniciales = None
        self.marcaDescripcion = None
        self.marcaMiembroDesde = None
        self.marcaCorreo = None
        self.marcaTwitter = None
        self.marcaInstagram = None
        self.marcaFacebook = None
        self.marcaPermiteReferenciados=None
        self.marcaProductoTipoReferenciado=None
        self.marcaPorcentajeAvisoCuposRestantes = None
        self.marcaDuenoAlias=None
        self.marcaRazonSocial=None
        self.marcaRif=None
        self.marcaCedula=None
        self.marcaCuentasBancarias=None
        self.marcaEsPublica=None
        self.marcaEstadoConfiguracion=None
        self.marcaTiene=None
        self.marcaTipoCuenta=None
        self.marcaTiempoReversible=None
        self.marcaTiempoIreversible=None
        self.marcaDisciplina1Id=None
        self.marcaDisciplina2Id=None
        self.marcaDisciplina3Id=None
        self.marcaNotificacionesPendientes=None
        self.marcaUnicoProductoEsReferenciado=False
        self.rutaAvatar=None
        self.cargaInfoMarca()

    def cargaInfoMarca(self):
        marca = Marca.objects.filter(m_alias=self.marcaAlias)
        self.marcaId = marca[0].id
        self.marcaNombre = marca[0].m_nombre
        self.marcaAlias = marca[0].m_alias
        self.marcaDireccionCompleta = marca[0].full_dir
        self.marcaCalleAvenida=marca[0].m_calle
        self.marcaEdificioCasa=marca[0].m_edificioCasa
        self.marcaUrbanizacion=marca[0].m_urbanizacion
        self.marcaMunicipio=marca[0].m_municipio
        self.marcaCiudad=marca[0].m_ciudad
        self.marcaPais=marca[0].m_pais
        self.marcaLocalidad=marca[0].m_municipio
        if marca[0].m_telefono1:
            self.marcaTelefono1 = marca[0].m_telefono1
        else:
            self.marcaTelefono1=''
        if marca[0].m_telefono2:
            self.marcaTelefono2 = marca[0].m_telefono2
        else:
            self.marcaTelefono2=''
        self.marcaIniciales = marca[0].m_iniciales

        self.marcaTiene={}

        if not self.marcaIniciales:
            words=self.marcaNombre.split()
            tempIniciales=''
            if len(words)>=3:
                for word in words:
                    if len(tempIniciales)>=3:
                        break
                    if word:
                        tempIniciales+=word[0:1].upper()
            elif len(words)>=2:
                for word in words:
                    if len(tempIniciales)>=3:
                        break
                    if word:
                        tempIniciales+=word[0:2].upper()
                tempIniciales=tempIniciales[0:3]
            elif len(words)>=1:
                for word in words:
                    if len(tempIniciales)>=3:
                        break
                    if word:
                        tempIniciales+=word[0:3].upper()
                tempIniciales=tempIniciales[0:3]
            marcaTemp=Marca.objects.get(m_alias=marca[0].m_alias)
            marcaTemp.m_iniciales=tempIniciales
            marcaTemp.save()
            self.marcaIniciales=tempIniciales


        self.marcaDescripcion = marca[0].m_descripcion
        self.marcaMiembroDesde = marca[0].m_created_at
        self.marcaTwitter = marca[0].m_redSocial_Twitter
        self.marcaInstagram = marca[0].m_redSocial_Instagram
        self.marcaFacebook = marca[0].m_redSocial_Facebook
        self.marcaCorreo = marca[0].m_correo
        self.marcaPermiteReferenciados=marca[0].m_permite_referenciados
        self.marcaPorcentajeAvisoCuposRestantes = marca[0].m_porcentaje_aviso_cupos_restantes
        self.marcaRazonSocial=marca[0].m_razon_social
        self.marcaTiempoReversible=marca[0].m_est_rrev
        self.marcaTiempoIreversible=marca[0].m_est_irrev
        if marca[0].m_tipoCuenta=='J':
            self.marcaRif=marca[0].m_doc_ident
        else:
            self.marcaCedula=marca[0].m_doc_ident
        self.marcaEsPublica=marca[0].m_public
        self.marcaTipoCuenta=marca[0].m_tipoCuenta
        if self.marcaPermiteReferenciados:
            self.marcaProductoTipoReferenciado=Producto.objects.get(p_marca_id=self.marcaId,p_tipo=3)

        try:
            self.marcaDuenoAlias=Dueno.objects.get(d_marca_id=self.marcaId).d_user.profile.u_alias
        except:
            pass

        self.marcaTiene['planUnicoReferenciado'] = False
        self.marcaTiene['planes'] = False
        self.marcaTiene['cuentas'] = False
        self.marcaTiene['salas'] = False
        self.marcaTiene['instructores'] = False
        self.marcaTiene['actividades'] = False

        productosVigentes=self.marcaProductosVigentes()
        if productosVigentes:
            if len(productosVigentes) == 1 and productosVigentes[0]['productoNombre'] == 'Referenciado':
                self.marcaUnicoProductoEsReferenciado = True
                self.marcaTiene['planUnicoReferenciado']=True
            else:
                self.marcaTiene['planes'] = True

        marcaCuentasBancarias=Cuenta.objects.filter(c_marca_id=self.marcaId,c_status=True)
        if marcaCuentasBancarias:
            self.marcaTiene['cuentas'] = True
            self.marcaCuentasBancarias=[]
            for cuenta in marcaCuentasBancarias:
                self.marcaCuentasBancarias.append({'banco':cuenta.c_banco,'numero':cuenta.c_numero_cuenta})

        if self.marcaSalones():
           self.marcaTiene['salas'] = True

        if self.marcaInstructores():
           self.marcaTiene['instructores'] = True

        if self.diasUltimaActividad() > -1:
           self.marcaTiene['actividades'] = True

        if self.diasUltimaActividad()>-1 and self.marcaInstructores()  and self.marcaSalones() and self.marcaProductosVigentes() and self.marcaCuentasBancarias:
            self.marcaEstadoConfiguracion=5
        elif self.marcaInstructores()  and self.marcaSalones() and self.marcaProductosVigentes():
            self.marcaEstadoConfiguracion = 4
        elif self.marcaSalones() and self.marcaProductosVigentes():
            self.marcaEstadoConfiguracion = 3
        elif self.marcaCuentasBancarias:
            self.marcaEstadoConfiguracion = 2
        elif self.marcaProductosVigentes():
            if len(productosVigentes)==1 and productosVigentes[0]['productoNombre']=='Referenciado':
                self.marcaEstadoConfiguracion = 11
            else:
                self.marcaEstadoConfiguracion = 1
        else:
            self.marcaEstadoConfiguracion = 0

        try:
            self.marcaDisciplina1Id=marca[0].m_displinafav1.id
        except:
            pass
        try:
            self.marcaDisciplina2Id=marca[0].m_displinafav2.id
        except:
            pass
        try:
            self.marcaDisciplina3Id=marca[0].m_displinafav3.id
        except:
            pass
        self.marcaNotificacionesPendientes=str(Marca_Notificacion.objects.filter(mn_marca_id=self.marcaId,mn_estado='C').count())
        if self.marcaNotificacionesPendientes=='0':
           self.marcaNotificacionesPendientes='0'
        self.rutaAvatar = marca[0].full_ruta_avatar
        return
    def marcaInfoGeneral(self):
        return Marca.objects.filter(id=self.marcaId).values()[0]

    def marcaDisciplinas(self):
        disciplinasRegistro=[]
        if self.marcaDisciplina1Id:
            disciplinasRegistro.append(self.marcaDisciplina1Id)
        if self.marcaDisciplina2Id:
            disciplinasRegistro.append(self.marcaDisciplina2Id)
        if self.marcaDisciplina3Id:
            disciplinasRegistro.append(self.marcaDisciplina3Id)
        disciplinasBase=Disciplina.objects.filter(id__in=disciplinasRegistro)
        disciplinas = Actividad.objects.filter(
            ac_marca_id=self.marcaId).values('ac_disciplina').annotate(ocurrencias=Count('ac_disciplina')).order_by(
            '-ocurrencias')
        disciplinasJson = []
        for itemDisciplina in disciplinas:
            if len(disciplinasJson)>5:
                break
            disciplina = Disciplina.objects.get(id=itemDisciplina['ac_disciplina'])
            disciplinaJson = {}
            disciplinaJson['idDisciplina'] = disciplina.id
            disciplinaJson['nombreDisciplina'] = disciplina.d_nombre
            disciplinaJson['imagenDisciplinaNormal'] = disciplina.d_imagen
            disciplinaJson['imagenDisciplinaNegra'] = disciplina.d_imagen_negra
            disciplinasJson.append(disciplinaJson)
        for disciplina in disciplinasBase:
            if len(disciplinasJson)>5:
                break
            for disciplinaWork in disciplinasJson:
                if disciplinaWork['idDisciplina']==disciplina.id:
                    continue
            disciplinaJson = {}
            disciplinaJson['idDisciplina'] = disciplina.id
            disciplinaJson['nombreDisciplina'] = disciplina.d_nombre
            disciplinaJson['imagenDisciplinaNormal'] = disciplina.d_imagen
            disciplinaJson['imagenDisciplinaNegra'] = disciplina.d_imagen_negra
            disciplinasJson.append(disciplinaJson)
        return disciplinasJson

    def marcaDisciplinasTodas(self):
        disciplinasJson = []
        disciplinas = Disciplina.objects.filter()
        for disciplina in disciplinas:
            disciplinaJson = {}
            disciplinaJson['idDisciplina'] = disciplina.id
            disciplinaJson['nombreDisciplina'] = disciplina.d_nombre
            disciplinaJson['imagenDisciplinaNormal'] = disciplina.d_imagen
            disciplinaJson['imagenDisciplinaNegra'] = disciplina.d_imagen_negra
            disciplinasJson.append(disciplinaJson)
        return disciplinasJson

    def marcaInstructores(self):
        instructoresJson = []
        relaciones=Relacion.objects.filter(r_marca_id=self.marcaId,r_estado='A',r_entrenador=True)
        for relacion in relaciones:
            pi = PerfilInstructor(relacion.r_user.profile.u_alias, None)
            if pi:
                if pi.atletaActivo and pi.atletaEsInstructor:
                    instructorJson={}
                    instructorJson['idInstructor']=pi.atletaId
                    instructorJson['idProfileInstructor']=pi.atletaProfileId
                    instructorJson['nombreInstructor']=pi.atletaNombres
                    instructorJson['aliasInstructor']=pi.atletaAlias
                    instructorJson['inicialesInstructor']=pi.atletaIniciales
                    instructoresJson.append(instructorJson)
        return instructoresJson

    def marcaAtletas(self):
        atletasJson = []
        relaciones=Relacion.objects.filter(r_marca_id=self.marcaId,r_estado='A')
        for relacion in relaciones:
            pa=PerfilAtleta(relacion.r_user.profile.u_alias,None)
            atletaJson={}
            atletaJson['idatleta']=pa.atletaId
            atletaJson['idProfileatleta']=pa.atletaProfileId
            atletaJson['nombreatleta']=pa.atletaNombres
            atletaJson['aliasatleta']=pa.atletaAlias
            atletasJson.append(atletaJson)
        return atletasJson

    def marcaSalones(self):
        salonesJson = []
        salones=Salon.objects.filter(s_marca_id=self.marcaId)
        for salon in salones:
            salonJson={}
            salonJson['idSalon']=salon.id
            salonJson['nombreSalon']=salon.s_nombre
            salonJson['capacidadSalon']=salon.s_capacidad
            salonJson['esReferenciado']=salon.s_referenciado
            salonesJson.append(salonJson)
        return salonesJson

    def marcaCuentas(self):
        cuentaesJson = []
        cuentas=Cuenta.objects.filter(c_marca_id=self.marcaId)
        for cuenta in cuentas:
            cuentaJson={}
            cuentaJson['idCuenta']=cuenta.id
            cuentaJson['numero']=cuenta.c_numero_cuenta
            cuentaJson['banco']=cuenta.c_banco
            cuentaJson['status']=cuenta.c_status
            cuentaesJson.append(cuentaJson)
        return cuentaesJson

    def diasUltimaActividad(self):
        novigentes=Actividad.objects.filter(ac_marca__id=self.marcaId).order_by('-ac_fecha')
        centroActividades = []
        for actividad in novigentes:
            centroActividades.append(actividad.id)
        if centroActividades:
            ultima = Actividad.objects.get(id=centroActividades[0]).ac_fecha
            return abs((datetime.today().date() - ultima).days)
        else:
            return -1

    def actividadesVigentes(self):
        apa = []
        tipoVigente = TipoEstatus().tipoVigente
        actividadesVigentes = Actividad.objects.filter(ac_marca_id=self.marcaId, ac_estado_id__in=tipoVigente) \
            .values('id').order_by('ac_fecha', 'ac_hora_ini')
        for actividad in actividadesVigentes:
            apa.append(PerfilActividad(actividad['id']))
        return apa

    def actividadesVigentesConCanceladas(self):
        apa = []
        tipoVigenteConCanceladas = TipoEstatus().tipoVigenteConCanceladas
        actividadesVigentes = Actividad.objects.filter(ac_fecha__gte=datetime.today(),ac_marca_id=self.marcaId, ac_estado_id__in=tipoVigenteConCanceladas) \
            .values('id').order_by('ac_fecha', 'ac_hora_ini')
        for actividad in actividadesVigentes:
            apa.append(PerfilActividad(actividad['id']))
        return apa

    def actividadesVigentesEntreFechas(self, fechaInicio=None, fechaFinalizacion=None, disciplina=None, localidad=None, instructor=None,vs=None):
        if fechaInicio==None:
            dt=datetime.today()
            start = dt
            end = start + timedelta(days=15)
        else:
            start = datetime.strptime(fechaInicio, '%Y-%m-%d')
            if fechaFinalizacion==None:
                end = start + timedelta(days=6)
            else:
                end = datetime.strptime(fechaFinalizacion, '%Y-%m-%d')
        apa = []
        if vs:
            if vs.tipoSesion==vs.ATLETA:
                tipoVigente = TipoEstatus().tipoVigenteConCanceladas
            else:
                tipoVigente = TipoEstatus().tipoVigenteConCanceladasYConflictivas
        else:
            tipoVigente = TipoEstatus().tipoVigenteConCanceladas
        actividadesVigentes = Actividad.objects.filter(ac_marca_id=self.marcaId, \
            ac_estado_id__in=tipoVigente, ac_fecha__gte=start, ac_fecha__lte=end) \
            .values('id').order_by('ac_fecha', 'ac_hora_ini')
        for actividad in actividadesVigentes:
            pa = PerfilActividad(actividad['id'])
            ok=True
            if disciplina is not None and disciplina !=u'':
                if pa.actividadDisciplinaNombre!=disciplina:
                    ok=False
            if localidad is not None and localidad!=u'':
                if pa.actividadMarca.m_municipio.z_municipio!=localidad:
                    ok=False
            if instructor is not None and instructor!=u'':
                if pa.actividadNombreInstructor!=instructor:
                    ok=False
            if ok:
                apa.append(pa)
        return apa


    def actividadesTodasEntreFechas(self,request):

        def chequearValidez(actividadId):
            pa = PerfilActividad(actividadId)
            ok=True
            if not (pa.actividadFecha>=fechaInicio.date() and pa.actividadFecha<=fechaFinalizacion.date()):
                ok=False
            else:
                if searchString is not None and searchString !=u'':
                    if searchString.isdigit():
                        if pa.actividadId!=int(searchString):
                           ok=False
                    else:
                        if not pa.lookInto(searchString):
                            ok=False
                    if ok:
                        if instructor is not None and instructor != u'' and instructor.lower() != u'todos':
                            if pa.actividadNombreInstructor != instructor:
                                ok = False
                        if disciplina is not None and disciplina != u'' and disciplina.lower() != u'todos':
                            if pa.actividadDisciplinaNombre != disciplina:
                                ok = False
                        if localidad is not None and localidad != u'' and localidad.lower() != u'todos':
                            if pa.actividadMarca.m_municipio.z_municipio != localidad:
                                ok = False
                        if status is not None and status != u'' and status.lower() != u'todos':
                            if pa.actividadEstado != status:
                                ok = False
                else:
                    if instructor is not None and instructor !=u'' and instructor.lower() != u'todos':
                        if pa.actividadNombreInstructor != instructor:
                            ok=False
                    if disciplina is not None and disciplina !=u'' and disciplina.lower() != u'todos':
                        if pa.actividadDisciplinaNombre!=disciplina:
                            ok=False
                    if localidad is not None and localidad!=u'' and localidad.lower() != u'todos':
                        if pa.actividadMarca.m_municipio.z_municipio!=localidad:
                            ok=False
                    if status is not None and status!=u'' and status.lower() != u'todos':
                        if pa.actividadEstado != status:
                            ok=False
            return (ok,pa)

        apaActividadesTodas=[]
        manejoFechas=ManejoFechas()
        try:
            fechaInicio=manejoFechas.dateStr2DateTime(request.GET['fechaInicio'])
        except:
            fechaInicio=datetime.today()
        try:
            fechaFinalizacion=manejoFechas.dateStr2DateTime(request.GET['fechaFinalizacion'])
        except:
            fechaFinalizacion=datetime.today()+timedelta(days=365)

        if 'disciplina' in request.GET:
            disciplina = request.GET['disciplina']
        else:
            disciplina=None
        if 'localidad' in request.GET:
            localidad = request.GET['localidad']
        else:
            localidad=None
        if 'instructor' in request.GET:
            instructor = request.GET['instructor']
        else:
            instructor=None
        if 'marcaAlias' in request.GET:
            marcaAlias = request.GET['marcaAlias']
        else:
            marcaAlias=None
        if 'searchString' in request.GET:
            searchString = request.GET['searchString']
        else:
            searchString=None
        if 'status' in request.GET:
            status = request.GET['status']
        else:
            status=None

        tipoTodasPlus = TipoEstatus().tipoTodasPlus

        actividadesTodas = Actividad.objects.filter(ac_marca_id=self.marcaId, ac_estado_id__in=tipoTodasPlus, \
                            ac_fecha__gte=fechaInicio, ac_fecha__lte=fechaFinalizacion) \
                            .values('id').order_by('ac_fecha', 'ac_hora_ini')


        for actividad in actividadesTodas:
            resultado=chequearValidez(actividad['id'])
            ok=resultado[0]
            pa=resultado[1]
            if ok:
                apaActividadesTodas.append(pa)


        return (apaActividadesTodas)

    def actividadesNoVigentesEntreFechas(self, fechaInicio=None, fechaFinalizacion=None, disciplina=None, localidad=None,instructor=None):
        if fechaInicio==None:
            dt=datetime.today()
            start = dt - timedelta(days=7)
            end = dt
        else:
            start = datetime.strptime(fechaInicio, '%Y-%m-%d')
            if fechaFinalizacion==None:
                end = start + timedelta(days=6)
            else:
                end = datetime.strptime(fechaFinalizacion, '%Y-%m-%d')
        apa = []
        tipoNoVigente = TipoEstatus().tipoNoVigente
        actividadesNoVigentes = Actividad.objects.filter(ac_estado_id__in=tipoNoVigente,ac_marca_id=self.marcaId, \
            ac_fecha__gte=start, ac_fecha__lte=end) \
            .values('id').order_by('-ac_fecha', '-ac_hora_ini')
        for actividad in actividadesNoVigentes:
            pa = PerfilActividad(actividad['id'])
            ok=True
            if disciplina is not None and disciplina!=u'':
                if pa.actividadDisciplinaNombre!=disciplina:
                    ok=False
            if localidad is not None and localidad!=u'':
                if pa.actividadMarca.m_municipio.z_municipio!=localidad:
                    ok=False
            if instructor is not None and instructor!=u'':
                if pa.actividadNombreInstructor!=instructor:
                    ok=False
            if ok:
                apa.append(pa)
        return apa


    def actividadesPlanificadasEntreFechas(self, fechaInicio=None, fechaFinalizacion=None, disciplina=None, localidad=None,instructor=None, marcaAlias=None):
        if fechaInicio==None:
            dt=datetime.today()
            start = dt - timedelta(days=dt.weekday())
            end = start + timedelta(days=6)
        else:
            start = datetime.strptime(fechaInicio, '%Y-%m-%d')
            if fechaFinalizacion==None:
                end = start + timedelta(days=6)
            else:
                end = datetime.strptime(fechaFinalizacion, '%Y-%m-%d')
        apa = []
        tipoPlanificadas = ['Planifico']
        actividadesPlanificadas = Actividad.objects.filter(ac_estado_id__in=tipoPlanificadas,ac_marca__m_alias=self.marcaAlias,\
            ac_fecha__gte=start,ac_fecha__lte=end) \
            .values('id').order_by('ac_fecha', 'ac_hora_ini')
        for actividad in actividadesPlanificadas:
            pa = PerfilActividad(actividad['id'])
            ok=True
            if disciplina is not None and disciplina !=u'':
                if pa.actividadDisciplinaNombre!=disciplina:
                    ok=False
            if localidad is not None and localidad!=u'':
                if pa.actividadMarca.m_municipio!=localidad:
                    ok=False
            if ok:
                apa.append(pa)
        return apa

    def marcaProductosVigentes(self):
        productosJson=[]
        productos=Producto.objects.filter(p_activo=True,p_marca_id=self.marcaId)
        if productos:
            for producto in productos:
                productosJson.append({'productoId':producto.id,'productoNombre':producto.p_nombre})
        return productosJson

    def marcaPagosMensuales(self,mes,anno,criteria):

        pagos=Pago.objects.filter(p_marca_id=self.marcaId,
                                  p_fecha_registro__month=mes,
                                  p_fecha_registro__year=anno)\
            .order_by('-p_fecha_registro')

        pagosJSON=[]
        totalesJSON={}
        for sc in Pago.STATUS_CHOICES:
            totalesJSON[sc[1]]=0
        totalesJSON['Descuentos']=0
        totalesJSON['Total'] = 0
        totalesJSON['Becas'] = 0
        for pago in pagos:
            if pago.p_producto.p_tipo==3:
                continue
            if criteria['searchString']:
                ss=criteria['searchString']
                ok=False
                if ss == pago.p_pagador.profile.u_alias:
                    ok=True
                if pago.p_referencia:
                    try:
                        if int(ss) == pago.p_referencia:
                            ok=True
                    except:
                        pass
                if not ok:
                    continue
            if criteria['idStatus']:
                if pago.p_status != int(criteria['idStatus']):
                    continue
            if criteria['idMedio']:
                if pago.p_medio != int(criteria['idMedio']):
                    continue
            if criteria['idPlan']:
                if pago.p_producto.id != int(criteria['idPlan']):
                    continue
            dtoGral=pago.p_dtoGeneral
            dtoPart=pago.p_dtoParticular
            precio=pago.p_precio
            dtoLiteral=''
            dtoGralLit=''
            dtoPartLit=''
            if dtoPart>0:
                if dtoGral>0:
                    dtoPartLit = str(int(round(dtoPart*100/(precio-dtoGral))))+'%'
                    dtoGralLit = str(int(round(dtoGral*100/(precio))))+'%'
                    dtoLiteral = dtoGralLit + '+' +dtoPartLit
                else:
                    dtoPartLit = str(int(round(dtoPart * 100 / (precio)))) + '%'
                    dtoLiteral = dtoPartLit
            else:
                if dtoGral>0:
                   dtoGralLit = str(int(round(dtoGral * 100 / (precio)))) + '%'
                   dtoLiteral = dtoGralLit
            if precio==(dtoGral+dtoPart):
                totalesJSON['Becas'] += precio
            else:
                totalesJSON['Descuentos']+=(dtoGral+dtoPart)
            statusLiteral=pago.get_p_status_display()
            if statusLiteral=='Conciliado':
                fechaConciliacion=pago.p_fecha_Conciliacion
            else:
                fechaConciliacion = None


            if pago.p_status==0: # Por Conciliar
                clase1CSS='vic-circle-edopago-1 disabled'
                clase2CSS = ''
            elif pago.p_status==1: # Conciliado
                clase1CSS = 'vic-circle-edopago-1 '
                clase2CSS = ''
            elif pago.p_status==2: # No Conciliado
                clase1CSS = 'vic-circle-edopago-1 disabled'
                clase2CSS='linea-suspendido-edocuenta'
            elif pago.p_status==3: # Pendiente de Pago
                clase1CSS = 'vic-circle-edopago-1 disabled'
                clase2CSS = ''

            totalesJSON[pago.get_p_status_display()]+=pago.p_monto
            totalesJSON['Total']+=pago.p_monto

            pagoJSON={}
            pagoJSON['id'] = pago.id
            pagoJSON['fechaRegistro']=pago.p_fecha_registro
            pagoJSON['fechaTransaccion'] = pago.p_fecha_transaccion
            pagoJSON['planId'] = pago.p_plan_id
            pagoJSON['nombrePlan'] = pago.p_plan.p_nombre
            pagoJSON['pagadorAlias'] = pago.p_pagador.profile.u_alias
            pagoJSON['monto'] = pago.p_monto
            pagoJSON['descuento']=dtoLiteral
            pagoJSON['codigoInterno']=pago.p_codigoInterno
            pagoJSON['medio']=pago.get_p_medio_display()
            pagoJSON['referencia']=pago.p_referencia
            pagoJSON['porCobrar'] = pago.p_porcobrar
            pagoJSON['statusLiteral'] = statusLiteral
            pagoJSON['clase1CSS']=clase1CSS
            pagoJSON['clase2CSS']=clase2CSS
            pagoJSON['fechaConciliacion'] = fechaConciliacion

            pagosJSON.append(pagoJSON)

        return (pagosJSON,totalesJSON)


class PerfilBasicoAtleta:
    """Facilita parte basica del perfil tanto para atletas como para instructores"""

    def __init__(self, atletaIn, vs=None):
        self.atletaId = None
        self.atletaProfileId=None
        self.atletaAlias = atletaIn
        self.atletaNombreCompleto = None
        self.atletaNombres = None
        self.atletaPrimerNombre = None
        self.atletaDireccionCompleta = None
        self.atletaTelefono = None
        self.atletaTelefonoSecundario = None
        self.atletaObjetivos = None
        self.atletaCorreo = None
        self.atletaEsInstructor = None
        self.atletaIniciales = None
        self.atletaSaldos = []
        self.atletaTieneRelacionConMarcas=None
        self.atletaEnEsperaDeAceptaciones=None
        self.vs = vs
        self.atletaEsPublico=None
        self.atletaEstadoConfiguracion = None
        self.puedeRegistrarMarca=None
        self.rutaAvatar=None
        self.atletaTieneMarca=None
        self.atletaFechaNacimiento=None
        self.atletaActivo=None
        self.cargaInfoAtleta()


    def cargaInfoAtleta(self):
        profile = UserProfile.objects.filter(u_alias=self.atletaAlias)[0]
        self.atletaId = profile.u_user.id
        self.atletaProfileId=profile.id
        self.atletaPrimerNombre = profile.u_user.first_name
        self.atletaNombres = profile.u_user.first_name + ' ' + profile.u_user.last_name
        self.atletaIniciales = profile.u_iniciales
        self.atletaNombreCompleto = profile.u_user.first_name + ' ' + \
                                    profile.u_secondname + ' ' + \
                                    profile.u_user.last_name + ' ' + \
                                    profile.u_secondlastname
        if not self.atletaIniciales:
            words=self.atletaNombreCompleto.split()
            tempIniciales=''
            if len(words)>=3:
                for word in words:
                    if len(tempIniciales)>=3:
                        break
                    if word:
                        tempIniciales+=word[0:1].upper()
            elif len(words)>=2:
                for word in words:
                    if len(tempIniciales)>=3:
                        break
                    if word:
                        tempIniciales+=word[0:2].upper()
                tempIniciales=tempIniciales[0:3]
            elif len(words)>=1:
                for word in words:
                    if len(tempIniciales)>=3:
                        break
                    if word:
                        tempIniciales+=word[0:3].upper()
                tempIniciales=tempIniciales[0:3]
            tempProfile=UserProfile.objects.get(u_alias=self.atletaAlias)
            tempProfile.u_iniciales=tempIniciales
            tempProfile.save()
            self.atletaIniciales=tempIniciales

        self.atletaDireccionCompleta = profile.full_dir
        if profile.u_telefono:
            self.atletaTelefono = profile.u_telefono
        else:
            self.atletaTelefono = ''
        if profile.u_fecha_nac:
            self.atletaFechaNacimiento = profile.u_fecha_nac
        else:
            self.atletaFechaNacimiento = None
        self.atletaCorreo = profile.u_user.username
        self.atletaEsInstructor = profile.u_entrenador
        self.disciplinasBD = []
        if Relacion.objects.filter(r_estado='A',r_user_id=self.atletaId):
            self.atletaTieneRelacionConMarcas=True
        else:
            self.atletaTieneRelacionConMarcas = False
            if Relacion.objects.filter(r_estado='P', r_user_id=self.atletaId):
                self.atletaEnEsperaDeAceptaciones=True
            else:
                self.atletaEnEsperaDeAceptaciones = False
        try:
            self.disciplinasBD.append(profile.u_displinafav1.d_nombre)
            self.disciplinasBD.append(profile.u_displinafav2.d_nombre)
            self.disciplinasBD.append(profile.u_displinafav3.d_nombre)
        except:
            pass
        self.atletaObjetivos = profile.u_objetivos + self.repetirChar(' ', 130)[0:130]
        saldos = Saldo.objects.filter(s_user=profile.u_user)
        for saldo in saldos:
            saldoJson = {}
            saldoJson['marcaAlias'] = saldo.s_marca.m_alias
            saldoJson['saldoRestante'] = saldo.s_saldo
            saldoJson['saldoUsado'] = saldo.s_bloqueado
            saldoJson['saldoCompuesto'] = str(saldo.s_bloqueado) + '/' + str(saldo.s_saldo + saldo.s_bloqueado)
            planes = Planes.objects.filter(p_marca__m_alias=saldo.s_marca.m_alias, p_usuario=saldo.s_user,
                                           p_historico=False)
            if len(planes) > 1:
                saldoJson['saldoCompuesto'] += '+'
            self.atletaSaldos.append(saldoJson)
        self.atletaEsPublico=profile.u_public

        if self.atletaTieneRelacionConMarcas or self.atletaEnEsperaDeAceptaciones:
            self.atletaEstadoConfiguracion=1
        else:
            self.atletaEstadoConfiguracion = 0
        planes=Planes.objects.filter(p_usuario_id=self.atletaId).exclude(p_tipo=3)
        if planes:
            self.atletaEstadoConfiguracion = 2
        participaciones=Participantes.objects.filter(pa_usuario_id=self.atletaId)
        esperas = Espera.objects.filter(es_usuario_id=self.atletaId)
        if participaciones or esperas:
            self.atletaEstadoConfiguracion = 3
        self.puedeRegistrarMarca=profile.u_puede_registrar_marca
        cantidadMarcasRegistradas=Dueno.objects.filter(d_user_id=self.atletaId).count()
        if cantidadMarcasRegistradas>=profile.u_cantidad_marcas_permitidas:
           self.puedeRegistrarMarca=False

        self.rutaAvatar=profile.full_ruta_avatar
        self.atletaTieneMarca=profile.u_marca
        self.atletaActivo=profile.u_user.is_active


    def atletaInfoGeneral(self):
        return UserProfile.objects.filter(u_user_id=self.atletaId).values()[0]

    def saldoEnMarca(self, marcaAlias):
        saldoEnMarca = None
        for saldoJson in self.atletaSaldos:
            if saldoJson['marcaAlias'] == marcaAlias:
                saldoEnMarca = saldoJson
                break
        return saldoEnMarca

    def repetirChar(self, s, length):
        r = ''
        for i in range(0, length):
            r += s
        return r

    def esInstructorEnMarca(self):
        es=False
        if self.vs:
            if self.vs.tipoSesion==self.vs.MARCA:
                marcaEnUsoId=self.vs.marcaEnUso.id
                relacion=Relacion.objects.filter(r_estado='A',r_entrenador=True,r_marca_id=marcaEnUsoId,r_user_id=self.atletaId)
                if relacion:
                    es=True
        return es

    def bolivares(self,valor):
        locale.setlocale(locale.LC_ALL, 'es_VE.utf8')
        try:
            valor = float(valor)
        except:
            valor = 0
        valorFormateado = locale.format("%.0f", valor, grouping=True)
        valorFormateado += ' Bs.'
        return valorFormateado

class PerfilAtleta(PerfilBasicoAtleta):
    """Facilita el despliegue de informacion en template del perfil del atleta"""

    def tieneVigentes(self):
        result = (self.actividadesVigentesEntreFechas() == None)
        return result

    def diasUltimaActividad(self):
        misReservas = self.actividadesReservadas()
        misEsperas = self.actividadesEnListaDeEspera()
        misHistoricas = self.actividadesHistoricas()

        misActividades = []
        for actividad in misReservas + misEsperas + misHistoricas:
            misActividades.append(actividad['actividadId'])
        if misActividades:
            ultima=PerfilActividad(misActividades[0]).actividadFecha
            return (datetime.today().date()-ultima).days
        else:
            return -1

    def atletaMarcas(self):
        atletaRelacionesMarcas=Relacion.objects.filter(r_estado='A',r_user_id=self.atletaId)
        marcas=[]
        for atletaRelacion in atletaRelacionesMarcas:
            marca=Marca.objects.get(id=atletaRelacion.r_marca_id)
            if not marca.m_iniciales:
               pm=PerfilMarca(marca.m_alias)
               marca = Marca.objects.get(id=atletaRelacion.r_marca_id)
            marcas.append(marca)
        return marcas

    def instructorMarcas(self):
        instructorRelacionesMarcas=Relacion.objects.filter(r_estado='A',r_entrenador=True,r_user_id=self.atletaId)
        marcas=[]
        for atletaRelacion in instructorRelacionesMarcas:
            marca=Marca.objects.get(id=atletaRelacion.r_marca_id)
            if not marca.m_iniciales:
               pm=PerfilMarca(marca.m_alias)
               marca = Marca.objects.get(id=atletaRelacion.r_marca_id)
            marcas.append(marca)
        return marcas

    def atletaMarcasPendientes(self):
        atletaRelacionesMarcas=Relacion.objects.filter(r_estado__in=['P'],r_user_id=self.atletaId)
        marcas=[]
        for atletaRelacion in atletaRelacionesMarcas:
            marca=Marca.objects.get(id=atletaRelacion.r_marca_id)
            if not marca.m_iniciales:
               pm=PerfilMarca(marca.m_alias)
               marca = Marca.objects.get(id=atletaRelacion.r_marca_id)
            marcas.append(marca)
        return marcas

    def atletaMarcasAprobadasPendientes(self):
        atletaRelacionesMarcas=Relacion.objects.filter(r_estado__in=['A','P'],r_user_id=self.atletaId)
        marcas=[]
        for atletaRelacion in atletaRelacionesMarcas:
            marca=Marca.objects.get(id=atletaRelacion.r_marca_id)
            if not marca.m_iniciales:
               pm=PerfilMarca(marca.m_alias)
               marca = Marca.objects.get(id=atletaRelacion.r_marca_id)
            marcas.append(marca)
        marcasOrdenadas=sorted(marcas, key=lambda x: x.m_nombre, reverse=False)
        return marcasOrdenadas

    def atletaInstructores(self,marcaAlias=None):
        atletaMarcas = self.atletaMarcas()
        instructoresJson = []
        for marca in atletaMarcas:
            relaciones=Relacion.objects.filter(r_marca=marca,r_entrenador=True)
            for relacion in relaciones:
                instructorJson={}
                instructorJson['nombreInstructor']=relacion.r_user.first_name+' '+relacion.r_user.last_name
                instructorJson['aliasInstructor']=relacion.r_user.profile.u_alias
                instructoresJson.append((instructorJson))
        unique = set()
        for d in instructoresJson:
            t = tuple(d.items())
            unique.add(t)
        instructoresJson=[dict(x) for x in unique]
        return instructoresJson

    def atletaLocalidades(self, marcaAlias=None):
        atletaMarcas = self.atletaMarcas()
        localidadesJson = []
        for marca in atletaMarcas:
            localidadJson = {}
            if marca.m_municipio:
                localidadJson['nombreLocalidad']=marca.m_municipio
            else:
                localidadJson['nombreLocalidad'] = 'indefinida'
            localidadesJson.append(localidadJson)
        unique = set()
        for d in localidadesJson:
            t = tuple(d.items())
            unique.add(t)
        localidadesJson = [dict(x) for x in unique]
        return localidadesJson

    def atletaDisciplinas(self,marcaAlias=None):
        disciplinasJson = []
        if marcaAlias==None:
            disciplinas = Participantes.objects.filter(pa_usuario_id=self.atletaId).values(
                'pa_actividad__ac_disciplina').annotate(ocurrencias=Count('pa_actividad__ac_disciplina')).order_by(
                '-ocurrencias')
        else:
            disciplinas = Participantes.objects.filter(pa_usuario_id=self.atletaId,pa_actividad__ac_marca__m_alias=marcaAlias).values(
                'pa_actividad__ac_disciplina').annotate(ocurrencias=Count('pa_actividad__ac_disciplina')).order_by(
                '-ocurrencias')
        for itemDisciplina in disciplinas:
            disciplina = Disciplina.objects.get(id=itemDisciplina['pa_actividad__ac_disciplina'])
            disciplinaJson = {}
            disciplinaJson['nombreDisciplina'] = disciplina.d_nombre
            disciplinaJson['imagenDisciplinaNormal'] = disciplina.d_imagen
            disciplinaJson['imagenDisciplinaNegra'] = disciplina.d_imagen_negra
            disciplinasJson.append(disciplinaJson)
        while len(disciplinasJson) < 4:
            for disciplinaBD in self.disciplinasBD:
                for itemDisciplina in disciplinasJson:
                    if disciplinaBD == itemDisciplina['nombreDisciplina']:
                        break
                else:
                    disciplina = Disciplina.objects.get(d_nombre=disciplinaBD)
                    disciplinaJson = {}
                    if marcaAlias==None:
                        disciplinaJson['nombreDisciplina'] = disciplina.d_nombre
                    else:
                        disciplinaJson['nombreDisciplina'] = '*'+disciplina.d_nombre
                    disciplinaJson['imagenDisciplinaNormal'] = disciplina.d_imagen
                    disciplinaJson['imagenDisciplinaNegra'] = disciplina.d_imagen_negra
                    disciplinasJson.append(disciplinaJson)
            break
        unique = set()
        for d in disciplinasJson:
            t = tuple(d.items())
            unique.add(t)
        disciplinasJson=[dict(x) for x in unique]
        return disciplinasJson

    def planesActivos(self):
        vs = self.vs
        if vs.tipoSesion == vs.ATLETA:
            centros=Relacion.objects.values_list('r_marca_id', flat=True).filter(r_user_id=self.atletaId,r_estado='A')
            planes = Planes.objects.filter(p_usuario=self.atletaId, p_historico=False, p_marca_id__in=centros).order_by('p_fecha_caducidad')
        else:
            planes = Planes.objects.filter(p_usuario=self.atletaId, p_marca__m_alias=vs.marcaEnUso.m_alias,
                                           p_historico=False).order_by('p_fecha_caducidad')
        paJson = self.armaJsonPlanes(planes)
        return paJson

    def planesActivosPagos(self,marcaAlias=None):
        if marcaAlias=='None':
            marcaAlias=None
        vs = self.vs
        if vs.tipoSesion == vs.ATLETA:
            if marcaAlias:
                centros = Relacion.objects.values_list('r_marca_id', flat=True).filter(r_user_id=self.atletaId,
                                                                                       r_estado='A',r_marca__m_alias=marcaAlias)
            else:
                centros = Relacion.objects.values_list('r_marca_id', flat=True).filter(r_user_id=self.atletaId,
                                                                                       r_estado='A')
            planes = Planes.objects.filter(p_usuario=self.atletaId, p_historico=False, p_marca_id__in=centros).order_by('p_fecha_caducidad').exclude(p_nombre='Referenciado')
        else:
            planes = Planes.objects.filter(p_usuario=self.atletaId, p_marca__m_alias=vs.marcaEnUso.m_alias,
                                           p_historico=False).order_by('p_fecha_caducidad').exclude(p_nombre='Referenciado')
        paJson = self.armaJsonPlanes(planes)
        return paJson

    def planesHistoricos(self,marcaAlias=None):
        if marcaAlias=='None':
            marcaAlias=None
        vs = self.vs
        if vs.tipoSesion == vs.ATLETA:
            if marcaAlias:
                centros = Relacion.objects.values_list('r_marca_id', flat=True).filter(r_user_id=self.atletaId,
                                                                                       r_estado='A',r_marca__m_alias=marcaAlias)
            else:
                centros = Relacion.objects.values_list('r_marca_id', flat=True).filter(r_user_id=self.atletaId,
                                                                                       r_estado='A')
            planes = Planes.objects.filter(p_usuario=self.atletaId, p_historico=True, p_marca_id__in=centros).exclude(p_nombre='Referenciado').order_by('-p_fecha_caducidad')
        else:
            planes = Planes.objects.filter(p_usuario=self.atletaId, p_marca__m_alias=vs.marcaEnUso.m_alias,
                                           p_historico=True).exclude(p_nombre='Referenciado').order_by('-p_fecha_caducidad')
        paJson = self.armaJsonPlanes(planes)
        return paJson

    def armaJsonPlanes(self, planes):
        paJson = []
        for plan in planes:
            planJson = {}
            planJson['planId'] = plan.id
            planJson['planFechaCompra'] = plan.p_fecha_obtencion
            planJson['planFechaVencimiento'] = plan.p_fecha_caducidad
            planJson['planNombre'] = plan.p_nombre
            planJson['planMarcaNombre'] = plan.p_marca.m_nombre
            planJson['planMarcaAlias'] = plan.p_marca.m_alias
            planJson['planCreditosTotales'] = plan.p_creditos_totales
            planJson['planCreditosUsados'] = plan.p_creditos_usados
            planJson['planCreditosTotalesPlanMensual'] = plan.p_creditos_totales_plan_mensual
            planJson['planCreditosUsadosPlanMensual'] = plan.p_creditos_usados_plan_mensual
            try:
                planJson['PlanTipoString']=plan.p_producto.get_p_tipo_display()
            except:
                planJson['PlanTipoString'] = ''
            try:
                if plan.p_tipo==0:
                    planJson['planPorcentajeUtilizado'] = self.formatoPorcentaje(
                        plan.p_creditos_usados * 100 / plan.p_creditos_totales)
                elif plan.p_tipo==1:
                    planJson['planPorcentajeUtilizado'] = 0
                elif plan.p_tipo==2:
                    planJson['planPorcentajeUtilizado'] = self.formatoPorcentaje(
                        plan.p_creditos_usados_plan_mensual * 100 / plan.p_creditos_totales_plan_mensual)
                elif plan.p_tipo==3:
                    planJson['planPorcentajeUtilizado'] = 0
            except:
                planJson['planPorcentajeUtilizado'] = 0

            if plan.p_tipo==0:
                planJson['planEstadoConsumo'] = str(plan.p_creditos_usados) + '/' + str(plan.p_creditos_totales)
            elif plan.p_tipo==1:
                planJson['planEstadoConsumo']=''
            elif plan.p_tipo==2:
                planJson['planEstadoConsumo'] = str(plan.p_creditos_usados_plan_mensual) + '/' + str(plan.p_creditos_totales_plan_mensual)
            elif plan.p_tipo==3:
                planJson['planEstadoConsumo']=''
            pago = Pago.objects.get(p_plan_id=plan.id)
            planJson['planPrecio'] = pago.p_precio
            if pago.p_precio>0:
                planJson['planDescuentoGeneral'] = pago.p_dtoGeneral * 100 / pago.p_precio
                planJson['planDescuentoParticular'] = pago.p_dtoParticular * 100 / pago.p_precio
            else:
                planJson['planDescuentoGeneral']=0
                planJson['planDescuentoParticular'] =0
            planJson['planMontoPagado'] = pago.p_monto
            planJson['planTipo']=plan.p_tipo
            planJson['planProductoId']=plan.p_producto_id
            if pago.p_dtoGeneral > 0:
                planJson['planDescuentoArmado'] = self.formatoPorcentaje(pago.p_dtoGeneral * 100 / pago.p_precio)
                if pago.p_dtoParticular > 0:
                    planJson['planDescuentoArmado'] += ' + ' + self.formatoPorcentaje(
                        pago.p_dtoParticular * 100 / pago.p_precio)
                planJson['planDescuentoArmado'] += ' dto'
            else:
                if pago.p_dtoParticular > 0:
                    planJson['planDescuentoArmado'] = self.formatoPorcentaje(pago.p_dtoParticular * 100 / pago.p_precio)
                    planJson['planDescuentoArmado'] += ' dto'
            paJson.append(planJson)
        return paJson

    def formatoPorcentaje(self,value):
        value = round(value)
        if value - int(value) > 0:
            return locale.format("%.1f", value, grouping=True) + '%'
        else:
            return locale.format("%.0f", value, grouping=True) + '%'

    def actividadesTodas(self):
        from itertools import chain
        vs = self.vs
        if vs.tipoSesion == vs.ATLETA:
            participaciones = Participantes.objects.filter(pa_usuario_id=self.atletaId)\
                .values_list('pa_actividad', 'pa_num_cupo', 'pa_usuario')
        else:
            participaciones = Participantes.objects.filter(pa_usuario_id=self.atletaId,
                                                           pa_actividad__ac_marca__m_alias=vs.marcaEnUso.m_alias)\
                .values_list('pa_actividad', 'pa_num_cupo', 'pa_usuario')
        actividades = Actividad.objects.filter(id__in=[i[0] for i in participaciones]).order_by('-ac_fecha').values(
            'id')
        aRes = self.armarJsonActividades(zip(actividades, participaciones))

        if vs.tipoSesion == vs.ATLETA:
            espera = Espera.objects.filter(es_usuario_id=self.atletaId,
                                           es_actividad__ac_estado__ea_estado__in=['Abierta Reversible',
                                                                                   'Abierta Irreversible',
                                                                                   'Activa']).values_list(
                'es_actividad', 'es_num_cupo', 'es_usuario')
        else:
            espera = Espera.objects.filter(es_usuario_id=self.atletaId,
                                           es_actividad__ac_marca__m_alias=vs.marcaEnUso.m_alias,
                                           es_actividad__ac_estado__ea_estado__in=['Abierta Reversible',
                                                                                   'Abierta Irreversible',
                                                                                   'Activa']).values_list(
                'es_actividad', 'es_num_cupo', 'es_usuario')
        actividades = Actividad.objects.filter(id__in=[i[0] for i in espera]).order_by('-ac_fecha')
        aEsp = self.armarJsonActividades(zip(actividades, espera))
        aAct=sorted(chain(aRes,aEsp),key=lambda instance: instance['actividadFecha'], reverse=True)

        return aAct

    def actividadesReservadas(self,soloFuturas=False):
        vs = self.vs
        if vs.tipoSesion == vs.ATLETA:
            participaciones = Participantes.objects.filter(pa_usuario_id=self.atletaId)\
                .values_list('pa_actividad', 'pa_num_cupo', 'pa_usuario')
        else:
            participaciones = Participantes.objects.filter(pa_usuario_id=self.atletaId,
                                                           pa_actividad__ac_estado__ea_estado__in=['Abierta Reversible',
                                                                                   'Abierta Irreversible',
                                                                                   'Activa'],
                                                           pa_actividad__ac_marca__m_alias=vs.marcaEnUso.m_alias)\
                .values_list('pa_actividad', 'pa_num_cupo', 'pa_usuario')
        if soloFuturas:
            tipoTodas = TipoEstatus().tipoTodasFuturas
        else:
            tipoTodas = TipoEstatus().tipoTodasPlus
        actividades = Actividad.objects.filter(id__in=[i[0] for i in participaciones],ac_estado__in=tipoTodas).order_by('-ac_fecha')
        aAct = self.armarJsonActividades(zip(actividades, participaciones))
        return aAct

    def actividadesEnListaDeEspera(self,soloFuturas=False):
        vs = self.vs
        if vs.tipoSesion == vs.ATLETA:
            espera = Espera.objects.filter(es_usuario_id=self.atletaId,
                                           es_actividad__ac_estado__ea_estado__in=['Abierta Reversible',
                                                                                   'Abierta Irreversible',
                                                                                   'Activa']).values_list(
                'es_actividad', 'es_num_cupo', 'es_usuario')
        else:
            espera = Espera.objects.filter(es_usuario_id=self.atletaId,
                                           es_actividad__ac_marca__m_alias=vs.marcaEnUso.m_alias,
                                           es_actividad__ac_estado__ea_estado__in=['Abierta Reversible',
                                                                                   'Abierta Irreversible',
                                                                                   'Activa']).values_list(
                'es_actividad', 'es_num_cupo', 'es_usuario')
        if soloFuturas:
            tipoTodas = TipoEstatus().tipoTodasFuturas
        else:
            tipoTodas = TipoEstatus().tipoTodasPlus
        actividades = Actividad.objects.filter(id__in=[i[0] for i in espera],ac_estado__in=tipoTodas).order_by('-ac_fecha')
        aAct = self.armarJsonActividades(zip(actividades, espera))
        return aAct

    def actividadesHistoricas(self):
        vs = self.vs
        if vs.tipoSesion == vs.ATLETA:
            participaciones = Participantes.objects.filter(pa_usuario_id=self.atletaId,
                                                           pa_actividad__ac_estado__ea_estado='Culminada').values_list(
                'pa_actividad', 'pa_num_cupo', 'pa_usuario')
        else:
            participaciones = Participantes.objects.filter(pa_usuario_id=self.atletaId,
                                                           pa_actividad__ac_marca__m_alias=vs.marcaEnUso.m_alias,
                                                           pa_actividad__ac_estado__ea_estado='Culminada') \
                .values_list('pa_actividad', 'pa_num_cupo', 'pa_usuario')

        actividades = Actividad.objects.filter(id__in=[i[0] for i in participaciones]) \
            .order_by('-ac_fecha')
        aAct = self.armarJsonActividades(zip(actividades, participaciones))
        return aAct

    def armarJsonActividades(self, registroActividades):
        aAct = []
        for actividad, participacion in registroActividades:

            actJson = {}

            actJson['actividadId'] = actividad.id
            actJson['actividadNombre'] = actividad.ac_nombre
            actJson['actividadInicialesMarca'] = actividad.ac_marca.m_iniciales
            actJson['actividadNombreMarca'] = actividad.ac_marca.m_nombre
            actJson['actividadMarcaId'] = actividad.ac_marca_id
            actJson['actividadFecha'] = actividad.ac_fecha
            actJson['actividadHoraInicio'] = actividad.ac_hora_ini
            actJson['actividadDisciplinaNombre'] = actividad.ac_disciplina.d_nombre
            actJson['actividadDisciplinaImagenNormal'] = actividad.ac_disciplina.d_imagen
            actJson['actividadDisciplinaImagenNegra'] = actividad.ac_disciplina.d_imagen_negra
            actJson['actividadInstructorNombre'] = actividad.ac_instructor.u_user.first_name + actividad.ac_instructor.u_user.last_name
            actJson['actividadInstructorAlias'] = actividad.ac_instructor.u_alias
            actJson['actividadEstado'] = actividad.ac_estado.ea_estado
            actJson['actividadCreditos'] = actividad.ac_creditos
            if actividad.ac_cap_max > 0:
                actJson['actividadCapacidadLlena'] = ((actividad.ac_cap_max + actividad.ac_cap_max_espera) <= (
                        actividad.ac_cupos_reservados + actividad.ac_cupos_en_espera))
            else:
                actJson['actividadCapacidadLlena'] = False
            actJson['actividadAbiertaListaEspera'] = (actividad.ac_cap_max == actividad.ac_cupos_reservados)
            actJson['actividadBonificacionBase'] = actividad.ac_precio
            actJson['actividadAbiertaParaReservar'] = actividad.ac_estado.ea_estado in ['Abierta Reversible',
                                                                                  'Abierta Irreversible']

            actJson['actividadReferenciada'] = actividad.ac_referenciado

            actJson['actividadFecha'] = actividad.ac_fecha
            aAct.append(actJson)
        return aAct

    def armarJsonAtletaFast(self, marcaAlias, actividadId,planIdParaReservar):
        afastJson = {}
        afastJson['atletaId'] = self.atletaId
        afastJson['atletaNombres'] = self.atletaNombres
        afastJson['atletaAlias'] = self.atletaAlias

        try:
            for saldo in self.atletaSaldos:
                if saldo['marcaAlias'] == marcaAlias:
                    afastJson['atletaSaldoEnMarca'] = saldo['saldoCompuesto']
                    if saldo['saldoRestante'] >= Actividad.objects.get(id=actividadId).ac_creditos:
                        afastJson['tieneCreditosParaReservar'] = True
                    else:
                        afastJson['tieneCreditosParaReservar'] = False
            afastJson['planIdParaReservar'] = planIdParaReservar
            reservado = Participantes.objects.filter(pa_actividad_id=actividadId, pa_usuario_id=self.atletaId)
            espera = Espera.objects.filter(es_actividad_id=actividadId, es_usuario_id=self.atletaId)
            afastJson['marcadoEnAsistencia'] = False
            afastJson['participacionId'] = 0
            if reservado:
                afastJson['tieneReserva'] = True
                afastJson['puestoReserva'] = reservado[0].pa_num_cupo
                afastJson['marcadoEnAsistencia'] = reservado[0].pa_asistencia
                afastJson['participacionId'] = reservado[0].id
            else:
                afastJson['tieneReserva'] = False
                afastJson['puestoReserva'] = None
            if espera:
                afastJson['estaEnListaDeEspera'] = True
                afastJson['puestoListaDeEspera'] = espera[0].es_num_cupo
            else:
                afastJson['estaEnListaDeEspera'] = False
                afastJson['puestoListaDeEspera'] = None
        except Exception as e:
            pass

        return afastJson

    def actividadesTodasEntreFechas(self,request,soloFuturas=False):

        def chequearValidez(actividadId):
            pa = PerfilActividad(actividadId)
            ok = True
            if not (pa.actividadFecha>=fechaInicio.date() and pa.actividadFecha<=fechaFinalizacion.date()):
                ok = False
            else:
                if searchString is not None and searchString != u'':
                    if searchString.isdigit():
                        if pa.actividadId != int(searchString):
                           ok = False
                    else:
                        if not pa.lookInto(searchString):
                            ok = False
                    if ok:
                        if marcaAlias is not None and marcaAlias != u'' and marcaAlias.lower() == u'suscripciones':
                            ok = self.puede_reservar_actividad(pa.actividadId)
                        if marcaAlias is not None and marcaAlias != u'' \
                                and marcaAlias.lower() not in ['todos', 'suscripciones']:
                            if pa.actividadAliasMarca != marcaAlias:
                                ok = False
                        if instructor is not None and instructor != u'' and instructor.lower() != u'todos':
                            if pa.actividadNombreInstructor != instructor:
                                ok = False
                        if disciplina is not None and disciplina != u'' and disciplina.lower() != u'todos':
                            if pa.actividadDisciplinaNombre != disciplina:
                                ok = False
                        if localidad is not None and localidad != u'' and localidad.lower() != u'todos':
                            if pa.actividadMarca.m_municipio.z_municipio != localidad:
                                ok = False
                else:
                    if marcaAlias is not None and marcaAlias != u'' and marcaAlias.lower() == u'suscripciones':
                        ok = self.puede_reservar_actividad(pa.actividadId)
                    if marcaAlias is not None and marcaAlias != u'' \
                            and marcaAlias.lower() not in ['todos', 'suscripciones']:
                        if pa.actividadAliasMarca != marcaAlias:
                            ok=False
                    if instructor is not None and instructor != u'' and instructor.lower() != u'todos':
                        if pa.actividadNombreInstructor != instructor:
                            ok=False
                    if disciplina is not None and disciplina != u'' and disciplina.lower() != u'todos':
                        if pa.actividadDisciplinaNombre!=disciplina:
                            ok=False
                    if localidad is not None and localidad != u'' and localidad.lower() != u'todos':
                        try:
                            if pa.actividadMarca.m_municipio.z_municipio != localidad:
                                ok=False
                        except:
                            if localidad != 'indefinida':
                                ok=False
            return (ok,pa)

        def remover(duplicados):
            final_list = []
            for num in duplicados:
                if num not in final_list:
                    final_list.append(num)
            return final_list

        apaActividadesTodas=[]
        apaMisActividades=[]

        manejoFechas=ManejoFechas()

        try:
            fechaInicio=manejoFechas.dateStr2DateTime(request.GET['fechaInicio'])
        except:
            fechaInicio=datetime.today()
        try:
            fechaFinalizacion=manejoFechas.dateStr2DateTime(request.GET['fechaFinalizacion'])
        except:
            fechaFinalizacion = datetime.today() + timedelta(days=365)

        if 'disciplina' in request.GET:
            disciplina = request.GET['disciplina']
        else:
            disciplina=None
        if 'localidad' in request.GET:
            localidad = request.GET['localidad']
        else:
            localidad=None
        if 'instructor' in request.GET:
            instructor = request.GET['instructor']
        else:
            instructor=None
        if 'marcaAlias' in request.GET:
            marcaAlias = request.GET['marcaAlias']
        else:
            marcaAlias='Suscripciones'
        if 'searchString' in request.GET:
            searchString = request.GET['searchString']
        else:
            searchString=None
        if soloFuturas:
            tipoTodas = TipoEstatus().tipoTodasFuturas
        else:
            tipoTodas = TipoEstatus().tipoTodasPlus

        actividadesTodas = Actividad.objects.filter(ac_marca__in=self.atletaMarcas(), ac_estado_id__in=tipoTodas, \
                            ac_fecha__gte=fechaInicio, ac_fecha__lte=fechaFinalizacion) \
                            .values('id').order_by('ac_fecha', 'ac_hora_ini').exclude(ac_estado_id='En Conflicto')

        misReservas = self.actividadesReservadas(soloFuturas)
        misEsperas = self.actividadesEnListaDeEspera(soloFuturas)
        misHistoricas=self.actividadesHistoricas()

        misActividades = []

        listaTotalActividades = sorted(misReservas + misEsperas + misHistoricas, key=lambda k: k['actividadFecha'])

        for actividad in listaTotalActividades:
            misActividades.append(actividad['actividadId'])

        for actividad in actividadesTodas:
            resultado=chequearValidez(actividad['id'])
            ok=resultado[0]
            pa=resultado[1]
            if ok:
                apaActividadesTodas.append(pa)

        misActividades=remover(misActividades)
        for actividadId in misActividades:
            resultado=chequearValidez(actividadId)
            ok=resultado[0]
            pa=resultado[1]
            if ok:
               apaMisActividades.append(pa)

        return (apaActividadesTodas,apaMisActividades)

    def actividadesVigentesEntreFechas(self, fechaInicio=None, fechaFinalizacion=None, disciplina=None, localidad=None, instructor=None, marcaAlias=None,fitroEnSoloLasMias=False):
        if fechaInicio==None:
            dt=datetime.today()
            start = dt
            end = start + timedelta(days=365)
        else:
            start = datetime.strptime(fechaInicio, '%Y-%m-%d')
            if fechaFinalizacion==None:
                end = start + timedelta(days=6)
            else:
                end = datetime.strptime(fechaFinalizacion, '%Y-%m-%d')
        apa = []
        tipoVigente = TipoEstatus().tipoVigente
        misReservas = self.actividadesReservadas()
        misEsperas = self.actividadesEnListaDeEspera()
        misActividades = []
        for actividad in misReservas + misEsperas:
            misActividades.append(actividad['actividadId'])
        if marcaAlias==None or marcaAlias==u'' or marcaAlias.upper()==u'TODOS' or marcaAlias.upper()==u'SOLOLASMIAS':
            if marcaAlias and marcaAlias.upper()==u'SOLOLASMIAS': #Esta es la logica cuando viene del calendario
                actividadesVigentes = Actividad.objects.filter(id__in=misActividades, ac_estado_id__in=tipoVigente,ac_fecha__gte=start, ac_fecha__lte=end) \
                    .values('id').order_by('ac_fecha', 'ac_hora_ini')
            else:
                if fitroEnSoloLasMias:
                    actividadesVigentes = Actividad.objects.filter(id__in=misActividades, ac_estado_id__in=tipoVigente,
                                                                   ac_fecha__gte=start, ac_fecha__lte=end) \
                        .values('id').order_by('ac_fecha', 'ac_hora_ini')
                else:
                    actividadesVigentes = Actividad.objects.filter(ac_estado_id__in=tipoVigente,
                                                                   ac_fecha__gte=start, ac_fecha__lte=end) \
                        .values('id').order_by('ac_fecha', 'ac_hora_ini')
        else:
            if fitroEnSoloLasMias:
                if marcaAlias:
                    actividadesVigentes = Actividad.objects.filter(id__in=misActividades, ac_marca__m_alias=marcaAlias,
                                                                   ac_estado_id__in=tipoVigente,
                                                                   ac_fecha__gte=start, ac_fecha__lte=end) \
                        .values('id').order_by('ac_fecha', 'ac_hora_ini')
                else:
                    actividadesVigentes = Actividad.objects.filter(id__in=misActividades, ac_estado_id__in=tipoVigente,
                                                                   ac_fecha__gte=start, ac_fecha__lte=end) \
                        .values('id').order_by('ac_fecha', 'ac_hora_ini')


        for actividad in actividadesVigentes:
            pa = PerfilActividad(actividad['id'])
            ok=True
            if disciplina is not None and disciplina !=u'':
                if pa.actividadDisciplinaNombre!=disciplina:
                    ok=False
            if localidad is not None and localidad!=u'':
                if pa.actividadMarca.m_municipio.z_municipio!=localidad:
                    ok=False
            if ok:
                apa.append(pa)
        return apa

    def actividadesNoVigentesEntreFechas(self, fechaInicio=None, fechaFinalizacion=None, disciplina=None, localidad=None,instructor=None, marcaAlias=None,fitroEnSoloLasMias=False):
        if fechaInicio==None:
            dt=datetime.today()
            start = dt - timedelta(days=365)
            end = dt
        else:
            start = datetime.strptime(fechaInicio, '%Y-%m-%d')
            if fechaFinalizacion==None:
                end = start + timedelta(days=6)
            else:
                end = datetime.strptime(fechaFinalizacion, '%Y-%m-%d')
        apa = []
        tipoNoVigente = TipoEstatus().tipoNoVigente

        misHistoricas = self.actividadesHistoricas()
        misActividades = []
        for actividad in misHistoricas:
            misActividades.append(actividad['actividadId'])

        if marcaAlias == None or marcaAlias == u'' or marcaAlias.upper() == u'TODOS' or marcaAlias.upper() == u'SOLOLASMIAS':
            if marcaAlias and marcaAlias.upper() == u'SOLOLASMIAS':
                actividadesNoVigentes = Actividad.objects.filter(id__in=misActividades, ac_estado_id__in=tipoNoVigente,
                                                               ac_fecha__gte=start, ac_fecha__lte=end) \
                    .values('id').order_by('-ac_fecha', '-ac_hora_ini')
            else:
                if fitroEnSoloLasMias:
                    actividadesNoVigentes = Actividad.objects.filter(id__in=misActividades,
                                                                   ac_estado_id__in=tipoNoVigente,
                                                                   ac_fecha__gte=start, ac_fecha__lte=end) \
                        .values('id').order_by('-ac_fecha', '-ac_hora_ini')
                else:
                    actividadesNoVigentes = Actividad.objects.filter(ac_estado_id__in=tipoNoVigente,
                                                                   ac_fecha__gte=start, ac_fecha__lte=end) \
                        .values('id').order_by('-ac_fecha', '-ac_hora_ini')
        else:
            if fitroEnSoloLasMias:
                if marcaAlias:
                    actividadesNoVigentes = Actividad.objects.filter(id__in=misActividades,
                                                                   ac_marca__m_alias=marcaAlias,
                                                                   ac_estado_id__in=tipoNoVigente,
                                                                   ac_fecha__gte=start, ac_fecha__lte=end) \
                        .values('id').order_by('-ac_fecha', '-ac_hora_ini')
                else:
                    actividadesNoVigentes = Actividad.objects.filter(id__in=misActividades,
                                                                   ac_estado_id__in=tipoNoVigente,
                                                                   ac_fecha__gte=start, ac_fecha__lte=end) \
                        .values('id').order_by('-ac_fecha', '-ac_hora_ini')

        for actividad in actividadesNoVigentes:
            pa = PerfilActividad(actividad['id'])
            ok=True
            if disciplina is not None and disciplina !=u'':
                if pa.actividadDisciplinaNombre!=disciplina:
                    ok=False
            if localidad is not None and localidad!=u'':
                if pa.actividadMarca.m_municipio!=localidad:
                    ok=False
            if ok:
                apa.append(pa)
        return apa

    def actividadesPlanificadasEntreFechas(self, fechaInicio=None, fechaFinalizacion=None, disciplina=None, localidad=None,instructor=None, marcaAlias=None):
        if fechaInicio==None:
            dt=datetime.today()
            start = dt - timedelta(days=dt.weekday())
            end = start + timedelta(days=6)
        else:
            start = datetime.strptime(fechaInicio, '%Y-%m-%d')
            if fechaFinalizacion==None:
                end = start + timedelta(days=6)
            else:
                end = datetime.strptime(fechaFinalizacion, '%Y-%m-%d')
        apa = []
        tipoPlanificadas = ['Planifico']
        if marcaAlias==None or marcaAlias==u'' or marcaAlias.upper()==u'TODOS' or marcaAlias.upper()==u'SOLOLASMIAS':
            actividadesPlanificadas = Actividad.objects.filter(ac_marca__in=self.atletaMarcas(),ac_estado_id__in=tipoPlanificadas,\
                ac_fecha__gte=start,ac_fecha__lte=end) \
                .values('id').order_by('-ac_fecha', '-ac_hora_ini')
        else:
            actividadesPlanificadas = Actividad.objects.filter(ac_marca__in=self.atletaMarcas(),ac_estado_id__in=tipoPlanificadas,ac_marca__m_alias=marcaAlias,\
                ac_fecha__gte=start,ac_fecha__lte=end) \
                .values('id').order_by('-ac_fecha', '-ac_hora_ini')


        for actividad in actividadesPlanificadas:
            pa = PerfilActividad(actividad['id'])
            ok=True
            if disciplina is not None and disciplina !=u'':
                if pa.actividadDisciplinaNombre!=disciplina:
                    ok=False
            if localidad is not None and localidad!=u'':
                if pa.actividadMarca.m_municipio!=localidad:
                    ok=False
            if ok:
                apa.append(pa)
        return apa

    def puede_reservar_actividad(self, actividadId):
        vs = self.vs
        actividad=Actividad.objects.get(id=actividadId)
        actividadInstructor = actividad.ac_instructor
        marcaActividadId=actividad.ac_marca_id

        try:
            if vs.userAlias == actividadInstructor.u_alias:
                return False
            else:
                try:
                    vicsafe = VicSafe(self.atletaId, marcaActividadId, None)
                    resultado = vicsafe.puedeReservarActividad(actividadId, vs) is not None
                    return resultado
                except:
                    return False
        except:
            return False

class PerfilInstructor(PerfilAtleta):
    """Facilita el despliegue de informacion en template del perfil del instructor"""

    def ingresosPorPercibir(self,marcaIn=None):
        vs = self.vs
        porDevengarMeses = []
        if vs.tipoSesion == vs.ATLETA:
            if marcaIn:
                actividadesMensuales = Actividad.objects.filter(ac_instructor__u_alias=self.atletaAlias,
                            ac_marca__m_alias=marcaIn,
                            ac_fecha__gt=datetime.today()) \
                    .exclude(ac_estado__ea_estado__in=['Cancelada']) \
                    .values('ac_marca__m_nombre') \
                    .annotate(month=TruncMonth('ac_fecha')) \
                    .values('ac_marca__m_nombre', 'month') \
                    .annotate(total=Sum('ac_precio')) \
                    .values('ac_marca__m_nombre', 'month', 'total') \
                    .annotate(cantidad=Count('ac_precio')) \
                    .values('ac_marca__m_nombre', 'month', 'total', 'cantidad') \
                    .order_by('ac_marca__m_nombre', '-month')
            else:
                actividadesMensuales = Actividad.objects.filter(ac_instructor__u_alias=self.atletaAlias,
                                                                ac_fecha__gt=datetime.today()) \
                    .exclude(ac_estado__ea_estado__in=['Cancelada']) \
                    .values('ac_marca__m_nombre') \
                    .annotate(month=TruncMonth('ac_fecha')) \
                    .values('ac_marca__m_nombre', 'month') \
                    .annotate(total=Sum('ac_precio')) \
                    .values('ac_marca__m_nombre', 'month', 'total') \
                    .annotate(cantidad=Count('ac_precio')) \
                    .values('ac_marca__m_nombre', 'month', 'total', 'cantidad') \
                    .order_by('ac_marca__m_nombre', '-month')
        else:
            actividadesMensuales = Actividad.objects.filter(ac_instructor__u_alias=self.atletaAlias,
                                                            ac_marca__m_alias=vs.marcaEnUso.m_alias,
                                                            ac_fecha__gt=datetime.today()) \
                .exclude(ac_estado__ea_estado__in=['Cancelada']) \
                .values('ac_marca__m_nombre') \
                .annotate(month=TruncMonth('ac_fecha')) \
                .values('ac_marca__m_nombre', 'month') \
                .annotate(total=Sum('ac_precio')) \
                .values('ac_marca__m_nombre', 'month', 'total') \
                .annotate(cantidad=Count('ac_precio')) \
                .values('ac_marca__m_nombre', 'month', 'total', 'cantidad') \
                .order_by('ac_marca__m_nombre', '-month')

        for actividadMensual in actividadesMensuales:
            month = getmes(actividadMensual['month'].month - 1)
            year = actividadMensual['month'].year
            mes = month + ' ' + str(year)
            marca = actividadMensual['ac_marca__m_nombre']
            total = self.bolivares(actividadMensual['total'])
            cantidad = actividadMensual['cantidad']
            porDevengarMes = {}
            porDevengarMes['marca'] = marca
            porDevengarMes['mes'] = mes
            porDevengarMes['total'] = total
            porDevengarMes['cantidad'] = cantidad
            porDevengarMeses.append(porDevengarMes)
        return porDevengarMeses

    def ingresosYaPercibidos(self,marcaIn=None):
        vs = self.vs
        devengadoMeses = []
        if vs.tipoSesion == vs.ATLETA:
            if marcaIn:
                actividadesMensuales = Actividad.objects.filter(ac_instructor__u_alias=self.atletaAlias,
                            ac_marca__m_alias=marcaIn,
                            ac_fecha__lte=datetime.today()) \
                    .exclude(ac_estado__ea_estado__in=['Cancelada']) \
                    .values('ac_marca__m_nombre') \
                    .annotate(month=TruncMonth('ac_fecha')) \
                    .values('ac_marca__m_nombre', 'month') \
                    .annotate(total=Sum('ac_precio')) \
                    .values('ac_marca__m_nombre', 'month', 'total') \
                    .annotate(cantidad=Count('ac_precio')) \
                    .values('ac_marca__m_nombre', 'month', 'total', 'cantidad') \
                    .order_by('ac_marca__m_nombre', '-month')
            else:
                actividadesMensuales = Actividad.objects.filter(ac_instructor__u_alias=self.atletaAlias,
                                                                ac_fecha__lte=datetime.today()) \
                    .exclude(ac_estado__ea_estado__in=['Cancelada']) \
                    .values('ac_marca__m_nombre') \
                    .annotate(month=TruncMonth('ac_fecha')) \
                    .values('ac_marca__m_nombre', 'month') \
                    .annotate(total=Sum('ac_precio')) \
                    .values('ac_marca__m_nombre', 'month', 'total') \
                    .annotate(cantidad=Count('ac_precio')) \
                    .values('ac_marca__m_nombre', 'month', 'total', 'cantidad') \
                    .order_by('ac_marca__m_nombre', '-month')
        else:
            actividadesMensuales = Actividad.objects.filter(ac_instructor__u_alias=self.atletaAlias,
                                                            ac_marca__m_alias=vs.marcaEnUso.m_alias,
                                                            ac_fecha__lte=datetime.today()) \
                .exclude(ac_estado__ea_estado__in=['Cancelada']) \
                .values('ac_marca__m_nombre') \
                .annotate(month=TruncMonth('ac_fecha')) \
                .values('ac_marca__m_nombre', 'month') \
                .annotate(total=Sum('ac_precio')) \
                .values('ac_marca__m_nombre', 'month', 'total') \
                .annotate(cantidad=Count('ac_precio')) \
                .values('ac_marca__m_nombre', 'month', 'total', 'cantidad') \
                .order_by('ac_marca__m_nombre', '-month')

        for actividadMensual in actividadesMensuales:
            month = getmes(actividadMensual['month'].month - 1)
            year = actividadMensual['month'].year
            mes = month + ' ' + str(year)
            marca = actividadMensual['ac_marca__m_nombre']
            total = self.bolivares(actividadMensual['total'])
            cantidad = actividadMensual['cantidad']
            devengadoMes = {}
            devengadoMes['marca'] = marca
            devengadoMes['mes'] = mes
            devengadoMes['total'] = total
            devengadoMes['cantidad'] = cantidad
            devengadoMeses.append(devengadoMes)
        return devengadoMeses

    def actividadesPorImpartir(self,marcaIn=None):
        vs = self.vs
        try:
            if vs.tipoSesion == vs.ATLETA:
                if marcaIn:
                    a = [[obj.id, obj.fechaHoraActividad] for obj in Actividad.objects.all()
                         if obj.fechaHoraActividad > datetime.today()
                         and obj.ac_instructor.u_alias == self.atletaAlias
                         and obj.ac_marca.m_alias == marcaIn
                         ]
                else:
                    a = [[obj.id, obj.fechaHoraActividad] for obj in Actividad.objects.all()
                         if obj.fechaHoraActividad > datetime.today()
                         and obj.ac_instructor.u_alias == self.atletaAlias
                         ]
            else:
                a = [[obj.id, obj.fechaHoraActividad] for obj in Actividad.objects.all()
                     if obj.fechaHoraActividad > datetime.today()
                     and obj.ac_instructor.u_alias == self.atletaAlias
                     and obj.ac_marca.m_alias == vs.marcaEnUso.m_alias
                     ]
            pk_list=[i[0] for i in a]
        except Exception as e:
            pass

        actividades = Actividad.objects.filter(id__in=pk_list).order_by('ac_fecha', 'ac_hora_ini').values('id')
        return self.armarJsonActividadesInstructor(actividades)

    def actividadesYaImpartidas(self,marcaIn=None):
        vs = self.vs
        try:
            if vs.tipoSesion == vs.ATLETA:
                if marcaIn:
                    a = [[obj.id, obj.fechaHoraActividad] for obj in Actividad.objects.all()
                         if obj.fechaHoraActividad <= datetime.today()
                         and obj.fechaHoraActividad > datetime.today() - timedelta(days=360)
                         and obj.ac_instructor.u_alias == self.atletaAlias
                         and obj.ac_marca.m_alias == marcaIn
                         ]
                else:
                    a = [[obj.id, obj.fechaHoraActividad] for obj in Actividad.objects.all()
                         if obj.fechaHoraActividad <= datetime.today()
                         and obj.fechaHoraActividad > datetime.today() - timedelta(days=360)
                         and obj.ac_instructor.u_alias == self.atletaAlias
                         ]
            else:
                a = [[obj.id, obj.fechaHoraActividad] for obj in Actividad.objects.all()
                     if obj.fechaHoraActividad <= datetime.today()
                     and obj.fechaHoraActividad > datetime.today()-timedelta(days=360)
                     and obj.ac_instructor.u_alias == self.atletaAlias
                     and obj.ac_marca.m_alias == vs.marcaEnUso.m_alias
                     ]

            pk_list=[i[0] for i in a]
        except Exception as e:
            pass

        actividades = Actividad.objects.filter(id__in=pk_list).order_by('-ac_fecha', '-ac_hora_ini').values('id')
        return self.armarJsonActividadesInstructor(actividades)

    def diasUltimaImpartida(self):
        vs = self.vs
        if vs.tipoSesion == vs.ATLETA:
            actividades = Actividad.objects.filter(ac_instructor__u_alias=self.atletaAlias,ac_estado__in=TipoEstatus().tipoNoVigente).order_by('-ac_fecha').values('id')
        else:
            actividades = Actividad.objects.filter(ac_instructor__u_alias=self.atletaAlias,
                                                   ac_marca__m_alias=vs.marcaEnUso.m_alias,ac_estado__in=TipoEstatus().tipoNoVigente).order_by('-ac_fecha').values('id')
        misActividades = []
        for actividad in actividades:
            misActividades.append(actividad['id'])
        if misActividades:
            ultima=PerfilActividad(misActividades[0]).actividadFecha
            return (datetime.today().date()-ultima).days
        else:
            return -1

    def armarJsonActividadesInstructor(self, actividades):
        aAct = []
        for actividad in actividades:
            actJson = PerfilActividad(actividad['id']).resumenActividadJson()
            aAct.append(actJson)
        return aAct

    def profifeInstructor(self):
        return UserProfile.objects.get(id=self.atletaProfileId).u_entrenador_profile

class PerfilActividad:
    """Facilita el despliegue de informacion en template del detalle de la actividad"""

    def __init__(self, actividadIn):
        self.actividadId = actividadIn
        self.actividadNombre = None
        self.actividadInicialesMarca = None
        self.actividadNombreMarca = None
        self.actividadAliasMarca = None
        self.actividadMarca = None
        self.actividadMarcaId=None
        self.actividadDescripcionMarca = None
        self.actividadFecha = None
        self.actividadFechaParaReservar = None
        self.actividadTiempoFaltanteParaReservar = None
        self.actividadHoraInicio = None
        self.actividadHoraFinalizacion = None
        self.actividadDuracion = None
        self.actividadDisciplinaNombre = None
        self.actividadDisciplinaImagenNormal = None
        self.actividadDisciplinaImagenNegra = None
        self.actividadNombreInstructor = None
        self.actividadInstructorId = None
        self.actividadInstructorAlias = None
        self.actividadNombreAyudante1 = None
        self.actividadAyudante1Id = None
        self.actividadAyudante1Alias = None
        self.actividadNombreAyudante2 = None
        self.actividadAyudante2Id = None
        self.actividadAyudante2Alias = None
        self.actividadSalonNombre = None
        self.actividadSalonUbicacion = None
        self.actividadCapacidadMaxima = None
        self.actividadCapacidadMinima = None
        self.actividadCapacidadEspera = None
        self.actividadReservados = None
        self.actividadEspera = None
        self.actividadCapacidadLlena = None
        self.actividadEsperandoLocacion = None
        self.actividadEstado = None
        self.actividadEstadoImprimible=None
        self.actividadIntensidad = None
        self.actividadDescripcion = None
        self.actividadInstrucciones = None
        self.actividadAbiertaParaReservar = None
        self.actividadAbiertaParaEliminar = None
        self.actividadAbiertaParaCancelar = None
        self.actividadAbiertaParaEditar = None
        self.actividadAbiertaParaGestionar = None
        self.actividadRepetirComo = None
        self.actividadAsistencia = None
        self.actividadCreditos = None
        self.actividadBonificacionBase = None
        self.actividadBonificacionAdicional = None
        self.actividadSePuedeCancelar = None
        self.actividadAbiertaMarcarParaAsistencia = None
        self.actividadProductosPermitidos=None
        self.actividadProductosPermitidosNombres=None
        self.actividadAvisoQuedanPuestos=None
        self.actividadReferenciada=None
        self.actividadLocalizador=None
        self.actividadInstructorProfile=None
        self.actividadEsSerie=None
        self.actividadSerieIdOriginaria = None
        self.actividadBaseSerieId = None
        self.actividadClaseCSS=None
        self.actividadTiempoIrreversible=None
        self.cargaInfoActividad()

    def cargaInfoActividad(self):
        tipos = dict((
            ('LM', 'Lunes, Miercoles y Viernes'),
            ('MJ', 'Martes y Jueves'),
            ('LV', 'Lunes a Viernes'),
            ('DI', 'Diario'),
            ('SM', 'Semanal'),
            ('', ''),))
        actividad = Actividad.objects.filter(id=self.actividadId)[0]
        self.actualizarCupos(actividad)
        self.actividadNombre = actividad.ac_nombre
        self.actividadMarca = actividad.ac_marca
        self.actividadMarcaId=actividad.ac_marca_id
        self.actividadInicialesMarca = actividad.ac_marca.m_iniciales
        self.actividadNombreMarca = actividad.ac_marca.m_nombre
        self.actividadAliasMarca = actividad.ac_marca.m_alias
        self.actividadDescripcionMarca = actividad.ac_marca.m_descripcion
        self.actividadFecha = actividad.ac_fecha
        self.actividadFechaParaReservar = datetime.today()
        self.actividadHoraInicio = actividad.ac_hora_ini
        self.actividadHoraFinalizacion = actividad.ac_hora_fin
        self.actividadDuracion = None
        self.actividadDisciplinaNombre = actividad.ac_disciplina.d_nombre
        self.actividadDisciplinaImagenNormal = actividad.ac_disciplina.d_imagen
        self.actividadDisciplinaImagenNegra = actividad.ac_disciplina.d_imagen_negra
        self.actividadProductosPermitidos=actividad.ac_productos_permitidos
        if self.actividadProductosPermitidos:
            self.actividadProductosPermitidosNombres=Producto.objects.filter(id__in=self.actividadProductosPermitidos).values('p_nombre')
        else:
            self.actividadProductosPermitidosNombres=['TODOS']
        self.actividadReferenciada=actividad.ac_referenciado
        if actividad.ac_instructor:
            self.actividadNombreInstructor = actividad.ac_instructor.u_user.first_name + ' ' + \
                                             actividad.ac_instructor.u_user.last_name
            self.actividadInstructorId = actividad.ac_instructor.id
            self.actividadInstructorAlias = actividad.ac_instructor.u_alias
            self.actividadInstructorIniciales = actividad.ac_instructor.u_iniciales
            if self.actividadInstructorId:
                self.actividadInstructorProfile=UserProfile.objects.get(id=self.actividadInstructorId).u_entrenador_profile
            else:
                self.actividadInstructorProfile=''
        else:
            self.actividadNombreInstructor = "Sin Instructor"
            self.actividadInstructorId = None
            self.actividadInstructorAlias = "Sin Instructor"
            self.actividadInstructorIniciales = "---"
        try:
            if actividad.ac_colaborador1:
                self.actividadAyudante1Id = actividad.ac_colaborador1
                self.actividadAyudante1Alias = UserProfile.objects.get(id=self.actividadAyudante1Id).u_alias
                self.actividadAyudante1Iniciales = UserProfile.objects.get(id=self.actividadAyudante1Id).u_iniciales
                self.actividadNombreAyudante1 = UserProfile.objects.get(
                    id=self.actividadAyudante1Id).u_user.first_name + ' ' + \
                                                UserProfile.objects.get(id=self.actividadAyudante1Id).u_user.last_name
            else:
                self.actividadNombreAyudante1 = "Sin Ayudante"
                self.actividadAyudante1Id = None
                self.actividadAyudante1Alias = "Sin Ayudante"
                self.actividadAyudante1Iniciales = "---"
        except:
            pass
        try:
            if actividad.ac_colaborador2:
                self.actividadAyudante2Id = actividad.ac_colaborador2
                self.actividadAyudante2Alias = UserProfile.objects.get(id=self.actividadAyudante2Id).u_alias
                self.actividadAyudante2Iniciales = UserProfile.objects.get(id=self.actividadAyudante2Id).u_iniciales
                self.actividadNombreAyudante2 = UserProfile.objects.get(
                    id=self.actividadAyudante2Id).u_user.first_name + ' ' + \
                                                UserProfile.objects.get(id=self.actividadAyudante2Id).u_user.last_name
            else:
                self.actividadNombreAyudante2 = "Sin Ayudante"
                self.actividadAyudante2Id = None
                self.actividadAyudante2Alias = "Sin Ayudante"
                self.actividadAyudante2Iniciales = "---"
        except:
            pass

        if actividad.ac_salon:
            self.actividadSalonNombre = actividad.ac_salon.s_nombre
        else:
            self.actividadSalonNombre = "Sin Sala"
        self.actividadSalonUbicacion = self.actividadMarca.m_municipio
        self.actividadCapacidadMaxima = actividad.ac_cap_max
        self.actividadCapacidadMinima = actividad.ac_cap_min
        self.actividadReservados = actividad.ac_cupos_reservados
        self.actividadCapacidadEspera = actividad.ac_cap_max_espera
        self.actividadEspera = actividad.ac_cupos_en_espera
        if self.actividadCapacidadMaxima>0:
            self.actividadCapacidadLlena = ((actividad.ac_cap_max + actividad.ac_cap_max_espera) <= (
                    actividad.ac_cupos_reservados + actividad.ac_cupos_en_espera))
            self.actividadEsperandoLocacion=False
        else:
            self.actividadCapacidadLlena=False
            self.actividadEsperandoLocacion=True
        self.actividadEstado = actividad.ac_estado.ea_estado
        if self.actividadEstado=='Planifico':
            self.actividadFechaParaReservar=self.actividadFecha+timedelta(days=-actividad.ac_marca.m_est_rrev)
            self.actividadTiempoFaltanteParaReservar=(self.actividadFechaParaReservar - datetime.today().date()).days
        self.actividadImagenEstado = actividad.ac_estado.ea_imagen
        self.actividadIntensidad = actividad.ac_intensidad
        self.actividadDescripcion = actividad.ac_descripcion
        self.actividadInstrucciones = actividad.ac_instrucciones
        self.actividadAbiertaParaReservar = actividad.ac_estado.ea_estado in ['Abierta Reversible',
                                                                              'Abierta Irreversible']
        if self.actividadSalonNombre=="Sin Sala":
           self.actividadAbiertaParaReservar=False

        self.actividadAbiertaParaEliminar = actividad.ac_estado.ea_estado in ['Cancelada','Planifico','En Conflicto']
        self.actividadAbiertaParaCancelar = actividad.ac_estado.ea_estado in ['Abierta Reversible','Abierta Irreversible','Planifico']
        self.actividadAbiertaParaEditar = actividad.ac_estado.ea_estado in ['Abierta Reversible', 'Abierta Irreversible', 'Planifico', 'Cancelada','En Conflicto']
        self.actividadAbiertaParaGestionar = actividad.ac_estado.ea_estado in ['Abierta Reversible','Abierta Irreversible']
        self.actividadAbiertaMarcarParaAsistencia = actividad.ac_estado.ea_estado in ['Activa','Culminada']
        self.actividadRepetirComo = tipos[actividad.ac_repetirComo]
        self.actividadAsistencia = Participantes.objects.filter(pa_actividad_id=self.actividadId,
                                                                pa_asistencia=True).count()
        self.actividadCreditos = actividad.ac_creditos
        self.actividadBonificacionBase = actividad.ac_precio
        self.actividadBonificacionAdicional = actividad.ac_bono
        self.actividadDuracion = self.actividadHoraFinalizacion.hour * 60 + self.actividadHoraFinalizacion.minute
        self.actividadDuracion -= self.actividadHoraInicio.hour * 60 + self.actividadHoraInicio.minute
        self.actividadDuracion = str(int(math.floor(self.actividadDuracion / 60))) + ':' + str(
            (self.actividadDuracion % 60))
        topeparacancelar = datetime.today()
        topeparacancelar = topeparacancelar.replace(day=actividad.ac_fecha.day, month=actividad.ac_fecha.month,
                                                    year=actividad.ac_fecha.year)
        topeparacancelar = topeparacancelar.replace(hour=actividad.ac_hora_ini.hour,
                                                    minute=actividad.ac_hora_ini.minute)
        topeparacancelar = topeparacancelar + timedelta(minutes=actividad.ac_marca.m_est_irrev)
        sepuedecancelar = (topeparacancelar > datetime.today())
        self.actividadSePuedeCancelar = sepuedecancelar

        porcentaje=Marca.objects.get(m_alias=self.actividadMarca.m_alias).m_porcentaje_aviso_cupos_restantes

        cantidadAviso=self.actividadCapacidadMaxima-porcentaje*self.actividadCapacidadMaxima/100
        if cantidadAviso>=(self.actividadCapacidadMaxima-self.actividadReservados) and self.actividadReservados<self.actividadCapacidadMaxima:
            self.actividadAvisoQuedanPuestos = str(cantidadAviso)+' puestos'
        else:
            self.actividadAvisoQuedanPuestos = ''

        if self.actividadEstado in TipoEstatus().tipoVigente:
            self.actividadClaseCSS="bg-info"
            self.actividadEstadoImprimible = self.actividadEstado.upper()
        elif self.actividadEstado=='Planifico':
            self.actividadEstadoImprimible = 'PRÓXIMAMENTE'
            self.actividadClaseCSS = "bg-secondary"
        elif self.actividadEstado=='Culminada':
            self.actividadEstadoImprimible = 'FINALIZADA'
            self.actividadClaseCSS = "bg-primary"
        elif self.actividadEstado=='Activa':
            self.actividadEstadoImprimible = 'EN PROGRESO'
            self.actividadClaseCSS = "bg-success"
        elif self.actividadEstado=='Cancelada':
            self.actividadEstadoImprimible = 'SUSPENDIDA'
            self.actividadClaseCSS = "bg-danger"
        elif self.actividadEstado=='En Conflicto':
            self.actividadEstadoImprimible = 'En Conflicto'
            self.actividadClaseCSS = "bg-warning"

        # if self.actividadCapacidadLlena:
        #     self.actividadEstadoImprimible = 'NO HAY CUPOS'

        self.actividadLocalizador='{0}{1}{2}{3}-{4}'.format(self.actividadInicialesMarca,
                                                            self.actividadFecha.year-2000,
                                                            '{:02}'.format(self.actividadFecha.month),
                                                            '{:02}'.format(self.actividadFecha.day),
                                                            self.actividadId)
        if actividad.ac_OpcionSerie=='Si':
            self.actividadEsSerie=True
            self.actividadBaseSerieId=actividad.ac_actividadBaseSerieId
        else:
            self.actividadEsSerie=False
            self.actividadBaseSerieId = actividad.ac_actividadBaseSerieId
            self.actividadSerieIdOriginaria = actividad.ac_serieId_originaria

        self.actividadTiempoIrreversible=actividad.ac_marca.m_est_irrev


    def resumenActividadJson(self):
        actividad = Actividad.objects.filter(id=self.actividadId)[0]
        actJson = {}
        actJson['actividadId'] = actividad.id
        actJson['actividadNombre'] = actividad.ac_nombre
        actJson['actividadInicialesMarca'] = actividad.ac_marca.m_iniciales
        actJson['actividadNombreMarca'] = actividad.ac_marca.m_nombre
        actJson['actividadMarcaId'] = actividad.ac_marca_id
        actJson['actividadFecha'] = actividad.ac_fecha
        actJson['actividadHoraInicio'] = actividad.ac_hora_ini
        actJson['actividadDisciplinaNombre'] = actividad.ac_disciplina.d_nombre
        actJson['actividadDisciplinaImagenNormal'] = actividad.ac_disciplina.d_imagen
        actJson['actividadDisciplinaImagenNegra'] = actividad.ac_disciplina.d_imagen_negra
        actJson['actividadInstructorNombre'] = self.actividadNombreInstructor
        actJson['actividadInstructorAlias'] = self.actividadInstructorAlias
        actJson['actividadEstado'] = self.actividadEstado
        actJson['actividadCreditos'] = self.actividadCreditos
        actJson['actividadCapacidadLlena'] = self.actividadCapacidadLlena
        actJson['actividadAbiertaListaEspera'] = (self.actividadCapacidadMaxima == self.actividadReservados)
        actJson['actividadSePuedeCancelar'] = self.actividadSePuedeCancelar
        actJson['actividadBonificacionBase'] = self.actividadBonificacionBase
        actJson['actividadAbiertaParaReservar'] = self.actividadAbiertaParaReservar
        actJson['actividadReferenciada'] = self.actividadReferenciada
        return actJson

    def actividadParticipantes(self):
        participantes = Participantes.objects.filter(pa_actividad_id=self.actividadId).order_by('pa_num_cupo')
        aParticipantes = []
        for participante in participantes:
            pa = PerfilBasicoAtleta(participante.pa_usuario.profile.u_alias)
            aParticipantes.append(self.participanteJson(pa, participante))
        return aParticipantes

    def participanteJson(self, pa, participante):
        pj = {}
        pj['participanteId'] = participante.id
        pj['participanteUserId'] = pa.atletaId
        pj['participanteNombre'] = pa.atletaNombres
        pj['participanteAlias'] = pa.atletaAlias
        pj['participanteIniciales'] = pa.atletaIniciales
        pj['participanteSaldo'] = pa.saldoEnMarca(self.actividadAliasMarca)['saldoCompuesto']
        pj['participantePuesto'] = participante.pa_num_cupo
        pj['participanteAsistio'] = participante.pa_asistencia
        pj['participanteEsPublico'] = pa.atletaEsPublico
        return pj

    def actividadEsperas(self):
        esperas = Espera.objects.filter(es_actividad_id=self.actividadId)
        aEsperas = []
        for espera in esperas:
            pa = PerfilBasicoAtleta(espera.es_usuario.profile.u_alias)
            aEsperas.append(self.esperaJson(pa, espera))
        return aEsperas

    def esperaJson(self, pa, espera):
        ej = {}
        ej['participanteUserId'] = pa.atletaId
        ej['participanteNombre'] = pa.atletaNombres
        ej['participanteAlias'] = pa.atletaAlias
        ej['participanteIniciales'] = pa.atletaIniciales
        ej['participanteSaldo'] = pa.saldoEnMarca(self.actividadAliasMarca)['saldoCompuesto']
        ej['participantePuesto'] = espera.es_num_cupo
        ej['participanteEsPublico'] = pa.atletaEsPublico
        return ej

    def actividadBonificaciones(self):
        actividad = Actividad.objects.filter(id=self.actividadId)[0]
        bonificaciones = {}
        bonificaciones['bonificacionBase'] = actividad.ac_precio
        bonificaciones['bonificacionExtra'] = actividad.ac_bono
        return bonificaciones

    def actualizarCupos(self, actividad):
        hoy = datetime.today()
        haceUnMes = hoy - timedelta(days=30)
        sietedias = hoy + timedelta(days=7)
        participantes = Participantes.objects.filter(pa_actividad_id=actividad.id).count()
        esperas = Espera.objects.filter(es_actividad_id=actividad.id).count()
        if actividad.ac_cupos_reservados != participantes or actividad.ac_cupos_en_espera != esperas:
            actividad.ac_cupos_reservados = participantes
            actividad.ac_cupos_en_espera = esperas
            actividad.save()

    def atletaAsistio(self,atletaId):
        asistio=False
        participantes = self.actividadParticipantes()
        for participante in participantes:
            if participante['participanteUserId']==atletaId:
                asistio=participante['participanteAsistio']
                break
        return asistio

    def atletaPuestoReserva(self,atletaId):
        puesto=''
        participantes = self.actividadParticipantes()
        for participante in participantes:
            if participante['participanteUserId']==atletaId:
                puesto=participante['participantePuesto']
                break
        return puesto

    def atletaReservado(self,atletaId):
        esta=False
        participantes = self.actividadParticipantes()
        for participante in participantes:
            if participante['participanteUserId']==atletaId:
                esta=True
                break
        return esta

    def atletaEnListaEspera(self,atletaId):
        esta=False
        participantes = self.actividadEsperas()
        for participante in participantes:
            if participante['participanteUserId']==atletaId:
                esta=True
                break
        return esta

    def atletaPuestoEnListaEspera(self,atletaId):
        puesto=''
        participantes = self.actividadEsperas()
        for participante in participantes:
            if participante['participanteUserId']==atletaId:
                puesto = participante['participantePuesto']
                break
        return puesto

    def lookInto(self,searchString):
        esta=False
        cadenaObjetivo=self.actividadNombre.lower()+', '
        cadenaObjetivo+=self.actividadNombreInstructor.lower()+', '
        cadenaObjetivo+=self.actividadDisciplinaNombre.lower()+', '
        cadenaObjetivo+=self.actividadInstructorAlias.lower()+', '
        cadenaObjetivo+=self.actividadNombreMarca.lower()+', '
        cadenaObjetivo+=self.actividadNombreAyudante1.lower()+', '
        cadenaObjetivo+=self.actividadNombreAyudante2.lower()+', '
        try:
            cadenaObjetivo+=self.actividadSalonUbicacion.z_municipio.lower()+', '
        except:
            cadenaObjetivo+='indefinida'
        if searchString.lower() in cadenaObjetivo:
            esta=True
        else:
            participantes=self.actividadParticipantes()
            for participante in participantes:
                cadenaObjetivo += participante['participanteNombre'].lower()+', '
                cadenaObjetivo += participante['participanteAlias'].lower()+', '
                if searchString.lower() in cadenaObjetivo:
                    esta=True
                    break
            if not esta:
                esperas = self.actividadEsperas()
                for participante in esperas:
                    cadenaObjetivo += participante['participanteNombre'].lower() + ', '
                    cadenaObjetivo += participante['participanteAlias'].lower() + ', '
                    if searchString.lower() in cadenaObjetivo:
                        esta = True
                        break
        return esta

class VicSafe:
    """Manejo de saldos"""

    ACCIONES = {
        'RA': 'Reserva de Actividad',
        'CR': 'Cancelacion de Reserva',
        'EE': 'Entrada en Lista de Espera',
        'SE': 'Salida de Lista de Espera',
        'PE': 'Promocion desde Lista de Espera',
        'SA': 'Suspension de Actividad',
        'CP': 'Compra de Plan',
        'RS': 'Reintegro Por Suspension',
        'RX': 'Reintegro Por No Participacion',
        'IP': 'Inactivacion de Plan',
    }

    def __init__(self, atletaId, marcaId, vs):
        self.atletaId = atletaId
        self.marcaId = marcaId
        self.vs = vs
        self.hoy = datetime.today()
        self.user = User.objects.get(id=atletaId)
        self.marca = Marca.objects.get(id=marcaId)
        self.saldo = Saldo.objects.get(s_user=self.user, s_marca=self.marca)
        self.userAlias = self.user.profile.u_alias
        self.actualizar_saldo()
        self.saldoActual=self.saldo.s_saldo
        self.usuarioResponsable=None
        if vs:
            self.usuarioResponsable=self.vs.user.username
        else:
            if User.objects.filter(is_superuser=True):
                self.usuarioResponsable = User.objects.filter(is_superuser=True)[0].username

    def saldo_actual_usuario(self):
        pass

    def registrar_compra_plan(self, planParametrosJson):

        # DECLARACION DE CONSTANTES
        TRANSFERENCIA = 0
        DEPOSITO = 1
        POS = 2
        VPOS = 3
        CHEQUE = 4
        EFECTIVO = 5
        POR_COBRAR = 6
        BECA = 7
        MEDIOS = []
        MEDIOS.append('TRANSFERENCIA')
        MEDIOS.append('DEPOSITO')
        MEDIOS.append('POS')
        MEDIOS.append('CHEQUE')
        MEDIOS.append('EFECTIVO')
        MEDIOS.append('POR COBRAR')
        MEDIOS.append('BECA')

        # Parametros de Entrada
        tipoIn = planParametrosJson['tipoIn']
        pagadorIn = User.objects.get(id=self.atletaId)
        productoIn = planParametrosJson['productoIn']
        montoIn = planParametrosJson['montoIn']
        precioIn = planParametrosJson['precioIn']
        dtoGeneralIn = planParametrosJson['dtoGeneralIn']
        dtoParticularIn = planParametrosJson['dtoParticularIn']
        fechaIn = planParametrosJson['fechaIn']
        referenciaIn = planParametrosJson['referenciaIn']
        cuentaIn = planParametrosJson['cuentaIn']

        planAccionadoId=0

        try:
            # Chequeo la existencia previa de esta referencia
            proxReferenciaUso = 0
            if Pago.objects.filter(p_marca_id=self.marcaId, p_referencia__iexact=referenciaIn, p_medio=tipoIn).exists():
                pagos = Pago.objects.filter(p_marca_id=self.marcaId, p_referencia__iexact=referenciaIn,
                                            p_medio=tipoIn).order_by('-p_referencia_uso')
                pago = pagos[0]
                saldo = pago.p_diferencia
                proxReferenciaUso = pago.p_referencia_uso + 1
                montoIn = saldo

            # En caso de Transferencias, depositos y Puntos de Ventas obtengo la cuanta bancaria
            # de lo contrario no es aplicable asi como la referencia

            if tipoIn in [TRANSFERENCIA, DEPOSITO, POS]:
                cuentaIn = Cuenta.objects.get(c_numero_cuenta=cuentaIn)
            else:
                referenciaIn = None
                cuentaIn = None
            statusIn = 0
            porCobrarIn = tipoIn in [POR_COBRAR]
            if porCobrarIn:
                statusIn=3

            # Primero creo el plan
            planOut = Planes()
            planOut.p_nombre = productoIn.p_nombre
            planOut.p_creditos_totales = productoIn.p_creditos
            planOut.p_fecha_obtencion = self.hoy
            planOut.p_fecha_caducidad = self.hoy + timedelta(days=365 / 12 * productoIn.p_duracion_meses)
            planOut.p_marca = self.marca
            planOut.p_usuario = self.user
            planOut.p_producto = productoIn
            planOut.p_tipo = productoIn.p_tipo
            planOut.save()

            planAccionadoId=planOut.id

            # Generacion del codigo interno
            nro = Pago.objects.filter(p_marca=self.marcaId).count() + 1
            codigoInterno = str(self.marcaId) + '-' + fechaIn + '-' + str(nro)


            # Segundo creo el pago
            pagoOut = Pago()
            pagoOut.p_pagador = self.user
            pagoOut.p_marca = self.marca
            pagoOut.p_plan = planOut
            pagoOut.p_producto = productoIn
            pagoOut.p_fecha_registro = self.hoy
            pagoOut.p_fecha_transaccion = fechaIn
            pagoOut.p_medio = tipoIn
            pagoOut.p_status = statusIn
            pagoOut.p_referencia = referenciaIn
            pagoOut.p_porcobrar = porCobrarIn
            pagoOut.p_monto = montoIn
            pagoOut.p_precio = precioIn
            pagoOut.p_dtoGeneral = dtoGeneralIn
            pagoOut.p_dtoParticular = dtoParticularIn
            pagoOut.p_diferencia = montoIn - (precioIn - dtoGeneralIn - dtoParticularIn)
            pagoOut.p_codigoInterno = codigoInterno
            pagoOut.p_referencia_uso = proxReferenciaUso

            if (cuentaIn is not None):
                pagoOut.p_cuenta_id = cuentaIn.pk
            else:
                pagoOut.p_cuenta_id = cuentaIn
            pagoOut.save()

            # Tercero Ajusto el Saldo
            if Saldo.objects.filter(s_user=pagadorIn, s_marca=self.marcaId).exists():
                saldo = Saldo.objects.get(s_user=pagadorIn, s_marca=self.marcaId)
                saldo.s_saldo += productoIn.p_creditos
                saldo.save()
            else:
                saldo = Saldo()
                saldo.s_saldo = productoIn.p_creditos
                saldo.s_user = pagadorIn
                saldo.s_marca = self.marcaId
                saldo.s_bloqueado = 0
                saldo.save()

            mensaje = 'ok'

            transaccionJson = {
                'accion': 'CP',
                'descripcion': self.ACCIONES['CP'] + ':' + planOut.p_nombre,
                'usuarioEjecutor': self.usuarioResponsable,
                'creditos': planOut.p_creditos_totales,
                'planId': planAccionadoId,
                'actividadId': None,
            }

            self.registrar_log(transaccionJson)

        except Exception as e:
            if planAccionadoId>0:
                Planes.objects.filter(id=planAccionadoId).delete()
            mensaje = "Error:" + str(e)

        return {'mensaje': mensaje, 'planOutId': planOut.id}

    def registrar_desactivacion_plan(self, planId):
        try:
            plan=Planes.objects.get(id=planId)
            plan.p_historico=True
            plan.save()
            transaccionJson = {
                'accion': 'IP',
                'descripcion': self.ACCIONES['IP'] + ':' + plan.p_nombre,
                'usuarioEjecutor': self.usuarioResponsable,
                'creditos': plan.p_creditos_totales-plan.p_creditos_usados,
                'planId': planId,
                'actividadId': None,
            }
            self.registrar_log(transaccionJson)
            mensaje='ok'
        except Exception as e:
            mensaje = "Error:" + str(e)

        return mensaje


    def registrar_reserva(self, actividadId,cupo=0):
        actividad = Actividad.objects.get(id=actividadId)

        planAccionadoId = self.puedeReservarActividad(actividadId=actividadId,vs=self.vs)
        # La funcion de arriba devuelve el plan que debe ustilizarse basado en algoritmo de negocio
        # Donde primero se revisa si el atleta tiene plan tipo mensual y si esta activo ese plan
        # Si la actividad permite que se utilice el plan mensual entonces la funcion devuekve el codigo
        # del plan. De no existir ningun plan adecuado la funcion devuelve nulo (None).
        # Seguidamente se chequean otros planes si son adecuados a las restricciones de la actividad

        plan=Planes.objects.get(id=planAccionadoId)

        if cupo == 0:
            reservados = list(
                Participantes.objects.values_list('pa_num_cupo', flat=True).filter(pa_actividad=actividad))
            i = 1
            while i < actividad.ac_cap_max:
                if i in reservados:
                    i += 1
                else:
                    break
        else:
            i = cupo

        try:

            Participantes.objects.create(pa_usuario=self.user, pa_actividad_id=actividadId, pa_num_cupo=i,
                                         pa_plan=plan)
            actividad.ac_cupos_reservados += 1

            mensaje = "ok"

            actividad.save()

            self.saldoActual = self.actualizar_saldo()

            transaccionJson = {
                'accion': 'RA',
                'descripcion': self.ACCIONES['RA'] + ':' + actividad.ac_nombre,
                'usuarioEjecutor': self.usuarioResponsable,
                'creditos': actividad.ac_creditos,
                'planId': planAccionadoId,
                'actividadId': actividadId,
            }

            self.registrar_log(transaccionJson)

        except Exception as e:

            mensaje = "Error:" + str(e)

        return mensaje


    def promover_desde_lista_espera(self,actividadId):
        mf=ManejoFechas()
        actividad = Actividad.objects.get(id=actividadId)
        espera=Espera.objects.get(es_actividad_id=actividadId,es_usuario_id=self.user.id)
        planAccionadoId=espera.es_plan_id
        plan=Planes.objects.get(id=planAccionadoId)

        try:
            espera.delete()
            actividad.ac_cupos_en_espera-=1
            # Re-Asigno lugares en lista de espera
            esperas = Espera.objects.filter(es_actividad_id=actividadId).order_by('es_num_cupo')
            n = 0
            for espera in esperas:
                n += 1
                espera.es_num_cupo = n
                espera.save()

            actividad.ac_cupos_reservados += 1
            planAccionadoId = plan.id
            reservados = list(
                Participantes.objects.values_list('pa_num_cupo', flat=True).filter(pa_actividad=actividad))
            i = 1
            while i < actividad.ac_cap_max:
                if i in reservados:
                    i += 1
                else:
                    break
            Participantes.objects.create(pa_usuario=self.user, pa_actividad_id=actividadId, pa_num_cupo=i,
                                         pa_plan=plan)

            mensaje = "ok"

            actividad.save()

            self.saldoActual = self.actualizar_saldo()

            transaccionJson = {
                'accion': 'PE' ,
                'descripcion': self.ACCIONES['PE'] + ':' + actividad.ac_nombre,
                'usuarioEjecutor': self.usuarioResponsable,
                'creditos': actividad.ac_creditos,
                'planId': planAccionadoId,
                'actividadId': actividadId,
            }

            self.registrar_log(transaccionJson)

        except Exception as e:
            mensaje = "Error:" + str(e)

        return mensaje

    def registrar_lista_espera(self, actividadId):
        actividad = Actividad.objects.get(id=actividadId)

        planAccionadoId = self.puedeReservarActividad(actividadId=actividadId,vs=self.vs)
        # La funcion de arriba devuelve el plan que debe ustilizarse basado en algoritmo de negocio
        # Donde primero se revisa si el atleta tiene plan tipo mensual y si esta activo ese plan
        # Si la actividad permite que se utilice el plan mensual entonces la funcion devuekve el codigo
        # del plan. De no existir ningun plan adecuado la funcion devuelve nulo (None).
        # Seguidamente se chequean otros planes si son adecuados a las restricciones de la actividad

        try:
            plan = Planes.objects.get(id=planAccionadoId)
            i=actividad.ac_cupos_en_espera+1
            Espera.objects.create(es_usuario=self.user, es_actividad_id=actividadId, es_num_cupo=i,
                                         es_plan=plan)
            actividad.ac_cupos_en_espera += 1

            mensaje = "ok"

            actividad.save()
            self.saldoActual = self.actualizar_saldo()

            transaccionJson = {
                'accion': 'EE',
                'descripcion': self.ACCIONES['EE'] + ':' + actividad.ac_nombre,
                'usuarioEjecutor': self.usuarioResponsable,
                'creditos': actividad.ac_creditos,
                'planId': planAccionadoId,
                'actividadId': actividadId,
            }

            self.registrar_log(transaccionJson)

        except Exception as e:
            mensaje = "Error:" + str(e)

        return mensaje

    def registrar_cancelar_reserva(self, actividadId):
        actividad = Actividad.objects.get(id=actividadId)
        participacion=Participantes.objects.get(pa_actividad_id=actividadId,pa_usuario_id=self.user.id)
        planAccionadoId=participacion.pa_plan_id

        try:
            participacion.delete()
            actividad.ac_cupos_reservados-=1

            mensaje = "ok"

            actividad.save()
            self.saldoActual = self.actualizar_saldo()

            transaccionJson = {
                'accion': 'CR' ,
                'descripcion': self.ACCIONES['CR'] + ':' + actividad.ac_nombre,
                'usuarioEjecutor': self.usuarioResponsable,
                'creditos': actividad.ac_creditos,
                'planId': planAccionadoId,
                'actividadId': actividadId,
            }

            self.registrar_log(transaccionJson)

        except Exception as e:
            mensaje = "Error:" + str(e)

        return mensaje

    def registrar_reintegro_por_suspension(self, pa):
        mf=ManejoFechas()
        actividadId=pa.actividadId
        actividad = Actividad.objects.get(id=actividadId)
        if pa.atletaEnListaEspera(self.atletaId):
            registro=Espera.objects.get(es_actividad_id=actividadId,es_usuario_id=self.atletaId)
            planAccionadoId=registro.es_plan_id
        elif pa.atletaReservado(self.atletaId):
            registro=Participantes.objects.get(pa_actividad_id=actividadId,pa_usuario_id=self.atletaId)
            planAccionadoId=registro.pa_plan_id
        else:
            mensaje = "no se encuentra reservado ni en espera"
            return mensaje

        try:
            plan = Planes.objects.get(id=planAccionadoId)
            plan.p_creditos_usados -= pa.actividadCreditos
            plan.save()
            if registro.__class__.__name__=='Participantes':
                actividad.ac_cupos_reservados-=1
            elif registro.__class__.__name__=='Espera':
                actividad.ac_cupos_en_espera -= 1
            registro.delete()

            mensaje = "ok"

            actividad.save()
            self.saldoActual = self.actualizar_saldo()

            transaccionJson = {
                'accion': 'RS' ,
                'descripcion': self.ACCIONES['RS'] + ':' + actividad.ac_nombre,
                'usuarioEjecutor': self.usuarioResponsable,
                'creditos': actividad.ac_creditos,
                'planId': planAccionadoId,
                'actividadId': actividadId,
            }

            self.registrar_log(transaccionJson)

        except Exception as e:
            mensaje = "Error:" + str(e)

        return mensaje

    def registrar_reintegro_por_no_participacion(self, pa):
        actividadId=pa.actividadId
        actividad = Actividad.objects.get(id=actividadId)
        if pa.atletaEnListaEspera(self.atletaId):
            registro=Espera.objects.get(es_actividad_id=actividadId,es_usuario_id=self.atletaId)
            planAccionadoId=registro.es_plan_id
        else:
            mensaje = "no se encuentra en espera"
            return mensaje

        try:
            plan = Planes.objects.get(id=planAccionadoId)
            plan.p_creditos_usados -= pa.actividadCreditos
            plan.save()
            actividad.ac_cupos_en_espera -= 1
            registro.delete()

            mensaje = "ok"

            actividad.save()
            self.saldoActual = self.actualizar_saldo()

            transaccionJson = {
                'accion': 'RX' ,
                'descripcion': self.ACCIONES['RX'] + ':' + actividad.ac_nombre,
                'usuarioEjecutor': self.usuarioResponsable,
                'creditos': actividad.ac_creditos,
                'planId': planAccionadoId,
                'actividadId': actividadId,
            }

            self.registrar_log(transaccionJson)

        except Exception as e:
            mensaje = "Error:" + str(e)

        return mensaje

    def registrar_cancelar_lista_espera(self, actividadId):
        actividad = Actividad.objects.get(id=actividadId)
        espera=Espera.objects.get(es_actividad_id=actividadId,es_usuario_id=self.user.id)
        planAccionadoId=espera.es_plan_id

        try:
            espera.delete()
            actividad.ac_cupos_en_espera-=1
            self.actualizar_saldo()

            mensaje = "ok"

            actividad.save()
            self.saldoActual = self.actualizar_saldo()

            # Re-Asigno lugares en lista de espera
            esperas = Espera.objects.filter(es_actividad_id=actividadId).order_by('es_num_cupo')
            n = 0
            for espera in esperas:
                n += 1
                espera.es_num_cupo = n
                espera.save()

            transaccionJson = {
                'accion': 'SE' ,
                'descripcion': self.ACCIONES['SE'] + ':' + actividad.ac_nombre,
                'usuarioEjecutor': self.usuarioResponsable,
                'creditos': actividad.ac_creditos,
                'planId': planAccionadoId,
                'actividadId': actividadId,
            }

            self.registrar_log(transaccionJson)

        except Exception as e:
            mensaje = "Error:" + str(e)

        return mensaje

    def registrar_log(self, transaccionJson):
        tl = TransactionLog()
        tl.tl_usuario = self.user
        tl.tl_marca = self.marca
        tl.tl_accion = transaccionJson['accion']
        tl.tl_descripcion = transaccionJson['descripcion']
        tl.tl_usuarioEjecutor = transaccionJson['usuarioEjecutor']
        tl.tl_creditos = transaccionJson['creditos']
        tl.tl_plan_accionado_id = transaccionJson['planId']
        tl.tl_actividad_id=transaccionJson['actividadId']
        tl.save()
        return

    def reportar_transacciones_marca(self, fecha_desde, fecha_hasta):
        pass

    def reportar_transacciones_usuario(self, fecha_desde, fecha_hasta):
        pass

    def enviar_correo_transaccion(self, strTransaccion):
        pass

    def actualizar_saldo(self):
        saldo = self.saldo
        marca = self.marca
        user = self.user
        planesAtleta = Planes.objects.filter(p_usuario=user, p_marca=marca,
                                              p_fecha_caducidad__gte=datetime.today()).order_by('p_fecha_caducidad')
        participaciones = Participantes.objects.filter(pa_usuario=user).values_list('pa_plan_id', 'pa_actividad_id')
        esperas = Espera.objects.filter(es_usuario=user).values_list('es_plan_id', 'es_actividad_id')
        actividades = dict(Actividad.objects.filter(ac_marca=marca).values_list('id', 'ac_creditos'))
        creditosContratados = 0
        creditosUsados = 0
        saldoCalculado = 0
        try:
            for plan in planesAtleta:

                planCreditosUsados = 0

                for participacion in participaciones:
                    if participacion[0] == plan.id:
                        planCreditosUsados += actividades[participacion[1]]

                for espera in esperas:
                    if espera[0] == plan.id:
                        planCreditosUsados += actividades[espera[1]]

                creditosContratados += plan.p_creditos_totales
                creditosUsados += planCreditosUsados
                saldoCalculado = creditosContratados - creditosUsados

                if plan.p_tipo == 0:
                    plan.p_creditos_usados = planCreditosUsados
                    if plan.p_creditos_usados < plan.p_creditos_totales and plan.p_fecha_caducidad >= datetime.today():
                       plan.p_historico=False
                    else:
                       plan.p_historico = True
                    # Esto lo hago porque el cron.py ha podido poner en historico el plan si hubo sobrepasado
                    # la cantidad de creditos. En el caso de una cancelacion de reserva es posible que se hubiese
                    # puesto en historico previamente y al cancelarla el plan permanece en historico.
                    plan.save()
                elif plan.p_tipo == 1:
                    plan.p_creditos_usados_plan_mensual = planCreditosUsados
                    plan.save()
                elif plan.p_tipo == 2:
                    plan.p_creditos_usados_plan_mensual = planCreditosUsados
                    if plan.p_creditos_usados < plan.p_creditos_totales and plan.p_fecha_caducidad >= datetime.today():
                       plan.p_historico=False
                    else:
                       plan.p_historico = True
                    plan.save()

            saldo.s_bloqueado = creditosUsados
            saldo.s_saldo = saldoCalculado
            saldo.save()
            return saldoCalculado
        except:
            return None

    def puedeReservarActividad(self,actividadId,vs):
        """
        Esta funcion devuelve el plan que debe ustilizarse basado en algoritmo de negocio
        Donde primero se revisa si el atleta tiene plan tipo mensual y si esta activo ese plan
        Si la actividad permite que se utilice el plan mensual entonces la funcion devuekve el codigo
        del plan. De no existir ningun plan adecuado la funcion devuelve nulo (None).
        Seguidamente se chequean otros planes si son adecuados a las restricciones de la actividad

        """
        planIdParaReservar=None
        actividad = Actividad.objects.get(id=actividadId)

        actividadProductosPermitidos=actividad.ac_productos_permitidos
        centros = Relacion.objects.values_list('r_marca_id', flat=True).filter(r_user_id=self.atletaId, r_estado='A')
        planesAtleta = Planes.objects.filter(p_usuario=self.atletaId, p_historico=False,
                                             p_marca_id__in=[actividad.ac_marca_id]).order_by(
            'p_fecha_caducidad')

        if actividadProductosPermitidos:
            # (1) Chequeo si tiene un plan mensual ilimitado o referenciado y si la actividad lo permite
            for productoPermitidoId in actividadProductosPermitidos:
                for plan in planesAtleta:
                    if plan.p_producto.id == productoPermitidoId:
                       if plan.p_tipo==1 or plan.p_tipo==3:
                           planIdParaReservar=plan.id
                           break
        else:
            # (2) Chequeo si tiene un plan mensual ilimitado y si la actividad carece de restricciones
            #Cuando es None se consideran Todos los productos
            for plan in planesAtleta:
               if plan.p_tipo==1:
                   planIdParaReservar = plan.id
                   break

        if not planIdParaReservar:
            if actividadProductosPermitidos:
                # (3) Chequeo si tiene un plan mensual limitado y si la actividad lo permite
                for productoPermitidoId in actividadProductosPermitidos:
                    for plan in planesAtleta:
                        if plan.p_producto.id == productoPermitidoId:
                           if plan.p_tipo==2:
                               if plan.p_creditos_totales_plan_mensual>0:
                                   if (plan.p_creditos_totales_plan_mensual - plan.p_creditos_usados_plan_mensual) >= actividad.ac_creditos:
                                       planIdParaReservar = plan.id
                                       break
            else:
                # (4) Chequeo si tiene un plan mensual limitado y si la actividad carece de restricciones
                #Cuando es None se consideran Todos los productos
                for plan in planesAtleta:
                   if plan.p_tipo==2:
                       if plan.p_creditos_totales_plan_mensual > 0:
                           if (plan.p_creditos_totales_plan_mensual - plan.p_creditos_usados_plan_mensual) >= actividad.ac_creditos:
                               planIdParaReservar = plan.id
                               break

        if not planIdParaReservar:
            if actividadProductosPermitidos:
                # (5) Chequeo si tiene algun plan no mensual que soporte el producto exigido por la actividad
                for productoPermitidoId in actividadProductosPermitidos:
                    for plan in planesAtleta:
                        if plan.p_producto.id == productoPermitidoId:
                            if plan.p_tipo == 0:
                                planIdParaReservar = plan.id
                                break
            else:
                # (6) Chequeo si tiene algun otro plan con creditos suficientes
                for plan in planesAtleta:
                    if plan.p_tipo == 0:
                        if (plan.p_creditos_totales-plan.p_creditos_usados)>=actividad.ac_creditos:
                            planIdParaReservar = plan.id
                            break

        return planIdParaReservar

class ManejoFechas:
    """Facilita el manejo de los formatos de fechas"""

    def __init__(self):
        pass

    def dateStr2DateTime(self,fechaIn):
        return datetime.strptime(fechaIn, '%d/%m/%Y')

    def date2dateStr(self,datetimeIn):
        return '{0}/{1}/{2}'.format(datetimeIn.day,datetimeIn.month,datetimeIn.year)

    def hms_string(self,sec_elapsed):
        h = int(sec_elapsed / (60 * 60))
        m = int((sec_elapsed % (60 * 60)) / 60)
        s = sec_elapsed % 60.
        return "{}:{:>02}:{:>05.2f}".format(h, m, s)

    def desdeCuando_(self,fechaHora):
        start_time = fechaHora
        end_time = datetime.now()
        seconds_elapsed = int((end_time - start_time).total_seconds())
        return "hace {0}".format(self.hms_string(seconds_elapsed))

    def desdeCuando(self,fechaHora):
        today = datetime.now()
        tdiff = today - fechaHora
        strmes = "mes"
        strdia="día"
        strhora="hora"
        strminuto="min"

        if tdiff.days/30 > 1:
            strmes += 'es'
        if tdiff.days>1:
            strdia += 's'
        if tdiff.seconds/3600 > 1:
            strhora += 's'
        if tdiff.seconds/60 > 1:
            strminuto += 's'

        if tdiff.days/30 > 0:
            s = "%d " + strmes
            return s % (tdiff.days/30)
        elif tdiff.days > 0:
            s="%d "+strdia
            return s % tdiff.days
        elif tdiff.seconds/3600 > 0:
            s="%d " + strhora + " "
            return s % (tdiff.seconds / 3600)
        elif tdiff.seconds/60 > 0:
            s="%d " + strminuto + " "
            return s % (tdiff.seconds / 60)
        else:
            return "ahora"

    def mesLiteral(self,mes):
        meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre',
                 'noviembre', 'diciembre']
        return meses[mes-1]

    def diaLiteral(self,dia):
        dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        return dias[dia-1]

    def fechaCorta(self,fechaIn):
        if type(fechaIn).__name__ == 'date' or type(fechaIn).__name__ == 'datetime':
            fecha = fechaIn
        else:
            fecha = datetime.strptime(fechaIn, "%I:%M %p").time()
        fechaFormateada = str(fecha.day) + '/' + str(fecha.month) + '/' + str(fecha.year)
        return fechaFormateada

    def fechaCortaConHora(self,fechaIn):
        fecha = fechaIn
        fechaFormateada = str(fecha.day) + '/' + str(fecha.month) + '/' + str(fecha.year)
        fechaFormateada += ' '
        fechaFormateada += self.horaCivil(fechaIn.time())
        return fechaFormateada

    def horaCivil(self,horaIn):
        if type(horaIn).__name__ == 'time' or type(horaIn).__name__ == 'datetime.time':
            hora = horaIn
        else:
            hora = datetime.strptime(horaIn, "%I:%M %p").time()
        horaFormateada = hora.strftime("%I:%M %P")
        return horaFormateada

    def fechaEspecial(self,fechaIn):  # Solo un argumento.
        hoy = datetime.now().date()
        fechaFormateada = ''
        dias = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']
        meses = ['enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio', 'julio', 'agosto', 'septiembre', 'octubre',
                 'noviembre', 'diciembre']
        if fechaIn == 'ahora':
            fechaIn = datetime.now()
        if type(fechaIn).__name__ == 'date' or type(fechaIn).__name__ == 'datetime':
            fecha = fechaIn
        else:
            fecha = datetime.strptime(fechaIn, "%I:%M %p").time()
        d = fecha.weekday()
        dia = dias[d][:3].capitalize()
        if fecha == hoy:
            fechaFormateada = 'hoy'
        elif fecha == hoy + timedelta(days=1):
            fechaFormateada = 'mañana'
        elif fecha == hoy - timedelta(days=1):
            fechaFormateada = 'ayer'
        elif fecha.month == hoy.month and fecha.year == hoy.year:
            fechaFormateada = dia + ' ' + str(fecha.day)
        elif fecha.year == hoy.year:
            fechaFormateada += str(fecha.day) + ' '
            fechaFormateada += meses[fecha.month - 1][:3].capitalize()
        else:
            fechaFormateada += str(fecha.day) + ' '
            fechaFormateada += meses[fecha.month - 1][:3].capitalize() + ', '
            fechaFormateada += str(fecha.year)
        return fechaFormateada


class ManejoNotificaciones:
    """Permite crear, obtener, cambiar estado y listar notificaciones"""

    def __init__(self):
        pass

    def atleta_solicita_afiliacion(self,usuario,marca):
        tipoNotificacion=TipoNotificacion.objects.get(tn_tipo='SA')
        notificacion=Notificacion()
        notificacion.nt_tipo=tipoNotificacion
        notificacion.nt_texto=tipoNotificacion.tn_texto_base.replace('<atleta>',usuario.first_name+' '+usuario.last_name)
        notificacion.save()

        marcaNotificacion=Marca_Notificacion()
        marcaNotificacion.mn_estado='C'
        marcaNotificacion.mn_marca=marca
        marcaNotificacion.mn_usuario=usuario
        marcaNotificacion.mn_notificacion=notificacion
        marcaNotificacion.mn_parametros='marcaId='+str(marca.id)+',userId='+str(usuario.id)+',notificacionId='+str(notificacion.id)
        marcaNotificacion.save()

        return

    def marca_invita_atleta_afiliacion(self,usuario,marca):
        tipoNotificacion=TipoNotificacion.objects.get(tn_tipo='IA')
        notificacion=Notificacion()
        notificacion.nt_tipo=tipoNotificacion
        notificacion.nt_texto=tipoNotificacion.tn_texto_base.replace('<marca>',marca.m_nombre)
        notificacion.save()

        usuarioNotificacion=Usuario_Notificacion()
        usuarioNotificacion.un_estado='C'
        usuarioNotificacion.un_marca=marca
        usuarioNotificacion.un_usuario=usuario
        usuarioNotificacion.un_notificacion=notificacion
        usuarioNotificacion.un_parametros='marcaId='+str(marca.id)+',userId='+str(usuario.id)+',notificacionId='+str(notificacion.id)
        usuarioNotificacion.save()

        return

    def marca_informa_atleta(self,usuario,marca,texto,tipo='MI'):

        try:
            tipoNotificacion=TipoNotificacion.objects.get(tn_tipo=tipo)
            notificacion=Notificacion()
            notificacion.nt_tipo=tipoNotificacion
            if isinstance(texto, str):
                notificacion.nt_texto=tipoNotificacion.tn_texto_base.replace('<marca>',marca.m_nombre)+' '+texto

            if isinstance(texto,dict):
                if tipo=='CA':
                    if 'actividad' in texto:
                        notificacion.nt_texto='La actividad '+texto['actividad'] + ' con ' +\
                            texto['instructor'] + ' ' + texto['fechaHora'] + ' en ' + marca.m_nombre + ' ' +\
                            texto['mensaje']
                elif tipo=='RL':
                    if 'actividad' in texto:
                        notificacion.nt_texto=texto['mensaje'] + ' a la actividad '+texto['actividad'] + ' con ' +\
                            texto['instructor'] + ' ' + texto['fechaHora'] + ' en ' + marca.m_nombre
                elif tipo=='RP':
                    if 'plan' in texto:
                        notificacion.nt_texto=texto['mensaje'] + texto['plan'] + ' en ' + marca.m_nombre
                elif tipo=='RR':
                    if 'actividad' in texto:
                        notificacion.nt_texto=texto['mensaje'] + ' a la actividad '+texto['actividad'] + ' con ' +\
                            texto['instructor'] + ' ' + texto['fechaHora'] + ' en ' + marca.m_nombre
                elif tipo=='VP':
                    if 'plan' in texto:
                        notificacion.nt_texto='Plan ' + texto['plan'] + ' en ' + marca.m_nombre + ' ' +  texto['mensaje']
                elif tipo == 'MA':
                    if 'actividad' in texto:
                        notificacion.nt_texto='La actividad '+texto['actividad'] + ' con ' +\
                            texto['instructor'] + ' ' + texto['fechaHora'] + ' en ' + marca.m_nombre + ' ' +\
                            texto['mensaje']

            notificacion.save()

            usuarioNotificacion=Usuario_Notificacion()
            usuarioNotificacion.un_estado='C'
            usuarioNotificacion.un_usuario=usuario
            usuarioNotificacion.un_marca=marca
            usuarioNotificacion.un_notificacion=notificacion
            usuarioNotificacion.un_parametros=None
            usuarioNotificacion.save()
        except Exception as e:
            pass

        return

    def marca_informa_marca(self,usuario,marca,texto,tipo='MI'):

        try:
            tipoNotificacion=TipoNotificacion.objects.get(tn_tipo=tipo)
            notificacion=Notificacion()
            notificacion.nt_tipo=tipoNotificacion

            if isinstance(texto, str):
                notificacion.nt_texto=tipoNotificacion.tn_texto_base.replace('<marca>',marca.m_nombre)+' '+texto

            if isinstance(texto,dict):
                if tipo=='CA':
                    if 'actividad' in texto:
                        notificacion.nt_texto='La actividad '+texto['actividad'] + ' con ' +\
                            texto['instructor'] + ' ' + texto['fechaHora'] + ' ' +  texto['mensaje']
                if tipo=='CE':
                    if 'actividad' in texto:
                        notificacion.nt_texto='La actividad '+texto['actividad'] + ' con ' +\
                            texto['instructor'] + ' ' + texto['fechaHora'] + ' ' +  texto['mensaje']

            notificacion.save()

            marcaNotificacion=Marca_Notificacion()
            marcaNotificacion.mn_estado='C'
            marcaNotificacion.mn_marca=marca
            marcaNotificacion.mn_usuario=usuario
            marcaNotificacion.mn_notificacion=notificacion
            marcaNotificacion.mn_parametros=None
            marcaNotificacion.save()

        except Exception as e:
            pass

        return

    def atleta_informa_marca(self,usuario,marca,texto):

        try:
            tipoNotificacion=TipoNotificacion.objects.get(tn_tipo='AI')
            notificacion=Notificacion()
            notificacion.nt_tipo=tipoNotificacion
            notificacion.nt_texto = tipoNotificacion.tn_texto_base.replace('<atleta>',usuario.first_name + ' ' + usuario.last_name)+' '+texto
            notificacion.save()

            marcaNotificacion=Marca_Notificacion()
            marcaNotificacion.mn_estado='C'
            marcaNotificacion.mn_marca=marca
            marcaNotificacion.mn_usuario=usuario
            marcaNotificacion.mn_notificacion=notificacion
            marcaNotificacion.mn_parametros=None
            marcaNotificacion.save()

        except Exception as e:
            pass

        return

    def listaNotificacionesAtleta(self,usuarioId,estado):
        notificacionesUsuario=Usuario_Notificacion.objects.filter(un_usuario_id=usuarioId,un_estado__in=estado).order_by('-un_notificacion__nt_fecha')
        listaNotificaciones=[]
        for notificacionUsuario in notificacionesUsuario:
            notificacion=notificacionUsuario.un_notificacion
            listaNotificaciones.append(self.notificacion2JSON(notificacion))
            if notificacion.nt_tipo.tn_requiere_accion:
                pass
            else:
                notificacionUsuario.un_estado='V'
                notificacionUsuario.save()
        return listaNotificaciones

    def listaNotificacionesMarca(self,marcaId,estado):
        notificacionesMarca=Marca_Notificacion.objects.filter(mn_marca_id=marcaId,mn_estado__in=estado).order_by('-mn_notificacion__nt_fecha')
        listaNotificaciones=[]
        for notificacionMarca in notificacionesMarca:
            notificacion=notificacionMarca.mn_notificacion
            listaNotificaciones.append(self.notificacion2JSON(notificacion))
            if notificacion.nt_tipo.tn_requiere_accion:
                pass
            else:
                notificacionMarca.mn_estado='V'
                notificacionMarca.save()
        return listaNotificaciones

    def notificacion2JSON(self,notificacion):
        mf=ManejoFechas()
        tipoNotificacion=notificacion.nt_tipo

        if tipoNotificacion.tn_requiere_accion:
            acciones = AccionesNotificacion.objects.get(an_tipo_notificacion=tipoNotificacion)
        else:
            acciones=None

        notificacionJSON={}

        if Marca_Notificacion.objects.filter(mn_notificacion=notificacion).exists():
            marcaNotificacion = Marca_Notificacion.objects.filter(mn_notificacion=notificacion)[0]
            notificacionJSON['notificacionId']=notificacion.id
            notificacionJSON['tipoNotificacion']=notificacion.nt_tipo
            notificacionJSON['textoNotificacion']=notificacion.nt_texto
            notificacionJSON['descripcion']=tipoNotificacion.tn_descripcion
            notificacionJSON['tiempoEmitida']=mf.desdeCuando(notificacion.nt_fecha)
            notificacionJSON['estado']=marcaNotificacion.get_mn_estado_display()
            if acciones:
                notificacionJSON['acciones']={'aceptar': True, 'rechazar': True}
                notificacionJSON['funcionAceptar']= acciones.an_funcion_aceptar + '(' + marcaNotificacion.mn_parametros + ')'
                notificacionJSON['funcionRechazar']= acciones.an_funcion_rechazar + '(' + marcaNotificacion.mn_parametros + ')'
                notificacionJSON['callbackAceptar']= acciones.an_callback_aceptar
                notificacionJSON['callbackRechazar']= acciones.an_callback_rechazar
            else:
                notificacionJSON['acciones']={'aceptar': False, 'rechazar': False}
                notificacionJSON['funcionAceptar']= None
                notificacionJSON['funcionRechazar']= None
                notificacionJSON['callbackAceptar']= None
                notificacionJSON['callbackRechazar']= None


        if Usuario_Notificacion.objects.filter(un_notificacion=notificacion).exists():
            usuarioNotificacion = Usuario_Notificacion.objects.filter(un_notificacion=notificacion)[0]
            notificacionJSON['notificacionId']=notificacion.id
            notificacionJSON['tipoNotificacion']=notificacion.nt_tipo
            notificacionJSON['textoNotificacion']=notificacion.nt_texto
            notificacionJSON['descripcion']=tipoNotificacion.tn_descripcion
            notificacionJSON['tiempoEmitida']=mf.desdeCuando(notificacion.nt_fecha)
            notificacionJSON['estado']=usuarioNotificacion.get_un_estado_display()
            if acciones:
                notificacionJSON['acciones']={'aceptar': True, 'rechazar': True}
                notificacionJSON['funcionAceptar']= acciones.an_funcion_aceptar + '(' + usuarioNotificacion.un_parametros + ')'
                notificacionJSON['funcionRechazar']= acciones.an_funcion_rechazar + '(' + usuarioNotificacion.un_parametros + ')'
                notificacionJSON['callbackAceptar']= acciones.an_callback_aceptar
                notificacionJSON['callbackRechazar']= acciones.an_callback_rechazar
            else:
                notificacionJSON['acciones']={'aceptar': False, 'rechazar': False}
                notificacionJSON['funcionAceptar']= None
                notificacionJSON['funcionRechazar']= None
                notificacionJSON['callbackAceptar']= None
                notificacionJSON['callbackRechazar']= None

        return notificacionJSON

    def marca_acepta_atleta(self,notificacionId):
        marcaNotificacion=Marca_Notificacion.objects.get(mn_notificacion_id=notificacionId)
        marcaNotificacion.mn_estado='A'
        marcaNotificacion.save()
        self.marca_informa_atleta(marcaNotificacion.mn_usuario,marcaNotificacion.mn_marca,'ha aceptado tu solicitud.')
        return

    def atleta_informa_desafiliacion(self,usuario,marca):
        self.atleta_informa_marca(usuario,marca,'ha dejado de seguirte')
        return

    def marca_rechaza_atleta(self,notificacionId):
        marcaNotificacion=Marca_Notificacion.objects.get(mn_notificacion_id=notificacionId)
        marcaNotificacion.mn_estado='R'
        marcaNotificacion.save()
        return

    def atleta_acepta_marca(self,notificacionId):
        usuarioNotificacion=Usuario_Notificacion.objects.get(un_notificacion_id=notificacionId)
        usuarioNotificacion.un_estado='A'
        usuarioNotificacion.save()
        self.atleta_informa_marca(usuarioNotificacion.un_usuario,usuarioNotificacion.un_marca,'ha aceptado su invitación.')
        return

    def atleta_rechaza_marca(self,notificacionId):
        usuarioNotificacion=Usuario_Notificacion.objects.get(un_notificacion_id=notificacionId)
        usuarioNotificacion.un_estado='R'
        usuarioNotificacion.save()
        return

    def eliminarNotificacionAtletaMarca(self,marcaId,usuarioId,tipo):
        marcaNotificaciones=Marca_Notificacion.objects.filter(mn_marca_id=marcaId,mn_usuario_id=usuarioId,mn_notificacion__nt_tipo__tn_tipo=tipo).order_by('-mn_notificacion__nt_fecha')
        if marcaNotificaciones:
            marcaNotificacion=marcaNotificaciones[0]
            notificacion=marcaNotificacion.mn_notificacion
            marcaNotificacion.delete()
            notificacion.delete()
        return


    def eliminarNotificacionMarcaAtleta(self,marcaId,usuarioId,tipo):
        atletaNotificaciones=Usuario_Notificacion.objects.filter(un_marca_id=marcaId,un_usuario_id=usuarioId,un_notificacion__nt_tipo__tn_tipo=tipo).order_by('-un_notificacion__nt_fecha')
        if atletaNotificaciones:
            atletaNotificacion=atletaNotificaciones[0]
            notificacion=atletaNotificacion.un_notificacion
            atletaNotificacion.delete()
            notificacion.delete()
        return










