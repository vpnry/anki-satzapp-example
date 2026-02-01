# Anki: Satzapp Examples

This Anki add-on automatically fetches German example sentences and their English translations from [Satzapp](https://www.satzapp.com/saetze/) for your vocabulary terms. It's designed to help you quickly add context to your flashcards.

---

##  What It Does

- Scans selected decks in your collection for notes containing a `term` field.
- Fetches the first 5 example sentences from Satzapp for each term.
- Includes English translations for the fetched sentences.
- Inserts the formatted HTML list into the note's `Example` field.
- Optionally replaces existing example sentences if desired.

---

## 🧭 How to Use

1. **Open Anki** and go to the `Tools` menu.
2. Click on **"📖 Fetch German Example Sentences for Notes"**.
3. Select one or more decks you want to scan.
4. Choose whether to replace existing example sentences.
5. The add-on will process the notes and update the `Example` field automatically.

---

## 🗂 Field Requirements

Your notes should have:
- A `term` field (the German word or phrase).
- An `Example` field (where the example sentences will be inserted).

---

## 🛠 Requirements

- Anki 2.1.65+ (compatible with Qt6)
- Python libraries `requests` and `beautifulsoup4` (usually bundled with Anki or available in the environment).

---

## Credits

- Based on AnkiAddonGenerateAudio by Frank Valenziano
- Source URL: Based on https://github.com/frankvalenziano/AnkiAddonGenerateAudio
- Content Source: Example sentences provided by [Satzapp](https://www.satzapp.com)
---

## ⚖️ License & Attribution

### Add-on Code
This project is licensed under the GNU General Public License v3.0. See the [LICENSE](LICENSE) file for full details.

### Content Attribution
The example sentences and translations fetched by this add-on are provided by **Netzverb ([www.satzapp.com](https://www.satzapp.com))**. Unless otherwise stated, this content is available under the **[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/)** license. You are free to use, copy, and modify this content, provided you give appropriate credit to the author.

