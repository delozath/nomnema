from unittest.mock import Mock, patch

from omegaconf import OmegaConf

from nomnema.services.retrieve_orchestrator import RetrieveOrchestrator


def test_get_doi_uses_manually_configured_doi(tmp_path):
    origin = tmp_path / "article.pdf"
    origin.touch()
    orchestrator = RetrieveOrchestrator.__new__(RetrieveOrchestrator)
    orchestrator.cfg = OmegaConf.create(
        {"origin": str(origin), "doi": "10.1000/manual"}
    )

    doi, resolved_origin = orchestrator._get_doi()

    assert doi == "10.1000/manual"
    assert resolved_origin == origin


def test_run_cancelled_preview_does_not_move_file_or_update_bib_db(tmp_path):
    origin = tmp_path / "article.pdf"
    origin.touch()
    destination = tmp_path / "library"

    orchestrator = RetrieveOrchestrator.__new__(RetrieveOrchestrator)
    orchestrator.destination = destination
    orchestrator._get_doi = Mock(return_value=("10.1000/cancelled", origin))
    orchestrator.fetch_bib_entry = Mock()
    orchestrator.fetch_bib_entry.perform.return_value = "bib entry"
    orchestrator._get_abstract = Mock(return_value="abstract")
    orchestrator.bib_driver = Mock()
    orchestrator.bib_driver.append_abstract.return_value = {
        "doi": "10.1000/cancelled"
    }
    orchestrator.bib_driver.cache_unique_doi = []
    orchestrator.bib_driver.dict_to_bibtex.return_value = "bib preview"

    with (
        patch(
            "nomnema.services.retrieve_orchestrator.preview_entry_window",
            return_value=None,
        ),
        patch("nomnema.services.retrieve_orchestrator.move") as move_file,
    ):
        orchestrator.run()

    move_file.assert_not_called()
    orchestrator.bib_driver.add_entry.assert_not_called()
    orchestrator.bib_driver.save.assert_not_called()
    assert origin.exists()
    assert not destination.exists()
