# -*- coding: utf-8 -*-

from Tix import *               # Modules graphiques
from tkFileDialog import *
from tkMessageBox import *
from tkColorChooser import *

from PIL import Image, ImageTk  # Modules pour les images
import QImage

from random import randrange    #Modules divers
import time, marshal




class QFen(Toplevel):
    """ Une classe qui permet de gérer les fenetres affichant les images quantifiées """
    
    def __init__(self, fp, image, algo, nb_coul):
        """
        Constructeur :
            -> Crée une fenetre et affiche l'image de base
            -> Lance la quantification
        """
        Toplevel.__init__(self)     # Constructeur parent :)

        self.algo = algo            # Stockage de quelques infos...
        self.nb_coul = nb_coul
        self.fp = fp
        self.image = image
        self.couleur_fond = '#F5F5F5'

        # Création de la barre d'outils
        self.barre_outils = BarreOutils(self, self.couleur_fond)
        self.barre_outils.ajouter_bouton("sauver_img.gif", self.sauvegarderImage)

        # Récupération du nom de l'image
        chemin_complet = fp.split("/")
        self.titre = chemin_complet[len(chemin_complet)-1]  
        # Ajout du Canvas
        self.title(self.titre)
        self.cadre = Canvas(self, bg='#F0F0F0', relief=FLAT, bd=0)
        #print fp
        self.ouvrirImage(self.fp)
        self.nom_tmp = ""

        # On rajoute la barre de progression
        self.barre_progression = Meter(self, value=0.)
        # Barre d'état
        self.barre_etat = BarreEtat(self, self.couleur_fond)
        self.barre_etat.modifierTexte("Extraction de la palette de l'image...")

        # On pack/grid tout comme il faut
        self.barre_outils.grid(row=0, column=0, pady=0, ipady=0, sticky=N+W+E+S)
        self.barre_outils.afficher_boutons()
        self.cadre.grid(row=1)
        self.barre_progression.grid(row=2)
        self.barre_etat.grid(row=3)
        self.grid()

        self.cadre.after(500, self.quantifier)      # Appel de quantifier() après une demi seconde



    def quantifier(self):
        """ Effectue la quantification de l'image grâce au package QImage, puis l'affiche dans la fenetre """
        
        self.barre_etat.modifierTexte("Traitement de l'image...")
        if self.image.im.mode in ["RGB", "RGBA"]:
            if self.algo == "MedianCut" :
                self.image.QMedianCut(self.barre_progression, self.barre_etat, self.nb_coul)
            elif self.algo == "Frequences" :
                self.image.QFrequences(self.barre_progression, self.barre_etat, self.nb_coul)
                
        elif self.image.im.mode == "L":
            print self.algo
            if self.algo == "Floyd & Steinberg":
                self.image.QFloydSteinberg(self.barre_progression, self.nb_coul)
            elif self.algo == "Seuillage":
                self.image.QSeuillage(self.barre_progression, self.nb_coul)

        self.barre_etat.modifierTexte("Traitement terminé")
        self.nom_tmp = "tmp"+str(self.nb_coul)+"_"+str(randrange(42424242))+".bmp"
        self.image.sauver(self.nom_tmp)

        # On attend que le fichier ait été correctement enregistré...
        while not os.path.isfile(self.nom_tmp):
            pass
        self.ouvrirImage(self.nom_tmp)   # Et on l'ouvre ;)


    def ouvrirImage(self, fp):
        """ Affiche l'image dans le canvas de la fenêtre """
        self.pointeur = Image.open(fp)
        self.photo = ImageTk.PhotoImage(self.pointeur)                          # Ouverture de l'image
        
        self.cadre.delete(ALL)                                                  # On efface tout dans le cadre
        pos_x, pos_y = (self.photo.width()/2)+1, (self.photo.height()/2)+1      # Position de l'image
        self.item = self.cadre.create_image(pos_x, pos_y, image=self.photo)     # Placement
        
        self.cadre["height"] = self.photo.height()+2                            # On redimensionne le canevas
        self.cadre["width"] = self.photo.width()+2

    def sauvegarderImage(self):
        fp_sauver = asksaveasfilename(parent=self, initialfile=str(self.titre)+"_"+str(self.nb_coul)+"couleurs.bmp", title="Répertoire de destination et nom de votre image")
        try:
            if fp_sauver != "":
                self.image.sauver(fp_sauver)
        except KeyError:
            showerror(title="Extension non valide", message="L'extension n'est pas reconnue.\nEnregistrez votre image en .bmp pour conserver le nombre de couleurs souhaité (Le format Bitmap n'est pas compressé).")
            


        
