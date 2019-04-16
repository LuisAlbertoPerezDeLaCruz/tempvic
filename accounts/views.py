# -*- coding: utf-8 -*-
#######################
# accounts.views.py #
#######################

from django.shortcuts import render, redirect
from django.contrib.auth import *
from accounts.forms import *
from web.models import *
from django.db import transaction
from django.contrib import messages
import random
import string
from django.core.mail import send_mail
from django.contrib import auth
from web.clases import *
from django.http import JsonResponse
import logging

app_name = 'accounts'

log = logging.getLogger('vicLog')

tokenValidator = ""

def validate_username(request):
    username = request.GET.get('username', None)
    user = User.objects.filter(username__iexact=username)
    is_taken = False
    registeredHere = False
    activo = False
    marca = None
    marcaNombre = None
    marcaDescripcion = None
    if user.exists():
        is_taken = True
        first_name = user[0].first_name
        last_name = user[0].last_name
        alias = user[0].profile.u_alias
        correo = user[0].email
        try:
            telefono = user[0].profile.u_telefono
        except:
            telefono = ''
        activo = user[0].is_active
        if 'vs' in request.session:
            marca = request.session['marca']
            marcaNombre = 'victorius'
            marcaDescripcion = 's'
            if Relacion.objects.filter(r_user=user, r_estado='A',r_marca=Marca.objects.filter(m_alias=request.session['marca'])[0]) == True:
                registeredHere = True

            if activo == False:
                token = Token.objects.filter(u_user=user[0])[0]
                from django.template import loader
                message = 'Correo de Bienvenida'
                data = {
                    'token': token,
                    'enlace': "http://" + request.META['HTTP_HOST'] + "/token/" + token.u_token,
                    'nombres': first_name + ' ' + last_name,
                    'alias': alias,
                    'marcaNombre': marcaNombre,
                    'marcaDescripcion': marcaDescripcion,
                    'activo': False,
                }
                html_message = loader.render_to_string(
                    'correoBienvenida.html',
                    data,
                )
                send_mail('Registro en Victorius', message, 'register@victorius.io', [correo], fail_silently=True,
                          html_message=html_message)
        else:
            pass
    else:
        is_taken = False
        first_name = ''
        last_name = ''
        alias = ''
        telefono = ''

    data = {
        'is_taken': is_taken,
        'registeredHere': registeredHere,
        'estaMarca': marca,
        'first_name': first_name,
        'last_name': last_name,
        'alias': alias,
        'telefono': telefono,
        'activo': activo,
    }

    return JsonResponse(data)


def validate_useralias(request):
    useralias = request.GET.get('useralias', None)
    is_taken = False
    usuario_pk = None
    if UserProfile.objects.filter(u_alias__iexact=useralias).exists():
        is_taken = True
        usuario_pk = UserProfile.objects.get(u_alias__iexact=useralias).u_user.pk
    else:
        usuario_pk = None
    data = {
        'is_taken': is_taken,
        'usuario_pk': usuario_pk,
    }
    return JsonResponse(data)


def validate_marcaalias(request):
    marcaalias = request.GET.get('marcaalias', None)
    data = {
        'is_taken': Marca.objects.filter(m_alias__iexact=marcaalias).exists()
    }
    return JsonResponse(data)


def cambiarmarca(request, pk):
    request.session['marca'] = pk
    manejarSesion(request, pk, True)

    return redirect("/" + request.session['marca'] + "/dashboard")


def get_client_ip(request):
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip

def user_logout(request):
    ip=get_client_ip(request)
    log.info('logout desde ('+ip+') :' + request.user.username)
    logout(request)
    return redirect('/')

