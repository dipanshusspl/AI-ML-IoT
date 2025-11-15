from django.db import models
from django.contrib.auth.models import User
import pyotp
import secrets
import json

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    two_factor_enabled = models.BooleanField(default=False)
    totp_secret = models.CharField(max_length=32, blank=True, null=True)
    backup_codes = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def generate_totp_secret(self):
        """Generate a new TOTP secret"""
        self.totp_secret = pyotp.random_base32()
        return self.totp_secret

    def get_totp(self):
        """Get TOTP object for verification"""
        if not self.totp_secret:
            return None
        return pyotp.TOTP(self.totp_secret)

    def generate_qr_code(self):
        """Generate QR code provisioning URI"""
        if not self.totp_secret:
            return None
        totp = self.get_totp()
        return totp.provisioning_uri(
            name=self.user.email or self.user.username,
            issuer_name='Django Auth 2FA'
        )

    def generate_backup_codes(self, count=10):
        """Generate backup codes"""
        codes = [secrets.token_hex(4).upper() for _ in range(count)]
        self.backup_codes = json.dumps(codes)
        return codes

    def verify_token(self, token):
        """Verify TOTP token with extended window"""
        if not self.totp_secret or not token:
            return False
        
        # valid_window=2 checks 3 time windows (current, ±1)
        # This gives ~90 second buffer for time sync issues
        try:
            totp = self.get_totp()
            if totp is None:
                return False
            
            # Clean token: remove spaces, ensure 6 digits
            token = str(token).strip().replace(" ", "")
            if not token.isdigit() or len(token) != 6:
                return False
            
            # Verify with extended window for time sync tolerance
            is_valid = totp.verify(token, valid_window=2)
            return is_valid
        except Exception as e:
            print(f"[v0] Token verification error: {str(e)}")
            return False

    def verify_backup_code(self, code):
        """Verify and consume backup code"""
        if not self.backup_codes or not code:
            return False
        
        try:
            codes = json.loads(self.backup_codes)
            code_clean = str(code).strip().upper()
            
            if code_clean in codes:
                codes.remove(code_clean)
                self.backup_codes = json.dumps(codes)
                self.save()
                return True
            return False
        except Exception as e:
            print(f"[v0] Backup code verification error: {str(e)}")
            return False

    def get_current_totp_code(self):
        """Get current TOTP code (for debugging)"""
        totp = self.get_totp()
        if totp:
            return totp.now()
        return None
