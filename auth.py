import hashlib
import secrets
import getpass
import time
import os
import sys
from datetime import datetime


# === Configuration des couleurs ANSI ===
class Colors:
    """Codes couleurs ANSI pour terminal"""
    RESET = '\033[0m'
    BOLD = '\033[1m'
    
    # Couleurs de texte
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    MAGENTA = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    
    # Couleurs de fond
    BG_RED = '\033[101m'
    BG_GREEN = '\033[102m'
    BG_BLUE = '\033[104m'

# === Fichiers de données ===
PASSWORD_FILE = "password.txt"
BANNED_FILE = "baned-user.txt"

# === Constantes de sécurité ===
MAX_ATTEMPTS_PER_CYCLE = 3  # 3 tentatives par cycle
TOTAL_CYCLES = 5  # Total de 5 cycles
BLOCK_DELAYS = [5, 10, 15, 20]  # Délais de blocage en secondes (cycles 1 à 4)
SALT_LENGTH = 5  # Longueur du salt (5 chiffres)

# === Dictionnaire en mémoire pour les tentatives ===
# Format: {username: {'failed_attempts': int, 'cycle_count': int}}
user_attempts = {}


def clear_screen():
    """Efface l'écran du terminal"""
    os.system('cls' if os.name == 'nt' else 'clear')


def print_animated(text, color=Colors.WHITE, delay=0.02):
    """Affiche du texte avec animation caractère par caractère"""
    for char in text:
        sys.stdout.write(color + char + Colors.RESET)
        sys.stdout.flush()
        time.sleep(delay)
    print()



def print_menu():
    """Affiche le menu principal"""
    menu = f"""
{Colors.BOLD}{Colors.BLUE}+-------------------------------+
|        MENU PRINCIPAL         |
+-------------------------------+{Colors.RESET}

{Colors.GREEN}1.{Colors.RESET} {Colors.BOLD}signup{Colors.RESET}  - Creer un nouveau compte
{Colors.YELLOW}2.{Colors.RESET} {Colors.BOLD}signin{Colors.RESET}  - Se connecter
{Colors.RED}3.{Colors.RESET} {Colors.BOLD}exit{Colors.RESET}    - Quitter le programme

"""
    print(menu)


def loading_animation(message, duration=1.0):
    """Affiche une animation de chargement"""
    frames = ['|', '/', '-', '\\']
    end_time = time.time() + duration
    i = 0
    
    while time.time() < end_time:
        sys.stdout.write(f'\r{Colors.CYAN}[{frames[i % len(frames)]}] {message}...{Colors.RESET}')
        sys.stdout.flush()
        time.sleep(0.1)
        i += 1
    
    sys.stdout.write('\r' + ' ' * (len(message) + 10) + '\r')
    sys.stdout.flush()


def success_message(message):
    """Affiche un message de succès"""
    print(f"\n{Colors.GREEN}{Colors.BOLD}[OK] {message}{Colors.RESET}\n")
    time.sleep(1)


def error_message(message):
    """Affiche un message d'erreur"""
    print(f"\n{Colors.RED}{Colors.BOLD}[X] {message}{Colors.RESET}\n")
    time.sleep(1)


def warning_message(message):
    """Affiche un message d'avertissement"""
    print(f"\n{Colors.YELLOW}{Colors.BOLD}[!] {message}{Colors.RESET}\n")


def info_message(message):
    """Affiche un message d'information"""
    print(f"\n{Colors.BLUE}[i] {message}{Colors.RESET}\n")


def initialize_files():
    """Crée les fichiers nécessaires s'ils n'existent pas"""
    files = [PASSWORD_FILE, BANNED_FILE]
    for file in files:
        if not os.path.exists(file):
            with open(file, 'w', encoding='utf-8') as f:
                pass


def generate_salt():
    """Génère un salt aléatoire de 5 chiffres"""
    return ''.join([str(secrets.randbelow(10)) for _ in range(SALT_LENGTH)])


def hash_password(password, salt):
    """Calcule le hash SHA-256 du mot de passe avec le salt"""
    combined = password + salt
    return hashlib.sha256(combined.encode()).hexdigest()


def validate_username(username):
    """
    Valide le username selon les règles :
    - Exactement 5 caractères
    - Uniquement des lettres minuscules (a-z)
    """
    if len(username) != 5:
        return False, "Le username doit contenir exactement 5 caractères"
    
    if not username.isalpha():
        return False, "Le username ne doit contenir que des lettres"
    
    if not username.islower():
        return False, "Le username ne doit contenir que des lettres minuscules"
    
    return True, "Username valide"


