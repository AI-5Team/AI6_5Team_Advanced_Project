from __future__ import annotations

from pathlib import Path

from services.worker.experiments.prompt_harness import (
    DEFAULT_TEMPLATE_SPEC_ROOT,
    build_scene_plan_preview,
    build_deterministic_reference_bundle,
    build_prompt_package,
    evaluate_korean_integrity,
    evaluate_copy_bundle,
    evaluate_scene_plan_preview,
    get_experiment_definition,
    get_model_comparison_definition,
    resolve_api_key_env,
)


def test_deterministic_reference_bundle_matches_fixed_baseline_rules() -> None:
    experiment = get_experiment_definition("EXP-01")
    context_root = Path(DEFAULT_TEMPLATE_SPEC_ROOT)
    context = build_deterministic_reference_bundle(context_root, experiment.scenario)
    from services.worker.experiments.prompt_harness import load_experiment_context

    loaded = load_experiment_context(context_root, experiment.scenario)
    evaluation = evaluate_copy_bundle(context, experiment.scenario, loaded["template"], loaded["copy_rule"])

    assert evaluation["region_slot_hits"] >= 2
    assert evaluation["caption_count"] == 3
    assert evaluation["hashtag_count"] == 5
    assert "region repeated more than allowed" in evaluation["failed_checks"]
    assert "sceneText missing roles" not in " ".join(evaluation["failed_checks"])


def test_slot_guidance_variant_changes_only_slot_instruction_block() -> None:
    experiment = get_experiment_definition("EXP-01")
    baseline_prompt = build_prompt_package(DEFAULT_TEMPLATE_SPEC_ROOT, experiment.scenario, experiment.baseline_variant)
    candidate_prompt = build_prompt_package(DEFAULT_TEMPLATE_SPEC_ROOT, experiment.scenario, experiment.candidate_variants[0])

    assert baseline_prompt["system_instruction"] == candidate_prompt["system_instruction"]
    assert baseline_prompt["user_prompt"] != candidate_prompt["user_prompt"]
    assert "[슬롯 지시]" in baseline_prompt["user_prompt"]
    assert "[슬롯 지시]" in candidate_prompt["user_prompt"]
    assert experiment.candidate_variants[0].lever_id == "slot_instruction"


def test_audience_tone_variant_changes_only_audience_guidance_block() -> None:
    experiment = get_experiment_definition("EXP-02")
    baseline_prompt = build_prompt_package(DEFAULT_TEMPLATE_SPEC_ROOT, experiment.scenario, experiment.baseline_variant)
    candidate_prompt = build_prompt_package(DEFAULT_TEMPLATE_SPEC_ROOT, experiment.scenario, experiment.candidate_variants[0])

    assert baseline_prompt["system_instruction"] == candidate_prompt["system_instruction"]
    assert baseline_prompt["user_prompt"] != candidate_prompt["user_prompt"]
    assert "[타깃 고객/톤 지시]" in baseline_prompt["user_prompt"]
    assert "[타깃 고객/톤 지시]" in candidate_prompt["user_prompt"]
    assert experiment.candidate_variants[0].lever_id == "audience_tone"


def test_service_aligned_b_grade_variant_changes_only_audience_guidance_block() -> None:
    experiment = get_experiment_definition("EXP-15")
    baseline_prompt = build_prompt_package(DEFAULT_TEMPLATE_SPEC_ROOT, experiment.scenario, experiment.baseline_variant)
    candidate_prompt = build_prompt_package(DEFAULT_TEMPLATE_SPEC_ROOT, experiment.scenario, experiment.candidate_variants[0])

    assert experiment.scenario.template_id == "T02"
    assert experiment.scenario.style_id == "b_grade_fun"
    assert baseline_prompt["system_instruction"] == candidate_prompt["system_instruction"]
    assert baseline_prompt["user_prompt"] != candidate_prompt["user_prompt"]
    assert '"benefit": "string"' in baseline_prompt["user_prompt"]
    assert '"urgency": "string"' in baseline_prompt["user_prompt"]
    assert experiment.candidate_variants[0].lever_id == "b_grade_tone"


