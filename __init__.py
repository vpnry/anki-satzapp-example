# __init__.py

# This file serves as the entry point for the Anki add-on that fetches 
# example sentences from Satzapp for German terms.

import html
from bs4 import BeautifulSoup
from aqt import mw
from aqt.qt import QAction, qconnect
from anki.notes import Note

# Importing helper utilities
from .sentence_scraper import get_example_sentences, CaptchaError
from .note_updates import process_notes
from .select_deck import select_decks_and_options
from aqt.operations import QueryOp
from aqt.utils import showInfo

def generate_examples_for_note(note: Note, replace_existing=False):
    """Fetch example sentences for a single Anki note's 'term' field from Satzapp."""
    # Case-insensitive field detection
    field_names = note.keys()
    term_field = next((f for f in field_names if f.lower() == "term"), None)
    example_field = next((f for f in field_names if f.lower() == "example"), None)

    if not term_field or not example_field:
        return

    term = note[term_field].strip()
    unescaped = html.unescape(term)
    soup = BeautifulSoup(unescaped, "html.parser")
    term = soup.get_text().strip()

    if not term:
        return

    # Add example sentences from Satzapp if Example field exists and is empty (or replacing)
    if not note[example_field].strip() or replace_existing:
        try:
            examples = get_example_sentences(term)
            if examples:
                note[example_field] = examples
                note.flush()
        except CaptchaError:
            # Re-raise CaptchaError so it can be handled by the caller/UI
            raise
        except Exception as e:
            # Silently log other errors to console for now
            print(f"❌ Error fetching examples for '{term}': {e}")

def _run_fetching_background(nids=None, selected_decks=None, replace=False):
    """Core background processing logic shared between deck and selection fetching."""
    def on_success(count):
        showInfo(f"✅ Example sentences fetched for {count} notes from Satzapp.")

    # Establish a checkpoint so user can undo (Main Thread)
    mw.checkpoint("Fetch Example Sentences")

    def update_progress(current, total):
        # Update progress label on the main thread
        def update():
            # Update both label and the progress bar (value/max)
            mw.progress.update(label=f"Processing note {current}/{total}...", value=current, max=total)

        if hasattr(mw, "taskman"):
            mw.taskman.run_on_main(update)
        elif hasattr(mw, "task_manager"):
            mw.task_manager.run_on_main(update)
        else:
            # Fallback for versions where task_manager/taskman is missing
            # Using progress.timer(0, ...) is a safe way to reach the main thread.
            mw.progress.timer(0, update, False)

    def do_work(col):
        return process_notes(replace, generate_examples_for_note, selected_decks=selected_decks, nids=nids, progress_callback=update_progress)

    def on_failure(e):
        if isinstance(e, CaptchaError):
            showInfo(f"🛑 Satzapp has requested a captcha! \n\nPlease open satzapp.com in your browser, solve the captcha, and then try again.\n\nError: {e}")
        else:
            showInfo(f"❌ An error occurred while fetching sentences: {e}")

    # Use QueryOp to run in background and show a progress spinner
    QueryOp(
        parent=mw,
        op=do_work,
        success=on_success,
    ).failure(on_failure).with_progress().run_in_background()

def run_example_fetching():
    """Initiate the example sentence fetching process for specific decks."""
    selected_decks, replace = select_decks_and_options()
    if not selected_decks:
        return
    _run_fetching_background(selected_decks=selected_decks, replace=replace)

def run_example_fetching_for_selection(browser):
    """Initiate the example sentence fetching process for selected notes in browser."""
    nids = browser.selectedNotes()
    if not nids:
        showInfo("No notes selected.")
        return
    
    # For selection, we might still want to ask about overwriting, but skip deck selection.
    # However, to keep it simple and consistent with how browser tools usually work:
    # Let's just ask if they want to replace existing.
    from aqt.utils import askUser
    replace = askUser("Replace existing example sentences if they are not empty?")
    
    _run_fetching_background(nids=nids, replace=replace)

def setup_browser_menu(browser):
    """Add a menu item to the browser's Edit menu."""
    menu = browser.form.menuEdit
    menu.addSeparator()
    action = QAction("📖 Fetch German Example Sentences for Selected Notes", browser)
    qconnect(action.triggered, lambda: run_example_fetching_for_selection(browser))
    menu.addAction(action)

# Register a menu item in Anki's Tools menu
action = QAction("📖 Fetch German Example Sentences for Notes", mw)
qconnect(action.triggered, run_example_fetching)
mw.form.menuTools.addAction(action)

# Register the browser menu hook
from anki.hooks import addHook
addHook("browser.setupMenus", setup_browser_menu)