# Lecture de complétude du deck: preseed-deck.pdf

**Stade**: pre-seed · **Version de la grille**: 2026-09-08 · **Lu le**: 2026-09-08 · **Extraits vérifiés contre**: la couche texte du PDF

> Ce rapport mesure la complétude du deck au regard de la grille pre-seed : le deck répond-il aux questions qu'un investisseur va poser. Il ne mesure pas la qualité de l'entreprise. Il ne contient ni verdict, ni note, ni recommandation d'investissement.
>
> Le texte qui n'apparaît que dans des images (graphiques, captures) n'est pas dans la couche texte du PDF et ne peut pas être cité ; il est traité comme absent.

## Fiche du deck

- **Secteur**: procurement software for industrial SMEs (p. 8: "Procurement software for industrial SMEs is a 40 billion dollar market worldwide")
- **Modèle économique**: monthly subscription per site (p. 7: "Pricing: 150 EUR per month per site.")
- **Type de client**: B2B (p. 7: "the plant director signs the subscription")
- **Stade annoncé**: pre-seed (p. 1: "Pre-seed round - September 2026")
- **Langue du deck**: en
- **Pages**: 12

## Complétude du deck

| Bloc | | % |
|---|---|---:|
| A. Problème et terrain (poids 3) | `██████████████████░░` | 87.5 % |
| B. Preuves (poids 3) | `██████████████░░░░░░` | 70 % |
| C. Économie (poids 1) | `███████████████░░░░░` | 75 % |
| D. Marché et moment (poids 2) | `███████░░░░░░░░░░░░░` | 33.3 % |
| E. Équipe (poids 3) | `██████████░░░░░░░░░░` | 50 % |
| F. Argent et prochaine étape (poids 2) | `████████████████████` | 100 % |
| **Global (pondéré)** | `██████████████░░░░░░` | **68.9 %** |

**Blocs rouges (sous 50 %)**: D. Marché et moment

**Signaux rouges du stade (absents)**: B4

Passes de vérification : 3 (confirmation déclenchée, complétude dans la bande 65-80 % ; chaque valeur est la médiane des passes)

**Questions instables (les passes ont divergé)**: A2

## Lecture

### Manques principaux

[B4] Le deck ne mentionne aucun pivot, aucune hypothèse invalidée ni aucune fonctionnalité abandonnée, ni ce qui aurait déclenché un changement de cap.

[E3] Le deck ne dit pas si Lena ou Marc travaillent à temps plein sur l'entreprise.

[E4] Le deck ne donne pas la répartition du capital entre les fondateurs, et ne dit pas non plus que cette information est disponible sur demande.

### Questions pour l'appel

**A — Problème et terrain**
[A4] Que vous ont dit, mot pour mot, les 14 responsables achats que vous avez interrogés ?

**B — Preuves**
[B1] Votre prototype Figma a-t-il été utilisé par des acheteurs en conditions réelles au-delà des tests ponctuels, et où en est le développement du moteur de lecture des emails ?
[B4] Qu'avez-vous testé et abandonné depuis le début du projet, et qu'est-ce qui vous a fait changer de direction ?

**C — Économie**
[C1] Avez-vous testé ce prix de 150 euros par mois et par site auprès de prospects réels, et si oui, quelle a été leur réaction ?
[C3] Avez-vous une marge, un coût d'acquisition client ou un chiffre de rétention à date ?

**D — Marché et moment**
[D1] Pouvez-vous refaire votre calcul de marché en partant du nombre de clients potentiels multiplié par le prix, avec les hypothèses détaillées ?
[D3] Pourquoi un acteur déjà en place n'a-t-il pas déjà construit cette solution ?

**E — Équipe**
[E1] Chez quelle entreprise Marc a-t-il travaillé, quel était son rôle exact, et qu'a-t-il concrètement construit ou livré, à quelle échelle ?
[E3] Lena et Marc travaillent-ils à temps plein sur Gantrix, et depuis quelle date ?
[E4] Quelle est la répartition du capital entre Lena et Marc ?

### Ce que le deck ne dit pas

Bloc D, Marché et moment : le deck ne calcule pas la taille du marché en partant du nombre de clients possibles multiplié par un prix avec des hypothèses visibles, et n'explique pas pourquoi un acteur déjà en place n'a pas déjà construit cette solution.

## Question par question

### A. Problème et terrain — poids 3 — 87.5 %

