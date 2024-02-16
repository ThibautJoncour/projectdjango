#!/usr/bin/env python
# coding: utf-8

import os
import pandas as pd
import sqlite3
from django.conf import settings

chemin_user = os.path.expanduser('~')
chemin_base_de_donnees = settings.CHEMIN_BASE_DE_DONNEES
# Obtenez le chemin vers le répertoire utilisateur

# Créez le chemin d'accès pour le dossier 'output_CRE_LIQUID'
chemin_output = os.path.join(chemin_user, 'output_python')
chemin_regle = os.path.join(chemin_output, 'regles')

# Assurez-vous que le dossier existe, sinon créez-le
if not os.path.exists(chemin_output):
       os.makedirs(chemin_output)

if not os.path.exists(chemin_regle):
       os.makedirs(chemin_regle)
# In[56]:

def concat_nominal(row):
    if row['Quantité'] == 'Nominal':
        return (row['Nominal'])
    else:
        return 0
   

def concat_montant(row):
    if row['Montant'] == 'Amount':
        return (row['Amount'])
    elif row['Montant'] == 'Settlement Amount':
        return (row['Settlement Amount'])
    
def Tiers(row):
    if row['Tiers'] == 'Clearer Party ID':
        return (row['Clearer Party ID'])
    
def concat_columns(row):
    if row['Rule'] == 'R001':
        return f"{row['Préfixe']} / {row['EventSubType']}"
    elif row['Rule'] == 'R002':
        return f"{row['Préfixe']} / {row['EventSubType']}"
    elif row['Rule'] == 'R003':
        return f"{row['Préfixe']} / {row['EventSubType']} / 'Buy' / {row['Price']}"
    elif row['Rule'] == 'R004':
        return f"{row['Préfixe']} / {row['ProcessType']} / {row['EventSubType']} / {row['BuySell']} /{row['Price']}"
    elif row['Rule'] == 'R005':
        return f"{row['Préfixe']} / {row['ProcessType']} / {row['EventSubType']} / {row['BuySell']} / {row['Price']}"



def utiliser_fichier_source(chemin_fichier_source):
    conn = sqlite3.connect(chemin_base_de_donnees)
    query_event = 'SELECT * FROM Dash'
    query_regle = 'SELECT * FROM Rules'

    df_condition = pd.read_sql_query(query_event, conn)
    df_regle = pd.read_sql_query(query_regle, conn)


    #query_event = 'SELECT * FROM Dash INNER JOIN Rules ON Dash.Rule = Rules.Rule;'
    #df_regle = pd.read_sql_query(query_event, conn)

    df_source = pd.read_excel(chemin_fichier_source, sheet_name=0)

    #df_regle = pd.read_excel(chemin_regle +"\\regles.xlsx", sheet_name=0, header=1)

    
    df_source.rename(columns={'Buy Sell':'BuySell',
                   'Event Type':'EventType',
                   'Event Sub Type':'EventSubType',
                    'Processing Type':'ProcessType'
                  }, inplace=True)
    
    data = pd.merge(df_condition, df_source, on=['Portfolio','BuySell','EventType','EventSubType','ProcessType'], how='inner')
    data2 = pd.merge(df_regle, data, on=['Rule'], how='inner')
    data2['Montant'] = data2.apply(concat_montant, axis=1)
    data2['Tiers'] = data2.apply(Tiers, axis=1)
    #data2['colonne_a'].str.replace(' ', '')
    data2['LibelleEcriture'] = data2.apply(concat_columns, axis=1)
    data2['Quantité'] = data2.apply(concat_nominal, axis=1)
    data2['Quantité'] = abs(data2['Quantité'])


    output = data2[['Rule','Préfixe','LibelleEcriture','Sens','Montant','Devise','Quantité','Type de pièce','Tiers']]

    output.rename(columns={'Type de pièce': 'TypeDePiece',
                  }, inplace=True)
    #output['Montant'] = output.apply(replace_values, axis=1)
    #[abs(output['Montant']) for i in output['Montant'] if i != None]
    output['Montant'] = abs(output['Montant'])




    output.to_excel(chemin_output +'//'+ "output_CRE_EVENT.xlsx",index=False)
    # Faites quelque chose avec le DataFrame (par exemple, imprimez les premières lignes)

    # Vous pouvez également retourner le DataFrame ou effectuer d'autres opérations ici
    return output

