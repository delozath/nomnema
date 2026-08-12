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
