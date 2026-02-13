class CompilerContext:
    def __init__(self):
        # Dictionnaire pour stocker "NOM_DU_LABEL" -> ID_NUMERIQUE
        # Ex: { "BOUCLE_DEBUT": 5, "FIN": 12 }
        self.labels = {}
        
    def add_label(self, name: str, id_instruction: int) -> None:
        '''
        Docstring for add_label.
        Ajoute un label avec son ID numérique associé.
        name: Le nom du label à ajouter.
        id_instruction: L'ID numérique associé au label.
        return: None
        '''
        if name in self.labels:
            raise Exception(f"Erreur: Le label '{name}' est défini deux fois.")
        self.labels[name] = id_instruction

    def get_label_id(self, name: str) -> int:
        '''
        Docstring for get_label_id.
        Récupère l'ID numérique associé au label donné.
        name: Le nom du label à rechercher.
        return: L'ID numérique du label.
        '''
        if name not in self.labels:
            raise Exception(f"Erreur: Saut vers un label inconnu '{name}'.")
        return self.labels[name]