def test_service_aligned_b_grade_review_variant_changes_only_audience_guidance_block() -> None:
    experiment = get_experiment_definition("EXP-16")
    baseline_prompt = build_prompt_package(DEFAULT_TEMPLATE_SPEC_ROOT, experiment.scenario, experiment.baseline_variant)
    candidate_prompt = build_prompt_package(DEFAULT_TEMPLATE_SPEC_ROOT, experiment.scenario, experiment.candidate_variants[0])

    assert experiment.scenario.template_id == "T04"
    assert experiment.scenario.purpose == "review"
    assert experiment.scenario.style_id == "b_grade_fun"
    assert baseline_prompt["system_instruction"] == candidate_prompt["system_instruction"]
    assert baseline_prompt["user_prompt"] != candidate_prompt["user_prompt"]
    assert '"review_quote": "string"' in baseline_prompt["user_prompt"]
    assert '"product_name": "string"' in baseline_prompt["user_prompt"]
    assert experiment.candidate_variants[0].lever_id == "b_grade_tone"


def test_review_slot_length_cap_variant_changes_only_slot_guidance_block() -> None:
    experiment = get_experiment_definition("EXP-17")
    baseline_prompt = build_prompt_package(DEFAULT_TEMPLATE_SPEC_ROOT, experiment.scenario, experiment.baseline_variant)
    candidate_prompt = build_prompt_package(DEFAULT_TEMPLATE_SPEC_ROOT, experiment.scenario, experiment.candidate_variants[0])

    assert experiment.scenario.template_id == "T04"
    assert baseline_prompt["system_instruction"] == candidate_prompt["system_instruction"]
    assert baseline_prompt["user_prompt"] != candidate_prompt["user_prompt"]
    assert "[슬롯 지시]" in candidate_prompt["user_prompt"]
    assert experiment.candidate_variants[0].lever_id == "review_slot_length_cap"


def test_review_region_repeat_variant_changes_only_slot_guidance_block() -> None:
    experiment = get_experiment_definition("EXP-18")
    baseline_prompt = build_prompt_package(DEFAULT_TEMPLATE_SPEC_ROOT, experiment.scenario, experiment.baseline_variant)
    candidate_prompt = build_prompt_package(DEFAULT_TEMPLATE_SPEC_ROOT, experiment.scenario, experiment.candidate_variants[0])

    assert experiment.scenario.template_id == "T04"
    assert baseline_prompt["system_instruction"] == candidate_prompt["system_instruction"]
    assert baseline_prompt["user_prompt"] != candidate_prompt["user_prompt"]
    assert "총 2회 이하" in candidate_prompt["user_prompt"]
    assert experiment.candidate_variants[0].lever_id == "region_repeat_constraint"


def test_review_cta_strength_variant_changes_only_slot_guidance_block() -> None:
    experiment = get_experiment_definition("EXP-19")
    baseline_prompt = build_prompt_package(DEFAULT_TEMPLATE_SPEC_ROOT, experiment.scenario, experiment.baseline_variant)
    candidate_prompt = build_prompt_package(DEFAULT_TEMPLATE_SPEC_ROOT, experiment.scenario, experiment.candidate_variants[0])

    assert experiment.scenario.template_id == "T04"
    assert baseline_prompt["system_instruction"] == candidate_prompt["system_instruction"]
    assert baseline_prompt["user_prompt"] != candidate_prompt["user_prompt"]
    assert "저장, 방문, 확인, 예약 중 최소 하나" in candidate_prompt["user_prompt"]
    assert experiment.candidate_variants[0].lever_id == "cta_strength"


def test_review_output_constraint_variant_changes_only_slot_guidance_block() -> None:
    experiment = get_experiment_definition("EXP-27")
    baseline_prompt = build_prompt_package(DEFAULT_TEMPLATE_SPEC_ROOT, experiment.scenario, experiment.baseline_variant)
    candidate_prompt = build_prompt_package(DEFAULT_TEMPLATE_SPEC_ROOT, experiment.scenario, experiment.candidate_variants[0])

    assert experiment.scenario.template_id == "T04"
    assert experiment.model.provider == "openai"
    assert experiment.model.model_name == "gpt-5-mini"
    assert baseline_prompt["system_instruction"] == candidate_prompt["system_instruction"]
    assert baseline_prompt["user_prompt"] != candidate_prompt["user_prompt"]
    assert "추가 output constraint" in candidate_prompt["user_prompt"]
    assert experiment.candidate_variants[0].lever_id == "output_constraint"


