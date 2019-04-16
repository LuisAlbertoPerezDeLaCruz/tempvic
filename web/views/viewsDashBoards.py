# -*- coding: utf-8 -*-
#######################
# viewsDashBoards.py #
#######################

from web.crons import *
from web.templatetags.filtrosEspeciales import *
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from accounts.views import manejarSesion
import json
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from random import randint


def armarTablaDeActividadesMarca(listaDeActividades, tags=None, tabs=None, multiAccion=False):
    hashAcum = 0
    lineas = [
        '{0}'.format('<table id="tblMarcaActividades" class=" table-compra t-consumen" border="0"\
                           style="vertical-align: middle;">'),
        '<colgroup class="destop">',
        '<col width="20%">',
        '<col width="20%">',
        '<col width="20%">',
        '<col width="20%">',
        '<col width="10%">',
        '<col width="10%">',
        '</colgroup>',
        '<colgroup class="movil">',
        '<col width="20%">',
        '<col width="20%">',
        '<col width="20%">',
        '<col width="20%">',
        '<col width="10%">',
        '<col width="10%">',
        '</colgroup>',
        '<tbody>',
    ]

    for actividad in listaDeActividades:
        pa = PerfilActividad(actividad.actividadId)
        hashAcum += hash(pa)
        ma = None
        ma = multiaccion_marca(pa)
        lineas.append('{0}'.format('<tr>'))
        lineas.append(formatTableDetail(
            fechaCortaPlus(actividad.actividadFecha) + '<BR>' + horaCivil(actividad.actividadHoraInicio), tabs=tabs,
            tags=tags))
        lineas.append(
            '\t<td> <img src = "{0}" style = "width: 30px; height: 30px; display: inline-block"><BR><a href="./clase-{2}">{1}</a> </td>'.format(
                actividad.actividadDisciplinaImagenNegra, actividad.actividadDisciplinaNombre, actividad.actividadId))
        lineas.append(
            formatTableDetail('<a href="./clase-{0}">{1}</a>'.format(actividad.actividadId,
                                                                     actividad.actividadNombre) + '<BR>' + actividad.actividadNombreInstructor + '<BR>' + '@' + actividad.actividadInstructorAlias,
                              tabs=tabs,
                              tags=tags))
        lineas.append(
            formatTableDetail(actividad.actividadInicialesMarca + '<BR>' + actividad.actividadSalonNombre, tabs=tabs,
                              tags=tags))
        lineas.append(
            formatTableDetail('{0}/{1}'.format(actividad.actividadReservados, actividad.actividadCapacidadMaxima),
                              tabs=tabs,
                              tags=tags))
        lineas.append(formatTableDetail('{0}'.format(ma), tabs=tabs))
        lineas.append('{0}'.format('</tr>'))
    lineas.append('</tbody>')
    lineas.append('{0}'.format('</table>'))
    return (lineas, hashAcum)