def login(request):
    ip=get_client_ip(request)
    # Comentario NADA
    if request.session.get('visited', False):
        pass
    else:
        request.session['visited'] = True
    disciplinas = Disciplina.objects.all()
    global tipo
    tipo = 0
    tip = tipo

    form = RegisterForm()
    if request.user.is_authenticated:
        try:
            actual = Dueno.objects.filter(d_user__username=request.user.username)[0]
            return redirect('/' + actual.d_marca.m_alias + "/dashboard")
        except:
            perfil = UserProfile.objects.get(u_user=request.user)
            return redirect('/' + perfil.u_alias + '/dashboard')
    elif request.method == 'POST':

        if request.POST['form-type'] == u"registro":
            form = RegisterForm(request.POST)
            if form.is_valid() or True:
                try:
                    with transaction.atomic():
                        user = form.save(commit=False)
                        user.set_password(request.POST.get('password', ''))
                        user.is_active = False
                        user.email=user.username
                        user.save()
                        disc1 = Disciplina.objects.get(d_nombre=request.POST.get('dic1', ''))
                        disc2 = Disciplina.objects.get(d_nombre=request.POST.get('dic2', ''))
                        telefono = request.POST.get('phone', '')

                        useralias = request.POST.get('useralias')

                        perfil = UserProfile.objects.create(u_user=user, u_alias=useralias, u_secondname='',
                                    u_secondlastname='',
                                    u_telefono=telefono, u_direccion='',
                                    u_displinafav1=disc1, u_displinafav2=disc2, u_displinafav3=None)
                        perfil.save()
                except:
                    messages.error(request, 'Found Error. Executed Rollback')
                    return redirect("/")
                t = "p-" + ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(25))
                token = Token.objects.create(u_user=user, u_token=t)
                correo = user.username

                from django.template import loader
                message = 'Correo de Bienvenida'
                data = {
                    'token': token,
                    'enlace': "http://" + request.META['HTTP_HOST'] + "/token/" + token.u_token,
                    'nombres': user.first_name + ' ' + user.last_name,
                    'alias': useralias,
                    'marcaNombre': 'victorius',
                    'activo': False,
                }
                html_message = loader.render_to_string(
                    'correoBienvenida.html',
                    data,
                )
                send_mail('Activa tu cuenta Victorius', message, 'register@victorius.io', [correo], fail_silently=True,
                          html_message=html_message)
                messages.success(request, "Le enviamos un correo para activar su cuenta",extra_tags='sticky')
                return redirect("/")
            else:
                mensaje = ""
                messages.error(request, "Forma no valida, debe completar la informacion solicitada")
                marcas_publicas = Marca.objects.filter(m_public=True).order_by('m_nombre')[0:5]
                return render(request, "index.html", {'next': 'index', 'disciplinas': disciplinas, 'mensaje': mensaje,
                                                      'marcas_publicas': marcas_publicas, })
        elif request.POST['form-type'] in ('prospectsMarcas','prospectsAtletas'):
            prospects=Prospect.objects.filter().order_by('-id')
            prospect=Prospect()
            if request.POST['form-type'] == 'prospectsMarcas':
                prospect.pr_tipo = 'M'
            else:
                prospect.pr_tipo = 'A'
            prospect.pr_nombre=request.POST['nombre']
            prospect.pr_apellido=request.POST['apellido']
            prospect.pr_correo=request.POST['correo']
            try:
                prospect.pr_aspiraciones=request.POST['aspiraciones']
            except:
                prospect.pr_aspiraciones=''
            try:
                prospect.pr_centros_frecuentados=request.POST['centrosFrecuentados']
            except:
                prospect.pr_centros_frecuentados=''
            try:
                prospect.pr_ubicacion_negocio=request.POST['lugarOperacion']
            except:
                prospect.pr_ubicacion_negocio=''
            try:
                prospect.pr_nombre_negocio=request.POST['nombreNegocio']
            except:
                prospect.pr_nombre_negocio =''
            try:
                prospect.pr_descripcion_negocio=request.POST['descripcionNegocio']
            except:
                prospect.pr_descripcion_negocio = ''
            prospect.save()
            messages.success(request, "Hemos registrado su información. Muchas gracias.", extra_tags='sticky')
            return redirect("/")
        else:
            usernameIn = request.POST.get('username', '')
            passwordIn = request.POST.get('password', '')
            global tokenValidator
            if request.POST.get('csrfmiddlewaretoken', '') == tokenValidator:
                tipo = 0
            else:
                tipo = 2
            if User.objects.filter(username=usernameIn).exists():
                if User.objects.get(username=usernameIn).profile.u_registrado == False:
                    request.POST = request.POST.copy()
                    mensaje = ""
                    marcas_publicas = Marca.objects.filter(m_public=True).order_by('m_nombre')[0:5]
                    messages.warning(request,
                                     "Verifique, correo enviado. <br><button onclick=reenviarcorreo('" + usernameIn + "') class='btn btn-defauld btn-xs reservar-active'>Reenviar Mensaje </button> ",
                                     extra_tags='sticky')
                    return render(request, "index.html",
                                  {'next': 'index', 'disciplinas': disciplinas, 'mensaje': mensaje,
                                   'marcas_publicas': marcas_publicas, 'tipon': tipo})
            tokenValidator = request.POST.get('csrfmiddlewaretoken', '')
            user = authenticate(username=usernameIn, password=passwordIn)
            if user is not None:
                auth.login(request, user)
                log.info('login desde ('+ip+') :' + request.user.username)
                perfil = UserProfile.objects.get(u_user=request.user)
                if perfil.u_marca:
                    actual = Dueno.objects.filter(d_user__username=usernameIn)[0]
                    request.session['marca'] = actual.d_marca.m_alias
                    return redirect('/' + actual.d_marca.m_alias + "/dashboard")
                else:
                    return redirect("/" + perfil.u_alias + "/dashboard")
            else:
                user = User.objects.filter(username=usernameIn)
                if user.count() > 0:
                    if user[0].is_active == False:
                        request.POST = request.POST.copy()
                        mensaje = ""
                        marcas_publicas = Marca.objects.filter(m_public=True).order_by('m_nombre')[0:5]
                        messages.warning(request,
                                         "Haga click en el link de verificacion en su correo. <button onclick=reenviarcorreo('" + usernameIn + "') class='btn btn-defauld btn-xs reservar-active'>Reenviar Mensaje </button> ",
                                         extra_tags='sticky')
                        return render(request, "index.html",
                                      {'next': 'index', 'disciplinas': disciplinas, 'mensaje': mensaje,
                                       'marcas_publicas': marcas_publicas, 'tipon': tipo})
                    else:
                        messages.error(request, "Login y/o Password invalido")
                        mensaje = ""
                        marcas_publicas = Marca.objects.filter(m_public=True).order_by('m_nombre')[0:5]
                        return render(request, "index.html",
                                      {'next': 'index', 'disciplinas': disciplinas, 'mensaje': mensaje,
                                       'marcas_publicas': marcas_publicas, 'tipon': tip, })
                else:
                    messages.error(request, "Login y/o Password invalido")
                    mensaje = ""
                    marcas_publicas = Marca.objects.filter(m_public=True).order_by('m_nombre')[0:5]
                    return render(request, "index.html",
                                  {'next': 'index', 'disciplinas': disciplinas, 'mensaje': mensaje,
                                   'marcas_publicas': marcas_publicas, 'tipon': tip, })
    else:
        mensaje = ""
        marcas_publicas = Marca.objects.filter(m_public=True).order_by('m_nombre')[0:5]
        return render(request, "index.html", {'next': 'index', 'disciplinas': disciplinas, 'mensaje': mensaje,
                                              'marcas_publicas': marcas_publicas, 'tipon': tip, })

