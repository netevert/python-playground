"""
Simple Python caesar cypher
"""
import argparse
import string

class EncryptionEngine:
    """
    Extensible Caesar cypher engine

    Attributes:
        text(str): message to be encrypted
        shift_key(int): key to shift alphabet characters
        alphabets(tuple): alphabet characters to be included in the engine 

    Methods:
        process():
            Encrypts/decrypts text depending on shift_key supplied to class
        shift(alphabet):
            Creates a shifted copy of an alphabet
    """
    def __init__(self, text, shift_key):
        self.text = text
        self.shift_key = shift_key
        self.__alphabets = (string.ascii_lowercase, string.ascii_uppercase, string.digits)

    def process(self):
        """Returns encrypted/decrypted text depending on shift key supplied"""
        # Create shifted alphabet based on shift key
        shifted_alphabets = tuple(map(self.shift_alphabet, self.__alphabets))
        
        # Create alphabet strings needed to create encrytion table
        joined_alphabets = ''.join(self.__alphabets)
        joined_shifted_alphabets = ''.join(shifted_alphabets)

        # Create encryption table by translating alphabet characters 
        # to shifted characters 
        table = str.maketrans(joined_alphabets, joined_shifted_alphabets)

        # Encrypt/decrypt text
        return self.text.translate(table)
    
    def shift_alphabet(self, alphabet):
        """Returns a shifted alphabet based on the shift key supplied
           
           Parameters:
              alphabet(str): A string of alphabet characters

           Returns:
              shifted alphabet(str): A string of alphabet characters 
                                     shifted according to the shift key 
        """
        return alphabet[self.shift_key:] + alphabet[:self.shift_key]

def main():
    """Main program entry point"""
    # Setup commandline paramenter
    parser = argparse.ArgumentParser(description="Simple caesar cypher")
    parser.add_argument("-m", "--message", help="The string to encrypt", required=True, type=str)
    parser.add_argument("-k", "--key", help="Encryption shift key", type=int, default=3)

    # Parse commandline arguments
    args = parser.parse_args()

    # Run encryption program and print result
    print(EncryptionEngine(args.message, args.key).process())

if __name__ == "__main__":
    main()
