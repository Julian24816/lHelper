# coding=utf-8
####################################################################################################
##
#  Latin Helper Projekt
##
#  module: datamanager
##
#  class Datamanager
##
##
#  @author: Julian M
#  @creationdate: 2016-04-14
##
####################################################################################################

import sqlite3,time
from data.classes import *

draft = False


def stringsAnpassen(*stringList)->list:
    '''passt Strings fuer ein SQL-statement an'''
    resList = []
    for string in stringList:
        resList.append(string.replace("'","''"))
    return resList


class Datamanager:
    '''Zustaendig fuer den Datenbankzugriff'''
    
    def __init__(self, dbfile):
        '''Initialisiert die Verbindung.'''
        self.cursor = sqlite3.connect(dbfile).cursor()
        #
        # # erstellt die Tabellen, falls sie noch nicht existieren
        # # = beim ersten Programmstart ohne mitgelieferte Daten
        # self.createTablesIfNotExist()


    def closeDB(self):
        '''schliesst die Datenbankverbindung'''
        self.cursor.connection.commit()
        self.cursor.connection.close()


#     def createTablesIfNotExist(self):
#         """Erstellt die Tabellen in denen die Daten gespeichert werden."""
#
#         # Woerter
#         self.cursor.execute(CREATE_WORD)
#         self.cursor.execute(CREATE_USAGE)
#
#         # Uebersetzungen
#         self.cursor.execute(CREATE_TRANSLATION)
#
#         # Vokabelkarten
#         self.cursor.execute(CREATE_CARD)
#
# ##        # Kartengruppen
# ##        self.cursor.execute(CREATE_CARDGROUP)
# ##        self.cursor.execute(GROUP)
# ##        self.cursor.execute(CREATE_GROUP_HIERARCHY)
#
#         # User
#         self.cursor.execute(CREATE_USER)
#         self.cursor.execute(CREATE_USED_CARD)

    def commit(self):
        self.cursor.connection.commit()



## Words

    def wordId(self, stammformen):
        '''Gibt die Id zurueck, falls das Wort exisitiert, sonst None'''
        
        (sf,) = stringsAnpassen(stammformen)
        stmt = "SELECT id FROM word WHERE stammformen = '{}';".format(sf)

        if draft: print(stmt)

        res = self.cursor.execute(stmt).fetchone()
        return None if res is None else res[0]
    

    def addWord(self, stammformen:str, anmerkungen:str, sprache:str):
        '''fuegt ein Wort hinzu und gibt die wordId zurueck'''

        sf,anmerkungen,sprache = stringsAnpassen(stammformen, anmerkungen, sprache)
        stmt = ("INSERT INTO word (stammformen, anmerkungen, sprache) VALUES "
                +"('{}','{}','{}');").format(sf, anmerkungen,sprache)

        if draft: print(stmt)

        self.cursor.execute(stmt)
        self.commit()
        return self.wordId(stammformen)


    def getWord(self, wordId):
        '''gibt das Wort mit wordId zurueck'''

        stmt = ("SELECT stammformen, anmerkungen, sprache FROM word "
                + "WHERE id={};").format(wordId)

        if draft:print(stmt)        
        
        return Word(*self.cursor.execute(stmt).fetchone())
        


## Usages

    def usageId(self, wordId, context):
        '''Gibt die Id zurueck, falls die Verwendung existiert, sonst None'''

        (c,) = stringsAnpassen(context)
        stmt = ("SELECT id FROM usage WHERE wordId = {} "
                +"AND context = '{}';").format(wordId, c)

        if draft: print(stmt)

        res = self.cursor.execute(stmt).fetchone()
        return None if res is None else res[0]
    

    def addUsage(self, wordId, context):
        '''fuegt eine Verwendung fuer das Wort hinzu und gibt die UsageId zurueck'''

        (c,) = stringsAnpassen(context)
        stmt = ("INSERT INTO usage (wordId,context) VALUES "
                +"({},'{}');").format(wordId, c)

        if draft: print(stmt)

        self.cursor.execute(stmt)
        self.commit()
        return self.usageId(wordId, context)


    def getUsage(self, usageId):
        '''gibt die Verwendung mit usageId zurueck'''

        stmt = "SELECT wordId, context FROM usage WHERE id={};".format(usageId)

        if draft:print(stmt)

        wordId, context = self.cursor.execute(stmt).fetchone()
        return Usage(self.getWord(wordId),context)        
        


## Translations

    def translationId(self, latinUsageId, germanUsageId):
        '''gibt die Id der Uebersetzung zurueck, falls sie existiert, sonst None'''

        stmt = ("SELECT id FROM translation WHERE latinUsageId = {} "
                +"AND germanUsageId = {};").format(latinUsageId,germanUsageId)

        res = self.cursor.execute(stmt).fetchone()
        return None if res is None else res[0]


    def addTranslation(self, latinUsageId, germanUsageId):
        '''fuegt eine Uebersetzung hinzu und gibt die translationId zurueck'''

        stmt = ("INSERT INTO translation (latinUsageId,germanUsageId) VALUES "
                +"({},{});").format(latinUsageId, germanUsageId)

        if draft: print(stmt)

        self.cursor.execute(stmt)
        self.commit()
        return self.translationId(latinUsageId, germanUsageId)


    def getTranslation(self, translationId):
        '''gibt die Uebersetzung mit translationId zurueck'''

        stmt = ("SELECT latinUsageId, germanUsageId FROM translation "
                +"WHERE id={};").format(translationId)

        if draft:print(stmt)

        latinId, germanId = self.cursor.execute(stmt).fetchone()
        return Translation(self.getUsage(latinId),self.getUsage(germanId))        
        