| # | Question | Valeur | Page | Extrait |
|---|---|---|---|---|
| A1 | Qui souffre du problème, précisément ? | 🟢 trouvée | 2 | "Purchasing managers in industrial SMEs (50 to 200 employees) chase supplier" |
| A2 | Combien le problème coûte à cette personne aujourd'hui ? | 🟢 trouvée ⚠ instable (partielle, trouvée, trouvée) | 2 | "a purchasing manager spends about 6 hours a week on supplier follow-ups. This is our estimate from the interviews, not a measured figure." / "One plant told us a late delivery stopped a line for two days in April 2026." |
| A3 | Comment elle se débrouille aujourd'hui sans le produit ? | 🟢 trouvée | 3 | "Today they use Excel and email threads. Every order has its own tab, updated by hand" |
| A4 | Combien d'utilisateurs le fondateur a interviewés, et que disent-ils ? | 🟠 partielle | 4 | "We interviewed 14 purchasing managers between March and June 2026" |

- **A4** — **Manque**: Un nombre d'entretiens est donné, mais aucune citation mot pour mot d'un responsable achats n'est reproduite dans le deck. **À demander**: Que vous ont dit, mot pour mot, les 14 responsables achats que vous avez interrogés ?

### B. Preuves — poids 3 — 70 %

| # | Question | Valeur | Page | Extrait |
|---|---|---|---|---|
| B1 | Le produit existe-t-il ? | 🟠 partielle | 5 | "Current state: a clickable prototype built in Figma, tested with 3 purchasing managers in June 2026. The email parsing engine is not built yet." |
| B2 | Quels signaux faibles d'intérêt ? | 🟢 trouvée | 6 | "Waiting list: 38 companies signed up on our landing page since May 2026." / "Letters of intent signed by Ferrolux SAS and Metalpro Ouest." / "One paid pilot: Ferrolux SAS pays 200 EUR per month since July 2026 for a manual version of the service (we update their sheet by hand)." |
| B3 | Des clients ou pilotes nommés ? | 🟢 trouvée | 6 | "Letters of intent signed by Ferrolux SAS and Metalpro Ouest." / "One paid pilot: Ferrolux SAS pays 200 EUR per month since July 2026 for a manual version of the service (we update their sheet by hand)." |
| B4 | Qu'est-ce qui a été testé et abandonné ? | 🔴 absente | — | — |
| B5 | Qu'a fait l'équipe depuis six mois ? | 🟢 trouvée | 6, 4 | "Since March 2026 we have: run 14 interviews, built the Figma prototype, signed 2 letters of intent, started 1 paid pilot." / "We interviewed 14 purchasing managers between March and June 2026, in the Lyon and Nantes areas." |

- **B1** — **Manque**: Le critère demande un prototype utilisé par de vraies personnes en usage réel ; le deck ne montre qu'une maquette cliquable Figma testée ponctuellement, et le moteur de lecture des emails n'est pas construit. **À demander**: Votre prototype Figma a-t-il été utilisé par des acheteurs en conditions réelles au-delà des tests ponctuels, et où en est le développement du moteur de lecture des emails ?
- **B4** — **Manque**: Le deck ne mentionne aucun pivot, aucune hypothèse invalidée ni aucune fonctionnalité abandonnée, ni ce qui aurait déclenché un changement de cap. **À demander**: Qu'avez-vous testé et abandonné depuis le début du projet, et qu'est-ce qui vous a fait changer de direction ?

### C. Économie — poids 1 — 75 %

| # | Question | Valeur | Page | Extrait |
|---|---|---|---|---|
| C1 | Quel prix, et testé sur qui ? | 🟠 partielle | 7 | "Pricing: 150 EUR per month per site. This price comes from our spreadsheet model and has not been tested with prospects yet." |
| C2 | Qui paie, et est-ce la même personne que celle qui souffre ? | 🟢 trouvée | 7 | "The purchasing manager uses the tool; the plant director signs the subscription. In the 14 companies we met, the director was always involved in software purchases above 100 EUR per month." |
| C3 | Marge, coût d'acquisition, rétention ? | ⚪ pour information (absente) | — | — |

- **C1** — **Manque**: Le deck donne un prix mais précise lui-même qu'il sort d'un modèle de tableur et n'a pas été testé auprès de prospects réels ; il manque la réaction de prospects à ce prix. **À demander**: Avez-vous testé ce prix de 150 euros par mois et par site auprès de prospects réels, et si oui, quelle a été leur réaction ?
- **C3** — **Manque**: Aucune page ne donne une marge, un coût d'acquisition ou un chiffre de rétention. **À demander**: Avez-vous une marge, un coût d'acquisition client ou un chiffre de rétention à date ?