def armarTablaDeActividadesAtleta(listaDeActividades, tags=None, tabs=None, multiAccion=False, vs=None):
    hashAcum = 0
    lineas = [
        '{0}'.format('<table id="tblMarcaActividades" class=" table-compra t-consumen" border="0"\
                           style="vertical-align: middle;">'),
        '<colgroup class="destop">',
        '<col width="15%">',
        '<col width="15%">',
        '<col width="20%">',
        '<col width="20%">',
        '<col width="10%">',
        '<col width="10%">',
        '<col width="5%">',
        '<col width="5%">',
        '</colgroup>',
        '<colgroup class="movil">',
        '<col width="15%">',
        '<col width="15%">',
        '<col width="20%">',
        '<col width="20%">',
        '<col width="10%">',
        '<col width="10%">',
        '<col width="5%">',
        '<col width="5%">',
        '</colgroup>',
        '<tbody>',
    ]

    for actividad in listaDeActividades:
        pa = PerfilActividad(actividad.actividadId)
        userId = vs.userId
        hashAcum += hash(pa)
        ma = None
        ma = multiaccion_atleta(pa, userId)
        estaReservado = pa.atletaReservado(vs.userId)
        estaEnListaDeEspera = pa.atletaEnListaEspera(vs.userId)
        asistio = pa.atletaAsistio(vs.userId)
        estaLleno = pa.actividadCapacidadLlena
        claseEstatus = None
        if asistio:
            colEstatus = 'Asistio'
            colPuesto = pa.atletaPuestoEnListaEspera(vs.userId)
            claseEstatus = 'asistio'
        elif estaEnListaDeEspera:
            colEstatus = 'Espera'
            colPuesto = pa.atletaPuestoEnListaEspera(vs.userId)
        elif estaReservado:
            colEstatus = 'Reservado'
            colPuesto = pa.atletaPuestoReserva(vs.userId)
            claseEstatus = 'reservado'
        elif estaLleno:
            colEstatus = 'lleno'
            claseEstatus = 'lleno'
            colPuesto = ''
        else:
            colEstatus = ''
            colPuesto = ''
        lineas.append('{0}'.format('<tr>'))
        lineas.append(formatTableDetail(
            fechaCortaPlus(actividad.actividadFecha) + '<BR>' + horaCivil(actividad.actividadHoraInicio), tabs=tabs,
            tags=tags))
        lineas.append(
            '\t<td> <img src = "{0}" style = "width: 30px; height: 30px; display: inline-block"><BR><a href="./clase-{2}">{1}</a> </td>'.format(
                actividad.actividadDisciplinaImagenNegra, actividad.actividadDisciplinaNombre, actividad.actividadId))
        lineas.append(
            formatTableDetail('<a href="./clase-{0}">{1}</a>'.format(actividad.actividadId,
                                                                     actividad.actividadNombre) + '<BR>' + actividad.actividadNombreInstructor + '<BR>' + '@' + actividad.actividadInstructorAlias,
                              tabs=tabs,
                              tags=tags))
        lineas.append(
            formatTableDetail(actividad.actividadInicialesMarca + '<BR>' + actividad.actividadSalonNombre, tabs=tabs,
                              tags=tags))
        lineas.append(
            formatTableDetail('{0}/{1}'.format(actividad.actividadReservados, actividad.actividadCapacidadMaxima),
                              tabs=tabs,
                              tags=tags))
        if colPuesto:
            lineas.append(
                formatTableDetail('P:{0}'.format(colPuesto), tabs=tabs, tags=['strong'], claseTags='puesto_salon'))
        else:
            lineas.append(formatTableDetail('{0}'.format(colPuesto), tabs=tabs))

        lineas.append(formatTableDetail('{0}'.format(colEstatus), tabs=tabs, tags=['p'], claseTags=claseEstatus))
        lineas.append(formatTableDetail('{0}'.format(ma), tabs=tabs))
        lineas.append('{0}'.format('</tr>'))
    lineas.append('</tbody>')
    lineas.append('{0}'.format('</table>'))
    return (lineas, hashAcum)


def valueHashList(lineas):
    n = 0
    for linea in lineas:
        for i in range(0, len(linea), 2):
            n += ord(linea[i:i + 1])
    return n


def formatTableDetail(data, tags=None, tabs=None, claseTD=None, claseTags=None, aRefRuta=None, aRefTexto=None):
    if 'Jue, 1 de Mar' in data:
        pass
    if tabs == None:
        strTabs = ''
    else:
        strTabs = '\t' * tabs
    tagsApertura = ''
    tagsCierre = ''
    if claseTags:
        claseTags = 'class=\"{0}\"'.format(claseTags)
    else:
        claseTags = ''
    if tags:
        for tag in tags:
            tagsApertura += '<{0} {1}>'.format(tag, claseTags)
            tagsCierre += '</{0}>'.format(tag)

    if claseTD:
        claseTD = 'class=\"{0}\"'.format(claseTD)
    else:
        claseTD = ''
    if aRefRuta:
        aref = '<a href=\"{0}\">{1}</a>'.format(aRefRuta, aRefTexto)
    else:
        aref = ''
    if '<BR>' in data:
        td = strTabs + '<td {1}>'
        td += tagsApertura + data[0:data.index('<BR>')] + tagsCierre + data[data.index('<BR>'):]
    else:
        td = strTabs + '<td {1}> ' + tagsApertura + '{0}' + tagsCierre + '</td>'
    td = td.format(data, claseTD)
    return td


def dashtableVigentes(request, pk):
    return HttpResponse(json.dumps(request.session['dashtableVigentes']), content_type='application/json')


def dashtableRecientes(request, pk):
    return HttpResponse(json.dumps(request.session['dashtableRecientes']), content_type='application/json')


