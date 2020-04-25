def data_departement_FR():

    import pandas as pd
    import os 
    import math
    from datetime import datetime

    chemin = os.path.dirname(__name__)

    chemin_fichier_meta = os.path.join(chemin,"metadonnees-tests-depistage-covid19.csv")
    chemin_fichier_quoti = os.path.join(chemin,"donnees-tests-covid19-labo-quotidien-2020-04-24-19h00.csv")
    chemin_fichier_trache_age = os.path.join(chemin,"code-tranches-dage.csv")
    chemin_fichier_hebdo = os.path.join(chemin,"donnees-tests-covid19-labo-hebdomadaire-2020-04-22-19h00.csv")



    metadonnees = pd.read_csv(chemin_fichier_meta, sep=";")
    donnees_quotidient = pd.read_csv(chemin_fichier_quoti, sep=";")
    donnees_hebdo = pd.read_csv(chemin_fichier_hebdo, sep=";")
    donnees_tranche_age = pd.read_csv(chemin_fichier_trache_age, sep=";")

    print(metadonnees)
    print(len(metadonnees['Description_EN']))

    print(donnees_quotidient)

    print(donnees_quotidient.shape[0])
    liste_test = []
    for elt in donnees_quotidient['nb_test']:
        liste_test.append(elt)

    print(len(liste_test))

    L = [i for i in range(12,24)]

    for index, elt in enumerate(L):
        print(f"l\'élément est {elt} et son indice est {index}")


    nb_test_total = 0 
    nb_test_positif_total = 0
    for index, elt in enumerate(donnees_quotidient['nb_test']):
        if donnees_quotidient['clage_covid'][index] == '0':
            nb_test_total += int(donnees_quotidient['nb_test'][index])
            nb_test_positif_total += int(donnees_quotidient['nb_pos'][index])
        else:
            continue

    print(f"Nombre de test effectués : {nb_test_total}")
    print(f"Nombre de test positifs : {nb_test_positif_total}")

    print(f"ratio test_positif/nb_test_total : {round(nb_test_positif_total/nb_test_total*100,3)}%")

    ## TEST DATE

    d1 = "2020-04-10"
    d2 = "2020-04-30"
    t1 = datetime.strptime(d1, "%Y-%m-%d")
    t2 = datetime.strptime(d2, "%Y-%m-%d")
    print(t1)
    print(t2)
    print(t1-t2)
    ##
    '''
    print(donnees_quotidient['dep'] == '01')
    print(donnees_quotidient.loc[(donnees_quotidient['dep'] == '01') & (donnees_quotidient['clage_covid'] == '0') ])


    departement = [str(i).zfill(2) for i in range(1,96)]
    departement.extend(str(i) for i in range(971,975))
    departement.append(str(976))

    print(departement)
    '''
    data_dep = []
    departement = donnees_quotidient['dep'].drop_duplicates().values
    print(departement)
    for dep in departement:
        donnees_dep = donnees_quotidient.loc[(donnees_quotidient['dep'] == str(dep)) & (donnees_quotidient['clage_covid'] == '0')]
        test_positif = donnees_dep['nb_pos'].values
        nb_test = donnees_dep['nb_test'].values
        data_chaine = []
        for i in range(len(test_positif)):
            chaine = str(test_positif[i]) + '/' + str(nb_test[i])
            data_chaine.append(chaine)

        df_dep = pd.DataFrame({
        dep: data_chaine
        }, donnees_dep['jour'].values)
        
        data_dep.append(df_dep)
        #data_dep.append(donnees_dep)
        #for elt in donnees_dep['']:

    data_dep = pd.concat(data_dep, axis=1)


    return data_dep


    #