# 🔐 Secure Authentication System

A Python-based terminal authentication system with advanced security features including password hashing, salt generation, attempt tracking, and progressive blocking mechanism.

## Features

- **Secure Password Hashing**: SHA-256 with random 5-digit salt
- **Username Validation**: Exactly 5 lowercase letters (a-z)
- **Strong Password Policy**: Minimum 8 characters with lowercase, uppercase, and digits
- **Progressive Blocking System**:
  - 5 cycles with 3 attempts each (15 total attempts)
  - Blocking delays: 5s → 10s → 15s → 20s
  - Permanent ban after final cycle
- **Color-coded Interface**: ANSI colors for better UX
- **Session Management**: In-memory attempt tracking
- **Hidden Password Input**: Uses `getpass` for secure input

## Requirements

- Python 3.6+
- No external dependencies (uses only standard library)

## Installation

```bash
git clone https://github.com/NourIslamAoudia/Secure-Auth-System.git
cd Secure-Auth-System
python auth.py
```

## Usage

### Menu Options

1. **signup** - Create a new account
2. **signin** - Login to existing account
3. **exit** - Quit the program

### Account Creation

```
Username: 5 lowercase letters only (e.g., alice)
Password: Min 8 chars, 1 lowercase, 1 uppercase, 1 digit (e.g., Pass1234)
```

### Login Attempts

- **Cycle 1-4**: 3 failed attempts → Temporary block → Next cycle
- **Cycle 5**: 3 failed attempts → Permanent ban
- Successful login resets all attempt counters

## File Structure

```
Secure-Auth-System/
├── auth.py           # Main authentication program
├── password.txt      # User credentials (username:salt:hash)
├── baned-user.txt    # List of banned usernames
└── Readme.md         # Documentation
```

## Security Features

- **SHA-256 Hashing**: Cryptographically secure password hashing
- **Random Salt**: 5-digit salt using `secrets` module
- **Progressive Delays**: Prevents brute-force attacks
- **Permanent Bans**: Blocks persistent attackers
- **No Plaintext Storage**: Passwords never stored in plain text

## Example Flow

```
Cycle 1: 3 attempts → Block 5s
Cycle 2: 3 attempts → Block 10s
Cycle 3: 3 attempts → Block 15s
Cycle 4: 3 attempts → Block 20s
Cycle 5: 3 attempts → BANNED
```

## Author

Nour Islam Aoudia

---

**Note**: Attempt counters reset when the program restarts. Banned users remain banned permanently.