## Cards

    def addCard(self, card):
        '''fuegt ein Card-Objekt zur Datenbank hinzu und gibt die Id zurueck'''

        # der Karte wird die naechstgroessere Id zugewiesen
        Id = self.cursor.execute("SELECT max(cardId) FROM card").fetchone()[0]
        if Id is None: Id = 1
        else: Id += 1
        
        # assoziere jede Translation mit der neuen CardId
        for translation in card.getTranslations():
            
            # usageIds herausfinden
            lUsage = translation.getLatinUsage()
            gUsage = translation.getGermanUsage()

            ids = {lUsage:None, gUsage:None}
            for usage in ids:
                
                # wordId herausfinden bzw. Wort hinzufuegen
                word = usage.getWord()
                wordId = self.wordId(word.getStammformen())
                if wordId is None:
                    wordId = self.addWord(word.getStammformen(),
                                          word.getAnmerkungen(),
                                          word.getSprache())
                    
                # usageIds herausfinden bzw. Verwendungen hinzufuegen
                ids[usage] = self.usageId(wordId, usage.getContext())
                if ids[usage] is None:
                    ids[usage] = self.addUsage(wordId, usage.getContext())

            # translationId herausfinden bzw. Uebersetzung hinzufuegen
            translationId = self.translationId(ids[lUsage],ids[gUsage])
            if translationId is None:
                translationId = self.addTranslation(ids[lUsage],ids[gUsage])

            # Uebersetzung mit Karte assoziieren
            stmt = "INSERT INTO card VALUES ({},{});".format(Id, translationId)

            if draft: print(stmt)

            self.cursor.execute(stmt)

        self.commit()
        return Id


    def getCard(self, cardId):
        '''gibt die Karte mit cardId zurueck'''

        stmt = "SELECT translationId FROM card WHERE cardId={};".format(cardId)

        if draft:print(stmt)

        translations = []
        for (translationId,) in self.cursor.execute(stmt).fetchall():
            translations.append(self.getTranslation(translationId))

        return Card(translations, cardId)



## Used Cards

    def addToUsedCards(self, cardId, userId):
        '''fuegt die Karte in Fach 0 ein'''
        stmt = "INSERT INTO usedCard (cardId, userId) VALUES ({},{});".format(cardId, userId)

        if draft:print(stmt)

        self.cursor.execute(stmt)
        

    def getDueCards(self, userId, maxFach = None):
        '''gibt alle Kerten zurueck, die heute oder vorher abgefragt werden sollen'''
        
        today = time.strftime('%Y-%m-%d')
        stmt = ("SELECT cardId FROM usedCard WHERE naechsteAbfrage <= '{}' "
                + "AND userId = {}").format(today,userId)
        if maxFach is not None:
            stmt += " AND fach <= {}".format(maxFach)
        stmt += ";"

        if draft:print(stmt)
        
        cards = []
        for (cardId,) in self.cursor.execute(stmt).fetchall():
            cards.append(self.getUsedCard(userId, cardId))

        return cards


    def getUsedCard(self, userId, cardId):
        '''gibt die Karteikarte mit cardId zurueck'''

        stmt = ("SELECT fach,naechsteAbfrage FROM usedCard "
                " WHERE userId = {} AND cardId = {};").format(userId, cardId)

        #print(stmt)

        fach, naechsteAbfrage = self.cursor.execute(stmt).fetchone()
        
        card = self.getCard(cardId)

        return UsedCard(cardId, fach, naechsteAbfrage, card.get_translations())
        

    def saveUsedCard(self, card):
        '''berichtigt das Fach und das naechsteAbfrageDatum in der DB'''

        userId = card.getUserId()
        cardId = card.getId()
        fach = card.getFach()
        naechsteAbfrage = card.getNaechsteAbfrage()

        stmt = ("UPDATE usedCard SET fach={}, naechsteAbfrage='{}' "
                + "WHERE cardId = {} AND userId = {};").format(
                    fach, naechsteAbfrage, cardId, userId)

        if draft:print(stmt)

        self.cursor.execute(stmt)
        self.commit()

    def getFachCounts(self, userId):
        stmt = "SELECT count(*),fach FROM usedCard WHERE userId={} GROUP BY fach ORDER BY fach DESC".format(userId)
        res = self.cursor.execute(stmt).fetchall()
        counts = []
        for i in range(len(res)):
            if res[i][0] == 0:
                continue
            if res[i][1] > len(counts)-1:
                counts += [0 for i in range(res[i][1] - len(counts) + 1)]
            counts[res[i][1]] = res[i][0]
        return counts


if __name__ == '__main__':
    dm = Datamanager('data.sqlite3')
    for card in dm.getDueCards(1):
        print(card)
        print()