print('cest ok')
# In[57]:



def utiliser_deuxieme_script(chemin_fichier_source):
    df_source = pd.read_excel(chemin_fichier_source, sheet_name=0)
    #df_regle = pd.read_excel(chemin_regle +"\\regles_liquid.xlsx", sheet_name=0, header=1)
    conn = sqlite3.connect(chemin_base_de_donnees)

    # Lisez le fichier Excel avec pandas
# Création d'un objet curseur



    query_event = 'SELECT * FROM blog_matable where blog_matable.CRE = "Liquidation"'
    df_regle = pd.read_sql_query(query_event, conn)
    df_source.rename(columns={'Buy Sell':'BuySell',
                   'Event Type':'EventType',
                   'Event Sub Type':'EventSubType',
                   'Date de pièce':'DatePiece'
                  }, inplace=True)
    df = pd.merge(df_regle, df_source, on=['BuySell','EventSubType'], how='inner')

    
    mask = (df['Amount'] > 0) & (df['Condition'] == 'Amount < 0')
    mask1 = (df['Amount'] < 0) & (df['Condition'] == 'Amount > 0')
    mask3 = (df['First Trade Realized Amount'] > 0) & (df['Condition'] == 'First Trade Realized Amount < 0')
    mask4 = (df['First Trade Realized Amount'] < 0) & (df['Condition'] == 'First Trade Realized Amount > 0')
    mask5 = (df['Second Trade Realized Amount'] > 0) & (df['Condition'] == 'Second Trade Realized Amount < 0')
    mask6 = (df['Second Trade Realized Amount'] < 0) & (df['Condition'] == 'Second Trade Realized Amount > 0')
    df1 = df[~mask]
    df0 = df1[~mask1]
    df2 = df0[~mask3]
    df3 = df2[~mask4]
    df4 = df3[~mask5]
    df5 = df4[~mask6]
    
    #df5['Montant'] = df5.apply(replace_values, axis=1)



    output = df5[['Id','Société','Etablissement','Journal','Date de pièce','Référence pièce','Compte général','Libellé écriture','Sens','Montant','Devise','Quantity','Type de pièce','Tiers']]
    output.rename(columns={'Id': 'vcTradeId',
                  }, inplace=True)   
    

    output.to_excel(chemin_output +"/"+"output_LIQUIDE.xlsx", index=False)

    return output


def insert_sql(df):

    conn = sqlite3.connect(chemin_base_de_donnees)

    table_name = 'TransactionOutput'
    df.to_sql(table_name, conn, index=False, if_exists='append')
    return



def call_fichier1():
    chemin_fichier_xlsx = chemin_output +"\\"+"output_LIQUIDE.xlsx"
    if os.path.exists(chemin_fichier_xlsx):
        print(chemin_fichier_xlsx)
        os.startfile(chemin_fichier_xlsx)
    else:
        print(f'Le fichier {chemin_fichier_xlsx} n\'existe pas.')

    chemin_fichier_xlsx = chemin_output +'//'+ "output_CRE_EVENT.xlsx"
    if os.path.exists(chemin_fichier_xlsx):
        print(chemin_fichier_xlsx)
        os.startfile(chemin_fichier_xlsx)
    else:
        print(f'Le fichier {chemin_fichier_xlsx} n\'existe pas.')

    

def call_fichier2():
    chemin_fichier_xlsx = chemin_output +'//'+ "output_CRE_EVENT.xlsx"
    if os.path.exists(chemin_fichier_xlsx):
        print(chemin_fichier_xlsx)
        os.startfile(chemin_fichier_xlsx)
    else:
        print(f'Le fichier {chemin_fichier_xlsx} n\'existe pas.')



