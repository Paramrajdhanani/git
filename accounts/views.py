import json
import random

from datetime import timedelta

from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from .forms import UserRegisterForm, UserProfileUpdateForm
from .models import UserProfile


# ==========================================================
# EMAIL HELPER
# ==========================================================

def send_otp_email(
    recipient_email,
    otp,
    first_name="User",
    subject="GitHub Profile Finder - Email Verification",
):
    """
    Send OTP email using Gmail SMTP configuration
    with attractive, responsive HTML email template for mobile & desktop.
    """

    # ------------------------------------------------------
    # Validate recipient email
    # ------------------------------------------------------

    recipient_email = (recipient_email or "").strip()

    if not recipient_email:
        raise ValueError("Recipient email is empty.")

    try:
        validate_email(recipient_email)
    except ValidationError:
        raise ValueError(
            f"Invalid recipient email: {recipient_email}"
        )

    # ------------------------------------------------------
    # Get sender email
    # ------------------------------------------------------

    sender_email = (
        getattr(settings, "DEFAULT_FROM_EMAIL", "")
        or getattr(settings, "EMAIL_HOST_USER", "")
    )

    sender_email = sender_email.strip()

    if not sender_email:
        raise ValueError(
            "DEFAULT_FROM_EMAIL / EMAIL_HOST_USER is empty."
        )

    try:
        validate_email(sender_email)
    except ValidationError:
        raise ValueError(
            f"Invalid sender email: {sender_email}"
        )

    # ------------------------------------------------------
    # Render rich HTML email template
    # ------------------------------------------------------

    context = {
        "otp": otp,
        "first_name": first_name or "Developer",
        "email": recipient_email,
    }

    try:
        html_message = render_to_string("accounts/emails/otp_email.html", context)
    except Exception as e:
        print("HTML Email Render Warning:", e)
        html_message = None

    # Plain text fallback
    plain_message = (
        f"Hello {first_name},\n\n"
        f"Your verification OTP code is: {otp}\n\n"
        "This OTP is valid for 10 minutes.\n\n"
        "If you did not request this verification, please ignore this email.\n\n"
        "GitHub Profile Finder Team"
    )

    # ------------------------------------------------------
    # Send email
    # ------------------------------------------------------

    return send_mail(
        subject=subject,
        message=plain_message,
        from_email=sender_email,
        recipient_list=[recipient_email],
        html_message=html_message,
        fail_silently=False,
    )


# ==========================================================
# REGISTER - SEND OTP
# ==========================================================

def register_view(request):

    if request.user.is_authenticated:
        return redirect("dashboard:index")

    if request.method == "POST":

        form = UserRegisterForm(request.POST)

        if form.is_valid():

            # --------------------------------------------------
            # Get cleaned form data
            # --------------------------------------------------

            username = form.cleaned_data["username"]
            email = form.cleaned_data["email"].strip()
            first_name = form.cleaned_data["first_name"]
            last_name = form.cleaned_data["last_name"]
            password = form.cleaned_data["password"]

            # --------------------------------------------------
            # Validate email
            # --------------------------------------------------

            try:
                validate_email(email)
            except ValidationError:

                messages.error(
                    request,
                    "Please enter a valid email address."
                )

                return render(
                    request,
                    "accounts/register.html",
                    {"form": form}
                )

            # --------------------------------------------------
            # Store registration data in session
            # --------------------------------------------------

            request.session["registration_data"] = {
                "username": username,
                "email": email,
                "first_name": first_name,
                "last_name": last_name,
                "password": password,
            }

            # --------------------------------------------------
            # Generate 6 digit OTP
            # --------------------------------------------------

            otp = str(random.randint(100000, 999999))

            # --------------------------------------------------
            # Store OTP in session
            # --------------------------------------------------

            request.session["registration_otp"] = otp

            request.session["otp_created_at"] = (
                timezone.now().isoformat()
            )

            request.session.modified = True

            # --------------------------------------------------
            # Send OTP email
            # --------------------------------------------------

            try:

                send_otp_email(
                    recipient_email=email,
                    otp=otp,
                    first_name=first_name,
                    subject=(
                        "GitHub Profile Finder - "
                        "Email Verification"
                    ),
                )

                messages.success(
                    request,
                    "OTP sent successfully to your email address."
                )

                return redirect(
                    "accounts:verify_otp"
                )

            except Exception as e:

                print("==========================================")
                print("EMAIL ERROR:", repr(e))
                print("EMAIL ERROR TYPE:", type(e).__name__)
                print("==========================================")

                # Remove OTP/session data if email failed

                request.session.pop(
                    "registration_otp",
                    None
                )

                request.session.pop(
                    "otp_created_at",
                    None
                )

                messages.error(
                    request,
                    "Unable to send OTP. Please check your Gmail configuration."
                )

        else:

            messages.error(
                request,
                "Please correct the errors below."
            )

    else:

        form = UserRegisterForm()

    return render(
        request,
        "accounts/register.html",
        {
            "form": form
        }
    )


