import re
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _

class StrongPasswordValidator:
    def validate(self, password, user=None):
        if len(password) < 8:
            raise ValidationError(_("Password must be atleast 8 characters long."))
        
        if not re.search(r"[A-Z]",password):
            raise ValidationError(_("Password must contain atleast one uppercase letter."))
        
        if not re.search(r"[a-z]", password):
            raise ValidationError(_("Password must contain atleast one lowercase letter."))
        
        if not re.search(r"[0-9]", password):
            raise ValidationError(_("Password must contain atleast one digit."))
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValidationError(_("Password must contain atleast one special character."))
        
        def get_help_text(self):
            return _(
                "Your password must contain at least 8 characters, including uppercase, lowercase, numeric, and special characters."
            )
