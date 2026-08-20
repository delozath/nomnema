from unittest.mock import Mock

import nomnema.services.retrieve_orchestrator as retrieve_orchestrator_module
from nomnema.services.retrieve_orchestrator import RetrieveOrchestrator


def test_cancelled_preview_does_not_move_or_save(monkeypatch, tmp_path):
    orchestrator = RetrieveOrchestrator.__new__(RetrieveOrchestrator)
    origin = tmp_path / "source.pdf"
    entry = {
        "ID": "Example2026",
        "doi": "10.1000/example",
    }

    orchestrator._get_doi = Mock(return_value=(entry["doi"], origin))
    orchestrator.fetch_bib_entry = Mock()
    orchestrator.fetch_bib_entry.perform.return_value = "retrieved entry"
    orchestrator._get_abstract = Mock(return_value="abstract")
    orchestrator.bib_driver = Mock()
    orchestrator.bib_driver.append_abstract.return_value = entry
    orchestrator.bib_driver.cache_unique_doi = []
    orchestrator.bib_driver.dict_to_bibtex.return_value = "preview"

    monkeypatch.setattr(
        retrieve_orchestrator_module,
        "preview_entry_window",
        lambda _: ("preview", False, False, True),
    )
    move = Mock()
    monkeypatch.setattr(retrieve_orchestrator_module, "move", move)

    orchestrator.run()

    move.assert_not_called()
    orchestrator.bib_driver.add_entry.assert_not_called()
    orchestrator.bib_driver.save.assert_not_called()
