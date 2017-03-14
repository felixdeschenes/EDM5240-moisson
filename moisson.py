# coding: utf-8

# Toutes les étapes qui suivent se basent sur la logique de moissonnage contenue dans le procédurier publié sur la page GitHub de Jean-Hugues Roy.
# La différence principale de procédure s'explique par une disposition de l'information en 8 pages séparées, qui sont chacunes associées à un URL différent.

import csv
import requests
from bs4 import BeautifulSoup

# Je crée une variable qui réfère au document .csv qui sera créé à partir de nos recherches.
fichiercsv = "contrats-StationSpatiale.csv"


# Je définis la présentation polie qui accompagnera chacune de mes requêtes.
entetes = {
	"User-Agent":"Félix Deschênes - Requête envoyée dans le cadre d'un cours de journalisme informatique à l'UQAM (EDM5240)",
	"From":"deschenes.felix@uqam.ca"
}

# L'information à trouver sur les contrats octroyés se trouve dans un tableau qui est décliné en 8 pages.
# Chaque page contient un URL propre; le seul changement d'URL entre chaque page à consulter se situe à la fin.
# C'est pourquoi j'utilise la technique suggérée par Jean-Philippe Guilbault, c'est-à-dire de changer ce numéro de page à la fin de l'URL
# à partir d'un «range» préalablement défini et appliqué en boucle. La fonction «.format» permettra d'ajouter chaque nombre défini dans le range à l'intérieur
# des {accolades} placées à la fin de l'URL. Ici, mon range s'étendra de 1 à 9, puisqu'il y a 8 pages à consulter.

listepages = list(range(1,9))


for unepage in listepages:
    urls = "http://www.asc-csa.gc.ca/fra/publications/contrats-liste.asp?trimestre=51&message=&membre=&pg={}".format(unepage)
    print(urls)


# Ces URLs contiennent l'information relative à tous les contrats de plus de 10 000$ octroyés par l'Agence spatiale canadienne.

# Je définis la variable «contenu», qui renvoie à ma tentative de copier l'information qui se trouve dans mes URLs, annexée à mes salutations polies.
    contenu = requests.get(urls, headers=entetes)

# En utilisant le module BeautifulSoup, je signale mon désir que la structure HTML du contenu copié depuis chaque URL soit décortiquée, puis analysée.
    page = BeautifulSoup(contenu.text,"html.parser")


# Définir une variable «i» me permettra d'éviter d'analyser et d'ajouter au .csv la ligne «0» des tableaux à analyser, qui renvoie aux entêtes non quantifiables.
    i = 0

# Après avoir étudié les URLs qui recensent les contrats, il semble que chaque ligne comprenant un hyperlien renvoyant à un contrat apparaît dans une balise HTML "tr".
# Je vais donc identifier chacune de ces balises "tr" pour en extraire l'hyperlien qu'il contient à même sa balise "href".
    for ligne in page.find_all("tr"):
        if i != 0:
        # print(ligne)
        
        # La variable "lien" correspond à la fin de l'URL propre à chaque hyperlien correspondant à un contrat.
            lien = ligne.a.get("href")
        # print(lien)
        
        # Puisque l'identification des balises "href" dans notre page nous a uniquement permis de cibler la fin de chaque URL, alors il convient de 
        # reconstituer l'hyperlien complet en ajoutant le début commun à chaque adresse.
            hyperlien = "http://www.asc-csa.gc.ca" + lien
            print(hyperlien)

        # Chaque hyperlien qui s'inscrit dans la précédente boucle mène vers une page où est consignée l'information propre à un contrat (contenu2).
        # Dans cette page du détail de chacun des contrats, nous ouvrons une nouvelle boucle qui fait appel à l'analyse HTML de BeautifulSoup.
            contenu2 = requests.get(hyperlien, headers=entetes)
            detail = BeautifulSoup(contenu2.text, "html.parser")
        
       # On attribue une variable à une liste vide, qui nous permettra de rassembler l'information que nous désirerons transposer dans le .csv final.
            contratAgenceSpatiale = []
        
        # À des fins de vérifications ultérieures, nous commençons par ajouter dans cette liste
        # l'hyperlien correspondant au détail de chaque contrat.
            contratAgenceSpatiale.append(hyperlien)
        
        # Nous sommes rendus à examiner l'HTML de chacune des pages de détail. Puisque l'information s'y trouve également
        # sous la forme d'un tableau, nous ciblons à nouveau les balises "tr" à l'aide de la fonction .find_all().
            for item in detail.find_all("tr"):
            # print(item)
            
        # Dans cette boucle, il convient d'ajouter à notre liste «contratAgenceSpatiale» seulement les cases qui contiennet de l'information utilisable.
                if item.td is not None:
                    contratAgenceSpatiale.append(item.td.text)
            
            # Si une case du tableau «td» est vide, on ajoutera la mention «Non disponible» à notre liste «contratAgenceSpatiale».
                else:
                    contratAgenceSpatiale.append("INFORMATION NON DISPONIBLE")
        
            print(contratAgenceSpatiale)
        
        # Écriture de nos données dans un fichier .csv que nous avons nommé tout en haut.
        # La fonction .writerow(x) permet d'indiquer à notre module d'écriture quelle information (x) sera consignée à chaque ligne du document .csv
            ouverture = open(fichiercsv,"a")
            fonctionecriture = csv.writer(ouverture)
            fonctionecriture.writerow(contratAgenceSpatiale)
        
            
        # ON AUGMENTE NOTRE COMPTEUR DE 1
        i =+ 1
        
        # CONSTATS FINAUX
        # Après avoir étudié le .csv final, il semble que 2 erreurs persistent:
        #     1- D'abord, les pages de détail des contrats varient. Certaines contiennent 10 rangées d'information «tr»
        #     et d'autres n'en contiennent que 7. Cela a pour effet de décaler les colonnes d'information dans le fichier .csv.
        #     J'ai tenté d'éviter cette erreur en utilisant une boucle qui aurait imposé des conditions à l'information «td» de manière
        #     à changer leur saisie avec la fonction .get (if page2.find_all("th", class_="align-right") == "Valeur du contrat")
            
        #     2- J'aurais également dû exclure la balise «td» qui correspond à la «date de livraison» de chaque contrat,
        #     puisqu'elle est systématiquement vide.
