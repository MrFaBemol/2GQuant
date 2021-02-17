# -*- coding: utf-8 -*-

import Image, numpy     # Importation des modules pour manipuler les images
import marshal          # Pour manipuler le fichier de configuration
import QAlgosGris       # Importation des modules contenant les différents algorithmes
import QMedianCut, QFrequences



# Définition de la classe QImage #
class QImage:
    """ Une classe abstraite qui permet de gérer une image à quantifier """
    
    # Constructeur
    def __init__(self, im):
        self.im = im
        self.pix_Mat = self.extraire();
        self.pix_Mat_org = self.extraire();
        
        # print "Construction de la palette en cours..."
        self.palette = {}       # Utilisation d'un dictionnaire pour extraire la palette
        self.palette_freq = {}  # Dictionnaire pour les fréquence
        self.nb_coul = 0        # Il est intéressant de connaitre le nombre de couleurs !
        self.construire_palette();      # Création de la palette dans self.palette


    def construire_palette(self):
        """ Extrait la palette de couleurs et la renvoie """
#        self.init_extremes()                    # On doit créer un tableau différent en fonction du type de l'image
        for ligne in self.pix_Mat:              # Parcours de la matrice
            for pixel in ligne:
                #print pixel
                self.ajouter_couleur(pixel)     # Méthode spécifique

    def extraire(self, im):
        raise NotImplementedError   # Méthode "abstraite"
    
    def ajouter_couleur(self):
        raise NotImplementedError   # Méthode "abstraite"
    


# Définition de la classe QImage_Gris #
class QImageGris(QImage):
    """ Une classe qui gère les images en niveaux de gris """

    # Constructeur
    def __init__(self, im):
        QImage.__init__(self, im)
        self.mode = "Gris"


    # Les fonctions abstraites
    def extraire(self):
        """ Extrait les valeurs des pixels et les met dans une matrice """
        array_pix = numpy.array(self.im.getdata())                      # Extraction des données
        # Création de l'array qui contiendra les pixels (une matrice à deux dimensions)
        return numpy.reshape(array_pix, (self.im.size[1], self.im.size[0]))
    

    def ajouter_couleur(self, pixel):
        """ Ajoute la couleur de @pixel à la palette si elle ne la contient pas déjà """
        if not self.palette.has_key( str(pixel) ):      # Test de l'existence
            self.palette[ str(pixel) ] = pixel          # Ajout de la couleur
            self.nb_coul += 1
            self.palette_freq[ str(pixel) ] = 1
        else:
            self.palette_freq[ str(pixel) ] += 1
    

    def sauver(self, fp):
        """ Sauvegarde l'image dans un nouveau fichier """
        # Création de la nouvelle image aux dimensions de la matrice !
        im_nouv = Image.new(self.im.mode, (self.pix_Mat.shape[1], self.pix_Mat.shape[0]))
        im_nouv.putdata(list(self.pix_Mat.flat))    # On injecte les pixels dans l'image
        im_nouv.save(str(fp))


    def matOrg(self):
        return numpy.reshape(list(self.pix_Mat_org), (self.im.size[1], self.im.size[0]))


    # Pour faire genre c'est de l'objet !  =P
    def QSeuillage(self, barre_progression, seuil):
        """ Modifie la matrice de l'image au moyen de l'algorithme de seuillage """
        self.pix_Mat = QAlgosGris.Seuillage(self.matOrg(), barre_progression, seuil)

    def QFloydSteinberg(self, barre_progression, nbCouleurs):
        """ Modifie la matrice de l'image au moyen de l'algorithme de Floyd et Steinberg """
	self.pix_Mat = QAlgosGris.FloydSteinberg(self.matOrg(), barre_progression, nbCouleurs)


    # Fin de QImage_Gris