def multiaccion_marca(pa):
    ma = ''
    if pa.actividadAbiertaParaEditar or pa.actividadAbiertaParaGestionar or \
            pa.actividadAbiertaParaEliminar or pa.actividadAbiertaParaCancelar:
        ma += '<div class="btn-group moreOpsBt">\n'
        ma += '<button type="button" class="btn btn-sm btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">&nbsp;</button>\n'
        ma += '<ul class="dropdown-menu" style="right: 30px; top: 0px;">\n'
        if pa.actividadAbiertaParaGestionar:
            ma += '<li role="presentation">\n'
            ma += '<a href="#"\n'
            ma += 'onclick="return reserva(' + str(pa.actividadId) + ');">Gestionar Actividad'
            ma += '</a>\n'
            ma += '</li>\n'
        if pa.actividadAbiertaParaEditar:
            ma += '<li role="presentation">\n'
            ma += '<a href="#"\n'
            ma += 'onclick="serie=false;modi=true;modichange(true);return modificar(' + str(
                pa.actividadId) + ');">Editar Actividad'
            ma += '</a>\n'
            ma += '</li>\n'
        if pa.actividadAbiertaParaEliminar:
            ma += '<li role="presentation">\n'
            ma += '<a href="#"\n'
            ma += 'onclick="serie=false;modi=true;modichange(true);return eliminarActividad(' + str(
                pa.actividadId) + ');">Eliminar Actividad'
            ma += '</a>\n'
            ma += '</li>\n'
        if pa.actividadAbiertaParaCancelar:
            ma += '<li role="presentation">\n'
            ma += '<a href="#"\n'
            ma += 'onclick="serie=false;modi=true;modichange(true);return suspender(' + str(
                pa.actividadId) + ');">Suspender'
            ma += '</a>\n'
            ma += '</li>\n'
        ma += '</ul>\n'
        ma += '</div>\n'
    return ma


def multiaccion_atleta(pa, userId):
    ma = ''

    if pa.atletaReservado(userId):
        ma += '<div class="btn-group moreOpsBt">\n'
        ma += '<button type="button" class="btn btn-sm btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">&nbsp;</button>\n'
        ma += '<ul class="dropdown-menu" style="right: 30px; top: 0px;">\n'
        ma += '<li role="presentation">\n'
        ma += '<a href="#"\n'
        ma += 'onclick=\"return cancelarreserva({0},{1},{2});">Cancelar Reserva'.format(userId, pa.actividadId, 0)
        ma += '</a>\n'
        ma += '</li>\n'
        ma += '</ul>\n'
        ma += '</div>\n'
    else:
        if pa.actividadAbiertaParaReservar and not pa.actividadCapacidadLlena:
            ma += '<div class="btn-group moreOpsBt">\n'
            ma += '<button type="button" class="btn btn-sm btn-default dropdown-toggle" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">&nbsp;</button>\n'
            ma += '<ul class="dropdown-menu" style="right: 30px; top: 0px;">\n'
            ma += '<li role="presentation">\n'
            ma += '<a href="#"\n'
            ma += 'onclick=\"return reservausuario({0},{1},{2});">Reservar'.format(userId, pa.actividadId, 0)
            ma += '</a>\n'
            ma += '</li>\n'
            ma += '</ul>\n'
            ma += '</div>\n'

    return ma


def pruebaLoad(request):
    return render(request, 'prueba-load.html')


def ultimaFechaActividadesVigentes(pa=None, pm=None, vs=None):
    tipoVigente = TipoEstatus().tipoVigente
    tipoNoVigente = TipoEstatus().tipoNoVigente
    if pm:
        actividadesVigentes = Actividad.objects.filter(ac_estado_id__in=tipoVigente, ac_marca_id=pm.marcaId) \
            .values('ac_fecha').order_by('-ac_fecha', '-ac_hora_ini')
    else:
        if pa:
            actividadesVigentes = Actividad.objects.filter(ac_estado_id__in=tipoVigente, ac_marca__in=pa.atletaMarcas()) \
                .values('ac_fecha').order_by('-ac_fecha', '-ac_hora_ini')
    if actividadesVigentes:
        fecha = actividadesVigentes[0]['ac_fecha']
        return fecha
    else:
        return None


def ultimaFechaActividadesNoVigentes(pa=None, pm=None, n=5, vs=None):
    tipoNoVigente = TipoEstatus().tipoNoVigente
    if pm:
        actividadesNoVigentes = Actividad.objects.filter(ac_estado_id__in=tipoNoVigente, ac_marca_id=pm.marcaId) \
            .values('ac_fecha').order_by('-ac_fecha', '-ac_hora_ini')
    else:
        if pa:
            actividadesNoVigentes = Actividad.objects.filter(ac_estado_id__in=tipoNoVigente,
                                                             ac_marca__in=pa.atletaMarcas()) \
                .values('ac_fecha').order_by('-ac_fecha', '-ac_hora_ini')
    if actividadesNoVigentes:
        if len(actividadesNoVigentes) >= n:
            fecha = actividadesNoVigentes[n - 1]['ac_fecha']
        else:
            fecha = actividadesNoVigentes[0]['ac_fecha']
        return fecha
    else:
        return datetime.today()