def token(request, pk):
    try:
        token = Token.objects.get(u_token=pk)
    except:
        messages.error(request, 'Realice su registro por favor')
        return redirect('/')
    usuario = token.u_user
    perfil = UserProfile.objects.get(u_user=usuario)

    usuario.activate = True
    usuario.save()
    token.u_data = True
    token.save()

    if not request.user.is_authenticated:
        auth.login(request, usuario)
        vs = manejarSesion(request, usuario.username, False)
    else:
        vs = manejarSesion(request, pk, False)

    telefono = perfil.u_telefono
    pais = Pais.objects.all()
    ciudad = Ciudad.objects.all()
    municipio = Zona.objects.all()
    marcasPublicas = Marca.objects.filter(m_public=True)
    marcasSeguidas = Relacion.objects.filter(r_user_id=usuario.id).values_list('r_marca_id__m_nombre', flat=True)
    marcas = Dueno.objects.filter(d_user=usuario)
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
        'dic1': str(dic1),
        'dic2': dic2,
        'dic3': dic3,
        'marcasPublicas': marcasPublicas,
        'marcasSeguidas': marcasSeguidas,
        'esmarca': False,
        'pais': pais,
        'ciudad': ciudad,
        'disciplinas': disciplinas,
        'municipio': municipio,
        'marcas': marcas,
        'vs': vs,
        'token': True,
    })


def register(request):
    return render(request, 'registro.html', {
        'disciplinas': Disciplina.objects.all(),
    })


def manejarSesion(request, pkIn, cambiarSesion):

    try:
        vs = None
        prev_tipo = None
        if 'vs' in request.session:  # and vs:
            vsJson = request.session['vs']
            vs = VicSession(request.user.username)
            vs.setear(vsJson)
            prev_tipo=vs.tipoSesion
            if cambiarSesion:
                vs.cambiarTipoSesion(pkIn)
            del request.session['vs']
            request.session['vs'] = vs.getJason()
            request.session.modified = True
            if vs.tipoSesion == vs.ATLETA:
                if prev_tipo!=vs.tipoSesion:
                    log.info('cambio a atleta :' + request.user.username)
            else:
                if prev_tipo != vs.tipoSesion:
                    log.info('cambio a marca :' + request.user.username)
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
        return None

    return vs