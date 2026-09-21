import os
import sys
from urllib.parse import urlparse

import instaloader


def extract_instagram_source(source):
    """
    Transforme un nom d'utilisateur ou une URL Instagram en source exploitable.

    Returns:
        Un tuple contenant le type de source ("profile" ou "post") et sa valeur.
    """
    # Si l'utilisateur fournit seulement un nom, on retire un éventuel @.
    if not source.startswith(("http://", "https://")):
        return "profile", source.lstrip("@/")

    # Analyse l'URL pour récupérer ses différentes parties.
    parsed_url = urlparse(source)
    path_parts = [part for part in parsed_url.path.split("/") if part]

    # Une URL de publication Instagram ressemble à /p/SHORTCODE/,
    # /reel/SHORTCODE/ ou /tv/SHORTCODE/.
    if len(path_parts) >= 2 and path_parts[0].lower() in {"p", "reel", "tv"}:
        return "post", path_parts[1]

    # Pour une URL de profil, le premier élément du chemin est le nom d'utilisateur.
    if path_parts:
        return "profile", path_parts[0].lstrip("@")

    raise ValueError("URL Instagram invalide")


def download_instagram(source, media_type="all", output_folder="./downloads",
                       login_user=None):
    """
    Télécharge des publications Instagram avec Instaloader.

    Args:
        source: Nom d'utilisateur, URL de profil ou URL d'une publication Instagram.
        media_type: "videos", "photos" ou "all".
        output_folder: Dossier dans lequel enregistrer les fichiers.
        login_user: Nom du compte Instagram utilisé pour charger une session optionnelle.

    Returns:
        True si le téléchargement s'est terminé correctement, sinon False.
    """
    if media_type not in {"videos", "photos", "all"}:
        print("Error: media_type must be videos, photos or all")
        return False

    try:
        source_type, source_value = extract_instagram_source(source)
    except ValueError as error:
        print(f"Error: {error}")
        return False

    # Instaloader crée les sous-dossiers nécessaires selon ce modèle.
    # {target} sera remplacé par le nom du profil Instagram.
    loader = instaloader.Instaloader(
        dirname_pattern=os.path.join(output_folder, "{target}"),
        # Enregistre les commentaires disponibles dans les métadonnées.
        download_comments=True,
        # Conserve les informations de chaque publication au format JSON.
        save_metadata=True,
    )

    if login_user:
        try:
            # Tente de réutiliser une session enregistrée pour éviter de saisir
            # le mot de passe à chaque exécution.
            print(f"Logging in as {login_user}...")
            loader.load_session_from_file(login_user)
            print("Session loaded successfully!\n")
        except FileNotFoundError:
            # Si aucune session n'existe, Instaloader demande le mot de passe
            # puis enregistre la session pour les prochaines utilisations.
            print("No saved session found. Logging in manually...")
            loader.login(login_user, input("Enter your Instagram password: "))
            loader.save_session_to_file()
            print("Session saved!\n")

    try:
        if source_type == "profile":
            print(f"Downloading @{source_value} ({media_type})...\n")
            profile = instaloader.Profile.from_username(
                loader.context,
                source_value,
            )

            # Parcourt les publications du profil une par une.
            posts = profile.get_posts()
            target = source_value
        else:
            print(f"Downloading Instagram post {source_value}...\n")
            # Récupère une publication à partir de son shortcode URL.
            posts = [instaloader.Post.from_shortcode(
                loader.context,
                source_value,
            )]
            target = source_value

        for post in posts:
            # Ignore les publications qui ne correspondent pas au filtre choisi.
            if media_type == "videos" and not post.is_video:
                continue
            if media_type == "photos" and post.is_video:
                continue

            # Télécharge le média, sa légende et ses métadonnées.
            # Les commentaires disponibles sont inclus dans les métadonnées.
            loader.download_post(post, target=target)

        print("\nDownload complete!")
        return True

    except (instaloader.exceptions.InstaloaderException, ValueError) as error:
        # Regroupe les erreurs Instaloader : profil privé, publication absente,
        # authentification refusée, limitation Instagram, etc.
        print(f"\nError during download: {error}")
        return False


if __name__ == "__main__":
    # Ce bloc ne s'exécute que si le fichier est lancé directement.
    if len(sys.argv) < 2:
        print("Usage: python script.py <username-or-url> [media_type] [output_folder] [login_user]")
        print("media_type: videos | photos | all")
        print("Example: python script.py natgeo videos ./downloads my_username")
        print("Example: python script.py https://www.instagram.com/natgeo/")
        print("Example: python script.py https://www.instagram.com/p/SHORTCODE/")
        sys.exit(1)

    # La source peut être un nom d'utilisateur ou une URL Instagram complète.
    source = sys.argv[1]
    media_type = sys.argv[2] if len(sys.argv) > 2 else "all"
    output_folder = sys.argv[3] if len(sys.argv) > 3 else "./downloads"
    login_user = sys.argv[4] if len(sys.argv) > 4 else None

    download_instagram(source, media_type, output_folder, login_user)
