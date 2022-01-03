import os
import re
import sys
import qrcode
import socket
import tkinter
from tkinter import ttk
from webbrowser import open_new_tab as link


class State:
    address = None

def gen_qr():
    """ Generate QR code server address """

    State.address = 'ws://' + get_ip() + ':8080'

    # Generate QR code of address
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=10,
        border=2,
    )
    qr.add_data(State.address)
    qr.make(fit=True)

    # Save QR code as image
    qr.make_image().save(resource_path('out.png'))


def window():
    """ Create a GUI """
    root = tkinter.Tk()
    screenHeight = root.winfo_screenheight()
    screenWidth = root.winfo_screenwidth()
    height = 500
    width = 400
    root.title('Kalman')
    root.geometry(f'{width}x{height}')
    root.resizable(0, 0)
    root.iconphoto(False, tkinter.PhotoImage(file=resource_path('kalman.png')))
    
    bgcolor = 'white'
    root.config(background=bgcolor)

    # Read QR code image
    img = tkinter.PhotoImage(file=resource_path('out.png'))

    print(img.height(), img.width())

    title = ttk.Label(root, text='Scan the QR code to get started.')
    title.config(
        background=bgcolor,
        font='Ariel 13 bold',
        wraplength=640,
        justify='center',
    )
    title.pack(pady=(40, 0))
    
    qrcode = ttk.Label(root, image=img, background=bgcolor)
    qrcode.pack()

    address = ttk.Label(root, text=State.address)
    address.config(
        font='Mono 14',
        background=bgcolor,
        foreground='blue',
        cursor='hand2'
    )
    address.bind('<Button-1>', lambda e: link(State.address))
    address.bind('<Enter>', lambda e: address.config(font='Mono 14 underline'))
    address.bind('<Leave>', lambda e: address.config(font='Mono 14'))
    address.pack()

    imaginelenses = ttk.Label(root, text='IMAGINELENSES')
    imaginelenses.config(
        background=bgcolor,
        foreground='lightgrey',
        font='Ariel 13',
        justify='center'
    )
    imaginelenses.pack(pady=(30, 20))
    
    root.mainloop()

    # Delete QR code image
    os.system('rm out.png')


def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # doesn't even have to be reachable
        s.connect(('10.225.225.225', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


def main():
    gen_qr()
    window()

if __name__ == '__main__':
    main()