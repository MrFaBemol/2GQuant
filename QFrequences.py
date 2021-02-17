# -*- coding: utf-8 -*-
from math import *


def creer_palette_freq(image, nb_couleurs):

    """ retourne la palette des couleurs quantifées par la fréquence """
    
    total_couleurs = 0                      # Entier déterminant le nombre de couleurs déjà mise dans la nouvelle palette
    palette_quant = {}                      # Palette ne contenant que les couleurs sélectionnées pour la quantification
    palette = {}
    palette.update(image.palette)           # Creation d'une copie de la palette de l'image

    while total_couleurs < nb_couleurs:
        #récupération de la couleur la plus fréquente
        freq_max = 0
        for key in palette:
            if freq_max < image.palette_freq[key]:
                freq_max = image.palette_freq[key]
                freq_max_key = key
        
        #ajout de la couleur a la plus haut fréquence dans la palette
        total_couleurs += 1
        palette_quant[total_couleurs] = palette[freq_max_key]
        del palette[freq_max_key]    #la couleur est suprimée de la copie pour ne pas la retenir plusieurs fois
        #print total_couleurs

        #on vérifie si le nombre maximum de couleur n'a pas été atteint
        if total_couleurs < nb_couleurs:
            distance_max = 0
            
            # dimensions de la couleur ayant la fréquence maximum
            rougeFreq = image.palette[freq_max_key][0]
            vertFreq = image.palette[freq_max_key][1]
            bleuFreq = image.palette[freq_max_key][2]
            
            for key in palette:         # parcours des couleurs restantes
                # dimension de la couleur courante
                rougeCourant = image.palette[key][0]
                vertCourant = image.palette[key][1]
                bleuCourant = image.palette[key][2]
                # calcul de la distance entre les deux couleurs
                distance = sqrt((rougeFreq - rougeCourant)**2+(vertFreq - vertCourant)**2+(bleuFreq - bleuCourant)**2)
                # sauvegarde de la couleur si elle est la plus éloignée
                if distance_max < distance:
                    distance_max = distance
                    distance_max_key = key
            
            # Ajout de la couleur la plus éloignée a la palette et suppression de la copie
            total_couleurs += 1
            palette_quant[total_couleurs] = palette[distance_max_key]
            del palette[distance_max_key]
            #print total_couleurs

    return palette_quant

def quantifier(image, barre_progression, barre_etat, nb_couleurs):

    """ Quantifie une image en couleur selon la méthode des fréquences """

    associations = {}


    barre_etat.modifierTexte("Création de la palette des couleurs...")
    palette = creer_palette_freq(image, nb_couleurs)


    barre_etat.modifierTexte("Traitement de l'image...")
    hauteur, largeur = len(image.pix_Mat), len(image.pix_Mat[0])
    for i in range(hauteur) :
        for j in range(largeur) :
            # Si la couleur avait déjà été rencontrée, on peut directement lui assigner sa nouvelle valeur
            if associations.has_key( str(image.pix_Mat[i][j][0])+"_"+str(image.pix_Mat[i][j][1])+"_"+str(image.pix_Mat[i][j][2]) ):
                image.pix_Mat[i][j] = associations[str(image.pix_Mat[i][j][0])+"_"+str(image.pix_Mat[i][j][1])+"_"+str(image.pix_Mat[i][j][2])]
            else:
                #sinon, on cherche la couleur la plus proche
                disMin = 42424242
                disMin_coul = [0, 0, 0]
                
                if image.mode == "Alpha" :
                    disMin_coul = [0, 0, 0, image.pix_Mat[i][j][3]]
                    
                # Récupération des dimension de la couleur traitée
                rouge = image.pix_Mat[i][j][0]
                vert = image.pix_Mat[i][j][1]
                bleu = image.pix_Mat[i][j][2]
                for key in palette :
                    # Récupération des dimensions de la couleur courante
                    rougeCourant = palette[key][0]
                    vertCourant = palette[key][1]
                    bleuCourant = palette[key][2]
                    # Calcul de la distance
                    distance = sqrt((rouge - rougeCourant)**2+(vert - vertCourant)**2+(bleu - bleuCourant)**2)
                    if  distance < disMin :       # Si la distance avec cette boite est + petite
                        disMin = distance
                        disMin_coul[0] = palette[key][0]
                        disMin_coul[1] = palette[key][1]
                        disMin_coul[2] = palette[key][2]

                # Enregistrement dans la table d'association la paire trouvée
                associations[ str(image.pix_Mat[i][j][0])+"_"+str(image.pix_Mat[i][j][1])+"_"+str(image.pix_Mat[i][j][2]) ] = disMin_coul
                image.pix_Mat[i][j] = disMin_coul

        barre_progression.config(value=float(i+1)/hauteur)
        barre_progression.update()


