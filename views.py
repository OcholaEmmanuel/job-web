import json
from django.core.mail import send_mail
from django.contrib.auth.models import User
from django.core.signing import TimestampSigner, BadSignature, SignatureExpired
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt

ADMIN_EMAIL = 'ocholaemmanuelotieno@gmail.com'

signer = TimestampSigner()


@csrf_exempt
def register_request(request):
    """
    Handles user registration request submissions from the front-end form.
    Creates an inactive user and emails an action link to the admin.
    """
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return JsonResponse({'error': 'Email and password are required.'}, status=400)

            if User.objects.filter(username=email).exists():
                return JsonResponse({'error': 'An account with this email already exists or is pending approval.'}, status=400)

            user = User.objects.create_user(username=email, email=email, password=password, is_active=False)

            approve_token = signer.sign(f"{user.id}:approve")
            deny_token = signer.sign(f"{user.id}:deny")

            base_url = "https://openedcareer.com"  
            approve_url = f"{base_url}/api/admin/action/?token={approve_token}"
            deny_url = f"{base_url}/api/admin/action/?token={deny_token}"

            subject = f"New User Account Request: {email}"
            message = (
                f"Hello Admin,\n\n"
                f"A new user has requested access to Opened Career:\n"
                f"Email: {email}\n\n"
                f"Select an action below to process this request:\n\n"
                f"APPROVE USER:\n{approve_url}\n\n"
                f"DENY & DELETE REQUEST:\n{deny_url}\n\n"
                f"Note: These action links expire in 24 hours."
            )

            send_mail(
                subject,
                message,
                'noreply@openedcareer.com',
                [ADMIN_EMAIL],
                fail_silently=False,
            )

            return JsonResponse({'message': 'Registration request submitted for admin review.'}, status=201)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON format in request body.'}, status=400)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Invalid request method.'}, status=405)


def admin_action(request):
    """
    Endpoint triggered when the admin clicks "Approve" or "Deny" inside their email inbox.
    """
    token = request.GET.get('token')

    if not token:
        return HttpResponse("Missing verification token.", status=400)

    try:
    
        value = signer.unsign(token, max_age=86400)
        user_id, action = value.split(':')

        user = User.objects.get(id=user_id)

        if action == 'approve':
            user.is_active = True
            user.save()

            send_mail(
                "Account Approved - Opened Career",
                "Hello,\n\nYour account request on Opened Career has been approved! You can now log in to access your dashboard.",
                'noreply@openedcareer.com',
                [user.email],
                fail_silently=True,
            )
            return HttpResponse(f"<h2>Success</h2><p>Account for <strong>{user.email}</strong> has been approved and activated.</p>")

        elif action == 'deny':
            user_email = user.email
            user.delete()
            return HttpResponse(f"<h2>Request Denied</h2><p>Account request for <strong>{user_email}</strong> was rejected and removed.</p>")

    except (BadSignature, SignatureExpired):
        return HttpResponse("<h2>Error</h2><p>This action link is invalid or has expired.</p>", status=400)
    except User.DoesNotExist:
        return HttpResponse("<h2>Error</h2><p>User account was not found or has already been processed.</p>", status=404)