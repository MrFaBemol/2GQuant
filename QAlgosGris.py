# -*- coding: utf-8 -*-


# Définition de la fonction Seuillage #
def Seuillage(mat, barre_progression, seuil):
    if not (0 < seuil < 255):
        raise IndexError
    #print mat
    #print seuil
    
    hauteur = len(mat)
    for i in range(len(mat)):           # Parcours total
        for j in range(len(mat[i])):
            if mat[i][j] <= seuil:
                mat[i][j] = 0
            else:
                mat[i][j] = 255
        
        barre_progression.config(value=float(i+1)/hauteur)
        barre_progression.update()
    
    return mat  # Fin de Seuillage
        

# Définition de la fonction FloydSteinberg#
def FloydSteinberg(mat, barre_progression, nbCouleurs):
    # Définition de la palette#
    if not (0 < nbCouleurs < 255):
        raise IndexError

    palette = []
    nbCouleurs = nbCouleurs - (nbCouleurs%2) # nbCouleurs est ramené a la puissance de deux la plus proche
    palier = 256/nbCouleurs
	
    for k in range(nbCouleurs):
        palette.append(palier*k)

	
    hauteur = len(mat)
    for i in range(len(mat)):			# Parcours total
        for j in range(len(mat[i])):
            for couleur in palette:		# Recherche de la couleur de la palette la plus proche
                if (mat[i][j] - couleur) < palier:
                    NewCouleur = couleur
                    break
	
            erreur = NewCouleur - mat[i][j]

            if i+1 < len(mat):
                mat[i+1][j] += int(float(erreur)*(5./16))
                if j-1 >= 0:
                    mat[i+1][j-1] += int(float(erreur)*(3./16))
                if j+1 < len(mat[i]):
                    mat[i+1][j+1] += int(float(erreur)*(1./16))
            if j+1 < len(mat[i]):
                mat[i][j+1] += int(float(erreur)*(7./16))
				
            mat[i][j] = NewCouleur
        
        barre_progression.config(value=float(i+1)/hauteur)
        barre_progression.update()
    return mat
	
