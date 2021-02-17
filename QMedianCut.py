# -*- coding: utf-8 -*-
import marshal


class Intervalle:
    """ Une classe qui gère les intervalles utilisés pour délimiter les boites """
    
    # Constructeur
    def __init__(self, debut, fin):
        self.debut = debut
        self.fin = fin

    def ecart(self):
        """ Retourne la distance entre les extrémités de l'intervalle """
        return self.fin - self.debut

    def contient(self, valeur):
        """ Retourne vrai si l'intervalle contient @valeur, faux sinon """
        return self.debut <= valeur <= self.fin
    

    def __repr__(self):
        return "["+ str(self.debut) +";"+ str(self.fin) +"]"

    def __str__(self):
        return "["+ str(self.debut) +";"+ str(self.fin) +"]"

    def __eq__(self, valeur):
        return self.ecart() == valeur


# ---------------------------------     Classe BOITE    ---------------------------------- #

class Boite:
    """ Une classe qui gère les "boites" de l'espace RVB """

    # Contructeur
    def __init__(self, R, V, B, palette):
        """ A partir des 3 composantes et de la palette associée, crée une boite et calcule le nombre de couleurs de la palette qu'elle contient """
        self.R = Intervalle(R[0], R[1])         # Initialisation des 3 composantes
        self.V = Intervalle(V[0], V[1])
        self.B = Intervalle(B[0], B[1])
        self.nb_coul = 0                        # Initialisation des informations sur les couleurs
        self.couleurs = {}
        self.moyenne = [0, 0, 0]
        self.couleurs_contenues(palette)
        self.estDecoupable = True
        
        
    def dimensionMax(self):
        """ Renvoie la valeur de la dimension maximum de la boite """
        eR, eV, eB = self.R.ecart(), self.V.ecart(), self.B.ecart()
        
        if eB > eR and eB > eV:
            return eB
        elif eV > eR:
            return eV
        else:
            return eR


    def couleurs_contenues(self, palette):
        """ Renvoie le nombre total de couleurs contenues dans la boite et les enregistre en dans l'objet courant """
        self.nb_coul = 0
        # Parcours total de la palette
        for i in palette:
            if self.R.contient(palette[i][0]) and self.V.contient(palette[i][1]) and self.B.contient(palette[i][2]) :   # Si la couleur est dans la boite
                self.nb_coul += 1
                self.couleurs[i] = palette[i]
                self.moyenne[0] += palette[i][0]
                self.moyenne[1] += palette[i][1]
                self.moyenne[2] += palette[i][2]
        if self.nb_coul > 0:
            for i in range(3):
                self.moyenne[i] /= self.nb_coul
        

    def calcul_mediane(self, composante, valeur_test, difference, val_prec = -1, diff_coul_prec = 0):
        """ Renvoie la valeur médiane de la composante donnée en paramètre """
        # Pour éviter les boucles infinies 
        if difference < 1:
            difference = 1

        #print "valeur : ", valeur_test, ", difference : ", difference
        
        # En fonction de la composante, création de la boite temporaire
        if composante == 'R' :
            Boite_tmp = Boite((valeur_test, self.R.fin), (self.V.debut, self.V.fin), (self.B.debut, self.B.fin), self.couleurs) # La boite qu'il faudra tester !
        elif composante == 'V' :
            Boite_tmp = Boite((self.R.debut, self.R.fin), (valeur_test, self.V.fin), (self.B.debut, self.B.fin), self.couleurs)
        else :
            Boite_tmp = Boite((self.R.debut, self.R.fin), (self.V.debut, self.V.fin), (valeur_test, self.B.fin), self.couleurs)

       

        diff_coul = (self.nb_coul/2)-Boite_tmp.nb_coul
        
         # On regarde si on a trouvé la bonne boite (donc la bonne valeur ^^)
        #print "Nouv boite : ", Boite_tmp.nb_coul, ", Origine : ", self.nb_coul, ", Diff coul : ", diff_coul, ", Precedent : ", diff_coul_prec
        # raw_input("Continuer...")
        
        # Si on ne part pas dans une boucle infinie (que la valeur suivante != de prec)
        if diff_coul < 0 and (valeur_test+difference != val_prec or abs(diff_coul) > diff_coul_prec):
            return self.calcul_mediane(composante, valeur_test+difference, difference/2, valeur_test, abs(diff_coul))   # On va chercher un point plus loin
        elif diff_coul > 0 and (valeur_test-difference != val_prec or abs(diff_coul) > diff_coul_prec):
            return self.calcul_mediane(composante, valeur_test-difference, difference/2, valeur_test, abs(diff_coul))   # On va chercher un point moins loin

        
        return valeur_test      # On a trouvé !!
        

    def distance(self, pixel):
        """ Renvoie la distance entre un pixel donné et la couleur de la boite courante """
        return abs(self.moyenne[0]-pixel[0]) + abs(self.moyenne[1]-pixel[1]) + abs(self.moyenne[2]-pixel[2])
    
    def __repr__(self):
        return "\nBoite(R : %s, V : %s, B : %s, coul : %s)" % (self.R, self.V, self.B, self.moyenne)

    def __eq__(self, boite):
        return self.R == boite.R and self.V == boite.V and self.B == boite.B
        


