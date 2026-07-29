from itemadapter import ItemAdapter


class CleanPipeline:

    def process_item(self, item):

        evenement = ItemAdapter(item)

        for champ in ["titre", "date", "url"]:

            valeur = evenement.get(champ)

            if valeur:
                evenement[champ] = " ".join(
                    valeur.split()
                )

        return item