class QMain(Tk):
    """ Une classe qui gère la/les fenetre(s) principale(s) """
    
    def __init__(self, fp = ""):
        """
        Constructeur :
            -> Crée une fenêtre
            -> Crée un menu
        """
        Tk.__init__(self)
        self.resizable(width=False, height=False)   # Empeche le redimmensionnement
        self.couleur_fond = '#F5F5F5'
        
        self.nb_coulImage = StringVar()     # le nombre de couleurs unique de l'image courante
        self.nom_algo = StringVar()
        self.nb_coul = StringVar()
        
        # *********************     Création du menu
        self.sys_menu = Menu(self, tearoff=0)
        
        menu1 = Menu(self.sys_menu, tearoff=0)
        self.sys_menu.add_cascade(label="Fichier", menu=menu1)
        menu1.add_command(label="Ouvrir...", command=self.ouvrirFichier)
        menu1.add_separator()
        menu1.add_command(label="Quitter", command=self.destroy)

        menu2 = Menu(self.sys_menu, tearoff=0)
        self.sys_menu.add_cascade(label="Outils", menu=menu2)
        menu2.add_command(label="Options...", command=self.ouvrirOptions)
        
        self.config(menu=self.sys_menu)
        # *********************     Fin du menu

        # Création de la barre d'outils
        self.barre_outils = BarreOutils(self, self.couleur_fond)
        self.barre_outils.ajouter_bouton("ouvrir_rep.gif", self.ouvrirFichier)
        self.barre_infos = Label(self.barre_outils, textvariable=self.nb_coulImage, bg=self.couleur_fond)

        # Création du Canevas qui contiendra l'image !
        self.cadre = Canvas(self, bg='#F0F0F0', relief=FLAT, bd=0)

        # Création des paramètres en bas
        self.barre_bas = Frame(self, bg='#F5F5F5')
        self.texte_algo = Label(self.barre_bas, text="Choix de l'algo :", bg=self.couleur_fond)
        self.select_algo = ComboBox(self.barre_bas, editable=1, dropdown=1, variable=self.nom_algo)
        self.select_algo.entry.config(state='readonly')      # Lecture seule
        
        self.text_nbcoul = Label(self.barre_bas, text="Nombre de couleurs :", bg=self.couleur_fond)
        self.entry_nbcoul = Entry(self.barre_bas, textvariable=self.nb_coul,width=4)
        self.entry_nbcoul.config(state = NORMAL)
        
        self.bouton_quant = Button(self.barre_bas, text="Quantifier", command=self.quantifier)
        
        
        # Gridage (jsais pas si ça se dit :D)
        self.barre_outils.grid(row=0, column=0, pady=0, ipady=0, sticky=N+W+E+S)    #1ère ligne
        self.barre_outils.afficher_boutons()
        self.barre_infos.pack(side=RIGHT)
        
        self.cadre.grid(row=1, column=0, padx=3, pady=3)        # 2ème ligne
        
        self.barre_bas.grid(row=2, column=0, sticky=N+W+E+S)    # 3ème ligne
        self.texte_algo.grid(row=0, column=0, padx=30, pady=5)
        self.select_algo.grid(row=1, column=0)
        self.text_nbcoul.grid(row=0, column=1, padx=30, pady=5)
        self.entry_nbcoul.grid(row=1, column=1)
        self.bouton_quant.grid(row=0, column=2, padx=30, pady=5, rowspan=2)



        # Initialisation avec une image
        self.ouvrirFichier(fp)
        

    def ouvrirFichier(self, fp = ""):
        """ Ouvre un fichier Image et l'affiche dans la fenetre """
        # On fait un bloc try au cas ou le fichier ouvert ne soit pas une image (quel coquin cet utilisateur ^^)
        try:
            # On demande quelle image ouvrir, si besoin
            if fp == "":
                fp = askopenfilename(parent=self, title="Sélectionnez votre image")
            self.fp = fp
            
            self.pointeur = Image.open(fp)
            #if self.pointeur.mode != "L" and self.pointeur.mode != "RGB" :
            #    raise IOError
            self.photo = ImageTk.PhotoImage(self.pointeur)              # Ouverture de l'image
            
            self.cadre.delete(ALL)                          # On efface tout dans le cadre
            pos_x, pos_y = (self.photo.width()/2)+1, (self.photo.height()/2)+1
            self.item = self.cadre.create_image(pos_x, pos_y, image=self.photo)
            self.cadre["height"] = self.photo.height()+2        #On redimmensionne le canevas
            self.cadre["width"] = self.photo.width()+2

            # Modification du choix des algos
            self.select_algo.subwidget_list['slistbox'].subwidget_list['listbox'].delete(0, END)
            if self.pointeur.mode == "L":
                #self.select_algo.insert(0, "Brutal")
                self.select_algo.insert(0, "Floyd & Steinberg")
                self.select_algo.insert(1, "Seuillage")
                self.text_nbcoul.config(text="Nombre de couleurs /\nValeur de seuillage :")
            else:
                self.select_algo.insert(0, "MedianCut")
                self.select_algo.insert(1, "Frequences")
                self.text_nbcoul.config(text="Nombre de couleurs")
            self.entry_nbcoul.config(state = NORMAL)

            
            #Désactivation du boutons
            self.nb_coulImage.set( "Calculs sur l'image en cours... " )
            self.barre_infos["fg"] = "red"
            self.bouton_quant["state"] = "disabled"
            self.cadre.after(200, self.chargerImage)
            


        # En cas d'erreur =)
        except IOError:
            if fp != "" :
                showerror(title="Image non valide", message="Impossible d'ouvrir le fichier.\nVous ne pouvez ouvrir que des fichiers images.")

    def quantifier(self):
        algo = self.nom_algo.get()
        if algo == "":
            showerror(title="Erreur", message="Choisissez un algorithme !")
            return
        
        try:
            nb_coul = int(self.nb_coul.get())
        except ValueError:
            showerror(title="Erreur", message="Entrez un nombre valide !")
            return
        

        nouv_fen = QFen(self.fp, self.image, algo, nb_coul)
        nouv_fen.mainloop()
        

    def chargerImage(self):
        #Affichage d'une fenetre faisant patienter l'utilisateur
        configs = marshal.load(open("options.2gq", "rb"))       # Récupération de la configuration
        if configs[2]:
            showinfo(title="Patientez...", message="Calculs en cours sur l'image...\n(Modifiez les options pour ne plus voir ce message)")
        self.image = QImage.ouvrir(self.fp)
        self.nb_coulImage.set( "Couleurs uniques : "+str(self.image.nb_coul) )
        self.barre_infos["fg"] = "black"
        self.bouton_quant["state"] = "normal"
        

    def ouvrirOptions(self):
        opt = QFenOptions()
        opt.title("Options")
        opt.mainloop()