# ==========================================================
# VERIFY OTP
# ==========================================================

def verify_otp_view(request):

    registration_data = request.session.get(
        "registration_data"
    )

    stored_otp = request.session.get(
        "registration_otp"
    )

    otp_created_at = request.session.get(
        "otp_created_at"
    )

    # ------------------------------------------------------
    # Registration session missing
    # ------------------------------------------------------

    if not registration_data or not stored_otp:

        messages.error(
            request,
            "Your registration session has expired. Please register again."
        )

        return redirect(
            "accounts:register"
        )

    # ------------------------------------------------------
    # Check OTP expiry
    # ------------------------------------------------------

    if otp_created_at:

        try:

            created_time = timezone.datetime.fromisoformat(
                otp_created_at
            )

            if timezone.is_naive(created_time):

                created_time = timezone.make_aware(
                    created_time
                )

            if (
                timezone.now()
                > created_time + timedelta(minutes=10)
            ):

                request.session.pop(
                    "registration_otp",
                    None
                )

                request.session.pop(
                    "otp_created_at",
                    None
                )

                messages.error(
                    request,
                    "OTP has expired. Please register again."
                )

                return redirect(
                    "accounts:register"
                )

        except Exception:

            request.session.pop(
                "registration_otp",
                None
            )

            request.session.pop(
                "otp_created_at",
                None
            )

            messages.error(
                request,
                "Invalid OTP session. Please register again."
            )

            return redirect(
                "accounts:register"
            )

    # ------------------------------------------------------
    # POST - Verify OTP
    # ------------------------------------------------------

    if request.method == "POST":

        entered_otp = request.POST.get(
            "otp",
            ""
        ).strip()

        # --------------------------------------------------
        # Empty OTP
        # --------------------------------------------------

        if not entered_otp:

            messages.error(
                request,
                "Please enter the OTP."
            )

            return render(
                request,
                "accounts/verify_otp.html",
                {
                    "email": registration_data["email"]
                }
            )

        # --------------------------------------------------
        # Wrong OTP
        # --------------------------------------------------

        if entered_otp != stored_otp:

            messages.error(
                request,
                "Invalid OTP. Please try again."
            )

            return render(
                request,
                "accounts/verify_otp.html",
                {
                    "email": registration_data["email"]
                }
            )

        # ==================================================
        # OTP CORRECT - CREATE USER
        # ==================================================

        try:

            # --------------------------------------------------
            # Check if username already exists
            # --------------------------------------------------

            if User.objects.filter(
                username=registration_data["username"]
            ).exists():

                messages.error(
                    request,
                    "Username already exists. Please register again."
                )

                request.session.pop(
                    "registration_data",
                    None
                )

                request.session.pop(
                    "registration_otp",
                    None
                )

                request.session.pop(
                    "otp_created_at",
                    None
                )

                return redirect(
                    "accounts:register"
                )

            # --------------------------------------------------
            # Check if email already exists
            # --------------------------------------------------

            if User.objects.filter(
                email=registration_data["email"]
            ).exists():

                messages.error(
                    request,
                    "This email is already registered. Please login."
                )

                request.session.pop(
                    "registration_data",
                    None
                )

                request.session.pop(
                    "registration_otp",
                    None
                )

                request.session.pop(
                    "otp_created_at",
                    None
                )

                return redirect(
                    "accounts:register"
                )

            # --------------------------------------------------
            # Create user
            # --------------------------------------------------

            user = User.objects.create_user(
                username=registration_data["username"],
                email=registration_data["email"],
                password=registration_data["password"],
                first_name=registration_data["first_name"],
                last_name=registration_data["last_name"],
            )

            # --------------------------------------------------
            # Create/Get profile
            # --------------------------------------------------

            profile, _ = UserProfile.objects.get_or_create(
                user=user
            )

            # --------------------------------------------------
            # Mark email verified
            # --------------------------------------------------

            if hasattr(profile, "is_email_verified"):
                profile.is_email_verified = True

            if hasattr(profile, "otp_code"):
                profile.otp_code = ""

            if hasattr(profile, "otp_created_at"):
                profile.otp_created_at = None

            profile.save()

            # --------------------------------------------------
            # Clear registration session
            # --------------------------------------------------

            request.session.pop(
                "registration_data",
                None
            )

            request.session.pop(
                "registration_otp",
                None
            )

            request.session.pop(
                "otp_created_at",
                None
            )

            # --------------------------------------------------
            # Login user
            # --------------------------------------------------

            login(
                request,
                user
            )

            messages.success(
                request,
                f"Welcome to GitHub Profile Finder, @{user.username}!"
            )

            return redirect(
                "dashboard:index"
            )

        except Exception as e:

            print("==========================================")
            print("USER CREATION ERROR:", repr(e))
            print("USER CREATION ERROR TYPE:", type(e).__name__)
            print("==========================================")

            messages.error(
                request,
                "Unable to create your account. Please try again."
            )

    # ------------------------------------------------------
    # GET / Default
    # ------------------------------------------------------

    return render(
        request,
        "accounts/verify_otp.html",
        {
            "email": registration_data["email"]
        }
    )