### D. Marché et moment — poids 2 — 33.3 %

| # | Question | Valeur | Page | Extrait |
|---|---|---|---|---|
| D1 | Taille du marché calculée par le bas ? | 🔴 absente | — | — |
| D2 | Pourquoi maintenant ? | 🟢 trouvée | 8 | "Why now: since 2025 the EU e-invoicing mandate forces suppliers to send structured documents, which makes the emails machine-readable for the first time." |
| D3 | Pourquoi ce n'est pas déjà fait par un acteur en place ? | 🔴 absente | — | — |

- **D1** — **Manque**: Le deck ne calcule pas la taille de marché en partant du bas (nombre de clients possibles multiplié par un prix, avec des hypothèses visibles). Le seul chiffre de marché cité est une estimation d'analyste externe. **À demander**: Pouvez-vous refaire votre calcul de marché en partant du nombre de clients potentiels multiplié par le prix, avec les hypothèses détaillées ?
- **D3** — **Manque**: Le deck n'explique pas pourquoi un acteur déjà installé n'a pas déjà construit cette solution. **À demander**: Pourquoi un acteur déjà en place n'a-t-il pas déjà construit cette solution ?

### E. Équipe — poids 3 — 50 %

| # | Question | Valeur | Page | Extrait |
|---|---|---|---|---|
| E1 | Qui a fait quoi, concrètement, avant ? | 🟠 partielle | 9 | "Lena Vartan, CEO. 8 years as purchasing manager at Forgeval Industries (fictional group, 180 employees), where she led a team of 6 buyers." / "Marc Delorme, CTO. Ex-BigTech engineer." |
| E2 | Quel lien entre les fondateurs et le problème ? | 🟢 trouvée | 9 | "8 years as purchasing manager at Forgeval Industries (fictional group, 180 employees), where she led a team of 6 buyers. She lived the problem every week." |
| E3 | Temps plein ou pas ? | 🔴 absente | — | — |
| E4 | Répartition des parts entre fondateurs ? | 🔴 absente | — | — |
| E5 | Les compétences couvrent-elles produit, technique et vente ? | 🟢 trouvée | 9 | "Roles: product and sales discovery (Lena), tech (Marc). Sales: no one yet. We plan to hire a first sales person after the round." |

- **E1** — **Manque**: Le deck ne donne pas de résultat vérifiable pour Marc Delorme (seulement « Ex-BigTech engineer », sans rôle ni réalisation chiffrée) ; pour Lena Vartan, l'expérience est décrite en ancienneté et taille d'équipe mais pas comme une réalisation construite et mesurée. **À demander**: Chez quelle entreprise Marc a-t-il travaillé, quel était son rôle exact, et qu'a-t-il concrètement construit ou livré, à quelle échelle ?
- **E3** — **Manque**: Le deck ne précise à aucun moment si Lena ou Marc travaillent à temps plein ou à temps partiel sur Gantrix. **À demander**: Lena et Marc travaillent-ils à temps plein sur Gantrix, et depuis quelle date ?
- **E4** — **Manque**: Aucune répartition du capital entre les fondateurs n'est indiquée dans le deck, ni de mention que cette information est disponible sur demande. **À demander**: Quelle est la répartition du capital entre Lena et Marc ?

### F. Argent et prochaine étape — poids 2 — 100 %

| # | Question | Valeur | Page | Extrait |
|---|---|---|---|---|
| F1 | Combien est demandé, et à quoi ça sert ? | 🟢 trouvée | 10 | "We are raising 400,000 EUR in this pre-seed round." / "Use of funds: 60% product (email parsing engine, 2 developers), 25% first sales hire, 15% operations." |
| F2 | Quelle preuve la boîte doit obtenir avant le tour suivant ? | 🟢 trouvée | 11 | "Goal before the seed round: 20 paying customers within 12 months of closing." |
| F3 | Le montant permet-il d'atteindre cette preuve ? | 🟢 trouvée | 11 | "At the current plan, 400,000 EUR covers 14 months of spending, which leaves 2 months of margin after the 12-month goal." |
| F4 | Qui a déjà mis de l'argent ? | 🟢 trouvée | 12 | "Founders: 30,000 EUR of their own money, invested in January 2026." / "Regional innovation grant: 25,000 EUR, received in May 2026." / "No business angel so far." |
