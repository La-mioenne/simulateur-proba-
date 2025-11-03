import random
import matplotlib.pyplot as plt
import tkinter as tk
from tkinter import messagebox

class SauvetageGenetique:
    def __init__(self):
        self.population_effectif = 0  # Effectif estimé de la population
        self.frequence_allele_A = 0.5  # Fréquence initiale de l'allèle A (neutre)
        self.generations = 100  # Nombre de générations pour la simulation
        self.fragmentation = False  # Si l'écosystème est fragmenté
        self.corridors = False  # Si des corridors écologiques sont mis en place

    # Module A : Estimation d'Abondance par CMR
    def estimer_abondance_cmr(self, M, n, m):
        """
        Calcule l'effectif total N en utilisant la formule de CMR : N = (M * n) / m
        M : individus capturés et marqués
        n : individus recapturés
        m : individus marqués recapturés
        """
        if m == 0:
            raise ValueError("Impossible de calculer : aucun individu marqué recapturé.")
        N = (M * n) / m
        self.population_effectif = int(N)
        print(f"Effectif estimé de la population : {self.population_effectif}")
        # Intervalle de confiance approximatif (simplifié pour 95%)
        variance = (M * n * (M - m) * (n - m)) / (m**3)
        ecart_type = variance**0.5
        ic_bas = N - 1.96 * ecart_type
        ic_haut = N + 1.96 * ecart_type
        print(f"Intervalle de confiance (95%) : [{max(0, int(ic_bas))}, {int(ic_haut)}]")
        return self.population_effectif

    # Module B : Simulation de Dérive Génétique
    def simuler_dérive_génétique(self, effectif, generations=100):
        """
        Simule la dérive génétique pour un gène avec deux allèles A et B (neutres).
        effectif : taille de la population (petite pour fragmentation, grande sinon)
        Retourne les fréquences de A au fil des générations.
        """
        frequences_A = [self.frequence_allele_A]
        for gen in range(generations):
            # Reproduction : tirage aléatoire basé sur l'effectif
            alleles = ['A'] * int(effectif * frequences_A[-1]) + ['B'] * int(effectif * (1 - frequences_A[-1]))
            if len(alleles) < effectif:
                alleles.extend(['A'] * (effectif - len(alleles)))  # Ajustement pour éviter les erreurs
            random.shuffle(alleles)
            # Nouvelle fréquence : proportion d'A dans la génération suivante
            nouvelle_freq = alleles.count('A') / effectif
            frequences_A.append(nouvelle_freq)
        return frequences_A

    def afficher_simulation(self, frequences_petite, frequences_grande):
        """
        Affiche les graphiques de simulation pour petite et grande population.
        """
        plt.figure(figsize=(10, 5))
        plt.subplot(1, 2, 1)
        plt.plot(frequences_petite, label='Fréquence allèle A')
        plt.title('Dérive dans petite population (N=100)')
        plt.xlabel('Générations')
        plt.ylabel('Fréquence')
        plt.ylim(0, 1)

        plt.subplot(1, 2, 2)
        plt.plot(frequences_grande, label='Fréquence allèle A')
        plt.title('Dérive dans grande population (N=5000)')
        plt.xlabel('Générations')
        plt.ylabel('Fréquence')
        plt.ylim(0, 1)
        plt.tight_layout()
        plt.show()

    # Module C : Interventions (simplifié)
    def appliquer_intervention(self, action):
        """
        Applique une intervention : corridors ou migration.
        action : 'corridors' ou 'migration'
        """
        if action == 'corridors':
            self.corridors = True
            self.population_effectif *= 2  # Augmente l'effectif effectif
            print("Corridors écologiques mis en place : effectif augmenté, dérive ralentie.")
        elif action == 'migration':
            self.frequence_allele_A = (self.frequence_allele_A + 0.5) / 2  # Mélange avec une autre population
            print("Migration appliquée : diversité génétique renforcée.")
        else:
            print("Action non reconnue.")

    # Jeu principal avec interface simple
    def jouer(self):
        root = tk.Tk()
        root.title("Le Sauvetage Génétique")

        # Module A : Entrée CMR
        tk.Label(root, text="Module A : Estimation CMR").pack()
        tk.Label(root, text="M (marqués) :").pack()
        entry_M = tk.Entry(root)
        entry_M.pack()
        tk.Label(root, text="n (recapturés) :").pack()
        entry_n = tk.Entry(root)
        entry_n.pack()
        tk.Label(root, text="m (marqués recapturés) :").pack()
        entry_m = tk.Entry(root)
        entry_m.pack()

        def calculer_cmr():
            try:
                M = int(entry_M.get())
                n = int(entry_n.get())
                m = int(entry_m.get())
                self.estimer_abondance_cmr(M, n, m)
                messagebox.showinfo("Résultat", f"Effectif estimé : {self.population_effectif}")
            except ValueError as e:
                messagebox.showerror("Erreur", str(e))

        tk.Button(root, text="Calculer CMR", command=calculer_cmr).pack()

        # Module B : Simulation
        tk.Button(root, text="Simuler Dérive Génétique", command=lambda: self.afficher_simulation(
            self.simuler_dérive_génétique(100),  # Petite population
            self.simuler_dérive_génétique(5000)  # Grande population
        )).pack()

        # Module C : Interventions
        tk.Label(root, text="Module C : Interventions").pack()
        tk.Button(root, text="Appliquer Corridors", command=lambda: self.appliquer_intervention('corridors')).pack()
        tk.Button(root, text="Appliquer Migration", command=lambda: self.appliquer_intervention('migration')).pack()

        root.mainloop()

# Lancer le jeu
if __name__ == "__main__":
    jeu = SauvetageGenetique()
    jeu.jouer()
