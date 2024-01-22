
import base64

from django.shortcuts import render
from django.http import HttpResponse
from django.views import View
from django.db import transaction
from django.core.validators import validate_email
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout as auth_logout
from django.contrib.auth.decorators import login_required

from django.contrib.auth import authenticate, login as auth_login
from django.http import JsonResponse, Http404
from django.shortcuts import redirect
from django.views.generic import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView


from django.urls import reverse_lazy
    
from django.shortcuts import render, reverse
from django.http import HttpResponseRedirect


from django.core.exceptions import ValidationError
from django.core.mail import EmailMessage
from django.http import Http404, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.exceptions import ObjectDoesNotExist
from django.core.mail import EmailMessage, mail_managers
from django.shortcuts import redirect, reverse
from django.template.loader import render_to_string
from django.contrib.sites.shortcuts import get_current_site
from django.views.generic import FormView
from django.utils.encoding import force_str

##MODELS
from Apps.nomina_app.models import Account


from django.utils.http import urlsafe_base64_encode
#from django.utils.six.moves.urllib.parse import urlencode

from .forms.register import UserForm, ActivationForm


User = get_user_model()



def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('nomina_app:dashboard'))
    return render(request, 'auth/login.html')

#class Index(LoginRequiredMixin, TemplateView):
#    template_name = 'auth/login.html'
#
#    def dispatch(self, request, *args, **kwargs):
#        if request.user.is_authenticated:
#            return redirect(reverse_lazy('dashboard'))
#        return super().dispatch(request, *args, **kwargs)

class LoginView(View):
    http_method_names = ['POST']

    def post(self, request):
        
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Validate input
        if not username or not password:
            return JsonResponse({'success': False, 'message': 'Please provide both username and password.'})

        try:
            user = authenticate(request, username=username, password=password)  # Use authenticate with request object
            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    if user.is_superuser and user.role == 'A':  # Combine checks for clarity
                        return redirect('dashboard/users')
                    elif user.role in ('A', 'S', 'B', 'E'):
                        return redirect('dashboard/')
                    else:
                        return JsonResponse({'success': False, 'message': 'Invalid user role.'})
                else:
                    return JsonResponse({'success': False, 'message': 'Inactive user.'})
            else:
                return JsonResponse({'success': False, 'message': 'Invalid username or password.'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})



@method_decorator(csrf_exempt, name='dispatch')
class RegistrationView(FormView):
    email_body_template_html = "registration/activation_email_html.txt"
    email_body_template_string = "registration/activation_email_string.txt"
    email_subject_template = "registration/activation_email_subject.txt"
    form_class = UserForm
    success_url = reverse_lazy("dashboard")
    template_name = "registration/register.html"

    def dispatch(self, request, *args, **kwargs):
        try:
            self.account = Account.objects.get(
                taxpayer_id=kwargs.get('taxpayer_id'),
                user__role__in=['A', 'F']
            )
            self.is_provider = True
        except ObjectDoesNotExist:
            self.account = None
            self.is_provider = False
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save(commit=False)
        user.is_active = False
        user.role = 'P' if self.is_provider else 'A'
        user.save()

        try:
            account_user = Account.objects.get(user=user)
            account_user.first_name = form.cleaned_data['name']
            account_user.save()
            self.send_activation_email(user)
        except Exception:
            transaction.rollback()  # Assuming you have a transaction management setup
            return JsonResponse({'success': False, 'message': 'Failed to create account'})

        return super().form_valid(form)

    def get_success_url(self):
        return self.success_url

    def send_activation_email(self, user):
        activation_key = generate_activation_key(user)
        context = self.get_email_context(activation_key)
        subject = render_to_string(self.email_subject_template, context)
        subject = force_str(subject).strip()
        text_message = render_to_string(self.email_body_template_string, context)
        html_message = render_to_string(self.email_body_template_html, context)

        try:
            msg = EmailMessage(
                subject, html_message, settings.DEFAULT_FROM_EMAIL, [user.email]
            )
            msg.content_subtype = "html"  # Main content is now text/html
            msg.send()
        except Exception as e:
            mail_managers("Registration Email Error", f"Error sending activation email: {e}")

    def get_email_context(self, activation_key):
        encoded_activation_key = urlsafe_base64_encode(force_str(activation_key).encode("utf-8"))
        activation_url = reverse("activate", kwargs={"activation_key": encoded_activation_key})
        return {
            "taxpayer_id": self.taxpayer_id,
            "site": get_current_site(self.request),
            "activation_url": self.request.build_absolute_uri(activation_url),
            "name": self.request.POST.get("name"),
        }

    def form_invalid(self, form):
        errors = form.errors.as_json()
        return JsonResponse(errors, status=400)
    
@method_decorator(login_required(login_url='/'), name='dispatch')
class LogoutView(View):
    def get(self, request, *args, **kwargs):
        user = request.user
        auth_logout(request)
        return HttpResponseRedirect(reverse('index'))    


