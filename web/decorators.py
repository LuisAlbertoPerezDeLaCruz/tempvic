from django.core.exceptions import PermissionDenied
from django.http import Http404
from web.templatetags.filtrosEspeciales import *
from django.shortcuts import render,redirect



def user_is_legal(function):
    def wrap(request, *args, **kwargs):

        NULO=0
        ATLETA=1
        MARCA=2
        OTRO=3
        
        contenidoPK=NULO
        contenidoPKA=NULO
        
        if 'pk' in kwargs:
            pk = kwargs['pk']
            if Marca.objects.filter(m_alias=pk).exists():
                contenidoPK=MARCA
            elif UserProfile.objects.filter(u_alias=pk).exists():
                contenidoPK = ATLETA
            else:
                contenidoPK = OTRO
                
        if 'pka' in kwargs:
            pka = kwargs['pka']
            if Marca.objects.filter(m_alias=pka).exists():
                contenidoPKA=MARCA
            elif UserProfile.objects.filter(u_alias=pka).exists():
                contenidoPKA = ATLETA
            else:
                contenidoPKA = OTRO

        #Casos Especiales:
        # (1) Trae el pk de la marca en pka y nada en pk
        nombreFuncion=function.__name__
        casosEspeciales1=('configuracionGeneral','confmarca','gestionarPlanes','gestionarSalas','gestionarCuentas')
        if nombreFuncion in casosEspeciales1:
            if contenidoPKA==MARCA:
                pk=pka
                pka=None
                contenidoPK = MARCA
                contenidoPKA = NULO
            else:
                raise Http404
        # (2) No trae ni pk ni pka, vienen en el request.
        casosEspeciales2=('habilitarplanajax',)
        if nombreFuncion in casosEspeciales2:
            if 'pk' in request.GET:
                pk=request.GET['pk']
                if Marca.objects.filter(m_alias=pk).exists():
                    contenidoPK=MARCA
                elif UserProfile.objects.filter(u_alias=pk).exists():
                    contenidoPK = ATLETA
                else:
                    contenidoPK = OTRO
                contenidoPKA = NULO
            else:
                raise Http404

        # Caso 1 - Solicitud de logout
        if contenidoPK==OTRO:
            if pk=='logout':
                return redirect('logout')
            else:
               raise Http404

        # caso 2 - marca logueada o atleta logueado solicita informacion de marca
        elif contenidoPK==MARCA and contenidoPKA==NULO:
            vs = manejarSesion(request, pk, False)
            if vs.tipoSesion == vs.MARCA and vs.marcaEnUsoAlias != pk:
                if vs.userAlias != pk:
                    raise PermissionDenied
            else:
                if vs.tipoSesion == vs.ATLETA:
                    tieneRelacion = Relacion.objects.filter(r_user__profile__u_alias=vs.userAlias,r_marca__m_alias=pk,r_estado='A').exists()
                    marcaPublica=Marca.objects.filter(m_alias=pk)[0].m_public
                    if not tieneRelacion and not marcaPublica:
                        raise PermissionDenied

        # caso 3 - marca logueada solicita informacion de alias inexistente
        elif contenidoPK==MARCA and contenidoPKA==OTRO:
            vs = manejarSesion(request, pk, False)
            if vs.tipoSesion == vs.MARCA and vs.marcaEnUsoAlias != pk:
                if vs.userAlias != pk:
                    raise PermissionDenied
            else:
                raise Http404

        # caso 4 - marca solicita informacion de atleta
        # pk debe ser la marca y pka debe ser el atleta
        # chequea si la marca logueada es la misma del url
        elif contenidoPK==MARCA and contenidoPKA==ATLETA:
            vs = manejarSesion(request, pk, False)
            if vs.tipoSesion == vs.MARCA and vs.marcaEnUsoAlias != pk:
                if vs.userAlias != pk:
                    raise PermissionDenied
                tieneRelacion=Relacion.objects.filter(r_marca=vs.marcaEnUso,r_user__profile__u_alias=pka,r_estado='A').exists()
                if not tieneRelacion:
                    raise PermissionDenied

        # caso 5 - atleta solicita informacion de atleta
        # pk debe ser el atleta logueado y pka debe ser el atleta solicitado
        # chequea si el atleta logueado es la mismo del solicitado el la url
        elif contenidoPK == ATLETA and contenidoPKA == ATLETA:
            vs = manejarSesion(request, pk, False)
            if 'HTTP_REFERER' in request.META:
                url=request.META['HTTP_REFERER']
                if vs.tipoSesion == vs.ATLETA and vs.userAlias != pk:
                    if vs.userAlias != pk and 'clase' not in url:
                        if 'instructor' in request.path:
                            pass
                        else:
                            raise PermissionDenied

        # caso 6 - atleta solicita informacion de marca
        # pk debe ser el atleta logueado y pka debe ser el atleta solicitado
        # chequea si el atleta logueado es la mismo del solicitado el la url
        elif contenidoPK == ATLETA and contenidoPKA == MARCA:
            vs = manejarSesion(request, pk, False)
            if vs.tipoSesion == vs.ATLETA:
                raise PermissionDenied


        return function(request, *args, **kwargs)

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

def manejarSesion(request, pkIn, cambiarSesion):
    vs = None

    try:
        if 'vs' in request.session:  # and vs:
            vsJson = request.session['vs']
            vs = VicSession(request.user.username)
            vs.setear(vsJson)
            if cambiarSesion:
                vs.cambiarTipoSesion(pkIn)
            del request.session['vs']
            request.session['vs'] = vs.getJason()
            request.session.modified = True
        else:
            vs = VicSession(request.user.username)
            vsJson = vs.getJason()
            vs.setear(vsJson)
            pkWork = request.user.profile.u_alias
            if vs.tipoSesion == VicSession.MARCA:
                pkWork = vs.marcaEnUso.m_alias
            vs.cambiarTipoSesion(pkWork)
            request.session['vs'] = vs.getJason()
            request.session.modified = True
    except:
        return redirect('logout')

    return vs