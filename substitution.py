import wave
import os
import shutil
import global_variables as g
from cryptography.fernet import Fernet

def lsb_encrypt(encrypt=None):
    # Check path
    dirname = os.getcwd()
    original_song_name = dirname + "/resources/" + g.filename_wav
    edit_song_name = dirname + "/media/" + g.filename_wav
    # read wave audio file
    song = wave.open(original_song_name, mode='rb')

    # Read frames and convert to byte array
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))
    #print("You can write "+ {len(frame_bytes)/8} +" of bits")

    # The "secret" text message
    print("\n\u001b[33m[!]\u001b[0m Tell me your secret: ", end='')
    secret = input()
    encr_message = secret
    if encrypt == 1:
        #Generate the key(32 bytes url-safe encoded)
        key = Fernet.generate_key()
        print("\n\u001b[36m[*]\u001b[0m The key is: "+str(key.decode("utf-8")))
        print("\t*Please share it with the receiver")
        
        #Create Fernet instance
        fernet = Fernet(key)
        #Encrypt the message
        encr_message = fernet.encrypt(secret.encode())
        encr_message = encr_message.decode("utf-8")
    # Append dummy data to fill out rest of the bytes. Receiver shall detect and remove these characters.
    string = encr_message + int((len(frame_bytes)-(len(encr_message)*8*8))/8) *'$'
    # Convert text to bit array
    bits = list(map(int, ''.join([bin(ord(i)).lstrip('0b').rjust(8,'0') for i in string])))
    # Replace LSB of each byte of the audio data by one bit from the text bit array
    for i, bit in enumerate(bits):
        frame_bytes[i] = (frame_bytes[i] & 254) | bit
    # Get the modified bytes
    frame_modified = bytes(frame_bytes)

    # Write bytes to a new wave audio file
    fd = wave.open(edit_song_name, 'wb')
    fd.setparams(song.getparams())
    fd.writeframes(frame_modified)
    fd.close()
    song.close()

    print("\u001b[32m[*]\u001b[0m Done!")

def lsb_decrypt(encrypt=None):
    # Check path
    dirname = os.getcwd()
    song_name = dirname + "/media/" + g.filename_wav

    song = wave.open(song_name, mode='rb')
    # Convert audio to byte array
    frame_bytes = bytearray(list(song.readframes(song.getnframes())))

    # Extract the LSB of each byte
    extracted = [frame_bytes[i] & 1 for i in range(len(frame_bytes))]
    
    # Convert byte array back to string
    string = "".join(chr(int("".join(map(str,extracted[i:i+8])),2)) for i in range(0,len(extracted),8))
    
    # Cut off at the filler characters
    record = string.split("$$$")[0]
    decoded = record.encode()
    result = decoded

    if encrypt == 1:
        #The message is decrypted using the same key
        print("\n\u001b[33m[!]\u001b[0m Please insert the key: ", end='')
        key = input()
        fernet = Fernet(key)
        result = fernet.decrypt(decoded)

    # Print the extracted text
    print("\n\u001b[34m[*]\u001b[0m Succesfully extracted audio file")
    print("\u001b[32m[*]\u001b[0m The hidden text is: "+ result.decode("utf-8"))

    song.close()

def options():

    while True:
        print("""\nOptions
    \u001b[33m[a] Generate audio stego\u001b[0m
    \u001b[33m[b] Generate audio stego using Fernet\u001b[0m
    \u001b[33m[c] Extract information from audio stego\u001b[0m
    \u001b[33m[d] Extract encrypted information from audio stego\u001b[0m
    [e] Exit""")
    
        option = input("Please select an option: ")

        if option == "a":
            if g.filename_wav == "":
                print("\u001b[31m[!]\u001b[0m This option is only for music files!")
            else:
                lsb_encrypt()
        elif option == "b":
            if g.filename_wav == "":
                print("\u001b[31m[!]\u001b[0m This option is only for music files!")
            else:
                lsb_encrypt(1)
        elif option == "c":
            if g.filename_wav == "":
                print("\u001b[31m[!]\u001b[0m This option is only for music files!")
            else:
                lsb_decrypt()
        elif option == "d":
            if g.filename_wav == "":
                print("\u001b[31m[!]\u001b[0m This option is only for music files!")
            else:
                lsb_decrypt(1)
        elif option == "e":
            break
        else:
            print ("Please select a valid option")