def calculaFechas(fechaInicio=None, fechaFinalizacion=None, vs=None):
    if vs.tipoSesion == vs.MARCA:
        pm = PerfilMarca(vs.marcaEnUsoAlias)
        if fechaFinalizacion == None:
            fechaFinalizacion = ultimaFechaActividadesVigentes(pm=pm, vs=vs)
        if fechaInicio == None:
            fechaInicio = ultimaFechaActividadesNoVigentes(pm=pm, n=10)
    else:
        pa = PerfilAtleta(vs.userAlias)
        if fechaFinalizacion == None:
            fechaFinalizacion = ultimaFechaActividadesVigentes(pa=pa, vs=vs)
        if fechaInicio == None:
            fechaInicio = ultimaFechaActividadesNoVigentes(pa=pa, n=10, vs=vs)

    if fechaInicio == None or fechaFinalizacion == None:
        fechaInicio = datetime.today() - timedelta(days=datetime.today().weekday())
        fechaFinalizacion = fechaInicio + timedelta(days=6)

    fechaRetornoInicio = '{0}/{1}/{2}'.format(fechaInicio.day, fechaInicio.month, fechaInicio.year)
    if fechaFinalizacion:
        fechaRetornoFinalizacion = '{0}/{1}/{2}'.format(fechaFinalizacion.day, fechaFinalizacion.month,
                                                        fechaFinalizacion.year)
    else:
        dt = datetime.today()
        fechaFinalizacion = (dt - timedelta(days=dt.weekday())) + timedelta(days=6)
        fechaRetornoFinalizacion = '{0}/{1}/{2}'.format(fechaFinalizacion.day, fechaFinalizacion.month,
                                                        fechaFinalizacion.year)
    fechaInicio = str(fechaInicio)[0:10]
    fechaFinalizacion = str(fechaFinalizacion)[0:10]

    fechasJson = {
        'fechaInicio': fechaInicio,
        'fechaFinalizacion': fechaFinalizacion,
        'fechaRetornoInicio': fechaRetornoInicio,
        'fechaRetornoFinalizacion': fechaRetornoFinalizacion,
    }

    return fechasJson


def dashboard(request, pk=None):
    if 'fechaInicio' in request.GET and 'fechaFinalizacion' in request.GET:
        vs = manejarSesion(request, pk, False)
    else:
        cambiarTipoSesion = True
        # chequeo el caso donde el usuario atleta es dueno de la marca
        # viene de centros buscando el calendario y queremos que se
        # mantenga el tipo de sesion
        if 'vs' in request.session:
            vs = VicSession(request.user.username)
            if vs.tipoSesion == vs.ATLETA:
                try:
                    if PerfilMarca(pk).marcaDuenoAlias == vs.userAlias:
                        cambiarTipoSesion = False
                except:
                    cambiarTipoSesion = False
        vs = manejarSesion(request, pk, cambiarTipoSesion)
        update_activities()
        actualizar_planes_tokens()
    if vs.tipoSesion == vs.MARCA:
        return redirect('/' + vs.marcaEnUsoAlias + '/calendario-marca')
    else:
        return redirect('/' + vs.userAlias + '/calendario-atleta')


