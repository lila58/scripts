import os
import subprocess
import sys


def download_tiktok_videos(tiktok_url, output_folder="./downloads"):
    """
    Télécharge des vidéos TikTok à l'aide de yt-dlp.

    Args:
        tiktok_url: URL d'un profil TikTok, d'une vidéo ou d'une playlist publique.
        output_folder: Dossier dans lequel enregistrer les vidéos téléchargées.

    Returns:
        True si le téléchargement s'est terminé correctement, sinon False.
    """
    # Crée le dossier de destination s'il n'existe pas déjà.
    # exist_ok=True évite une erreur lorsque le dossier existe déjà.
    os.makedirs(output_folder, exist_ok=True)

    # Construit la commande qui sera exécutée via le terminal.
    # Les éléments de cette liste correspondent aux arguments passés à yt-dlp.
    # L'option -o définit le format de stockage des fichiers téléchargés.
    # Ici, chaque vidéo est enregistrée dans un dossier nommé d'après l'uploader,
    # puis son titre est utilisé comme nom de fichier.
    command = [
        "yt-dlp",
        "-o",
        f"{output_folder}/%(uploader)s/%(title)s.%(ext)s",
        "--write-description",  # Enregistre aussi la description dans un fichier texte.
        "--write-comments",  # Tente de récupérer les commentaires disponibles.
        "--write-info-json",  # Sauvegarde toutes les métadonnées dans un fichier .info.json.
        "--no-warnings",  # Masque les avertissements non bloquants.
        "--progress",  # Affiche la progression du téléchargement.
        tiktok_url  # URL du profil, de la vidéo ou de la playlist publique.
    ]

    # Informe l'utilisateur de la source et du dossier de destination.
    print(f"Downloading TikTok videos from: {tiktok_url}")
    print(f"Saving to: {output_folder}\n")

    try:
        # Exécute yt-dlp en gardant une erreur si la commande échoue.
        # check=True permet d'attraper les erreurs de téléchargement ici.
        subprocess.run(command, check=True)
        print("\nDownload complete!")
        return True
    except subprocess.CalledProcessError as e:
        # Cette erreur indique que yt-dlp a démarré mais n'a pas réussi.
        # Cela peut arriver si l'URL est invalide, si TikTok bloque la requête,
        # ou si le contenu est inaccessible.
        print(f"\nError during download: {e}")
        return False
    except FileNotFoundError:
        # Cette erreur survient quand yt-dlp n'est pas installé ou n'est pas
        # présent dans la variable PATH du système.
        print("Error: yt-dlp is not installed or not found in PATH")
        print("Install it with: pip install yt-dlp")
        return False


# Ce bloc n'est exécuté que lorsque le script est lancé directement.
# Il ne s'exécute pas si le fichier est importé depuis un autre script.
if __name__ == "__main__":
    # Vérifie qu'un argument au moins a bien été fourni.
    # On accepte désormais soit un nom d'utilisateur, soit une URL complète.
    if len(sys.argv) < 2:
        print("Usage: python script.py <username-or-url> [output_folder]")
        print("Example: python script.py khaby.lame")
        print("Example: python script.py https://www.tiktok.com/@username")
        sys.exit(1)

    # Récupère la source donnée sur la ligne de commande.
    source = sys.argv[1]

    # Si l'utilisateur donne déjà une URL complète, on l'utilise directement.
    # Sinon, on construit une URL de profil TikTok à partir du nom d'utilisateur.
    if source.startswith(("http://", "https://")):
        tiktok_url = source
    else:
        username = source.lstrip("@")
        tiktok_url = f"https://www.tiktok.com/@{username}"

    # Utilise le deuxième argument comme dossier de sortie s'il est fourni.
    # Sinon, le dossier ./downloads est utilisé par défaut.
    output_folder = sys.argv[2] if len(sys.argv) > 2 else "./downloads"

    # Lance le téléchargement avec l'URL calculée ou fournie.
    download_tiktok_videos(tiktok_url, output_folder)
