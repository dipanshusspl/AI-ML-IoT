from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
import qrcode
import io
import base64
from .models import UserProfile
from .forms import RegisterForm, LoginForm, TOTPVerifyForm, BackupCodeForm


def register(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(user=user)
            messages.success(request, 'Account created! Please log in.')
            return redirect('login')
    else:
        form = RegisterForm()
    
    return render(request, 'register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            
            user = authenticate(username=username, password=password)
            if user:
                profile = UserProfile.objects.get(user=user)
                if profile.two_factor_enabled:
                    request.session['pre_2fa_user_id'] = user.id
                    return redirect('verify_2fa')
                else:
                    login(request, user)
                    return redirect('dashboard')
            else:
                messages.error(request, 'Invalid username or password')
    else:
        form = LoginForm()
    
    return render(request, 'login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, 'Logged out successfully')
    return redirect('login')


@login_required(login_url='login')
def dashboard(request):
    profile = UserProfile.objects.get(user=request.user)
    return render(request, 'dashboard.html', {'profile': profile})


@login_required(login_url='login')
def setup_2fa(request):
    profile = UserProfile.objects.get(user=request.user)
    
    if profile.two_factor_enabled:
        messages.warning(request, '2FA already enabled')
        return redirect('dashboard')
    
    if request.method == 'GET' and not profile.totp_secret:
        profile.generate_totp_secret()
        profile.save()
        print(f"[v0] Generated secret for user {profile.user.username}: {profile.totp_secret}")
    
    if request.method == 'POST':
        token = request.POST.get('token', '').strip()
        print(f"[v0] Verifying token: {token} for user {profile.user.username}")
        print(f"[v0] User secret: {profile.totp_secret}")
        print(f"[v0] Current TOTP code should be: {profile.get_current_totp_code()}")
        
        if profile.verify_token(token):
            profile.two_factor_enabled = True
            profile.save()
            print(f"[v0] 2FA enabled for user {profile.user.username}")
            messages.success(request, '2FA enabled successfully!')
            return redirect('backup_codes')
        else:
            print(f"[v0] Token verification FAILED for user {profile.user.username}")
            messages.error(request, 'Invalid token. Ensure your phone time is synced. Try again.')
    
    # Generate QR code
    provisioning_uri = profile.generate_qr_code()
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(provisioning_uri)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    img_str = base64.b64encode(buffer.getvalue()).decode()
    
    context = {
        'secret': profile.totp_secret,
        'qr_code': img_str,
    }
    
    return render(request, 'setup_2fa.html', context)


def verify_2fa(request):
    """Verify 2FA token or backup code during login"""
    user_id = request.session.get('pre_2fa_user_id')
    if not user_id:
        return redirect('login')
    
    try:
        user = User.objects.get(id=user_id)
        profile = UserProfile.objects.get(user=user)
    except User.DoesNotExist:
        return redirect('login')
    
    if request.method == 'POST':
        token = request.POST.get('token', '').strip()
        backup_code = request.POST.get('backup_code', '').strip()
        
        print(f"[v0] 2FA verification attempt for user {user.username}")
        print(f"[v0] Token submitted: {token}, Backup code submitted: {backup_code}")
        
        if token:
            if profile.verify_token(token):
                print(f"[v0] TOTP verification SUCCESS for {user.username}")
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                del request.session['pre_2fa_user_id']
                return redirect('dashboard')
            else:
                print(f"[v0] TOTP verification FAILED for {user.username}")
        
        if backup_code:
            if profile.verify_backup_code(backup_code):
                print(f"[v0] Backup code verification SUCCESS for {user.username}")
                login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                del request.session['pre_2fa_user_id']
                messages.info(request, 'Logged in with backup code')
                return redirect('dashboard')
            else:
                print(f"[v0] Backup code verification FAILED for {user.username}")
        
        messages.error(request, 'Invalid code. Please try again or use a backup code.')
    
    totp_form = TOTPVerifyForm()
    backup_form = BackupCodeForm()
    
    return render(request, 'verify_2fa.html', {
        'totp_form': totp_form,
        'backup_form': backup_form,
        'username': user.username
    })


@login_required(login_url='login')
def backup_codes(request):
    profile = UserProfile.objects.get(user=request.user)
    
    if not profile.two_factor_enabled:
        return redirect('setup_2fa')
    
    # Generate backup codes if not already generated
    if not profile.backup_codes:
        codes = profile.generate_backup_codes()
        profile.save()
    
    import json
    codes = json.loads(profile.backup_codes)
    
    return render(request, 'backup_codes.html', {'codes': codes})


@login_required(login_url='login')
def disable_2fa(request):
    if request.method == 'POST':
        profile = UserProfile.objects.get(user=request.user)
        profile.two_factor_enabled = False
        profile.totp_secret = ''
        profile.backup_codes = ''
        profile.save()
        messages.success(request, '2FA disabled')
    
    return redirect('dashboard')
