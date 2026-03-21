#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Replace 4 guide steps with 5 in index.html"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the block to replace - from the intro-steps-wrap content to the dots section
start_marker = '        <div class="intro-step active" data-step="0">\n          <div class="intro-step-icon">&#127756;</div>'
end_marker = '      <!-- Indicateur de page -->'

start = content.find(start_marker)
end = content.find(end_marker)

if start == -1:
    print("ERROR: start marker not found")
    exit(1)
if end == -1:
    print("ERROR: end marker not found")
    exit(1)

print(f"Replacing lines {start}-{end}")

new_steps = '''        <div class="intro-step active" data-step="0">
          <div class="intro-step-icon">&#128640;</div>
          <h3>Comment jouer</h3>
          <p>Marche dans <strong>le monde r&#233;el</strong> jusqu&#8217;&#224; sentir l&#8217;ast&#233;ro&#239;de changer de couleur.<br>
          Quand il vire au <span style="color:#4FC3F7">bleu</span>, tu es arriv&#233;&nbsp;! Appuie sur <strong>&#128640; Jouer</strong> pour lancer la Lune.</p>
        </div>

        <div class="intro-step" data-step="1">
          <div class="intro-step-icon">&#127769;</div>
          <h3>Les 9 Lunes</h3>
          <ul style="text-align:left;font-size:.82rem;line-height:1.7;list-style:none;padding:0;margin:0">
            <li>&#127761; <strong>Lune de Verre</strong> &mdash; Lance cosmique (fronde)</li>
            <li>&#127762; <strong>Lune de Cendre</strong> &mdash; Vol de cosmonaute</li>
            <li>&#127763; <strong>Lune de Lierre</strong> &mdash; Sauts infinis</li>
            <li>&#127764; <strong>Lune de Givre</strong> &mdash; Cordes &amp; grappin</li>
            <li>&#127765; <strong>Lune d&#8217;Ombre</strong> &mdash; Labyrinthe obscur</li>
            <li>&#127766; <strong>Lune de Fer</strong> &mdash; Absorbe les particules</li>
            <li>&#127767; <strong>Lune de Temp&#234;te</strong> &mdash; Jetpack &amp; obstacles</li>
            <li>&#127768; <strong>Lune de Cristal</strong> &mdash; Traverse le vide</li>
            <li>&#127761; <strong>Lune d&#8217;&#201;clipse</strong> &mdash; Duel r&#233;flexe final</li>
          </ul>
        </div>

        <div class="intro-step" data-step="2">
          <div class="intro-step-icon">&#11088;</div>
          <h3>Poussi&#232;res d&#8217;&#233;toile</h3>
          <p>Chaque Lune r&#233;compense en &#10024; <strong>poussi&#232;res d&#8217;&#233;toile</strong>.<br>
          Rejoue pour en accumuler davantage&nbsp;!<br>
          D&#233;pense-les &#224; la <strong>Boutique Lunaire</strong> &#127978; pour recharger ton &#233;nergie.</p>
        </div>

        <div class="intro-step" data-step="3">
          <div class="intro-step-icon">&#127756;</div>
          <h3>Les objets</h3>
          <ul style="text-align:left;font-size:.83rem;line-height:1.8;list-style:none;padding:0;margin:0">
            <li>&#128153; <strong>&#201;clat</strong> &mdash; Recharge 10% d&#8217;&#233;nergie (5 &#10024;)</li>
            <li>&#128142; <strong>Fragment</strong> &mdash; Recharge 25% d&#8217;&#233;nergie (15 &#10024;)</li>
            <li>&#128311; <strong>Gros Fragment</strong> &mdash; Recharge 50% d&#8217;&#233;nergie (35 &#10024;)</li>
            <li>&#10084;&#65039; <strong>C&#339;ur Lunaire</strong> &mdash; &#201;nergie &#224; 100% (80 &#10024;)</li>
          </ul>
        </div>

        <div class="intro-step" data-step="4">
          <div class="intro-step-icon">&#128161;</div>
          <h3>Astuces</h3>
          <ul style="text-align:left;font-size:.83rem;line-height:1.8;list-style:none;padding:0;margin:0">
            <li>&#128308; Halo <strong>rouge</strong> = encore loin (+100m)</li>
            <li>&#129001; Halo <strong>orange</strong> = tu approches (50-100m)</li>
            <li>&#128994; Halo <strong>vert</strong> = presque l&#224; (10-50m)</li>
            <li>&#128309; Halo <strong>bleu</strong> = tu y es&nbsp;! (-10m)</li>
            <li>&#10145;&#65039; <strong>Point suivant</strong> : passer sans jouer si tu veux</li>
            <li>&#128260; <strong>Rejouer</strong> une Lune pour plus de &#10024;</li>
          </ul>
        </div>

      </div>

      <!-- Indicateur de page -->
      <div class="intro-dots" aria-hidden="true">
        <span class="intro-dot active" data-dot="0"></span>
        <span class="intro-dot" data-dot="1"></span>
        <span class="intro-dot" data-dot="2"></span>
        <span class="intro-dot" data-dot="3"></span>
        <span class="intro-dot" data-dot="4"></span>
      </div>
'''

# Replace from start to end_marker (including the old dots section after it)
# Find the end of the dots section
dots_end_marker = '      <!-- Boutons navigation -->'
dots_end = content.find(dots_end_marker)
if dots_end == -1:
    print("ERROR: dots end marker not found")
    exit(1)

old_block = content[start:dots_end]
print(f"Old block length: {len(old_block)}")

new_content = content[:start] + new_steps + content[dots_end:]

with open('index.html', 'w', encoding='utf-8', newline='') as f:
    f.write(new_content)

print("SUCCESS")

# Verify
with open('index.html', 'r', encoding='utf-8') as f:
    verify = f.read()
print("Has 'Comment jouer':", 'Comment jouer' in verify)
print("Has 'Bienvenue dans GPS0':", 'Bienvenue dans GPS0' in verify)
print("Has 5th dot:", 'data-dot="4"' in verify)
