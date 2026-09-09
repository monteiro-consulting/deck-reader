#!/usr/bin/env python3
"""Draft the email to the founder. Standard library only; no model writes this text.

Usage:
    founder_email.py --kind none      --deck DECK.pdf --lang fr --out email.md
    founder_email.py --kind missing   --deck DECK.pdf --lang fr --gate gate.json --out email.md
    founder_email.py --kind leftovers --deck DECK.pdf --lang fr --gate gate.json --out email.md

none       the deck came without annexes: a short, generic request. No list on purpose: the
           deck without proof does the work, not the tool.
missing    annexes were given but the key claims are not covered: one line per claim, with the
           page, what the deck states and the document that would back it.
leftovers  the reading continued; these are the claims still not covered, same format.

The draft is written to a file. The user sends it, or not. The tool never sends anything.
"""
import argparse
import json
import os
import sys

from claims_lib import load_json

T = {
    "en": {
        "subject": "Subject: your deck {deck} - supporting documents",
        "hello": "Hello,",
        "none": "Thank you for sending your deck. It arrived without any supporting document. Before we read it, could you send the documents that back the figures it states (revenue export, customer list, retention or cohort data, financial model, cap table)? We will then come back to you with our questions.",
        "missing": "Thank you for sending your deck and the attached documents. Some of the figures the deck states are not backed by what we received. Could you send the following?",
        "leftovers": "Thank you for sending your deck and the attached documents. We have read them. A few figures in the deck are still not backed by a document; could you send the following before our call?",
        "line": "- Page {page}: \"{statement}\". Document expected: {proof}.",
        "close": "Thank you,",
        "note": "Draft written by the deck reader. Review before sending; the tool sends nothing.",
    },
    "fr": {
        "subject": "Objet : votre deck {deck} - pièces justificatives",
        "hello": "Bonjour,",
        "none": "Merci pour l'envoi de votre deck. Il nous est arrivé sans aucune pièce justificative. Avant de le lire, pourriez-vous nous envoyer les documents qui appuient les chiffres qu'il avance (export de revenus, liste clients, données de rétention ou cohortes, modèle financier, table de capitalisation) ? Nous reviendrons ensuite vers vous avec nos questions.",
        "missing": "Merci pour l'envoi de votre deck et des documents joints. Certains chiffres du deck ne sont pas appuyés par ce que nous avons reçu. Pourriez-vous nous envoyer les éléments suivants ?",
        "leftovers": "Merci pour l'envoi de votre deck et des documents joints. Nous les avons lus. Quelques chiffres du deck ne sont pas encore appuyés par un document ; pourriez-vous nous envoyer les éléments suivants avant notre échange ?",
        "line": "- Page {page} : « {statement} ». Document attendu : {proof}.",
        "close": "Merci,",
        "note": "Brouillon rédigé par le lecteur de deck. À relire avant envoi ; l'outil n'envoie rien.",
    },
}


def draft(kind, deck, lang, to_request=None):
    t = T.get(lang, T["en"])
    name = os.path.basename(deck)
    lines = [t["subject"].format(deck=name), "", t["hello"], ""]
    if kind == "none":
        lines.append(t["none"])
    else:
        lines.append(t[kind])
        lines.append("")
        for item in to_request or []:
            lines.append(t["line"].format(page=item.get("page", "?"), statement=item.get("statement", "").strip(), proof=item.get("proof") or "-"))
    lines += ["", t["close"], "", f"_{t['note']}_", ""]
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--kind", required=True, choices=["none", "missing", "leftovers"])
    ap.add_argument("--deck", required=True)
    ap.add_argument("--lang", default="en")
    ap.add_argument("--gate", default=None, help="gate.json from seed_gate.py annexes (for missing / leftovers)")
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    to_request = []
    if args.kind != "none":
        if not args.gate:
            print("founder_email.py: --gate is required for missing / leftovers", file=sys.stderr)
            return 2
        to_request = load_json(args.gate).get("to_request", [])
        if not to_request:
            print(json.dumps({"out": None, "items": 0, "note": "nothing to request"}))
            return 0
    text = draft(args.kind, args.deck, args.lang, to_request)
    with open(args.out, "w", encoding="utf-8") as f:
        f.write(text)
    print(json.dumps({"out": args.out, "kind": args.kind, "items": len(to_request)}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
