def user_directory_path(instance, filename):
    return f'user_{instance.user.id}/{filename}'

def normalize_name(text):
    return text.strip().title() if text else ""
