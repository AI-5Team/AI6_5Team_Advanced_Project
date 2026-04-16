from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

from services.worker.experiments.video_harness import get_video_experiment_definition, run_video_experiment, wrap_text_by_pixels
from services.worker.utils.runtime import load_font


def test_video_harness_renders_variant_artifacts(tmp_path: Path) -> None:
    sample_a = tmp_path / "sample-a.png"
    sample_b = tmp_path / "sample-b.png"
    Image.new("RGB", (1200, 1600), (224, 140, 82)).save(sample_a)
    Image.new("RGB", (1200, 1600), (118, 82, 204)).save(sample_b)

    experiment = get_video_experiment_definition("EXP-03")
    scenario = experiment.scenario
    patched_experiment = type(experiment)(
        experiment_id=experiment.experiment_id,
        title=experiment.title,
        objective=experiment.objective,
        scenario=type(scenario)(
            scenario_id=scenario.scenario_id,
            style_id=scenario.style_id,
            template_id=scenario.template_id,
            asset_paths=(sample_a, sample_b),
            scene_specs=scenario.scene_specs,
        ),
        baseline_variant=experiment.baseline_variant,
        candidate_variants=experiment.candidate_variants,
    )

    artifact = run_video_experiment(patched_experiment, artifact_root=tmp_path / "artifacts")

    assert Path(artifact["artifact_path"]).exists()
    for result in artifact["results"]:
        assert Path(result["video_path"]).exists()
        assert Path(result["first_scene_path"]).exists()
        assert result["evaluation"]["bgrade_signal_score"] > 0
        assert result["evaluation"]["service_loop_fit_score"] > 0
        assert result["rendered_scene_specs"]


def test_video_harness_supports_owner_made_reference_experiment() -> None:
    experiment = get_video_experiment_definition("EXP-04")

    assert experiment.baseline_variant.overlay_mode == "flyer_poster"
    assert experiment.candidate_variants[0].overlay_mode == "owner_made_safe"
    assert experiment.candidate_variants[0].lever_id == "product_visibility_protection"


def test_video_harness_supports_handdrawn_reference_experiment() -> None:
    experiment = get_video_experiment_definition("EXP-05")

    assert experiment.baseline_variant.overlay_mode == "owner_made_safe"
    assert experiment.candidate_variants[0].overlay_mode == "hand_drawn_menu"
    assert experiment.candidate_variants[0].lever_id == "visual_style_reference"


def test_video_harness_supports_service_aligned_opening_priority_experiment() -> None:
    experiment = get_video_experiment_definition("EXP-06")

    assert experiment.scenario.template_id == "T02"
    assert experiment.baseline_variant.overlay_mode == "owner_made_safe"
    assert experiment.baseline_variant.opening_focus == "benefit_first"
    assert experiment.candidate_variants[0].opening_focus == "menu_first"
    assert experiment.candidate_variants[0].lever_id == "opening_scene_priority"
    assert experiment.candidate_variants[0].scene_text_overrides is not None
    assert experiment.candidate_variants[0].scene_text_overrides["s1"]["primary_text"] == "겉바 규카츠"


def test_video_harness_supports_visual_baseline_rebuild_experiment() -> None:
    experiment = get_video_experiment_definition("EXP-07")

    assert experiment.baseline_variant.overlay_mode == "owner_made_safe"
    assert experiment.candidate_variants[0].overlay_mode == "structured_bgrade_v2"
    assert experiment.candidate_variants[0].lever_id == "baseline_rebuild"


def test_video_harness_supports_multi_photo_validation_experiment() -> None:
    experiment = get_video_experiment_definition("EXP-08")

    assert experiment.baseline_variant.overlay_mode == "structured_bgrade_v2"
    assert len(experiment.scenario.asset_paths) == 5
    assert len(experiment.scenario.scene_specs) == 5
    assert experiment.candidate_variants == ()


def test_wrap_text_by_pixels_prefers_space_boundaries() -> None:
    image = Image.new("RGB", (720, 1280), (255, 255, 255))
    draw = ImageDraw.Draw(image)
    font = load_font(50, bold=True)

    lines = wrap_text_by_pixels(draw, "지금 바로 저장 말고 방문", font, 220)

    assert not any(line.endswith("저") for line in lines)
    assert not any(line.startswith("장") for line in lines)
    assert any("저장" in line for line in lines)