class QFenOptions(Toplevel):
    """ Une classe qui permet de gérer la fenetre des options """
    
    def __init__(self):
        """
        Constructeur :
            -> Crée une fenetre et affiche les différentes options

        """
        Toplevel.__init__(self)     # Constructeur parent :)
        
        configs = marshal.load(open("options.2gq", "rb"))       # Récupération de la configuration
        self.valSeuil = StringVar()
        self.valCouleur = StringVar()
        self.valAlerte = IntVar()
        
        # On configure (on affiche dans le label les bonnes valeurs)
        texte = "("+str(configs[1][0])+", "+str(configs[1][1])+", "+str(configs[1][2])+"), "
        texteHexa = "#" + hex(configs[1][0])[2:] + hex(configs[1][1])[2:] + hex(configs[1][2])[2:]     # On transforme en HEXA
        self.valSeuil.set( str(configs[0]) )
        self.valCouleur.set( texte + texteHexa )
        self.valAlerte.set(configs[2])

        self.coulCour = ((configs[1][0], configs[1][1], configs[1][2]), texteHexa)      # On invente la couleur de base


        # Création des label, etc...
        self.labelAlerte = Label(self, text="Afficher une boite de dialogue\nlors de l'ouverture de l'image :")
	self.labelValAlerte = Checkbutton(self, variable=self.valAlerte)
        
        self.labelSeuillageAlpha = Label(self, text="Valeur seuil d'opacité : ")
        self.labelValSeuillage = Entry(self, textvariable=self.valSeuil, width=3)
        
        self.labelCouleurAlpha = Label(self, text="Couleur de fond : ")
        self.boutonCouleur = Button(self, text="", command=self.changerCouleur, bg=texteHexa, width=4)

        self.labelCouleurActuelle = Label(self, text="Couleur actuelle : ")
        self.labelValCouleur = Label(self, textvariable=self.valCouleur)


        self.boutonEnregistrer = Button(self, text="Enregistrer", command=self.enregistrer)


        # Gridage
        self.labelAlerte.grid(row=0, column=0, pady=10, padx=5, sticky=E)    # Boite de dialogue
	self.labelValAlerte.grid(row=0, column=1, pady=5, padx=10, sticky=W)
        
        self.labelSeuillageAlpha.grid(row=1, column=0, sticky=E)    # Seuil
        self.labelValSeuillage.grid(row=1, column=1, pady=10, padx=10, sticky=W)
        
        self.labelCouleurAlpha.grid(row=2, column=0, sticky=E)      # Couleur
        self.boutonCouleur.grid(row=2, column=1, padx=10, sticky=W)

        self.labelCouleurActuelle.grid(row=3, column=0, sticky=E)
        self.labelValCouleur.grid(row=3, column=1, padx=10, pady=10, sticky=W)

        self.boutonEnregistrer.grid(row=4, column=0, columnspan=3, pady=10)
        
        self.grid()



    def changerCouleur(self):
        configs = marshal.load(open("options.2gq", "rb"))       # Récupération de la configuration
        nouvCouleur = askcolor( initialcolor=(self.coulCour[0][0], self.coulCour[0][1], self.coulCour[0][2]) )
        if nouvCouleur != (None, None):
            self.coulCour = nouvCouleur
            #print nouvCouleur
            
            texte = "("+str(nouvCouleur[0][0])+", "+str(nouvCouleur[0][1])+", "+str(nouvCouleur[0][2])+")\n"         # On affiche la nouvelle couleur
            texte +=  nouvCouleur[1]     # On transforme en HEXA
            self.valCouleur.set( texte )
            self.boutonCouleur["bg"] = nouvCouleur[1]
            self.focus_set()

    def enregistrer(self):
        # On vérifie que c'est bien un nombre qui a été rentré
        try:
            valSeuillage = int(self.valSeuil.get())
        except ValueError:
            showerror(title="Erreur", message="Entrez un nombre valide !")
            return

	
        options = [valSeuillage, [self.coulCour[0][0], self.coulCour[0][1], self.coulCour[0][2]], self.valAlerte.get() ]
        marshal.dump(options, open("options.2gq", 'wb'))    # Sauvegarde des options
        self.destroy()
        


