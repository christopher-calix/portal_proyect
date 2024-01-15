# -*- encoding: utf-8 -*-

from django import forms
from django.db import models
from django.forms import Form
from Apps.users.models import User
from django.forms import ModelForm
from Apps.nomina_app.models import Account
from Apps.nomina_app.utils import validate_password


class UserForm(ModelForm):
  
  password = forms.CharField(
    label = ('Password'),
    widget = forms.PasswordInput(
      attrs={
        'max_length' : 10,
        'min_length' : 5,
        'placehoder' : 'Establece tu contraseña',
        'class' : 'password required form-control ',
        'id' : 'id_password',
        'name' : 'password',
        'autocomplete' : 'off',
      },
      render_value = True),
  )
  password_confirmation = forms.CharField(
    label = ('Password confirmation'),
    widget = forms.PasswordInput(
      attrs={
        'max_length' : 10,
        'min_length' : 5,
        'placehoder' : 'Confirma contraseña',
        'class' : 'password required form-control ',
        'id' : 'id_password_confirmation',
        'name' : 'password_confirmation',
        'autocomplete' : 'off',
      },
      render_value = True),
    
  )
  name = forms.CharField(
    label = ('Name'),
    widget = forms.TextInput(
      attrs={
        'max_length' : 26,
        'min_length' : 5,
        'placehoder' : 'Ingresa tu nombre',
        'class' : 'text required form-control ',
        'id' : 'id_name',
        'name' : 'name',
        'autocomplete' : 'off',
      },),
  )

  taxpayer_id = forms.CharField(
    label = ('RFC'),
    widget = forms.TextInput(
      attrs={
        'max_length' : 10,
        'min_length' : 5,
        'placehoder' : 'Ingresa tu rfc',
        'class' : 'text required form-control ',
        'id' : 'taxpayer_id',
        'name' : 'taxpayer_id',
        'autocomplete' : 'off',
      },),
    
  )
  
  class Meta:
    model = User
    fields = ['email']

  def clean_password(self):
    
    password = self.cleaned_data['password']
    self.cleaned_data['password'] = password
    return self.cleaned_data['password']

  def clean_password_confirmation(self):
    #import pdb; pdb.set_trace()

    password = self.cleaned_data['password']
    password_confirmation = self.cleaned_data['password_confirmation']
    if password and password != password_confirmation:

      raise forms.ValidationError(
        'Contraseñas no coiciden.'
      )
    success, message = validate_password(password)
    if not success:
      raise forms.ValidationError(message)
    return password_confirmation

  def clean_username(self):
    username = self.clean_username['email']
    try:
      User.objects.get(username__iexact=username)
    except User.DoesNotExist:
      self.clean_username['email'] = None
      return username
    raise forms.ValidationError("Usuario previamente registrado")

  def clean_taxpayer_id(self):
    taxpayer_id = self.cleaned_data['taxpayer_id']
    try:
      Account.objects.get(taxpayer_id__iexact=taxpayer_id)
    except Account.DoesNotExist:
      if (len(taxpayer_id)==12 or len(taxpayer_id)==13):
        self.cleaned_data['taxpayer_id'] = None
        return taxpayer_id
      else:
        raise forms.ValidationError("estructura del RFC invalida")
    raise forms.ValidationError("RFC previamente registrado")


  def save(self, commit=True):
    #import pdb; pdb.set_trace()
    try:
      user = super(UserForm, self).save(commit=False)
      user.set_password(self.cleaned_data['password'])
      user.email = self.cleaned_data['email']
      user._taxpayer_id = self.cleaned_data['taxpayer_id']
      if commit:
        user.save()
      return user 
    except Exception as e:
     print(e)



class ActivationForm(Form):

  activation_key = forms.CharField(
    label= ('Codigo de activación'),
    max_length=256,
    required=True,
    widget = forms.TextInput(
      attrs={
        'max_length' : 40,
        'class' : 'string required form-control',
        'placeholder' : 'Ingresa tu codigo de activación'
      }),
      error_messages = {
        'required' : ('The activation key is required'),
        'max_length' : ('The activation key have no more than 40 characters.')
      }
  )