def test_strict_json_output_constraint_variant_changes_only_slot_guidance_block() -> None:
    experiment = get_experiment_definition("EXP-28")
    baseline_prompt = build_prompt_package(DEFAULT_TEMPLATE_SPEC_ROOT, experiment.scenario, experiment.baseline_variant)
    candidate_prompt = build_prompt_package(DEFAULT_TEMPLATE_SPEC_ROOT, experiment.scenario, experiment.candidate_variants[0])

    assert experiment.scenario.template_id == "T02"
    assert experiment.model.provider == "google"
    assert experiment.model.model_name == "models/gemini-2.5-flash"
    assert baseline_prompt["system_instruction"] == candidate_prompt["system_instruction"]
    assert baseline_prompt["user_prompt"] != candidate_prompt["user_prompt"]
    assert "마지막 중괄호까지 완결된 JSON" in candidate_prompt["user_prompt"]
    assert experiment.candidate_variants[0].lever_id == "output_constraint"


def test_local_exaone_region_repeat_variant_changes_only_slot_guidance_block() -> None:
    experiment = get_experiment_definition("EXP-31")
    baseline_prompt = build_prompt_package(DEFAULT_TEMPLATE_SPEC_ROOT, experiment.scenario, experiment.baseline_variant)
    candidate_prompt = build_prompt_package(DEFAULT_TEMPLATE_SPEC_ROOT, experiment.scenario, experiment.candidate_variants[0])

    assert experiment.scenario.template_id == "T02"
    assert experiment.model.provider == "ollama"
    assert experiment.model.model_name == "exaone3.5:7.8b"
    assert baseline_prompt["system_instruction"] == candidate_prompt["system_instruction"]
    assert baseline_prompt["user_prompt"] != candidate_prompt["user_prompt"]
    assert "총 2회 이하" in candidate_prompt["user_prompt"]
    assert experiment.candidate_variants[0].lever_id == "region_repeat_constraint"


def test_local_exaone_output_constraint_variant_changes_only_slot_guidance_block() -> None:
    experiment = get_experiment_definition("EXP-33")
    baseline_prompt = build_prompt_package(DEFAULT_TEMPLATE_SPEC_ROOT, experiment.scenario, experiment.baseline_variant)
    candidate_prompt = build_prompt_package(DEFAULT_TEMPLATE_SPEC_ROOT, experiment.scenario, experiment.candidate_variants[0])

    assert experiment.scenario.template_id == "T02"
    assert experiment.model.provider == "ollama"
    assert experiment.model.model_name == "exaone3.5:7.8b"
    assert baseline_prompt["system_instruction"] == candidate_prompt["system_instruction"]
    assert baseline_prompt["user_prompt"] != candidate_prompt["user_prompt"]
    assert "hashtags는 정확히 5개" in candidate_prompt["user_prompt"]
    assert "이모지" in candidate_prompt["user_prompt"]
    assert experiment.candidate_variants[0].lever_id == "output_constraint"


def test_local_exaone_hashtag_region_budget_variant_changes_only_slot_guidance_block() -> None:
    experiment = get_experiment_definition("EXP-35")
    baseline_prompt = build_prompt_package(DEFAULT_TEMPLATE_SPEC_ROOT, experiment.scenario, experiment.baseline_variant)
    candidate_prompt = build_prompt_package(DEFAULT_TEMPLATE_SPEC_ROOT, experiment.scenario, experiment.candidate_variants[0])

    assert experiment.scenario.template_id == "T02"
    assert experiment.model.provider == "ollama"
    assert experiment.model.model_name == "exaone3.5:7.8b"
    assert baseline_prompt["system_instruction"] == candidate_prompt["system_instruction"]
    assert baseline_prompt["user_prompt"] != candidate_prompt["user_prompt"]
    assert "captions 3개에는 지역명을 넣지 마세요" in candidate_prompt["user_prompt"]
    assert "지역명이 들어간 해시태그는 최대 1개" in candidate_prompt["user_prompt"]
    assert experiment.candidate_variants[0].lever_id == "hashtag_region_budget"


