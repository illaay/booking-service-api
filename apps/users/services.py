def user_directory_path(instance, filename) -> str:
    """
    Generate a dynamic upload destination directory path for user media assets.

    :param instance: The instance of the user model where the file is being uploaded.
    :type instance: apps.users.models.User
    :param filename: The original file name of the uploaded asset.
    :type filename: str
    :return: Formatted system destination storage path string.
    :rtype: str
    """
    return f'user_{instance.id}/{filename}'


def normalize_name(text) -> str:
    """
    Strip leading or trailing whitespaces and enforce standard title capitalization.

    :param text: Raw input text representation of personal identities names.
    :type text: str
    :return: Cleaned and normalized text representation string.
    :rtype: str
    """
    return text.strip().title() if text else ""