# Définition de la classe QImage_Coul #
class QImageCoul(QImage):
    """ Une classe qui gère les images en couleurs """

    # Constructeur
    def __init__(self, im):
        QImage.__init__(self, im)
        self.mode = "Couleur"


    # Fonctions abstraites :
    def extraire(self):
        """ Extrait les valeurs des pixels et les met dans une matrice """
        array_pix = numpy.array(self.im.getdata())                         # Extraction des données
        # Création de l'array qui contiendra les pixels (une matrice à trois dimensions)
        return numpy.reshape(array_pix, (self.im.size[1], self.im.size[0], 3))

    def ajouter_couleur(self, pixel):
        """ Ajoute la couleur de @pixel à la palette si elle ne la contient pas déjà """
        if not self.palette.has_key( str(pixel[0])+"_"+str(pixel[1])+"_"+str(pixel[2]) ):
            self.palette[ str(pixel[0])+"_"+str(pixel[1])+"_"+str(pixel[2]) ] = pixel
            self.nb_coul += 1
            self.palette_freq[ str(pixel[0])+"_"+str(pixel[1])+"_"+str(pixel[2]) ] = 1
        else:
            self.palette_freq[ str(pixel[0])+"_"+str(pixel[1])+"_"+str(pixel[2]) ] += 1



    def sauver(self, fp):
        """ Sauvegarde l'image dans un nouveau fichier """
        # Création de la nouvelle image aux dimensions de la matrice !
        im_nouv = Image.new("RGB", (self.pix_Mat.shape[1], self.pix_Mat.shape[0]))
        #self.im.mode

        Mat_nouv = []
        for ligne in self.pix_Mat:      # Parcours de la liste ^^
            for pixel in ligne:
                Mat_nouv.append((pixel[0], pixel[1], pixel[2]))     # Ajout d'un tuple avec les valeurs du pixel

        im_nouv.putdata(Mat_nouv)    # On injecte les pixels dans l'image
        im_nouv.save(str(fp))

    def matOrg(self):
        return numpy.reshape(list(self.pix_Mat_org), (self.im.size[1], self.im.size[0], 3))



    # Fonctions de quantification
    def QMedianCut(self, barre_progression, barre_etat, nbCouleurs):
        """ Modifie la matrice de l'image au moyen de l'algorithme de MedianCut """
        self.pix_Mat = self.matOrg()
        QMedianCut.quantifier(self, barre_progression, barre_etat, nbCouleurs)

    def QFrequences(self, barre_progression, barre_etat, nbCouleurs):
        """ Modifie la matrice de l'image au moyen de l'algorithme des fréquences """
        self.pix_Mat = self.matOrg()
        QFrequences.quantifier(self, barre_progression, barre_etat, nbCouleurs)
    # Fin de QImage_Coul
    

class QImageAlpha(QImageCoul):
    """ Une classe qui gère les images en couleurs """

    # Constructeur
    def __init__(self, im):
        self.matAlpha = []
        QImageCoul.__init__(self, im)
        self.mode = "Alpha"
    
    # Fonctions abstraites :
    def extraire(self):
        """ Extrait les valeurs des pixels et les met dans une matrice """
        array_pix = numpy.array(self.im.getdata())                         # Extraction des données
        
        # Création de l'array qui contiendra les pixels (une matrice à quatre dimensions)
        Mat = numpy.reshape(array_pix, (self.im.size[1], self.im.size[0], 4))
        
        for ligne in Mat :
            nouvLigne = []
            for pixel in ligne :
                nouvLigne.append(pixel[3])
            self.matAlpha.append(nouvLigne)

        #print self.matAlpha
        return Mat


    def sauver(self, fp):
        """ Sauvegarde l'image dans un nouveau fichier """
        # Création de la nouvelle image aux dimensions de la matrice !
        im_nouv = Image.new("RGB", (self.pix_Mat.shape[1], self.pix_Mat.shape[0]))
        #self.im.mode

        Mat_nouv = []
        
        configs = marshal.load(open("options.2gq", "rb"))       # Récupération de la configuration
        
        for i in range(len(self.pix_Mat)):      # Parcours de la liste ^^
            for j in range(len(self.pix_Mat[0])):
                pixel = self.pix_Mat[i][j]
                
                # Si l'alpha est assez opaque, on insère la couleur véritable
                if self.matAlpha[i][j] > configs[0]:
                    Mat_nouv.append((pixel[0], pixel[1], pixel[2]))     # Ajout d'un tuple avec les valeurs du pixel
                # Sinon, on met la couleur de fond ;)
                else :
                    Mat_nouv.append((configs[1][0], configs[1][1], configs[1][2]))

        im_nouv.putdata(Mat_nouv)    # On injecte les pixels dans l'image
        im_nouv.save(str(fp))



# Fonction utilisée pour simplifer l'utilisation du module
def ouvrir(fp):
    """ Ouvre une image et crée un objet en fonction de son type """
    im = Image.open(fp)
    print "MODE : ", im.mode
    if im.mode == "L":
        return QImageGris(im)
    elif im.mode == "RGB" :
        return QImageCoul(im)
    elif im.mode == "RGBA" :
        return QImageAlpha(im)
    else :
        max = 0
        for coul in list(im.getdata()):
            if max < coul:
                max = coul
        print "Nb Coul : ", max+1
        lol = list(im.getpalette())
        print "\n\nPalette : ", len(lol), "\n\n", lol
        raise TypeError
    

