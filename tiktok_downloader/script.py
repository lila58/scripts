import os
import subprocess
import sys


def download_tiktok_videos(tiktok_url, output_folder="./downloads"):
    """
    Télécharge les vidéos TikTok à l'aide de yt-dlp.

    Args:
        tiktok_url: URL d'un profil TikTok ou d'une vidéo TikTok.
        output_folder: Dossier dans lequel enregistrer les vidéos téléchargées.

    Returns:
        True si le téléchargement s'est terminé correctement, sinon False.
    """
    # Crée le dossier de destination s'il n'existe pas déjà.
    # exist_ok=True évite une erreur lorsque le dossier existe déjà.
    os.makedirs(output_folder, exist_ok=True)

    # Construit la commande qui sera exécutée dans le terminal.
    # Les variables utilisées par yt-dlp permettent de classer les vidéos
    # dans un sous-dossier portant le nom de l'utilisateur qui les a publiées.
    command = [
        "yt-dlp",
        "-o", f"{output_folder}/%(uploader)s/%(title)s.%(ext)s",
        "--no-warnings",  # Masque les avertissements non bloquants.
        "--progress",  # Affiche la progression du téléchargement.
        tiktok_url  # URL du profil ou de la vidéo à télécharger.
    ]

    # Informe l'utilisateur de la source et du dossier de destination.
    print(f"Downloading TikTok videos from: {tiktok_url}")
    print(f"Saving to: {output_folder}\n")

    try:
        # Exécute yt-dlp et lève une exception si la commande échoue.
        subprocess.run(command, check=True)
        print("\nDownload complete!")
        return True
    except subprocess.CalledProcessError as e:
        # Cette erreur indique que yt-dlp a été lancé mais n'a pas pu
        # terminer correctement le téléchargement.
        print(f"\nError during download: {e}")
        return False
    except FileNotFoundError:
        # Cette erreur survient lorsque yt-dlp n'est pas installé ou
        # lorsque son exécutable n'est pas présent dans le PATH système.
        print("Error: yt-dlp is not installed or not found in PATH")
        print("Install it with: pip install yt-dlp")
        return False


# Ce bloc n'est exécuté que lorsque le fichier est lancé directement.
# Il ne s'exécute pas si la fonction est importée depuis un autre script.
if __name__ == "__main__":
    # Vérifie qu'un nom d'utilisateur a bien été fourni en argument.
    if len(sys.argv) < 2:
        print("Usage: python script.py <username> [output_folder]")
        print("Example: python script.py khaby.lame")
        sys.exit(1)

    # Récupère le nom d'utilisateur fourni sur la ligne de commande.
    username = sys.argv[1]

    # Accepte aussi bien "username" que "@username".
    # Le caractère @ est retiré avant de construire l'URL TikTok.
    if username.startswith('@'):
        username = username[1:]

    # Transforme le nom d'utilisateur en URL de profil TikTok complète.
    tiktok_url = f"https://www.tiktok.com/@{username}"

    # Utilise le deuxième argument comme dossier de sortie si celui-ci
    # est fourni ; sinon, le dossier ./downloads est utilisé par défaut.
    output_folder = sys.argv[2] if len(sys.argv) > 2 else "./downloads"

    # Lance le téléchargement avec les paramètres récupérés.
    download_tiktok_videos(tiktok_url, output_folder)