# ==========================================================
# RESEND OTP
# ==========================================================

def resend_otp_view(request):

    registration_data = request.session.get(
        "registration_data"
    )

    # ------------------------------------------------------
    # Registration session missing
    # ------------------------------------------------------

    if not registration_data:

        messages.error(
            request,
            "Registration session expired. Please register again."
        )

        return redirect(
            "accounts:register"
        )

    # ------------------------------------------------------
    # Generate new OTP
    # ------------------------------------------------------

    otp = str(
        random.randint(100000, 999999)
    )

    request.session["registration_otp"] = otp

    request.session["otp_created_at"] = (
        timezone.now().isoformat()
    )

    request.session.modified = True

    # ------------------------------------------------------
    # Send new OTP
    # ------------------------------------------------------

    try:

        send_otp_email(
            recipient_email=registration_data["email"],
            otp=otp,
            first_name=registration_data.get(
                "first_name",
                "User"
            ),
            subject="GitHub Profile Finder - New OTP",
        )

        messages.success(
            request,
            "A new OTP has been sent to your email."
        )

    except Exception as e:

        print("==========================================")
        print(
            "RESEND EMAIL ERROR:",
            repr(e)
        )
        print(
            "RESEND EMAIL ERROR TYPE:",
            type(e).__name__
        )
        print("==========================================")

        messages.error(
            request,
            "Unable to send OTP. Please try again."
        )

    return redirect(
        "accounts:verify_otp"
    )


# ==========================================================
# LOGIN
# ==========================================================

def login_view(request):

    if request.user.is_authenticated:
        return redirect(
            "dashboard:index"
        )

    if request.method == "POST":

        form = AuthenticationForm(
            request,
            data=request.POST
        )

        if form.is_valid():

            user = form.get_user()

            login(
                request,
                user
            )

            messages.success(
                request,
                f"Welcome back, @{user.username}!"
            )

            next_url = (
                request.GET.get("next")
                or "dashboard:index"
            )

            return redirect(
                next_url
            )

        else:

            messages.error(
                request,
                "Invalid username or password."
            )

    else:

        form = AuthenticationForm()

    return render(
        request,
        "accounts/login.html",
        {
            "form": form
        }
    )


# ==========================================================
# LOGOUT
# ==========================================================

def logout_view(request):

    logout(request)

    messages.info(
        request,
        "You have been logged out."
    )

    return redirect(
        "finder:home"
    )


# ==========================================================
# PROFILE SETTINGS
# ==========================================================

@login_required
def profile_settings_view(request):

    profile, created = (
        UserProfile.objects.get_or_create(
            user=request.user
        )
    )

    if request.method == "POST":

        form = UserProfileUpdateForm(
            request.POST,
            instance=profile
        )

        if form.is_valid():

            form.save()

            messages.success(
                request,
                "Profile preferences updated successfully!"
            )

            return redirect(
                "accounts:settings"
            )

    else:

        form = UserProfileUpdateForm(
            instance=profile
        )

    return render(
        request,
        "accounts/profile_settings.html",
        {
            "form": form,
            "profile": profile
        }
    )


# ==========================================================
# TOGGLE THEME
# ==========================================================

@require_POST
def toggle_theme(request):

    theme = "dark"

    if request.body:

        try:

            data = json.loads(
                request.body
            )

            theme = data.get(
                "theme",
                "dark"
            )

        except Exception:

            pass

    if request.user.is_authenticated:

        profile, _ = (
            UserProfile.objects.get_or_create(
                user=request.user
            )
        )

        profile.theme_preference = theme

        profile.save()

    request.session["theme_preference"] = theme

    return JsonResponse(
        {
            "status": "success",
            "theme": theme
        }
    )