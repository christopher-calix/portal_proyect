def check_password_or_email(get_response):

    def middleware(request):
        if request.user.is_authenticated() and request.user.role == "E":
            if request.method == "GET":
                success = request.user.update_password_or_email()
                if success:
                    request.GET._mutable = True
                    request.GET['activate_user_switch'] = success
                    request.GET._mutable = False
        response = get_response(request)
        return response

    return middleware
