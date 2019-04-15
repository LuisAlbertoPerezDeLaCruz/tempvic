from django import forms
from .models import *
from django.core.validators import *
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.core.validators import RegexValidator

class ProfileImageForm(forms.Form):
    image = forms.FileField(label='Select a profile Image')    

class RegisterMarcaForm(forms.Form):
	error_css_class = 'error'
	required_css_class = 'required'
	Correo = forms.EmailField(label="",widget=forms.EmailInput(attrs={'class':'btn-block input-agregar','placeholder':'Correo electronico'}))
	nombre = forms.CharField(label="",max_length=200,widget=forms.TextInput(attrs={'class':'btn-block input-agregar','placeholder':'Nombre del centro'}))
	telefono1 = forms.CharField(label="",widget=forms.TextInput(attrs={'class':'btn-block input-agregar','placeholder':'Telefono Local'}))
	telefono2 = forms.CharField(label="",widget=forms.TextInput(attrs={'class':'btn-block input-agregar','placeholder':'Telefono Particular'}))
	alias = forms.CharField(label="",max_length=30,widget=forms.TextInput(attrs={'class':'btn-block input-agregar','placeholder':'Alias'}))
	razon_social = forms.CharField(label="",max_length=150,widget=forms.TextInput(attrs={'class':'btn-block input-agregar','placeholder':'Razon Social'}))
	doc_ident = forms.CharField(label="",max_length=30,widget=forms.TextInput(attrs={'class':'btn-block input-agregar','placeholder':'RIF'}))
	calle = forms.CharField(label="",max_length=30,widget=forms.TextInput(attrs={'class':'btn-block input-agregar','placeholder':'Calle'}))
	urbanizacion = forms.CharField(label="",max_length=30,widget=forms.TextInput(attrs={'class':'btn-block input-agregar','placeholder':'Urbanizacion'}))
	edificio = forms.CharField(label="",max_length=30,widget=forms.TextInput(attrs={'class':'btn-block input-agregar','placeholder':'Edificio / Casa'}))
	ciudad = forms.ModelChoiceField(label="",queryset=Ciudad.objects.values_list('c_nombre',flat=True).all(),widget=forms.Select(attrs={'style':'-webkit-appearance: none;','class':'btn btn-lg btn-default dropdown-toggle drop-disciplina btn-block','placeholder':'Ciudad'}))
	municipio = forms.ModelChoiceField(label="",queryset=Zona.objects.values_list('z_municipio',flat=True).all(),widget=forms.Select(attrs={'style':'-webkit-appearance: none;','class':'btn btn-lg btn-default dropdown-toggle drop-disciplina btn-block','placeholder':'Municipio'}))
	public = forms.BooleanField(label="Desea ser una marca privada",widget=forms.CheckboxInput(attrs={'style':'transform:scale(2)','checked':'true','class':'checkbox-inline'}))
	descripcion = forms.CharField(label="",max_length=30,widget=forms.TextInput(attrs={'class':'btn-block input-agregar','placeholder':'Descripcion del centro'}))
	plan = forms.ModelChoiceField(label="",queryset=ProductoMarca.objects.all(),widget=forms.Select(attrs={'style':'-webkit-appearance: none;','class':'btn btn-lg btn-default dropdown-toggle drop-disciplina btn-block','placeholder':'Plan'}))
	terminos = forms.BooleanField(label="Acepto los terminos y condiciones",widget=forms.CheckboxInput(attrs={'style':'transform:scale(2)','class':'checkbox-inline'}))
	boletin = forms.BooleanField(label="Desea recibir nuestro boletin periodicamente",widget=forms.CheckboxInput(attrs={'checked':'true','style':'transform:scale(2)','class':'checkbox-inline'}))

def clean_Correo(self):
		cd=self.clean_data
		print(cd)
		usuario = cd.get('usuario')
		print("Usuario"+usuario)
		validate = EmailValidator()
		try:
			validate(usuario)
		except:
			raise forms.ValidationError("Correo no valido")
		return usuario

	# def clean_usuario(self):
	# 	cleaned_data = super(RegisterMarcaForm, self).clean()
	# 	usuario = cleaned_data.get('usuario')
	# 	validate = EmailValidator()
	# 	try:
	# 		validate(usuario)
	# 	except:
	# 		raise forms.ValidationError("Correo no valido")
	# 	return usuario