def calendarioAtleta(request, pk=None):
    vs = manejarSesion(request, pk, False)
    manejoFechas = ManejoFechas()
    if vs == None:
        return redirect('logout')
    pa = PerfilAtleta(vs.userAlias, vs)

    if vs.cantidadMarcas == 0:
        return render(request, 'calendario-vacio.html', {
            'vs': vs,
            'dummy': randint(0, 10000),
            'perfilAtleta': pa,
        })

    actividadesPorPagina = 25

    try:
        fechaInicio = manejoFechas.dateStr2DateTime(request.GET['fechaInicio'])
    except:
        fechaInicio = datetime.today()
    try:
        fechaFinalizacion = manejoFechas.dateStr2DateTime(request.GET['fechaFinalizacion'])
    except:
        fechaFinalizacion = datetime.today() + timedelta(days=365)

    if fechaInicio.date() < datetime.today().date():
        soloFuturas=False
    else:
        soloFuturas=True
    actividades = pa.actividadesTodasEntreFechas(request, soloFuturas)

    # Pagineo para tabIzquierdo
    paginaIZQ = int(request.GET.get('paginaIZQ', 1))
    paginatorIZQ = Paginator(actividades[0], actividadesPorPagina)
    try:
        actividadesIZQ = paginatorIZQ.page(paginaIZQ)
    except PageNotAnInteger:
        actividadesIZQ = paginatorIZQ.page(1)
    except EmptyPage:
        actividadesIZQ = paginatorIZQ.page(paginatorIZQ.num_pages)

    # Pagineo para tabDerecho
    paginaDER = int(request.GET.get('paginaDER', 1))
    paginatorDER = Paginator(actividades[1], actividadesPorPagina)
    try:
        actividadesDER = paginatorDER.page(paginaDER)
    except PageNotAnInteger:
        actividadesDER = paginatorDER.page(1)
    except EmptyPage:
        actividadesDER = paginatorDER.page(paginatorDER.num_pages)

    numPagesIZQ = actividadesIZQ.paginator.num_pages
    numPagesDER = actividadesDER.paginator.num_pages

    if actividadesIZQ.paginator.count == 0:
        numPagesIZQ = 0

    if actividadesDER.paginator.count == 0:
        numPagesDER = 0

    if 'reset' in request.GET:
        reset = request.GET['reset']
    else:
        reset = False

    marcaAlias = request.GET.get('marcaAlias','Suscripciones')
    if marcaAlias not in ['Suscripciones', 'Todos']:
        marcaNombre = Marca.objects.get(m_alias=request.GET['marcaAlias']).m_nombre
    else:
        marcaNombre = marcaAlias

    if paginaIZQ > 1 or paginaDER > 1 or reset:
        return render(request, 'calendario-atleta-table-plus.html', {
            'marcaNombre': marcaNombre,
            'marcaAlias': marcaAlias,
            'vs': vs,
            'dummy': randint(0, 10000),
            'perfilAtleta': pa,
            'actividadesIZQ': actividadesIZQ,
            'actividadesDER': actividadesDER,
            'numPagesIZQ': numPagesIZQ,
            'numPagesDER': numPagesDER,
            'urlPagineo': '/pagineo_calendario_atleta',
            'misActividadesTodas': actividades[1],
        })
    else:
        return render(request, 'calendario-atleta.html', {
            'vs': vs,
            'dummy': randint(0, 10000),
            'perfilAtleta': pa,
            'actividadesIZQ': actividadesIZQ,
            'actividadesDER': actividadesDER,
            'numPagesIZQ': numPagesIZQ,
            'numPagesDER': numPagesDER,
            'urlPagineo': '/pagineo_calendario_atleta',
            'misActividadesTodas': actividades[1],
        })


def calendarioMarca(request, pk=None):
    actividadesPorPagina = 25
    vs = manejarSesion(request, pk, False)
    if vs == None:
        return redirect('logout')
    numPages = 1
    try:
        pm = PerfilMarca(vs.marcaEnUsoAlias)
    except:
        return redirect('logout')
    actividades = pm.actividadesTodasEntreFechas(request)

    # Pagineo para tab Unico
    pagina = request.GET.get('pagina', 1)
    paginator = Paginator(actividades, actividadesPorPagina)

    if 'reset' in request.GET:
        reset = request.GET['reset']
    else:
        reset = False

    try:
        actividadesTodas = paginator.page(pagina)
    except PageNotAnInteger:
        actividadesTodas = paginator.page(1)
    except EmptyPage:
        actividadesTodas = paginator.page(paginator.num_pages)
    numPages = actividadesTodas.paginator.num_pages
    if actividadesTodas.paginator.count == 0:
        numPages = 0

    if pagina > 1 or reset:
        return render(request, 'calendario-marca-table.html', {
            'vs': vs,
            'perfilMarca': pm,
            'iniciales': pm.marcaIniciales,
            'status': TipoEstatus().tipoTodasPlus,
            'disciplinas': Disciplina.objects.filter(),
            'numPages': numPages,
            'actividadesTodas': actividadesTodas,
            'urlPagineo': '/pagineo_calendario_marca',
        })
    else:
        return render(request, 'calendario-marca.html', {
            'vs': vs,
            'perfilMarca': pm,
            'iniciales': pm.marcaIniciales,
            'status': TipoEstatus().tipoTodasPlus,
            'disciplinas': Disciplina.objects.filter(),
            'numPages': numPages,
            'actividadesTodas': actividadesTodas,
            'urlPagineo': '/pagineo_calendario_marca',
        })

