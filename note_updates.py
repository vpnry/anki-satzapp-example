# note_updates.py

from aqt import mw
from aqt.utils import showInfo
from .select_deck import is_note_in_selected_decks

def process_notes(replace, generate_examples_for_note, selected_decks=None, progress_callback=None):
    # This function is now intended to be run in a background thread via QueryOp
    note_ids = mw.col.db.list("SELECT id FROM notes")
    
    # Filter notes that belong to selected decks
    target_notes = []
    for nid in note_ids:
        note = mw.col.get_note(nid)
        if selected_decks and not is_note_in_selected_decks(note, selected_decks):
            continue
        target_notes.append(note)

    total = len(target_notes)
    updated = 0

    for i, note in enumerate(target_notes):
        if progress_callback:
            progress_callback(i + 1, total)
            
        if "term" in note:
            if "Example" in note:
                # Only update if field is empty OR we are in overwrite mode
                if not note["Example"].strip() or replace:
                    # Note: generate_examples_for_note will call note.flush()
                    generate_examples_for_note(note, replace_existing=replace)
                    updated += 1

    return updated
