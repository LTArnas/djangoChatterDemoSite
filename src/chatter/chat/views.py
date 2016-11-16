from django.shortcuts import render, get_object_or_404, get_list_or_404, redirect
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import check_password, make_password
from .models import Chatroom, Profile, Post

SESSION_ROOM_KEY_PREFIX = "chatroom"

def index(request):
    rooms = Chatroom.objects.all()
    return render(request, "chat/index.html", {"chatrooms": rooms})
"""
def profile(request, profile_id):
    profile = get_object_or_404()
"""
@login_required
def create_chatroom(request):
    render_template_name = "chat/create_chatroom.html"
    if request.method == "GET":
        return render(request, render_template_name)

    title = request.POST.get("title", None)
    description = request.POST.get("description", None)
    password = request.POST.get("password", None)
    password_retry = request.POST.get("password_retry", None)
    errors = []
    # Validation...
    if password != password_retry:
        errors.append("Passwords did not match.")
    if not password or password.isspace():
        password = ""
    if not title:
        errors.append("No title.")

    try:
        creator = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        errors.append(
            "Could not retrive your profile information. Try logging out then logging back in.")
    except Profile.MultipleObjectsReturned:
        errors.append(
            "You appear to have multiple profiles, this should not be possible. This needs to be fixed before a chatroom can be made.")

    if errors:
        return render(request, render_template_name, {"errors": errors})

    # By this point, we should be all good to make a chatroom...
    if password: # We store password as hash. Chatrooms be so secure.
        password = make_password(password)

    room = Chatroom.objects.create(
        title=title,
        description=description,
        password=password,
        creator=creator)

    if room:
        return redirect("chat:chatroom", int(room.id))
    else:
        errors.append("Failed to create room, sorry. Try again.")
        return render(request, render_template_name, {"errors":errors})

def chatroom(request, chatroom_id):
    render_template_name = "chat/chatroom.html"
    room = get_object_or_404(Chatroom, pk=chatroom_id)
    # The key used when storing room's login status in the session.
    # Must match what is set by the challenge.
    session_room_key = SESSION_ROOM_KEY_PREFIX + str(chatroom_id)
    if room.password and room.password.isspace():
        if not request.session.get(session_room_key, None) == str(True):
            return redirect("chat:chatroom_password_challenge", int(chatroom_id))
    # By this point, the we should be safe to show the chat.
    messages = Post.objects.filter(chatroom=room.id)
    context = {"chatroom": room, "messages": messages}
    return render(request, render_template_name, context)

def chatroom_post(request, chatroom_id):
    room = get_object_or_404(Chatroom, pk=chatroom_id)
    # The key used when storing room's login status in the session.
    # Must match what is set by the challenge.
    session_room_key = SESSION_ROOM_KEY_PREFIX + str(chatroom_id)
    if room.password and room.password.isspace():
        if not request.session.get(session_room_key, None) == str(True):
            return redirect("chat:chatroom_password_challenge", int(chatroom_id))
    if not request.user.is_authenticated:
        return redirect("chat:chatroom", int(chatroom_id))
    # By this point, we should be safe to create a message...
    message_content = request.POST.get("message", None)
    if not message_content:
        return redirect("chat:chatroom", int(chatroom_id))
    message_author = Profile.objects.get(user=request.user)
    Post.objects.create(
        content=message_content,
        author=message_author,
        chatroom=room)
    return redirect("chat:chatroom", int(chatroom_id))

def chatroom_password_challenge(request, chatroom_id):
    """ On success, sets the session object to have a chatroom-unique key, with value of "True".
        Otherwise does not set anything.
        Key is computed like this:
            SESSION_ROOM_KEY_PREFIX + str(room.id)"""
    render_template_name = "chat/chatroom_password_challenge.html"
    room = get_object_or_404(Chatroom, pk=chatroom_id)
    # The key used when storing room's login status in the session.
    session_room_key = SESSION_ROOM_KEY_PREFIX + str(room.id)

    if request.method == "GET":
        # May have already logged in to the room, recently.
        if request.session.get(session_room_key, None) == str(True):
            return redirect("chat:chatroom", int(room.id))
        else:
            return render(request, render_template_name, {"chatroom": room})

    password_attempt = request.POST.get("password", None)
    if check_password(password_attempt, room.password):
        request.session[SESSION_ROOM_KEY_PREFIX+str(room.id)] = str(True)
        return redirect("chat:chatroom", int(room.id))
    else:
        return render(request, render_template_name, {"chatroom": room})

def register_user(request):
    render_template_name = "chat/register.html"
    if request.method == "GET":
        return render(request, render_template_name)

    username = request.POST.get("username", None)
    email = request.POST.get("email", None)
    password = request.POST.get("password", None)
    password_retry = request.POST.get("password_retry", None)
    errors = []
    # Validation...
    if not username:
        errors.append("Username is required.")
    if not email:
        errors.append("Email is required.")
    if not password or not password_retry:
        errors.append("Password fields are required.")
    if password != password_retry:
        errors.append("Passwords did not match.")
    if errors:
        return render(request, render_template_name, {"errors": errors})
    # By this point, we should be all good to create user.
    user, created = User.objects.get_or_create(username=username, email=email)

    if created:
        user.set_password(password)
        user.save()
        return redirect(reverse("login"))
    else:
        errors.append("You seem to be already registered.")
        return render(request, render_template_name, {
            "errors": errors})

