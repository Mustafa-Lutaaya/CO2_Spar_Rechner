import random # Generates random passwords
import bcrypt # Securely hashes password
import string # Letters, digits & symbols choice

class PWDHandler:
    @staticmethod
    def generate_password(length=12):
        characters = string.ascii_letters + string.digits + string.punctuation # All possible characters
        return ''.join(random.choices(characters, k=length)) # Creates random password
    

    @staticmethod
    def hash_password(password):
        hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()) # Hashes password with bcrypt
        return hashed.decode('utf-8') # Returns hashed password as string
    
    @staticmethod
    def verify_password(plain_password, hashed_password):
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8')) # Checks if passwords match