@method_decorator(csrf_exempt, name='dispatch')
class ActivationView(View):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = ActivationForm  # Make sure to replace with your actual form
        return context

    def get(self, request, *args, **kwargs):
        activation_key = kwargs.get('activation_key')
        if activation_key:
            username = self.validate_key(activation_key)
            if username:
                user = self.get_user(username)
                if user:
                    try:
                        user.is_active = True
                        user.save()
                        url = reverse('dashboard')
                        return HttpResponseRedirect(url, {'success': True, 'message': 'La cuenta se activó satisfactoriamente.'})
                    except:
                        raise Http404
                else:
                    raise Http404
        return super().get(request, *args, **kwargs)



@method_decorator(csrf_exempt, name='dispatch')
class PassResetView(View):
    template_name = 'registration/pass_reset.html'

    def get(self, request, *args, **kwargs):
        return render(request, self.template_name)



@method_decorator(csrf_exempt, name='dispatch')
class BackPassResetView(View):
    template_name = 'registration/modpass_email.txt'

    def post(self, request, *args, **kwargs):
        try:
            success = False
            message = ''
            email = request.POST.get('email')
            
            try:
                user = User.objects.get(email=email)
                user_id = user.id
                string_id = str(user_id)
                cod_id = base64.b64encode(string_id.encode()).decode('utf-8')
                
                try:
                    subject = 'Cambio de contraseña'
                    from_email = settings.DEFAULT_FROM_EMAIL
                    name = user.name
                    activation_url = request.build_absolute_uri(reverse('password_reset', kwargs={'id_user': cod_id}))
                    
                    context = {
                        'activation_url': activation_url,
                        'name': name,
                    }
                    
                    html_message = render_to_string(self.template_name, context)
                    list_email = [email]

                    if subject and html_message and from_email and list_email:
                        msg = EmailMessage(subject, html_message, from_email, list_email)
                        msg.content_subtype = "html"
                        msg.send()
                        message = 'Se ha enviado el enlace de recuperación a tu correo'
                        success = True
                    else:
                        message = 'Error al enviar correo, por favor intenta nuevamente'
                
                except Exception as e:
                    print(str(e))
                    message = 'Error al enviar correo, por favor intenta nuevamente'
            
            except User.DoesNotExist:
                message = 'Usuario no existente'

            response = {
                'success': success,
                'message': message
            }

        except Exception as e:
            raise Http404

        print(response)
        return JsonResponse(response)



@method_decorator(csrf_exempt, name='dispatch')
class PasswordResetView(View):
    template_name = 'registration/password_reset.html'

    def post(self, request, id_user, *args, **kwargs):
        if request.is_ajax():
            try:
                success = False
                message = ''
                url = ''
                user_id = base64.b64decode(id_user).decode('utf-8')
                password = request.POST.get('password')
                password_confirmation = request.POST.get('password_confirmation')
                
                try:
                    user = User.objects.get(id=user_id)
                    if password == password_confirmation:
                        success_pass, message_pass = validate_password(password)
                        if success_pass:
                            user.set_password(password)
                            user.save()
                            success = True
                        else:
                            message = message_pass
                    else:
                        message = 'Contraseñas no corresponden'
                except User.DoesNotExist:
                    message = 'Usuario no existente'

                response = {
                    'success': success,
                    'message': message
                }
                return JsonResponse(response)
            except Exception as e:
                print(str(e))
                raise Http404

        return Http404

@method_decorator(csrf_exempt, name='dispatch')
class UpdatePasswordAndEmailView(View):

    def post(self, request, *args, **kwargs):
        success, message = False, "Error, favor de intentarlo más tarde!"

        try:
            if request.is_ajax():
                user_id = request.POST.get("user_id")
                if not user_id:
                    raise Exception("Usuario inválido")

                password = request.POST.get("password")
                if not password:
                    raise Exception("La contraseña es inválida")

                password2 = request.POST.get("password2")
                if not password2:
                    raise Exception("La contraseña es inválida")

                email = request.POST.get("email")
                if not email:
                    raise Exception("El email es inválido")

                user_filter = User.objects.filter(id=user_id)
                if not user_filter.exists():
                    raise Exception("El usuario no existe en el sistema")

                user_obj = user_filter[0]
                if user_obj.role != 'E' or user_obj.employee is None:
                    raise Exception("El usuario no corresponde a un empleado")
                employee_obj = user_obj.employee

                try:
                    validate_email(email)
                except ValidationError as e:
                    raise Exception("Email es inválido")

                if User.objects.filter(email=email).exists():
                    raise Exception("El email ya existe, por favor registra otro")

                if password != password2:
                    raise Exception("Las contraseñas son diferentes")

                user_obj.email = email
                user_obj.set_password(password)
                user_obj.save()
                employee_obj.email = [email]
                employee_obj.save()
                message = "Actualización exitosa"
                success = True

        except Exception as e:
            message = str(e)
            success = False
            print("Exception in update_password_and_email => {}".format(message))

        response = {"success": success, "message": message}
        return JsonResponse(response)