def test_scene_plan_preview_surfaces_b_grade_text_budget_pressure() -> None:
    experiment = get_experiment_definition("EXP-15")
    bundle = build_deterministic_reference_bundle(Path(DEFAULT_TEMPLATE_SPEC_ROOT), experiment.scenario)
    scene_plan = build_scene_plan_preview(Path(DEFAULT_TEMPLATE_SPEC_ROOT), experiment.scenario, bundle)
    metrics = evaluate_scene_plan_preview(Path(DEFAULT_TEMPLATE_SPEC_ROOT), experiment.scenario, bundle)

    assert scene_plan["templateId"] == "T02"
    assert scene_plan["sceneCount"] == 4
    assert metrics["max_text_per_scene"] == 16
    assert metrics["over_limit_scene_ids"]
    assert metrics["closing_cta_actionable"] is True


def test_scene_plan_preview_for_review_template_uses_three_scenes() -> None:
    experiment = get_experiment_definition("EXP-16")
    bundle = build_deterministic_reference_bundle(Path(DEFAULT_TEMPLATE_SPEC_ROOT), experiment.scenario)
    scene_plan = build_scene_plan_preview(Path(DEFAULT_TEMPLATE_SPEC_ROOT), experiment.scenario, bundle)

    assert scene_plan["templateId"] == "T04"
    assert scene_plan["sceneCount"] == 3
    assert [scene["textRole"] for scene in scene_plan["scenes"]] == ["review_quote", "product_name", "cta"]


def test_reservation_is_treated_as_action_keyword() -> None:
    experiment = get_experiment_definition("EXP-15")
    context_root = Path(DEFAULT_TEMPLATE_SPEC_ROOT)
    from services.worker.experiments.prompt_harness import load_experiment_context

    loaded = load_experiment_context(context_root, experiment.scenario)
    bundle = {
        "hookText": "규카츠 오늘만 특가",
        "captions": ["성수동 규카츠 할인", "오늘만 특가", "지금 예약하고 가기"],
        "hashtags": ["#성수동맛집", "#규카츠맛집", "#오늘만할인", "#서울숲맛집", "#퇴근후한잔"],
        "ctaText": "지금 바로 예약하기",
        "sceneText": {
            "hook": "규카츠 오늘만 특가",
            "benefit": "오늘만 특가 할인",
            "urgency": "재고 소진 시 종료",
            "cta": "지금 바로 예약!",
        },
        "subText": {
            "hook": "겉바속촉 규카츠",
            "benefit": "맥주까지 찰떡",
            "urgency": "오늘 지나면 끝",
            "cta": "성수동에서 만나요",
        },
    }

    evaluation = evaluate_copy_bundle(bundle, experiment.scenario, loaded["template"], loaded["copy_rule"])
    metrics = evaluate_scene_plan_preview(context_root, experiment.scenario, bundle)

    assert "ctaText lacks explicit action keyword" not in evaluation["failed_checks"]
    assert metrics["closing_cta_actionable"] is True


def test_save_is_treated_as_action_keyword() -> None:
    experiment = get_experiment_definition("EXP-19")
    context_root = Path(DEFAULT_TEMPLATE_SPEC_ROOT)
    from services.worker.experiments.prompt_harness import load_experiment_context

    loaded = load_experiment_context(context_root, experiment.scenario)
    bundle = {
        "hookText": "인생 라멘 발견",
        "captions": ["성수동 라멘 맛집", "오늘 저장해두기", "이번 주말 방문하기"],
        "hashtags": ["#성수동맛집", "#라멘맛집", "#서울숲맛집", "#인생라멘", "#먹스타그램"],
        "ctaText": "지금 바로 저장하기",
        "sceneText": {
            "review_quote": "국물 한 입에 극락 감",
            "product_name": "육즙 폭발 인생 라멘",
            "cta": "지금 바로 저장",
        },
        "subText": {
            "review_quote": "여기 안 가면 손해임",
            "product_name": "차슈가 녹는 찐 라멘",
            "cta": "이번 주말 방문각",
        },
    }

    evaluation = evaluate_copy_bundle(bundle, experiment.scenario, loaded["template"], loaded["copy_rule"])
    metrics = evaluate_scene_plan_preview(context_root, experiment.scenario, bundle)

    assert "ctaText lacks explicit action keyword" not in evaluation["failed_checks"]
    assert metrics["closing_cta_actionable"] is True


