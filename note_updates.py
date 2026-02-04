# note_updates.py

from aqt import mw
from aqt.utils import showInfo
from .select_deck import is_note_in_selected_decks

def process_notes(replace, generate_examples_for_note, selected_decks=None, nids=None, progress_callback=None):
    # This function is now intended to be run in a background thread via QueryOp
    if nids is None:
        note_ids = mw.col.db.list("SELECT id FROM notes")
    else:
        note_ids = nids
    
    # Filter notes that belong to selected decks and need processing
    target_notes = []
    for nid in note_ids:
        note = mw.col.get_note(nid)
        
        # 1. Deck filter
        if selected_decks is not None and not is_note_in_selected_decks(note, selected_decks):
            continue
            
        # 2. Field filter: Only process if "term" and "Example" exist (case-insensitive)
        field_names = note.keys()
        term_field = next((f for f in field_names if f.lower() == "term"), None)
        example_field = next((f for f in field_names if f.lower() == "example"), None)

        if term_field and example_field:
            has_content = bool(note[example_field].strip())
            if has_content and not replace:
                continue
            target_notes.append(note)

    total = len(target_notes)
    updated = 0

    for i, note in enumerate(target_notes):
        if progress_callback:
            progress_callback(i + 1, total)
            
        # Note: generate_examples_for_note will call note.flush()
        generate_examples_for_note(note, replace_existing=replace)
        updated += 1

    return updated