# ---------------------------------     Fonctions    ---------------------------------- #

def calcul_limites(palette):
    """ Renvoie une boite contenant toutes les couleurs de @palette """
    
    minR, minV, minB, maxR, maxV, maxB = 255, 255, 255, 0, 0, 0     # Initialisation des extremums
    
    for couleur in palette:                               # Parcours de toutes les couleurs
        
        if palette[couleur][0] > maxR:                   # Maximum ?
            maxR = palette[couleur][0]
        if palette[couleur][0] < minR:                   # Minimum ?
            minR = palette[couleur][0]

        if palette[couleur][1] > maxV:                   # Pour le Vert
            maxV = palette[couleur][1]
        if palette[couleur][1] < minV:
            minV = palette[couleur][1]

        if palette[couleur][2] > maxB:                   # Pour le Bleu
            maxB = palette[couleur][2]
        if palette[couleur][2] < minB:
            minB = palette[couleur][2]

    return Boite((minR, maxR), (minV, maxV), (minB, maxB), palette)


def decouper_boite(liste):
    """ Découpe une boite en 2 parmi celles de @liste, selon la méthode de la MedianCut """
    valMax = 0
    boite_Max = Boite((-1, -1), (-1, -1), (-1, -1), {})
    for boite in liste:                                                                         # Parcours de toutes les listes
        if boite.dimensionMax() > valMax and boite.nb_coul > 1 and boite.estDecoupable:       # Si on a trouvé une dimension plus grande qu'avant
            valMax = boite.dimensionMax()                                                   # On se rappelle de cette valeur et de la position de la boite
            boite_Max = boite

    if boite_Max == Boite((-1, -1), (-1, -1), (-1, -1), {}) :
        return

    # On calcule les valeurs utiles en fonction de la composante sur laquelle couper la boite
    if boite_Max.R.ecart() == valMax:
        valeur_test = boite_Max.R.debut + valMax/2
        comp = 'R'
    elif boite_Max.V.ecart() == valMax:
        valeur_test = boite_Max.V.debut + valMax/2
        comp = 'V'
    else:
        valeur_test = boite_Max.B.debut + valMax/2
        comp = 'B'

    # On calcule le point médian de la composante, qui sera la valeur de début
    # de cette composante pour la boite 2
    mediane = boite_Max.calcul_mediane(comp, valeur_test, valMax/4)

    # Création des boites aux dimensions de la bonne composante
    if comp == 'R' :
        boite_TMP = Boite((boite_Max.R.debut, mediane-1), (boite_Max.V.debut, boite_Max.V.fin), (boite_Max.B.debut, boite_Max.B.fin), boite_Max.couleurs)
        boite_TMP2 = Boite((mediane, boite_Max.R.fin), (boite_Max.V.debut, boite_Max.V.fin), (boite_Max.B.debut, boite_Max.B.fin), boite_Max.couleurs)
    elif comp == 'V' :
        boite_TMP = Boite((boite_Max.R.debut, boite_Max.R.fin), (boite_Max.V.debut, mediane-1), (boite_Max.B.debut, boite_Max.B.fin), boite_Max.couleurs)
        boite_TMP2 = Boite((boite_Max.R.debut, boite_Max.R.fin), (mediane, boite_Max.V.fin), (boite_Max.B.debut, boite_Max.B.fin), boite_Max.couleurs)
    else :
        boite_TMP = Boite((boite_Max.R.debut, boite_Max.R.fin), (boite_Max.V.debut, boite_Max.V.fin), (boite_Max.B.debut, mediane-1), boite_Max.couleurs)
        boite_TMP2 = Boite((boite_Max.R.debut, boite_Max.R.fin), (boite_Max.V.debut, boite_Max.V.fin), (mediane, boite_Max.B.fin), boite_Max.couleurs)

    #print boite_Max, "\n\n composante : ", comp, ", valeur mediane : ", mediane, boite_TMP, boite_TMP2
    # raw_input("...\n")

    # Si la boite n'est pas découpable, on n'effectue pas l'opération ;/
    if boite_TMP.nb_coul == boite_Max.nb_coul or boite_TMP2.nb_coul == boite_Max.nb_coul :
        boite_Max.estDecoupable = False
    else :
        liste.remove(boite_Max)
        liste.append(boite_TMP)
        liste.append(boite_TMP2)
    