# --------------------------------------------------------      Utilitaires :)

class BarreOutils(Frame):
    """ Une classe gérant les barres d'outils """

    def __init__(self, root, bg):
        """ Constructeur qui appelle celui de Frame """
        Frame.__init__(self, root, bg=bg)
        self.liste_boutons = {}
        self.icones = {}
        self.bg = bg

    def ajouter_bouton(self, fp, commande):
        """ Permet d'ajouter un bouton associé à une commande à la barre d'outils """
        indice = len(self.liste_boutons.keys())
        self.icones[indice] = PhotoImage(file=fp)
        self.liste_boutons[indice] =  Button(self, image=self.icones[indice], command=commande, relief=FLAT, bg=self.bg)

    def afficher_boutons(self):
        """ Affiche tout les boutons de la barre ! """
        for i in range( len(self.liste_boutons.keys()) ):
            self.liste_boutons[i].pack(side=LEFT)


class BarreEtat(Frame):
    """ Une classe gérant les barres d'état (sans blague) """

    def __init__(self, root, bg):
        """ Constructeur qui appelle celui de Frame """
        Frame.__init__(self, root, bg=bg)
        self.var_texte = StringVar()
        self.texte = Label(self, textvariable=self.var_texte)
        self.texte.pack(side=LEFT)

    def modifierTexte(self, texte):
        self.var_texte.set(texte)
