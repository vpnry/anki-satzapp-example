# select_deck.py

from aqt import mw
from aqt.qt import QDialog, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QRadioButton, QGroupBox, QHBoxLayout
from PyQt6.QtWidgets import QAbstractItemView

def select_decks_and_options():
    """
    Opens a custom dialog allowing the user to select multiple decks
    and choose whether to overwrite or skip existing examples.
    Returns (selected_deck_names, overwrite_bool) or (None, None).
    """
    dialog = QDialog(mw)
    dialog.setWindowTitle("Satzapp Example Fetcher")

    layout = QVBoxLayout()
    
    # Deck Selection
    layout.addWidget(QPushButton("Select Decks:"))
    deck_list = QListWidget()
    deck_list.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)
    for name in sorted(mw.col.decks.all_names()):
        item = QListWidgetItem(name)
        deck_list.addItem(item)
    layout.addWidget(deck_list)

    # Behavior Options
    options_group = QGroupBox("Sentence Update Behavior")
    options_layout = QVBoxLayout()
    
    skip_radio = QRadioButton("Skip if exist")
    skip_radio.setChecked(True)
    overwrite_radio = QRadioButton("Overwrite examples")
    
    options_layout.addWidget(skip_radio)
    options_layout.addWidget(overwrite_radio)
    options_group.setLayout(options_layout)
    layout.addWidget(options_group)

    # Buttons
    btn_layout = QHBoxLayout()
    confirm_button = QPushButton("Fetch Sentences")
    confirm_button.clicked.connect(dialog.accept)
    cancel_button = QPushButton("Cancel")
    cancel_button.clicked.connect(dialog.reject)
    
    btn_layout.addWidget(confirm_button)
    btn_layout.addWidget(cancel_button)
    layout.addLayout(btn_layout)

    dialog.setLayout(layout)

    if dialog.exec():
        selected = [item.text() for item in deck_list.selectedItems()]
        if not selected:
            return None, None
        return selected, overwrite_radio.isChecked()
    return None, None

def is_note_in_selected_decks(note, selected_deck_names):
    """
    Checks if the note belongs to any of the selected decks.
    """
    card_ids = note.card_ids()
    for cid in card_ids:
        card = mw.col.get_card(cid)
        deck = mw.col.decks.name(card.did)
        if deck in selected_deck_names:
            return True
    return False