def quantifier(image, barre_progression, barre_etat, Nb_couleurs):
    """ Applique la méthode de la Median Cut à l'image passée en argument """
    

    total_boites = 1

    # Pour les images Alpha...
    configs = marshal.load(open("options.2gq", "rb"))
    couleurAlpha = configs[1]
    if image.mode == "Alpha" and not image.palette.has_key( str(couleurAlpha[0])+"_"+str(couleurAlpha[1])+"_"+str(couleurAlpha[2]) ):
        total_boites = 2

    # Calcul de la première boite !
    liste_boites = []
    barre_etat.modifierTexte("Calcul des dimensions de la boite...")
    liste_boites.append(calcul_limites(image.palette))

##    print "   ---> Rouge : (" + str(liste_boites[0].R.debut) + ", " + str(liste_boites[0].R.fin) + ")"      # Trace =)
##    print "   ---> Vert  : (" + str(liste_boites[0].V.debut) + ", " + str(liste_boites[0].V.fin) + ")"
##    print "   ---> Bleu  : (" + str(liste_boites[0].B.debut) + ", " + str(liste_boites[0].B.fin) + ")"

    # On découpe les boites jusqu'à obtenir un nombre suffisant...
    barre_etat.modifierTexte("Creation des boites de l'espace RVB...")
    while total_boites < Nb_couleurs :
        decouper_boite(liste_boites)
        total_boites += 1
        #print total_boites
        barre_progression.config(value=float(total_boites+1)/Nb_couleurs)
        barre_progression.update()

    #print "Toutes les boites :\n", liste_boites, "\n"   # Les boites sont toutes créées

    # On peut traiter l'image !
    barre_etat.modifierTexte("Traitement de l'image... ")
    pourcentage = 0.
    associations = {}       # Utilisation d'un dictionnaire pour les associations entre couleurs et boites (gain d'un peu de temps si précieux...)

    hauteur, largeur = len(image.pix_Mat), len(image.pix_Mat[0])
    for i in range(hauteur) :
        for j in range(largeur) :
            # Si on avait déja fait une association entre une couleur et une boite, on la reprend
            if associations.has_key( str(image.pix_Mat[i][j][0])+str(image.pix_Mat[i][j][1])+str(image.pix_Mat[i][j][2]) ):
                image.pix_Mat[i][j] = associations[str(image.pix_Mat[i][j][0])+str(image.pix_Mat[i][j][1])+str(image.pix_Mat[i][j][2])]
            else :
                # Sinon, on cherche la boite la plus proche de la couleur concernée
                disMin = 1000
                disMin_coul = [0, 0, 0]
                if image.mode == "Alpha" :
                    disMin_coul = [0, 0, 0, image.pix_Mat[i][j][3]]
                
                for boite in liste_boites :
                    if boite.distance(image.pix_Mat[i][j]) < disMin :       # Si la distance avec cette boite est + petite
                        disMin = boite.distance(image.pix_Mat[i][j])
                        disMin_coul[0] = boite.moyenne[0]
                        disMin_coul[1] = boite.moyenne[1]
                        disMin_coul[2] = boite.moyenne[2]

                # On l'ajoute à la liste des associations...
                associations[ str(image.pix_Mat[i][j][0])+str(image.pix_Mat[i][j][1])+str(image.pix_Mat[i][j][2]) ] = disMin_coul
                #print image.pix_Mat[i][j], disMin_coul, image.mode
                image.pix_Mat[i][j] = disMin_coul

        barre_progression.config(value=float(i+1)/hauteur)
        barre_progression.update()
        #print "Avancement : ", i, "/", hauteur
    


