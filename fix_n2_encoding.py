"""Fix encodage mojibake dans niveau2.html"""
import re

FILEPATH = r"c:\Users\Jules\Desktop\GPS0\minijeux\niveau2.html"

with open(FILEPATH, 'r', encoding='utf-8') as f:
    raw = f.read()

# Table de remplacement mojibake → Unicode correct
fixes = [
    # Emojis / symboles unicode cassés
    ('â¤â¤â¤',  '❤❤❤'),
    ('â¤â¤',    '❤❤'),
    ('â¤',      '❤'),
    ('âœ¨',     '✨'),
    ('âœ¦',     '✦'),
    ('âš¡',     '⚡'),
    ('â†\u2019',  '\u2192'),
    ('â€"',     '—'),
    ('â€™',     '\u2019'),
    ('â€œ',     '\u201C'),
    ('â€',      '\u201D'),
    # Lettres accentuées françaises
    ('Ã‰',      'É'),
    ('Ã©',      'é'),
    ('Ã¨',      'è'),
    ('Ã ',      'à'),
    ('Ã¹',      'ù'),
    ('Ã®',      'î'),
    ('Ã´',      'ô'),
    ('Ã»',      'û'),
    ('Ã§',      'ç'),
    ('Ã¯',      'ï'),
    ('Ã¢',      'â'),
    ('Ãª',      'ê'),
    ('Ã¼',      'ü'),
    ('Ã¤',      'ä'),
    ('Ã¶',      'ö'),
    ('Ã',       'À'),   # doit être après É pour ne pas casser
    ('Â·',      '·'),
    ('Â»',      '»'),
    ('Â«',      '«'),
    ('Â ',      '\u00A0'),
    ('Â©',      '©'),
    ('Â°',      '°'),
    ('Â²',      '²'),
    ('Â³',      '³'),
    ('Â½',      '½'),
    ('Â',       ''),   # Â seul restant = artifact, supprimer
    # Tirets / guillemets typographiques
    ('â"€',     '─'),
    ('â•',      '═'),
    ('CÅ"ur',   'Cœur'),
    ('Å"',      'œ'),
    ('â‚¬',     '€'),
    # Espaces
    ('\u00a0\u00a0', ' '),
]

result = raw
for bad, good in fixes:
    result = result.replace(bad, good)

# Fix résiduel: Ã suivi de char inconnu → À
result = re.sub(r'Ã(?=[^©éèàùîôûçïâêüäöÉ\s])', 'À', result)

with open(FILEPATH, 'w', encoding='utf-8') as f:
    f.write(result)

print(f"Fixes appliqués. Taille: {len(result)} chars")

# Vérification rapide
remains = []
for pat in ['â¤','âœ','âš','Ã‰','Ã©','Â·','â€']:
    if pat in result:
        idx = result.index(pat)
        remains.append(f"  RESTE: '{pat}' à pos {idx}: ...{result[max(0,idx-20):idx+20]}...")
if remains:
    print("⚠ Caractères encore cassés:")
    for r in remains:
        print(r)
else:
    print("✅ Aucun caractère mojibake détecté")