def validate_password(password):
    """
    Valide le password selon les règles :
    - Au moins 8 caractères
    - Au moins une minuscule
    - Au moins une majuscule
    - Au moins un chiffre (0-9)
    """
    if len(password) < 8:
        return False, "Le mot de passe doit contenir au moins 8 caractères"
    
    has_lower = any(c.islower() for c in password)
    has_upper = any(c.isupper() for c in password)
    has_digit = any(c.isdigit() for c in password)
    
    if not has_lower:
        return False, "Le mot de passe doit contenir au moins une minuscule"
    
    if not has_upper:
        return False, "Le mot de passe doit contenir au moins une majuscule"
    
    if not has_digit:
        return False, "Le mot de passe doit contenir au moins un chiffre"
    
    return True, "Mot de passe valide"


def username_exists(username):
    """Vérifie si un username existe déjà"""
    try:
        with open(PASSWORD_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                stored_username = line.strip().split(':')[0]
                if stored_username == username:
                    return True
    except FileNotFoundError:
        pass
    return False


def is_user_banned(username):
    """Vérifie si un utilisateur est banni"""
    try:
        with open(BANNED_FILE, 'r', encoding='utf-8') as f:
            banned_users = [line.strip() for line in f]
            return username in banned_users
    except FileNotFoundError:
        return False


def ban_user(username):
    """Bannit un utilisateur"""
    with open(BANNED_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{username}\n")


def get_user_attempts(username):
    """Récupère les informations de tentatives d'un utilisateur depuis la mémoire"""
    if username in user_attempts:
        return user_attempts[username]
    return {'failed_attempts': 0, 'cycle_count': 0}


def update_user_attempts(username, failed_attempts, cycle_count):
    """Met à jour les informations de tentatives d'un utilisateur en mémoire"""
    user_attempts[username] = {
        'failed_attempts': failed_attempts,
        'cycle_count': cycle_count
    }


def reset_user_attempts(username):
    """Réinitialise les tentatives d'un utilisateur"""
    if username in user_attempts:
        del user_attempts[username]


def signup():
    print(f"{Colors.BOLD}{Colors.GREEN}═══ INSCRIPTION ═══{Colors.RESET}\n")
    
    # Demande du username
    while True:
        username = input(f"{Colors.CYAN}Username (5 lettres minuscules) : {Colors.RESET}").strip()
        
        valid, message = validate_username(username)
        if not valid:
            error_message(message)
            continue
        
        # Vérification si le username existe déjà
        if username_exists(username):
            error_message(f"Le username '{username}' existe déjà")
            continue
        
        break
    
    # Demande du password
    while True:
        password = getpass.getpass(f"{Colors.CYAN}Password (min 8 car, 1 min, 1 MAJ, 1 chiffre) : {Colors.RESET}")
        
        valid, message = validate_password(password)
        if not valid:
            error_message(message)
            continue
        
        # Confirmation du password
        password_confirm = getpass.getpass(f"{Colors.CYAN}Confirmez le password : {Colors.RESET}")
        
        if password != password_confirm:
            error_message("Les mots de passe ne correspondent pas")
            continue
        
        break
    
    # Génération du salt et du hash
    loading_animation("Création du compte")
    
    salt = generate_salt()
    password_hash = hash_password(password, salt)
    
    # Enregistrement dans le fichier
    with open(PASSWORD_FILE, 'a', encoding='utf-8') as f:
        f.write(f"{username}:{salt}:{password_hash}\n")
    
    success_message(f"Compte cree avec succes ! Bienvenue {username} !")
    time.sleep(2)


def signin():
    """Fonction de connexion"""
    print(f"{Colors.BOLD}{Colors.YELLOW}═══ CONNEXION ═══{Colors.RESET}\n")
    
    # Demande du username
    username = input(f"{Colors.CYAN}Username : {Colors.RESET}").strip()
    
    # Vérification si le compte existe
    if not username_exists(username):
        error_message(f"Le compte '{username}' n'existe pas")
        time.sleep(2)
        return
    
    # Vérification si le compte est banni
    if is_user_banned(username):
        error_message(f"Le compte '{username}' est BANNI définitivement 🚫")
        time.sleep(2)
        return
    
    # Récupération des données du compte
    user_data = None
    with open(PASSWORD_FILE, 'r', encoding='utf-8') as f:
        for line in f:
            parts = line.strip().split(':')
            if parts[0] == username:
                user_data = {'username': parts[0], 'salt': parts[1], 'hash': parts[2]}
                break
    
    # Boucle de tentatives de connexion
    while True:
        # Récupération des tentatives actuelles
        attempts_data = get_user_attempts(username)
        failed_attempts = attempts_data['failed_attempts']
        cycle_count = attempts_data['cycle_count']
        
        # Calcul du numéro de cycle actuel (1-based pour l'affichage)
        current_cycle_number = cycle_count + 1
        
        # Affichage de l'état actuel seulement si des tentatives ont échoué
        if failed_attempts > 0 or cycle_count > 0:
            if current_cycle_number == TOTAL_CYCLES:
                print(f"{Colors.YELLOW}{Colors.BOLD}[!] DERNIER CYCLE {current_cycle_number}/{TOTAL_CYCLES} ! Tentatives echouees : {failed_attempts}/{MAX_ATTEMPTS_PER_CYCLE}{Colors.RESET}\n")
            else:
                print(f"{Colors.BLUE}[i] Cycle {current_cycle_number}/{TOTAL_CYCLES} | Tentatives echouees : {failed_attempts}/{MAX_ATTEMPTS_PER_CYCLE}{Colors.RESET}\n")
        
        # Demande du password
        password = getpass.getpass(f"{Colors.CYAN}Password : {Colors.RESET}")
        
        # Vérification du password
        password_hash = hash_password(password, user_data['salt'])
        
        if password_hash == user_data['hash']:
            # Connexion réussie
            reset_user_attempts(username)
            success_message(f"Connexion reussie ! Bienvenue {username} !")
            time.sleep(2)
            return  # Sortir de signin et retourner au menu
        else:
            # Échec de connexion
            failed_attempts += 1
            
            if failed_attempts >= MAX_ATTEMPTS_PER_CYCLE:
                # 3 tentatives échouées dans ce cycle
                
                # Vérifier si on est au dernier cycle (cycle 5)
                if current_cycle_number >= TOTAL_CYCLES:
                    # Bannissement définitif
                    ban_user(username)
                    error_message(f"3 echecs au cycle {current_cycle_number} ! Le compte '{username}' est BANNI DEFINITIVEMENT !")
                    time.sleep(3)
                    return
                else:
                    # Blocage temporaire (cycles 1 à 4)
                    block_time = BLOCK_DELAYS[cycle_count]
                    
                    warning_message(f"3 echecs au cycle {current_cycle_number} ! Blocage de {block_time} secondes...")
                    
                    # Animation de blocage
                    for remaining in range(block_time, 0, -1):
                        sys.stdout.write(f'\r{Colors.RED}{Colors.BOLD}[>>>] Deblocage dans : {remaining} secondes...{Colors.RESET}')
                        sys.stdout.flush()
                        time.sleep(1)
                    
                    print(f"\n")
                    
                    # Passer au cycle suivant et réinitialiser les tentatives
                    cycle_count += 1
                    failed_attempts = 0
                    update_user_attempts(username, failed_attempts, cycle_count)
                    
                    # Message après déblocage
                    next_cycle_number = cycle_count + 1
                    if next_cycle_number < TOTAL_CYCLES:
                        print(f"{Colors.BLUE}[OK] Debloque ! Passage au cycle {next_cycle_number}/{TOTAL_CYCLES} avec {MAX_ATTEMPTS_PER_CYCLE} nouvelles tentatives{Colors.RESET}\n")
                    else:
                        print(f"{Colors.YELLOW}{Colors.BOLD}[!] DERNIER CYCLE {next_cycle_number}/{TOTAL_CYCLES} ! Vous avez {MAX_ATTEMPTS_PER_CYCLE} dernieres tentatives avant BANNISSEMENT DEFINITIF !{Colors.RESET}\n")
                    
                    # Continuer la boucle pour les nouvelles tentatives
                    continue
            else:
                # Encore des tentatives dans le cycle actuel
                remaining = MAX_ATTEMPTS_PER_CYCLE - failed_attempts
                update_user_attempts(username, failed_attempts, cycle_count)
                
                print(f"{Colors.RED}{Colors.BOLD}[X] Mot de passe incorrect ! Il vous reste {remaining} tentative(s) dans ce cycle{Colors.RESET}\n")
                
                # Avertissement si on est au dernier cycle
                if current_cycle_number >= TOTAL_CYCLES:
                    print(f"{Colors.YELLOW}{Colors.BOLD}[!] ATTENTION ! Vous etes au DERNIER CYCLE avant bannissement !{Colors.RESET}\n")
                
                # Continuer la boucle pour une nouvelle tentative
                continue


def exit_program():
    """Fonction de sortie"""
    print_animated(f"Merci d'avoir utilise le systeme d'authentification securise !", delay=0.05)
    time.sleep(1)
    sys.exit(0)


def main():
    """Fonction principale"""
    # Initialisation des fichiers
    initialize_files()
    
    # Boucle principale
    while True:
        try:
            print_menu()
            
            choice = input(f"{Colors.BOLD}Votre choix : {Colors.RESET}").strip().lower()
            
            if choice in ['1', 'signup']:
                signup()
            elif choice in ['2', 'signin']:
                signin()
            elif choice in ['3', 'exit']:
                exit_program()
            else:
                error_message("Choix invalide ! Veuillez choisir 1, 2 ou 3")
                time.sleep(1)
        
        except KeyboardInterrupt:
            print(f"\n\n{Colors.YELLOW}Interruption détectée...{Colors.RESET}")
            exit_program()
        except Exception as e:
            error_message(f"Erreur inattendue : {str(e)}")
            time.sleep(2)


if __name__ == "__main__":
    main()