def test_model_comparison_definition_fixes_prompt_and_varies_models_only() -> None:
    experiment = get_model_comparison_definition("EXP-23")
    prompt = build_prompt_package(DEFAULT_TEMPLATE_SPEC_ROOT, experiment.scenario, experiment.prompt_variant)

    assert experiment.scenario.template_id == "T02"
    assert experiment.scenario.purpose == "promotion"
    assert experiment.prompt_variant.variant_id == "fixed_b_grade_tone_guidance"
    assert len(experiment.models) == 3
    assert {model.provider for model in experiment.models} == {"google", "openai"}
    assert '"benefit": "string"' in prompt["user_prompt"]
    assert '"urgency": "string"' in prompt["user_prompt"]


def test_provider_default_api_key_env_is_resolved_without_repo_side_effects() -> None:
    assert resolve_api_key_env("google") == "GEMINI_API_KEY"
    assert resolve_api_key_env("openai") == "OPENAI_API_KEY"
    assert resolve_api_key_env("huggingface") == "HF_TOKEN"
    assert resolve_api_key_env("ollama") == "OLLAMA_HOST"


def test_google_family_model_comparison_definition_uses_multiple_google_models() -> None:
    experiment = get_model_comparison_definition("EXP-24")

    assert experiment.scenario.template_id == "T02"
    assert len(experiment.models) == 3
    assert {model.provider for model in experiment.models} == {"google"}
    assert any(model.model_name == "models/gemini-2.5-flash" for model in experiment.models)


def test_openai_available_model_comparison_definition_matches_account_limited_models() -> None:
    experiment = get_model_comparison_definition("EXP-25")

    assert experiment.scenario.template_id == "T02"
    assert [model.model_name for model in experiment.models] == [
        "models/gemma-4-31b-it",
        "gpt-5-mini",
        "gpt-5-nano",
    ]


def test_review_model_comparison_definition_targets_t04_with_two_models() -> None:
    experiment = get_model_comparison_definition("EXP-26")

    assert experiment.scenario.template_id == "T04"
    assert experiment.scenario.purpose == "review"
    assert experiment.prompt_variant.variant_id == "fixed_review_region_repeat_guidance"
    assert [model.model_name for model in experiment.models] == [
        "models/gemma-4-31b-it",
        "gpt-5-mini",
    ]


def test_review_surface_lock_model_comparison_definition_targets_current_prompt() -> None:
    experiment = get_model_comparison_definition("EXP-223")

    assert experiment.scenario.template_id == "T04"
    assert experiment.scenario.purpose == "review"
    assert experiment.prompt_variant.variant_id == "fixed_review_surface_locked_exact_region_anchor"
    assert [model.model_name for model in experiment.models] == [
        "models/gemma-4-31b-it",
        "gpt-5-mini",
    ]


def test_huggingface_open_source_model_comparison_definition_uses_text_models() -> None:
    experiment = get_model_comparison_definition("EXP-29")

    assert experiment.scenario.template_id == "T02"
    assert all(model.provider == "huggingface" for model in experiment.models)
    assert [model.model_name for model in experiment.models] == [
        "Qwen/Qwen3-4B-Instruct-2507",
        "Qwen/Qwen3.5-27B",
    ]
    assert "text-only" in experiment.prompt_variant.description


def test_local_ollama_model_comparison_definition_uses_installed_local_models() -> None:
    experiment = get_model_comparison_definition("EXP-30")

    assert experiment.scenario.template_id == "T02"
    assert experiment.scenario.style_id == "b_grade_fun"
    assert all(model.provider == "ollama" for model in experiment.models)
    assert [model.model_name for model in experiment.models] == [
        "gemma3:12b",
        "exaone3.5:7.8b",
        "llama3.1:8b",
        "mistral-small3.1:24b-instruct-2503-q4_K_M",
    ]


def test_korean_integrity_detects_obvious_mojibake_marker() -> None:
    metrics = evaluate_korean_integrity(
        {
            "hookText": "성수동 Ã규카츠",
            "captions": ["오늘만 할인"],
            "hashtags": ["#성수동맛집"],
            "ctaText": "지금 방문",
        }
    )

    assert metrics["is_suspected_broken"] is True
    assert "Ã" in metrics["suspicious_markers"]
