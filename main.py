# -*- coding: utf-8 -*-

import QGUI, os
from re import *
from tkMessageBox import *

def supprimerTMP():
    for fichier in os.listdir(os.getcwd()):
        if match("tmp[0-9]*_[0-9]{1,8}\.bmp", fichier):
            try:
                os.remove(fichier)
            except OSError:
                showerror(title="Erreur", message="Problème lors de la destruction des fichiers temporaires.\n")
                break
    root.destroy()

root = QGUI.QMain("brian.jpg")
root.title("2GQuant")
root.protocol("WM_DELETE_WINDOW", supprimerTMP )
root.mainloop()



##image = QImage.ouvrir("images_quantifiables/lena.jpg")
##print image.nb_coul
##print image.palette_freq

print "\n\nAllright man !"
##raw_input("")



