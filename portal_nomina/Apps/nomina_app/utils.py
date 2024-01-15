import secrets



class FinkokWS(object):
    pass

class CreatePDF(object):
    pass

def validate_password(password):
  """
  Valida una contraseña según los siguientes criterios:
    * Debe tener al menos 8 caracteres.
    * Debe contener al menos una letra mayúscula, una letra minúscula, un dígito y un carácter especial.

  Args:
    password: La contraseña a validar.

  Returns:
    True si la contraseña es válida, False en caso contrario.
  """

  success = True
  message = "La contraseña es correcta"

  if len(password) < 8:
    success = False
    message = "La contraseña debe tener al menos 8 caracteres."

  if not any(c.isupper() for c in password):
    success = False
    message = "La contraseña debe contener al menos una letra mayúscula."

  if not any(c.islower() for c in password):
    success = False
    message = "La contraseña debe contener al menos una letra minúscula."

  if not any(c.isdigit() for c in password):
    success = False
    message = "La contraseña debe contener al menos un dígito."

  if not any(c.isalpha() and not c.isalnum() for c in password):
    success = False
    message = "La contraseña debe contener al menos un carácter especial."

  return success, message



def generate_activation_key(user):
    """
    Genera un código de activación único para un usuario.

    Args:
        user: El usuario para el que se generará el código de activación.

    Returns:
        Un código de activación de 32 bytes.
    """

    random_bytes = secrets.token_bytes(32)
