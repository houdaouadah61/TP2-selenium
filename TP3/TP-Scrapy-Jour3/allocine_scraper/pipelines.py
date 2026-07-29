class CleanPipeline:

    def process_item(self, item):

        
        champs_texte = [
            "titre",
            "realisateur",
            "url",
        ]

        for champ in champs_texte:
            if item.get(champ):
                item[champ] = item[champ].strip()

        
        if item.get("annee"):
            item["annee"] = int(item["annee"])

        
        champs_notes = [
            "note_presse",
            "note_spectateurs",
        ]

        for champ in champs_notes:

            if item.get(champ):

                valeur = item[champ].strip()
                valeur = valeur.replace(",", ".")

                try:
                    item[champ] = float(valeur)
                except ValueError:
                    item[champ] = None

        return item