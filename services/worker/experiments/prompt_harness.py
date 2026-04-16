from __future__ import annotations

import base64
import json
import os
import re
import socket
import time
import urllib.error
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

from services.common.env_loader import load_repo_env
from services.worker.adapters.template_loader import load_copy_rule, load_style, load_template
from services.worker.pipelines.generation import _build_copy_bundle
from services.worker.planning.scene_plan import build_scene_plan


load_repo_env()


ROOT_DIR = Path(__file__).resolve().parents[3]
DEFAULT_TEMPLATE_SPEC_ROOT = ROOT_DIR / "packages" / "template-spec"
DEFAULT_ARTIFACT_ROOT = ROOT_DIR / "docs" / "experiments" / "artifacts"
REGION_ACTION_KEYWORDS = ("방문", "들러", "오세요", "와보세요", "만나보세요", "주문", "체크", "확인", "예약", "저장")
AUDIENCE_CONTEXT_KEYWORDS = ("산책", "데이트", "오후", "여유", "나들이")
MOJIBAKE_MARKERS = ("�", "Ã", "ì", "ë", "ê", "ðŸ")
OLLAMA_DEFAULT_HOST = "http://localhost:11434"
DETAIL_LOCATION_GENERIC_TOKENS = ("근처", "인근", "부근", "근방", "주변", "앞", "옆")
LOCATION_POLICY_SURFACES = ("hookText", "ctaText", "captions", "hashtags", "sceneText", "subText")


def sanitize_error_message(message: str) -> str:
    sanitized = re.sub(r"sk-[A-Za-z0-9_\-]+", "sk-***", message)
    sanitized = re.sub(r"hf_[A-Za-z0-9]+", "hf_***", sanitized)
    sanitized = re.sub(r"(Incorrect API key provided:\s*)([^\.\n]+)", r"\1***", sanitized)
    return sanitized


@dataclass(frozen=True)
class ScenarioSpec:
    scenario_id: str
    business_type: str
    purpose: str
    style_id: str
    region_name: str
    detail_location: str | None
    template_id: str
    asset_paths: tuple[Path, ...]
    quick_options: dict[str, Any]


@dataclass(frozen=True)
class PromptVariant:
    variant_id: str
    lever_id: str
    changed_field: str
    description: str
    role_instruction: str
    slot_guidance: str
    audience_guidance: str = "추가 지시 없음. 스타일 기본값만 따르세요."


@dataclass(frozen=True)
class ModelConfig:
    provider: str
    model_name: str
    temperature: float = 0.2
    top_p: float = 0.9
    max_output_tokens: int = 1200


@dataclass(frozen=True)
class ExperimentDefinition:
    experiment_id: str
    experiment_title: str
    objective: str
    scenario: ScenarioSpec
    model: ModelConfig
    baseline_variant: PromptVariant
    candidate_variants: tuple[PromptVariant, ...]


@dataclass(frozen=True)
class ModelComparisonDefinition:
    experiment_id: str
    experiment_title: str
    objective: str
    scenario: ScenarioSpec
    prompt_variant: PromptVariant
    models: tuple[ModelConfig, ...]


def get_default_scenario() -> ScenarioSpec:
    return ScenarioSpec(
        scenario_id="scenario-cafe-new-menu-fixed",
        business_type="cafe",
        purpose="new_menu",
        style_id="friendly",
        region_name="성수동",
        detail_location="서울숲 근처",
        template_id="T01",
        asset_paths=(
            ROOT_DIR / "samples" / "input" / "cafe" / "cafe-latte-01.png",
            ROOT_DIR / "samples" / "input" / "cafe" / "cafe-dessert-02.png",
        ),
        quick_options={
            "highlightPrice": False,
            "shorterCopy": False,
            "emphasizeRegion": True,
        },
    )


def get_new_menu_minimal_region_anchor_scenario() -> ScenarioSpec:
    return ScenarioSpec(
        scenario_id="scenario-cafe-new-menu-fixed-region-off",
        business_type="cafe",
        purpose="new_menu",
        style_id="friendly",
        region_name="성수동",
        detail_location="서울숲 근처",
        template_id="T01",
        asset_paths=(
            ROOT_DIR / "samples" / "input" / "cafe" / "cafe-latte-01.png",
            ROOT_DIR / "samples" / "input" / "cafe" / "cafe-dessert-02.png",
        ),
        quick_options={
            "highlightPrice": False,
            "shorterCopy": False,
            "emphasizeRegion": False,
        },
    )


def get_new_menu_shorter_copy_minimal_region_anchor_scenario() -> ScenarioSpec:
    return ScenarioSpec(
        scenario_id="scenario-cafe-new-menu-fixed-region-off-shorter-copy",
        business_type="cafe",
        purpose="new_menu",
        style_id="friendly",
        region_name="성수동",
        detail_location="서울숲 근처",
        template_id="T01",
        asset_paths=(
            ROOT_DIR / "samples" / "input" / "cafe" / "cafe-latte-01.png",
            ROOT_DIR / "samples" / "input" / "cafe" / "cafe-dessert-02.png",
        ),
        quick_options={
            "highlightPrice": False,
            "shorterCopy": True,
            "emphasizeRegion": False,
        },
    )


def get_new_menu_highlight_price_minimal_region_anchor_scenario() -> ScenarioSpec:
    return ScenarioSpec(
        scenario_id="scenario-cafe-new-menu-fixed-region-off-highlight-price",
        business_type="cafe",
        purpose="new_menu",
        style_id="friendly",
        region_name="성수동",
        detail_location="서울숲 근처",
        template_id="T01",
        asset_paths=(
            ROOT_DIR / "samples" / "input" / "cafe" / "cafe-latte-01.png",
            ROOT_DIR / "samples" / "input" / "cafe" / "cafe-dessert-02.png",
        ),
        quick_options={
            "highlightPrice": True,
            "shorterCopy": False,
            "emphasizeRegion": False,
        },
    )


def get_new_menu_highlight_price_shorter_copy_minimal_region_anchor_scenario() -> ScenarioSpec:
    return ScenarioSpec(
        scenario_id="scenario-cafe-new-menu-fixed-region-off-highlight-price-shorter-copy",
        business_type="cafe",
        purpose="new_menu",
        style_id="friendly",
        region_name="성수동",
        detail_location="서울숲 근처",
        template_id="T01",
        asset_paths=(
            ROOT_DIR / "samples" / "input" / "cafe" / "cafe-latte-01.png",
            ROOT_DIR / "samples" / "input" / "cafe" / "cafe-dessert-02.png",
        ),
        quick_options={
            "highlightPrice": True,
            "shorterCopy": True,
            "emphasizeRegion": False,
        },
    )


def get_new_menu_shorter_copy_region_anchor_scenario() -> ScenarioSpec:
    return ScenarioSpec(
        scenario_id="scenario-cafe-new-menu-fixed-shorter-copy",
        business_type="cafe",
        purpose="new_menu",
        style_id="friendly",
        region_name="성수동",
        detail_location="서울숲 근처",
        template_id="T01",
        asset_paths=(
            ROOT_DIR / "samples" / "input" / "cafe" / "cafe-latte-01.png",
            ROOT_DIR / "samples" / "input" / "cafe" / "cafe-dessert-02.png",
        ),
        quick_options={
            "highlightPrice": False,
            "shorterCopy": True,
            "emphasizeRegion": True,
        },
    )


def get_new_menu_highlight_price_region_anchor_scenario() -> ScenarioSpec:
    return ScenarioSpec(
        scenario_id="scenario-cafe-new-menu-fixed-highlight-price",
        business_type="cafe",
        purpose="new_menu",
        style_id="friendly",
        region_name="성수동",
        detail_location="서울숲 근처",
        template_id="T01",
        asset_paths=(
            ROOT_DIR / "samples" / "input" / "cafe" / "cafe-latte-01.png",
            ROOT_DIR / "samples" / "input" / "cafe" / "cafe-dessert-02.png",
        ),
        quick_options={
            "highlightPrice": True,
            "shorterCopy": False,
            "emphasizeRegion": True,
        },
    )


def get_new_menu_highlight_price_shorter_copy_region_anchor_scenario() -> ScenarioSpec:
    return ScenarioSpec(
        scenario_id="scenario-cafe-new-menu-fixed-highlight-price-shorter-copy",
        business_type="cafe",
        purpose="new_menu",
        style_id="friendly",
        region_name="성수동",
        detail_location="서울숲 근처",
        template_id="T01",
        asset_paths=(
            ROOT_DIR / "samples" / "input" / "cafe" / "cafe-latte-01.png",
            ROOT_DIR / "samples" / "input" / "cafe" / "cafe-dessert-02.png",
        ),
        quick_options={
            "highlightPrice": True,
            "shorterCopy": True,
            "emphasizeRegion": True,
        },
    )


def get_service_aligned_bgrade_scenario() -> ScenarioSpec:
    sample_root = ROOT_DIR / "docs" / "sample"
    return ScenarioSpec(
        scenario_id="scenario-restaurant-promotion-b-grade-real-photo",
        business_type="restaurant",
        purpose="promotion",
        style_id="b_grade_fun",
        region_name="성수동",
        detail_location="서울숲 근처",
        template_id="T02",
        asset_paths=(
            sample_root / "음식사진샘플(규카츠).jpg",
            sample_root / "음식사진샘플(맥주).jpg",
        ),
        quick_options={
            "highlightPrice": True,
            "shorterCopy": True,
            "emphasizeRegion": False,
        },
    )


def get_service_aligned_bgrade_highlight_price_off_scenario() -> ScenarioSpec:
    sample_root = ROOT_DIR / "docs" / "sample"
    return ScenarioSpec(
        scenario_id="scenario-restaurant-promotion-b-grade-real-photo-highlight-price-off",
        business_type="restaurant",
        purpose="promotion",
        style_id="b_grade_fun",
        region_name="성수동",
        detail_location="서울숲 근처",
        template_id="T02",
        asset_paths=(
            sample_root / "음식사진샘플(규카츠).jpg",
            sample_root / "음식사진샘플(맥주).jpg",
        ),
        quick_options={
            "highlightPrice": False,
            "shorterCopy": True,
            "emphasizeRegion": False,
        },
    )


def get_service_aligned_bgrade_shorter_copy_off_scenario() -> ScenarioSpec:
    sample_root = ROOT_DIR / "docs" / "sample"
    return ScenarioSpec(
        scenario_id="scenario-restaurant-promotion-b-grade-real-photo-shorter-copy-off",
        business_type="restaurant",
        purpose="promotion",
        style_id="b_grade_fun",
        region_name="성수동",
        detail_location="서울숲 근처",
        template_id="T02",
        asset_paths=(
            sample_root / "음식사진샘플(규카츠).jpg",
            sample_root / "음식사진샘플(맥주).jpg",
        ),
        quick_options={
            "highlightPrice": True,
            "shorterCopy": False,
            "emphasizeRegion": False,
        },
    )


def get_service_aligned_bgrade_highlight_price_off_shorter_copy_off_scenario() -> ScenarioSpec:
    sample_root = ROOT_DIR / "docs" / "sample"
    return ScenarioSpec(
        scenario_id="scenario-restaurant-promotion-b-grade-real-photo-highlight-price-off-shorter-copy-off",
        business_type="restaurant",
        purpose="promotion",
        style_id="b_grade_fun",
        region_name="성수동",
        detail_location="서울숲 근처",
        template_id="T02",
        asset_paths=(
            sample_root / "음식사진샘플(규카츠).jpg",
            sample_root / "음식사진샘플(맥주).jpg",
        ),
        quick_options={
            "highlightPrice": False,
            "shorterCopy": False,
            "emphasizeRegion": False,
        },
    )


def get_service_aligned_bgrade_highlight_price_off_shorter_copy_off_region_emphasis_scenario() -> ScenarioSpec:
    sample_root = ROOT_DIR / "docs" / "sample"
    return ScenarioSpec(
        scenario_id="scenario-restaurant-promotion-b-grade-real-photo-highlight-price-off-shorter-copy-off-region-emphasis",
        business_type="restaurant",
        purpose="promotion",
        style_id="b_grade_fun",
        region_name="성수동",
        detail_location="서울숲 근처",
        template_id="T02",
        asset_paths=(
            sample_root / "음식사진샘플(규카츠).jpg",
            sample_root / "음식사진샘플(맥주).jpg",
        ),
        quick_options={
            "highlightPrice": False,
            "shorterCopy": False,
            "emphasizeRegion": True,
        },
    )


def get_service_aligned_bgrade_highlight_price_off_region_emphasis_scenario() -> ScenarioSpec:
    sample_root = ROOT_DIR / "docs" / "sample"
    return ScenarioSpec(
        scenario_id="scenario-restaurant-promotion-b-grade-real-photo-highlight-price-off-region-emphasis",
        business_type="restaurant",
        purpose="promotion",
        style_id="b_grade_fun",
        region_name="성수동",
        detail_location="서울숲 근처",
        template_id="T02",
        asset_paths=(
            sample_root / "음식사진샘플(규카츠).jpg",
            sample_root / "음식사진샘플(맥주).jpg",
        ),
        quick_options={
            "highlightPrice": False,
            "shorterCopy": True,
            "emphasizeRegion": True,
        },
    )


def get_service_aligned_bgrade_shorter_copy_off_region_emphasis_scenario() -> ScenarioSpec:
    sample_root = ROOT_DIR / "docs" / "sample"
    return ScenarioSpec(
        scenario_id="scenario-restaurant-promotion-b-grade-real-photo-shorter-copy-off-region-emphasis",
        business_type="restaurant",
        purpose="promotion",
        style_id="b_grade_fun",
        region_name="성수동",
        detail_location="서울숲 근처",
        template_id="T02",
        asset_paths=(
            sample_root / "음식사진샘플(규카츠).jpg",
            sample_root / "음식사진샘플(맥주).jpg",
        ),
        quick_options={
            "highlightPrice": True,
            "shorterCopy": False,
            "emphasizeRegion": True,
        },
    )


def get_service_aligned_bgrade_region_emphasis_scenario() -> ScenarioSpec:
    sample_root = ROOT_DIR / "docs" / "sample"
    return ScenarioSpec(
        scenario_id="scenario-restaurant-promotion-b-grade-real-photo-region-emphasis",
        business_type="restaurant",
        purpose="promotion",
        style_id="b_grade_fun",
        region_name="성수동",
        detail_location="서울숲 근처",
        template_id="T02",
        asset_paths=(
            sample_root / "음식사진샘플(규카츠).jpg",
            sample_root / "음식사진샘플(맥주).jpg",
        ),
        quick_options={
            "highlightPrice": True,
            "shorterCopy": True,
            "emphasizeRegion": True,
        },
    )


def get_service_aligned_bgrade_review_scenario() -> ScenarioSpec:
    sample_root = ROOT_DIR / "docs" / "sample"
    return ScenarioSpec(
        scenario_id="scenario-restaurant-review-b-grade-real-photo",
        business_type="restaurant",
        purpose="review",
        style_id="b_grade_fun",
        region_name="성수동",
        detail_location="서울숲 근처",
        template_id="T04",
        asset_paths=(
            sample_root / "음식사진샘플(라멘).jpg",
        ),
        quick_options={
            "highlightPrice": False,
            "shorterCopy": True,
            "emphasizeRegion": False,
        },
    )


def get_service_aligned_bgrade_review_shorter_copy_off_scenario() -> ScenarioSpec:
    sample_root = ROOT_DIR / "docs" / "sample"
    return ScenarioSpec(
        scenario_id="scenario-restaurant-review-b-grade-real-photo-shorter-copy-off",
        business_type="restaurant",
        purpose="review",
        style_id="b_grade_fun",
        region_name="성수동",
        detail_location="서울숲 근처",
        template_id="T04",
        asset_paths=(
            sample_root / "음식사진샘플(규카츠).jpg",
            sample_root / "음식사진샘플(라멘).jpg",
        ),
        quick_options={
            "highlightPrice": False,
            "shorterCopy": False,
            "emphasizeRegion": False,
        },
    )


def get_service_aligned_bgrade_review_highlight_price_shorter_copy_off_scenario() -> ScenarioSpec:
    sample_root = ROOT_DIR / "docs" / "sample"
    return ScenarioSpec(
        scenario_id="scenario-restaurant-review-b-grade-real-photo-highlight-price-shorter-copy-off",
        business_type="restaurant",
        purpose="review",
        style_id="b_grade_fun",
        region_name="성수동",
        detail_location="서울숲 근처",
        template_id="T04",
        asset_paths=(
            sample_root / "음식사진샘플(규카츠).jpg",
            sample_root / "음식사진샘플(라멘).jpg",
        ),
        quick_options={
            "highlightPrice": True,
            "shorterCopy": False,
            "emphasizeRegion": False,
        },
    )


def get_service_aligned_bgrade_review_highlight_price_scenario() -> ScenarioSpec:
    sample_root = ROOT_DIR / "docs" / "sample"
    return ScenarioSpec(
        scenario_id="scenario-restaurant-review-b-grade-real-photo-highlight-price",
        business_type="restaurant",
        purpose="review",
        style_id="b_grade_fun",
        region_name="성수동",
        detail_location="서울숲 근처",
        template_id="T04",
        asset_paths=(
            sample_root / "음식사진샘플(규카츠).jpg",
            sample_root / "음식사진샘플(라멘).jpg",
        ),
        quick_options={
            "highlightPrice": True,
            "shorterCopy": True,
            "emphasizeRegion": False,
        },
    )


def get_service_aligned_bgrade_review_region_emphasis_scenario() -> ScenarioSpec:
    sample_root = ROOT_DIR / "docs" / "sample"
    return ScenarioSpec(
        scenario_id="scenario-restaurant-review-b-grade-real-photo-region-emphasis",
        business_type="restaurant",
        purpose="review",
        style_id="b_grade_fun",
        region_name="성수동",
        detail_location="서울숲 근처",
        template_id="T04",
        asset_paths=(
            sample_root / "음식사진샘플(라멘).jpg",
        ),
        quick_options={
            "highlightPrice": False,
            "shorterCopy": True,
            "emphasizeRegion": True,
        },
    )


def get_service_aligned_bgrade_review_shorter_copy_off_region_emphasis_scenario() -> ScenarioSpec:
    sample_root = ROOT_DIR / "docs" / "sample"
    return ScenarioSpec(
        scenario_id="scenario-restaurant-review-b-grade-real-photo-shorter-copy-off-region-emphasis",
        business_type="restaurant",
        purpose="review",
        style_id="b_grade_fun",
        region_name="성수동",
        detail_location="서울숲 근처",
        template_id="T04",
        asset_paths=(
            sample_root / "음식사진샘플(규카츠).jpg",
            sample_root / "음식사진샘플(라멘).jpg",
        ),
        quick_options={
            "highlightPrice": False,
            "shorterCopy": False,
            "emphasizeRegion": True,
        },
    )


def get_service_aligned_bgrade_review_highlight_price_shorter_copy_off_region_emphasis_scenario() -> ScenarioSpec:
    sample_root = ROOT_DIR / "docs" / "sample"
    return ScenarioSpec(
        scenario_id="scenario-restaurant-review-b-grade-real-photo-highlight-price-shorter-copy-off-region-emphasis",
        business_type="restaurant",
        purpose="review",
        style_id="b_grade_fun",
        region_name="성수동",
        detail_location="서울숲 근처",
        template_id="T04",
        asset_paths=(
            sample_root / "음식사진샘플(규카츠).jpg",
            sample_root / "음식사진샘플(라멘).jpg",
        ),
        quick_options={
            "highlightPrice": True,
            "shorterCopy": False,
            "emphasizeRegion": True,
        },
    )


def get_service_aligned_bgrade_review_highlight_price_region_emphasis_scenario() -> ScenarioSpec:
    sample_root = ROOT_DIR / "docs" / "sample"
    return ScenarioSpec(
        scenario_id="scenario-restaurant-review-b-grade-real-photo-highlight-price-region-emphasis",
        business_type="restaurant",
        purpose="review",
        style_id="b_grade_fun",
        region_name="성수동",
        detail_location="서울숲 근처",
        template_id="T04",
        asset_paths=(
            sample_root / "음식사진샘플(규카츠).jpg",
            sample_root / "음식사진샘플(라멘).jpg",
        ),
        quick_options={
            "highlightPrice": True,
            "shorterCopy": True,
            "emphasizeRegion": True,
        },
    )


def get_experiment_definition(experiment_id: str = "EXP-01") -> ExperimentDefinition:
    common_role = "당신은 한국 지역 소상공인용 SNS 광고 카피를 구조화된 슬롯에 맞춰 작성하는 한국어 카피라이터입니다."
    baseline_variant = PromptVariant(
        variant_id="baseline_prompt_compact_slot_guidance",
        lever_id="baseline",
        changed_field="none",
        description="슬롯 이름만 간단히 설명하는 공통 baseline prompt입니다.",
        role_instruction=common_role,
        slot_guidance=(
            "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
            "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요."
        ),
    )

    if experiment_id == "EXP-01":
        explicit_slot_variant = PromptVariant(
            variant_id="explicit_slot_objective_guidance",
            lever_id="slot_instruction",
            changed_field="slot_guidance",
            description="슬롯별 역할을 한 줄씩 명시해 sceneText 품질 차이를 확인하는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText 작성 기준:\n"
                "- hook: 첫 장면에서 시선을 잡는 한 줄로 작성하세요.\n"
                "- product_name: 무엇을 홍보하는지 바로 알 수 있게 작성하세요.\n"
                "- difference: 왜 주목해야 하는지 드러나는 차별점이나 이점을 작성하세요.\n"
                "- cta: 바로 들르거나 방문하고 싶게 만드는 행동 유도로 작성하세요.\n"
                "- subText: 같은 role의 primary 문장을 그대로 반복하지 말고, 보조 설명이나 맥락을 덧붙이세요."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-01",
            experiment_title="Gemma 4 Prompt Lever Experiment - Slot Guidance",
            objective="Gemma 4에서 슬롯 지시 방식을 더 구체화했을 때 sceneText와 CTA 품질이 baseline 대비 개선되는지 확인합니다.",
            scenario=get_default_scenario(),
            model=ModelConfig(provider="google", model_name="models/gemma-4-31b-it"),
            baseline_variant=baseline_variant,
            candidate_variants=(explicit_slot_variant,),
        )

    if experiment_id == "EXP-02":
        audience_tone_variant = PromptVariant(
            variant_id="explicit_target_audience_guidance",
            lever_id="audience_tone",
            changed_field="audience_guidance",
            description="타깃 고객 상황과 말투 제한을 추가해 후킹과 캡션의 맥락 변화를 확인하는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=baseline_variant.slot_guidance,
            audience_guidance=(
                "타깃 고객은 서울숲 근처를 산책하거나 데이트 중인 20~30대 방문객입니다.\n"
                "톤은 친근하고 가볍게 권하되, 과한 감탄사나 오글거리는 표현은 피하세요.\n"
                "hook과 captions 중 최소 1개에는 산책, 데이트, 오후 여유 같은 고객 상황 맥락을 자연스럽게 녹여 주세요."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-02",
            experiment_title="Gemma 4 Prompt Lever Experiment - Audience/Tone Guidance",
            objective="같은 baseline prompt에서 타깃 고객/톤 지시를 추가했을 때 hook과 captions 맥락이 더 구체화되는지 확인합니다.",
            scenario=get_default_scenario(),
            model=ModelConfig(provider="google", model_name="models/gemma-4-31b-it"),
            baseline_variant=baseline_variant,
            candidate_variants=(audience_tone_variant,),
        )

    if experiment_id == "EXP-15":
        bgrade_tone_variant = PromptVariant(
            variant_id="explicit_b_grade_tone_guidance",
            lever_id="b_grade_tone",
            changed_field="audience_guidance",
            description="B급 감성 톤 가이드를 추가해 T02 프로모션 카피가 더 짧고 직접적으로 바뀌는지 확인하는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=baseline_variant.slot_guidance,
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "hook, benefit, urgency, cta는 각 장면에서 바로 읽히도록 짧고 직접적으로 쓰세요.\n"
                "추상 표현인 '분위기를 보여드립니다', '구성했습니다' 같은 문장은 피하고, 혜택·기간감·행동 단어를 앞쪽에 배치하세요."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-15",
            experiment_title="Gemma 4 Prompt Lever Experiment - Service-Aligned B-Grade Tone",
            objective="서비스 본선 시나리오(T02 promotion, b_grade_fun, 실제 음식 사진)에서 B급 톤 가이드 한 가지가 scene plan 길이와 직접성에 미치는 영향을 확인합니다.",
            scenario=get_service_aligned_bgrade_scenario(),
            model=ModelConfig(provider="google", model_name="models/gemma-4-31b-it"),
            baseline_variant=baseline_variant,
            candidate_variants=(bgrade_tone_variant,),
        )

    if experiment_id == "EXP-16":
        bgrade_review_tone_variant = PromptVariant(
            variant_id="explicit_b_grade_review_tone_guidance",
            lever_id="b_grade_tone",
            changed_field="audience_guidance",
            description="B급 감성 리뷰 톤 가이드를 추가해 T04 후기형 카피가 더 짧고 한줄 후기답게 바뀌는지 확인하는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=baseline_variant.slot_guidance,
            audience_guidance=(
                "타깃 고객은 성수동에서 믿고 갈 한 끼를 찾는 20~30대 방문객입니다.\n"
                "B급 감성 리뷰는 허세가 아니라 친구가 바로 보내는 한 줄 제보처럼 들려야 합니다.\n"
                "review_quote는 실제 반응처럼 짧고 말맛 있게 쓰고, product_name은 메뉴 장점을 한 번에 보이게 쓰세요.\n"
                "cta는 과장된 감탄보다 저장, 방문, 재방문 같은 행동 단어를 앞쪽에 두고 짧게 마무리하세요."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-16",
            experiment_title="Gemma 4 Prompt Lever Experiment - Service-Aligned B-Grade Review Tone",
            objective="서비스 본선 시나리오(T04 review, b_grade_fun, 실제 음식 사진)에서 B급 리뷰 톤 가이드 한 가지가 후기형 scene plan의 직접성과 길이에 미치는 영향을 확인합니다.",
            scenario=get_service_aligned_bgrade_review_scenario(),
            model=ModelConfig(provider="google", model_name="models/gemma-4-31b-it"),
            baseline_variant=baseline_variant,
            candidate_variants=(bgrade_review_tone_variant,),
        )

    if experiment_id == "EXP-17":
        review_length_cap_variant = PromptVariant(
            variant_id="explicit_review_slot_length_cap",
            lever_id="review_slot_length_cap",
            changed_field="slot_guidance",
            description="T04 후기형에서 slot별 길이 제한을 명시해 scene-plan 과긴 문구를 줄이는지 확인하는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText 작성 기준:\n"
                "- review_quote: 친구가 바로 보낸 한 줄 후기처럼 12자 안팎으로 짧게 쓰세요.\n"
                "- product_name: 메뉴 장점이 바로 보이게 12자 안팎으로 쓰세요.\n"
                "- cta: 저장, 방문, 재방문 같은 행동 단어를 앞쪽에 두고 10자 안팎으로 마무리하세요.\n"
                "- subText: primaryText보다 더 짧거나 같은 길이로 쓰고, 같은 문장을 반복하지 마세요."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-17",
            experiment_title="Gemma 4 Prompt Lever Experiment - Review Slot Length Cap",
            objective="서비스 본선 시나리오(T04 review, b_grade_fun, 실제 음식 사진)에서 slot 길이 제한 한 가지가 scene-plan 과긴 문구를 줄이는지 확인합니다.",
            scenario=get_service_aligned_bgrade_review_scenario(),
            model=ModelConfig(provider="google", model_name="models/gemma-4-31b-it"),
            baseline_variant=baseline_variant,
            candidate_variants=(review_length_cap_variant,),
        )

    if experiment_id == "EXP-18":
        review_region_repeat_variant = PromptVariant(
            variant_id="explicit_review_region_repeat_constraint",
            lever_id="region_repeat_constraint",
            changed_field="slot_guidance",
            description="T04 후기형에서 지역명 반복 규칙을 더 직접적으로 명시해 review 템플릿의 region repeat 초과를 줄이는지 확인하는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                "지역명은 hookText, captions, hashtags를 모두 합쳐 총 2회 이하로만 사용하세요.\n"
                "이미 해시태그에 지역명이 들어가면 본문 계열에서는 최대 1회만 더 허용됩니다.\n"
                "review_quote와 product_name에는 지역명을 억지로 반복하지 말고, 꼭 필요할 때만 한 번 쓰세요."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-18",
            experiment_title="Gemma 4 Prompt Lever Experiment - Review Region Repeat Constraint",
            objective="서비스 본선 시나리오(T04 review, b_grade_fun, 실제 음식 사진)에서 지역 반복 제약을 더 직접적으로 썼을 때 region repeat 초과가 줄어드는지 확인합니다.",
            scenario=get_service_aligned_bgrade_review_scenario(),
            model=ModelConfig(provider="google", model_name="models/gemma-4-31b-it"),
            baseline_variant=baseline_variant,
            candidate_variants=(review_region_repeat_variant,),
        )

    if experiment_id == "EXP-19":
        review_cta_strength_variant = PromptVariant(
            variant_id="explicit_review_cta_strength",
            lever_id="cta_strength",
            changed_field="slot_guidance",
            description="T04 후기형에서 CTA 행동성을 더 직접적으로 명시해 review 템플릿의 마지막 행동 유도를 강화하는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                "- cta와 ctaText는 감탄사보다 행동 단어를 먼저 두세요.\n"
                "- 저장, 방문, 확인, 예약 중 최소 하나를 반드시 포함하세요.\n"
                "- cta primary 문장은 10자 안팎으로 짧고 직접적으로 마무리하세요.\n"
                "- `가보자`, `달려가기`처럼 행동이 흐린 표현보다 `저장하기`, `방문하기`, `지금 확인`처럼 바로 이해되는 표현을 우선하세요."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-19",
            experiment_title="Gemma 4 Prompt Lever Experiment - Review CTA Strength",
            objective="서비스 본선 시나리오(T04 review, b_grade_fun, 실제 음식 사진)에서 CTA 강도 지시 한 가지가 review 템플릿의 마지막 행동 유도를 강화하는지 확인합니다.",
            scenario=get_service_aligned_bgrade_review_scenario(),
            model=ModelConfig(provider="google", model_name="models/gemma-4-31b-it"),
            baseline_variant=baseline_variant,
            candidate_variants=(review_cta_strength_variant,),
        )

    if experiment_id == "EXP-27":
        review_region_baseline_variant = PromptVariant(
            variant_id="fixed_review_region_repeat_guidance",
            lever_id="baseline",
            changed_field="none",
            description="T04 review에서 region repeat constraint만 적용한 baseline prompt입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                "지역명은 hookText, captions, hashtags를 모두 합쳐 총 2회 이하로만 사용하세요.\n"
                "이미 해시태그에 지역명이 들어가면 본문 계열에서는 최대 1회만 더 허용됩니다.\n"
                "review_quote와 product_name에는 지역명을 억지로 반복하지 말고, 꼭 필요할 때만 한 번 쓰세요."
            ),
        )
        review_render_ready_variant = PromptVariant(
            variant_id="review_render_ready_output_constraint",
            lever_id="output_constraint",
            changed_field="slot_guidance",
            description="T04 review에서 render-ready 출력을 위해 길이/반복/CTA 제약을 추가한 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                "지역명은 hookText, captions, hashtags를 모두 합쳐 총 2회 이하로만 사용하세요.\n"
                "이미 해시태그에 지역명이 들어가면 본문 계열에서는 최대 1회만 더 허용됩니다.\n"
                "review_quote와 product_name에는 지역명을 억지로 반복하지 말고, 꼭 필요할 때만 한 번 쓰세요.\n"
                "추가 output constraint:\n"
                "- review_quote primaryText는 14자 안팎으로 짧게 쓰세요.\n"
                "- product_name primaryText는 14자 안팎으로 유지하세요.\n"
                "- cta primaryText는 10자 안팎으로 쓰고, 저장/방문/확인/예약 중 하나로 시작하세요.\n"
                "- subText는 primaryText와 다른 문장으로 쓰고, 같은 표현을 반복하지 마세요."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-27",
            experiment_title="GPT-5 Mini Prompt Lever Experiment - Review Output Constraint",
            objective="T04 review, b_grade_fun, 실제 음식 사진에서 gpt-5-mini를 고정한 채 render-ready output constraint 한 가지가 scene-plan 길이/반복/CTA 안정성을 개선하는지 확인합니다.",
            scenario=get_service_aligned_bgrade_review_scenario(),
            model=ModelConfig(provider="openai", model_name="gpt-5-mini"),
            baseline_variant=review_region_baseline_variant,
            candidate_variants=(review_render_ready_variant,),
        )

    if experiment_id == "EXP-28":
        promotion_bgrade_baseline_variant = PromptVariant(
            variant_id="fixed_b_grade_tone_guidance",
            lever_id="baseline",
            changed_field="none",
            description="T02 promotion에서 B급 tone guidance만 적용한 Gemini 2.5 Flash baseline prompt입니다.",
            role_instruction=common_role,
            slot_guidance=baseline_variant.slot_guidance,
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "hook, benefit, urgency, cta는 각 장면에서 바로 읽히도록 짧고 직접적으로 쓰세요.\n"
                "추상 표현인 '분위기를 보여드립니다', '구성했습니다' 같은 문장은 피하고, 혜택·기간감·행동 단어를 앞쪽에 배치하세요."
            ),
        )
        strict_json_variant = PromptVariant(
            variant_id="strict_json_output_constraint",
            lever_id="output_constraint",
            changed_field="slot_guidance",
            description="Gemini 2.5 Flash에서 JSON 완결성을 높이기 위해 출력 형식 제약을 추가한 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                "추가 output constraint:\n"
                "- 응답은 JSON 객체 하나만 출력하세요.\n"
                "- 코드펜스, 설명문, 주석, 말머리를 절대 넣지 마세요.\n"
                "- 모든 필수 키를 정확히 한 번만 출력하고, 마지막 중괄호까지 완결된 JSON으로 끝내세요.\n"
                "- 각 string 값은 불필요하게 길게 쓰지 말고, 규칙에 맞는 최소 길이로 유지하세요."
            ),
            audience_guidance=promotion_bgrade_baseline_variant.audience_guidance,
        )
        return ExperimentDefinition(
            experiment_id="EXP-28",
            experiment_title="Gemini 2.5 Flash Prompt Lever Experiment - Strict JSON Output Constraint",
            objective="T02 promotion, b_grade_fun, 실제 음식 사진에서 Gemini 2.5 Flash를 고정한 채 strict JSON output constraint 한 가지가 format failure를 줄이는지 확인합니다.",
            scenario=get_service_aligned_bgrade_scenario(),
            model=ModelConfig(provider="google", model_name="models/gemini-2.5-flash"),
            baseline_variant=promotion_bgrade_baseline_variant,
            candidate_variants=(strict_json_variant,),
        )

    if experiment_id == "EXP-31":
        local_ollama_baseline_variant = PromptVariant(
            variant_id="fixed_b_grade_tone_guidance_local_ollama",
            lever_id="baseline",
            changed_field="none",
            description="T02 promotion에서 EXAONE 3.5 7.8B 로컬 모델에 B급 tone guidance만 적용한 baseline prompt입니다.",
            role_instruction=common_role,
            slot_guidance=baseline_variant.slot_guidance,
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "hook, benefit, urgency, cta는 각 장면에서 바로 읽히도록 짧고 직접적으로 쓰세요.\n"
                "추상 표현인 '분위기를 보여드립니다', '구성했습니다' 같은 문장은 피하고, 혜택·기간감·행동 단어를 앞쪽에 배치하세요.\n"
                "한국어 출력에서 깨짐(�, 이상한 라틴 문자 조합)이 생기지 않도록 자연스러운 한국어 문장만 사용하세요."
            ),
        )
        promotion_region_repeat_variant = PromptVariant(
            variant_id="promotion_region_repeat_constraint_local_exaone",
            lever_id="region_repeat_constraint",
            changed_field="slot_guidance",
            description="T02 promotion에서 지역 반복 제약을 더 직접적으로 명시해 로컬 EXAONE의 성수동 반복을 줄이는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                "지역명은 hookText, captions, hashtags를 모두 합쳐 총 2회 이하로만 사용하세요.\n"
                "이미 해시태그에 지역명이 들어가면 본문 계열에서는 최대 1회만 더 허용됩니다.\n"
                "product_name, benefit, urgency에는 지역명을 억지로 반복하지 말고, 꼭 필요한 경우에만 한 번 쓰세요."
            ),
            audience_guidance=local_ollama_baseline_variant.audience_guidance,
        )
        return ExperimentDefinition(
            experiment_id="EXP-31",
            experiment_title="Local EXAONE 3.5 7.8B Prompt Lever Experiment - Promotion Region Repeat Constraint",
            objective="RTX 4080 Super 16GB 환경에서 EXAONE 3.5 7.8B를 고정한 채 지역 반복 제약 한 가지가 T02 promotion의 region repeat 초과를 줄이는지 확인합니다.",
            scenario=get_service_aligned_bgrade_scenario(),
            model=ModelConfig(provider="ollama", model_name="exaone3.5:7.8b"),
            baseline_variant=local_ollama_baseline_variant,
            candidate_variants=(promotion_region_repeat_variant,),
        )

    if experiment_id == "EXP-33":
        local_ollama_baseline_variant = PromptVariant(
            variant_id="fixed_b_grade_tone_guidance_local_ollama",
            lever_id="baseline",
            changed_field="none",
            description="T02 promotion에서 EXAONE 3.5 7.8B 로컬 모델에 B급 tone guidance만 적용한 baseline prompt입니다.",
            role_instruction=common_role,
            slot_guidance=baseline_variant.slot_guidance,
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "hook, benefit, urgency, cta는 각 장면에서 바로 읽히도록 짧고 직접적으로 쓰세요.\n"
                "추상 표현인 '분위기를 보여드립니다', '구성했습니다' 같은 문장은 피하고, 혜택·기간감·행동 단어를 앞쪽에 배치하세요.\n"
                "한국어 출력에서 깨짐(�, 이상한 라틴 문자 조합)이 생기지 않도록 자연스러운 한국어 문장만 사용하세요."
            ),
        )
        local_ollama_output_constraint_variant = PromptVariant(
            variant_id="promotion_render_ready_output_constraint_local_exaone",
            lever_id="output_constraint",
            changed_field="slot_guidance",
            description="T02 promotion에서 로컬 EXAONE 출력 길이/이모지/CTA 형식을 직접 제한해 render-ready 품질을 높이는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                "추가 output constraint:\n"
                "- hook, benefit, urgency primaryText는 16자 안팎으로 짧게 쓰세요.\n"
                "- product_name primaryText는 14자 안팎으로 유지하세요.\n"
                "- ctaText와 cta primaryText는 10자 안팎으로 쓰고 방문/주문/저장/예약/확인 중 하나로 시작하세요.\n"
                "- captions는 정확히 3개, 각 28자 이하로 쓰세요.\n"
                "- hashtags는 정확히 5개만 쓰세요.\n"
                "- 이모지, 이모티콘, 특수 장식 기호는 사용하지 마세요.\n"
                "- subText는 primaryText와 다른 문장으로 쓰고, 같은 표현을 반복하지 마세요."
            ),
            audience_guidance=local_ollama_baseline_variant.audience_guidance,
        )
        return ExperimentDefinition(
            experiment_id="EXP-33",
            experiment_title="Local EXAONE 3.5 7.8B Prompt Lever Experiment - Promotion Output Constraint",
            objective="RTX 4080 Super 16GB 환경에서 EXAONE 3.5 7.8B를 고정한 채 output constraint 한 가지가 T02 promotion의 길이/CTA/format 안정성을 개선하는지 확인합니다.",
            scenario=get_service_aligned_bgrade_scenario(),
            model=ModelConfig(provider="ollama", model_name="exaone3.5:7.8b"),
            baseline_variant=local_ollama_baseline_variant,
            candidate_variants=(local_ollama_output_constraint_variant,),
        )

    if experiment_id == "EXP-35":
        local_ollama_baseline_variant = PromptVariant(
            variant_id="fixed_b_grade_tone_guidance_local_ollama",
            lever_id="baseline",
            changed_field="none",
            description="T02 promotion에서 EXAONE 3.5 7.8B 로컬 모델에 B급 tone guidance만 적용한 baseline prompt입니다.",
            role_instruction=common_role,
            slot_guidance=baseline_variant.slot_guidance,
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "hook, benefit, urgency, cta는 각 장면에서 바로 읽히도록 짧고 직접적으로 쓰세요.\n"
                "추상 표현인 '분위기를 보여드립니다', '구성했습니다' 같은 문장은 피하고, 혜택·기간감·행동 단어를 앞쪽에 배치하세요.\n"
                "한국어 출력에서 깨짐(�, 이상한 라틴 문자 조합)이 생기지 않도록 자연스러운 한국어 문장만 사용하세요."
            ),
        )
        local_ollama_hashtag_region_budget_variant = PromptVariant(
            variant_id="promotion_hashtag_region_budget_local_exaone",
            lever_id="hashtag_region_budget",
            changed_field="slot_guidance",
            description="T02 promotion에서 EXAONE 3.5 7.8B 로컬 모델의 지역명 반복을 줄이기 위해 hashtag/caption region budget만 추가한 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                "추가 hashtag/caption region budget:\n"
                "- 지역명은 전체 결과물에서 총 2회 이하로만 쓰세요.\n"
                "- hookText에는 지역명을 최대 1회만 넣을 수 있습니다.\n"
                "- captions 3개에는 지역명을 넣지 마세요. 위치감은 메뉴/분위기/혜택으로 대신 전달하세요.\n"
                "- hashtags는 5개만 쓰고, 지역명이 들어간 해시태그는 최대 1개만 허용됩니다.\n"
                "- hashtags 나머지는 메뉴명, 혜택, 방문 상황, 분위기 키워드로 채우세요."
            ),
            audience_guidance=local_ollama_baseline_variant.audience_guidance,
        )
        return ExperimentDefinition(
            experiment_id="EXP-35",
            experiment_title="Local EXAONE 3.5 7.8B Prompt Lever Experiment - Promotion Hashtag Region Budget",
            objective="RTX 4080 Super 16GB 환경에서 EXAONE 3.5 7.8B를 고정한 채 hashtag/caption region budget 한 가지가 T02 promotion의 지역명 반복 문제를 줄이는지 확인합니다.",
            scenario=get_service_aligned_bgrade_scenario(),
            model=ModelConfig(provider="ollama", model_name="exaone3.5:7.8b"),
            baseline_variant=local_ollama_baseline_variant,
            candidate_variants=(local_ollama_hashtag_region_budget_variant,),
        )

    if experiment_id == "EXP-100":
        hook_pack_baseline_variant = PromptVariant(
            variant_id="fixed_b_grade_tone_guidance_openai",
            lever_id="baseline",
            changed_field="none",
            description="T02 promotion에서 gpt-5-mini에 B급 tone guidance만 적용한 baseline prompt입니다.",
            role_instruction=common_role,
            slot_guidance=baseline_variant.slot_guidance,
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "hook, benefit, urgency, cta는 각 장면에서 바로 읽히도록 짧고 직접적으로 쓰세요.\n"
                "추상 표현인 '분위기를 보여드립니다', '구성했습니다' 같은 문장은 피하고, 혜택·기간감·행동 단어를 앞쪽에 배치하세요."
            ),
        )
        hook_pack_variant = PromptVariant(
            variant_id="reference_hook_pack_guidance",
            lever_id="hook_pack_guidance",
            changed_field="slot_guidance",
            description="reference-derived hook 후보를 직접 제시해 T02 promotion hook과 body 직접성이 좋아지는지 확인하는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_scenario())}"
            ),
            audience_guidance=hook_pack_baseline_variant.audience_guidance,
        )
        return ExperimentDefinition(
            experiment_id="EXP-100",
            experiment_title="GPT-5 Mini Prompt Lever Experiment - Reference Hook Pack Guidance",
            objective="T02 promotion, b_grade_fun, 실제 음식 사진에서 gpt-5-mini를 고정한 채 reference-derived hook 후보를 prompt에 직접 주면 hook과 sceneText 직접성이 baseline 대비 개선되는지 확인합니다.",
            scenario=get_service_aligned_bgrade_scenario(),
            model=ModelConfig(provider="openai", model_name="gpt-5-mini"),
            baseline_variant=hook_pack_baseline_variant,
            candidate_variants=(hook_pack_variant,),
        )

    if experiment_id == "EXP-103":
        hook_pack_baseline_variant = PromptVariant(
            variant_id="fixed_reference_hook_pack_guidance_openai",
            lever_id="baseline",
            changed_field="none",
            description="T02 promotion에서 gpt-5-mini에 reference hook guidance만 적용한 baseline prompt입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_scenario())}"
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "hook, benefit, urgency, cta는 각 장면에서 바로 읽히도록 짧고 직접적으로 쓰세요.\n"
                "추상 표현인 '분위기를 보여드립니다', '구성했습니다' 같은 문장은 피하고, 혜택·기간감·행동 단어를 앞쪽에 배치하세요."
            ),
        )
        hook_pack_region_length_variant = PromptVariant(
            variant_id="reference_hook_pack_region_length_constraint_openai",
            lever_id="region_length_constraint",
            changed_field="slot_guidance",
            description="gpt-5-mini에서 reference hook guidance 위에 region/length constraint를 추가해 흔들림을 줄이는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 14자 안팎으로 유지하세요.\n"
                "- benefit primaryText는 16자 안팎, urgency primaryText는 10자 안팎, cta primaryText는 8자 안팎으로 쓰세요.\n"
                "- benefit, urgency, cta primaryText에는 지역명을 넣지 마세요.\n"
                "- captions 3개 중 지역명은 최대 1개 caption에서만 1회 허용합니다.\n"
                "- hashtags는 5~6개로 쓰고, 지역명이 들어간 hashtag는 최대 1개만 허용합니다.\n"
                "- cta와 ctaText는 방문, 저장, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- subText에만 보조 설명을 넣고, primaryText는 최대한 짧게 유지하세요."
            ),
            audience_guidance=hook_pack_baseline_variant.audience_guidance,
        )
        return ExperimentDefinition(
            experiment_id="EXP-103",
            experiment_title="GPT-5 Mini Prompt Lever Experiment - Reference Hook Region/Length Constraint",
            objective="T02 promotion, b_grade_fun, 실제 음식 사진에서 gpt-5-mini를 고정한 채 reference hook guidance 위에 region/length constraint를 추가하면 region repeat와 scene length 흔들림이 줄어드는지 확인합니다.",
            scenario=get_service_aligned_bgrade_scenario(),
            model=ModelConfig(provider="openai", model_name="gpt-5-mini"),
            baseline_variant=hook_pack_baseline_variant,
            candidate_variants=(hook_pack_region_length_variant,),
        )

    if experiment_id == "EXP-104":
        hook_pack_baseline_variant = PromptVariant(
            variant_id="fixed_reference_hook_pack_guidance_gemma",
            lever_id="baseline",
            changed_field="none",
            description="T02 promotion에서 Gemma 4에 reference hook guidance만 적용한 baseline prompt입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_scenario())}"
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "hook, benefit, urgency, cta는 각 장면에서 바로 읽히도록 짧고 직접적으로 쓰세요.\n"
                "추상 표현인 '분위기를 보여드립니다', '구성했습니다' 같은 문장은 피하고, 혜택·기간감·행동 단어를 앞쪽에 배치하세요."
            ),
        )
        gemma_urgency_cta_variant = PromptVariant(
            variant_id="reference_hook_pack_urgency_cta_cap_gemma",
            lever_id="urgency_cta_cap",
            changed_field="slot_guidance",
            description="Gemma 4에서 reference hook guidance 위에 urgency/cta 길이 상한을 추가해 render-ready성을 높이는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_scenario())}\n"
                "추가 output constraint:\n"
                "- hook primaryText는 14자 안팎으로 유지하세요.\n"
                "- benefit primaryText는 16자 안팎으로 유지하세요.\n"
                "- urgency primaryText는 10자 안팎의 아주 짧은 기간 문구만 쓰세요. 예: 오늘 한정, 재고 소진 전.\n"
                "- cta primaryText와 ctaText는 8자 안팎으로 쓰고, 지금 바로 같은 부사를 빼고 행동 단어만 남기세요.\n"
                "- cta는 방문, 저장, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- 긴 설명은 subText로 보내고, primaryText는 poster headline처럼 짧게 유지하세요."
            ),
            audience_guidance=hook_pack_baseline_variant.audience_guidance,
        )
        return ExperimentDefinition(
            experiment_id="EXP-104",
            experiment_title="Gemma 4 Prompt Lever Experiment - Reference Hook Urgency/CTA Cap",
            objective="T02 promotion, b_grade_fun, 실제 음식 사진에서 Gemma 4를 고정한 채 reference hook guidance 위에 urgency/cta 길이 상한을 추가하면 render-ready성이 좋아지는지 확인합니다.",
            scenario=get_service_aligned_bgrade_scenario(),
            model=ModelConfig(provider="google", model_name="models/gemma-4-31b-it"),
            baseline_variant=hook_pack_baseline_variant,
            candidate_variants=(gemma_urgency_cta_variant,),
        )

    if experiment_id == "EXP-106":
        strict_anchor_baseline_variant = PromptVariant(
            variant_id="fixed_reference_hook_region_anchor_budget_openai",
            lever_id="baseline",
            changed_field="none",
            description="gpt-5-mini에서 region anchor와 length budget을 함께 고정한 baseline prompt입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 14자 안팎으로 유지하세요.\n"
                "- benefit primaryText는 16자 안팎, urgency primaryText는 10자 안팎, cta primaryText는 8자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 방문, 저장, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- 지역명은 hookText와 scene primaryText에는 넣지 마세요.\n"
                "- 지역명은 captions 중 정확히 1개 문장에 1회만 넣으세요.\n"
                "- 지역명이 들어간 hashtag는 정확히 1개만 쓰세요.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요.\n"
                "- subText에는 보조 설명을 넣되, primaryText보다 길어도 괜찮습니다."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "hook, benefit, urgency, cta는 각 장면에서 바로 읽히도록 짧고 직접적으로 쓰세요.\n"
                "추상 표현인 '분위기를 보여드립니다', '구성했습니다' 같은 문장은 피하고, 혜택·기간감·행동 단어를 앞쪽에 배치하세요."
            ),
        )
        exact_region_anchor_variant = PromptVariant(
            variant_id="reference_hook_exact_region_caption_anchor_openai",
            lever_id="exact_region_caption_anchor",
            changed_field="slot_guidance",
            description="gpt-5-mini에서 exact region string을 caption과 hashtag에 직접 고정해 지역 우회를 줄이는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 14자 안팎으로 유지하세요.\n"
                "- benefit primaryText는 16자 안팎, urgency primaryText는 10자 안팎, cta primaryText는 8자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 방문, 저장, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- 지역명은 hookText와 scene primaryText에는 넣지 마세요.\n"
                "- captions 3개 중 정확히 1개 caption에는 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- 위 caption에서 지역 표현을 '서울숲 근처', '서울숲 인근', '성수역', '근처', '동네' 같은 우회 표현으로 바꾸지 마세요.\n"
                "- 지역명이 들어간 hashtag는 정확히 1개만 쓰고, 그 hashtag는 '성수동' 문자열을 그대로 포함해야 합니다.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요.\n"
                "- subText에는 보조 설명을 넣되, primaryText보다 길어도 괜찮습니다."
            ),
            audience_guidance=strict_anchor_baseline_variant.audience_guidance,
        )
        return ExperimentDefinition(
            experiment_id="EXP-106",
            experiment_title="GPT-5 Mini Prompt Lever Experiment - Exact Region Caption Anchor",
            objective="T02 promotion, b_grade_fun, 실제 음식 사진에서 gpt-5-mini를 고정한 채 strict region anchor baseline 위에 exact region string constraint를 추가하면 성수동 우회 표현이 줄어드는지 확인합니다.",
            scenario=get_service_aligned_bgrade_scenario(),
            model=ModelConfig(provider="openai", model_name="gpt-5-mini"),
            baseline_variant=strict_anchor_baseline_variant,
            candidate_variants=(exact_region_anchor_variant,),
        )

    if experiment_id == "EXP-107":
        strict_anchor_baseline_variant = PromptVariant(
            variant_id="fixed_reference_hook_region_anchor_budget_gemma",
            lever_id="baseline",
            changed_field="none",
            description="Gemma 4에서 region anchor와 length budget을 함께 고정한 baseline prompt입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 14자 안팎으로 유지하세요.\n"
                "- benefit primaryText는 16자 안팎, urgency primaryText는 10자 안팎, cta primaryText는 8자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 방문, 저장, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- 지역명은 hookText와 scene primaryText에는 넣지 마세요.\n"
                "- 지역명은 captions 중 정확히 1개 문장에 1회만 넣으세요.\n"
                "- 지역명이 들어간 hashtag는 정확히 1개만 쓰세요.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요.\n"
                "- subText에는 보조 설명을 넣되, primaryText보다 길어도 괜찮습니다."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "hook, benefit, urgency, cta는 각 장면에서 바로 읽히도록 짧고 직접적으로 쓰세요.\n"
                "추상 표현인 '분위기를 보여드립니다', '구성했습니다' 같은 문장은 피하고, 혜택·기간감·행동 단어를 앞쪽에 배치하세요."
            ),
        )
        benefit_14_cap_variant = PromptVariant(
            variant_id="reference_hook_benefit_14_cap_gemma",
            lever_id="benefit_14_cap",
            changed_field="slot_guidance",
            description="Gemma 4에서 strict region anchor baseline 위에 benefit headline 14자 상한을 추가하는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 14자 안팎으로 유지하세요.\n"
                "- benefit primaryText는 가능하면 12~14자 안쪽으로 쓰고, 14자를 넘기지 마세요.\n"
                "- urgency primaryText는 10자 안팎, cta primaryText는 8자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 방문, 저장, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- 지역명은 hookText와 scene primaryText에는 넣지 마세요.\n"
                "- 지역명은 captions 중 정확히 1개 문장에 1회만 넣으세요.\n"
                "- 지역명이 들어간 hashtag는 정확히 1개만 쓰세요.\n"
                "- 긴 혜택 설명은 benefit subText로 보내고, benefit primaryText는 포스터 headline처럼 짧게 유지하세요.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요."
            ),
            audience_guidance=strict_anchor_baseline_variant.audience_guidance,
        )
        return ExperimentDefinition(
            experiment_id="EXP-107",
            experiment_title="Gemma 4 Prompt Lever Experiment - Benefit 14 Char Cap",
            objective="T02 promotion, b_grade_fun, 실제 음식 사진에서 Gemma 4를 고정한 채 strict region anchor baseline 위에 benefit 14자 상한을 추가하면 over-limit scene이 줄어드는지 확인합니다.",
            scenario=get_service_aligned_bgrade_scenario(),
            model=ModelConfig(provider="google", model_name="models/gemma-4-31b-it"),
            baseline_variant=strict_anchor_baseline_variant,
            candidate_variants=(benefit_14_cap_variant,),
        )

    if experiment_id == "EXP-128":
        review_direct_transfer_variant = PromptVariant(
            variant_id="promotion_baseline_direct_transfer_to_review",
            lever_id="baseline_transfer",
            changed_field="slot_guidance_and_audience_guidance",
            description="T02 promotion strict anchor baseline의 핵심 문구와 제약을 거의 그대로 T04 review에 옮겨, direct transfer가 실제로 버티는지 확인합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_review_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 14자 안팎으로 유지하세요.\n"
                "- benefit primaryText는 가능하면 12~14자 안쪽으로 쓰고, 14자를 넘기지 마세요.\n"
                "- urgency primaryText는 10자 안팎, cta primaryText는 8자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 방문, 저장, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- 지역명은 hookText와 scene primaryText에는 넣지 마세요.\n"
                "- captions 3개 중 정확히 1개 caption에는 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- 위 caption에서 지역 표현을 '서울숲 근처', '서울숲 인근', '성수역', '근처', '동네' 같은 우회 표현으로 바꾸지 마세요.\n"
                "- 지역명이 들어간 hashtag는 정확히 1개만 쓰고, 그 hashtag는 '성수동' 문자열을 그대로 포함해야 합니다.\n"
                "- 긴 혜택 설명은 benefit subText로 보내고, primaryText는 poster headline처럼 짧게 유지하세요.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "hook, benefit, urgency, cta는 각 장면에서 바로 읽히도록 짧고 직접적으로 쓰세요.\n"
                "추상 표현인 '분위기를 보여드립니다', '구성했습니다' 같은 문장은 피하고, 혜택·기간감·행동 단어를 앞쪽에 배치하세요."
            ),
        )
        review_slot_translated_variant = PromptVariant(
            variant_id="promotion_baseline_principles_translated_to_review",
            lever_id="baseline_transfer_translated",
            changed_field="slot_guidance_and_audience_guidance",
            description="strict anchor, exact region, CTA action성 같은 baseline 원칙은 유지하되 T04 review slot 구조로 다시 번역한 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_review_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 review_quote primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- product_name primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- cta primaryText는 8~10자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 저장, 방문, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- 지역명은 hookText, review_quote primaryText, product_name primaryText에는 넣지 마세요.\n"
                "- captions 3개 중 정확히 1개 caption에는 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- 위 caption에서 지역 표현을 '서울숲 근처', '서울숲 인근', '성수역', '근처', '동네' 같은 우회 표현으로 바꾸지 마세요.\n"
                "- 지역명이 들어간 hashtag는 정확히 1개만 쓰고, 그 hashtag는 '성수동' 문자열을 그대로 포함해야 합니다.\n"
                "- 긴 감상은 review_quote subText로 보내고, primaryText는 친구가 바로 보내는 한 줄처럼 짧게 유지하세요.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 믿고 갈 한 끼를 찾는 20~30대 방문객입니다.\n"
                "B급 감성 review는 친구가 채팅방에 바로 던지는 한 줄 제보처럼 들려야 합니다.\n"
                "review_quote는 짧고 말맛 있게, product_name은 다시 찾는 이유가 한 번에 보이게 쓰세요.\n"
                "cta는 감탄사보다 행동 단어를 앞쪽에 두고 짧게 마무리하세요."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-128",
            experiment_title="Prompt Baseline Transfer Check - T02 Promotion to T04 Review",
            objective="고정된 Gemma 4 baseline을 기준으로 T02 promotion strict baseline을 T04 review에 직접 옮겼을 때와 review slot 구조로 번역했을 때를 비교해, baseline이 어디까지 전이 가능한지 확인합니다.",
            scenario=get_service_aligned_bgrade_review_scenario(),
            model=ModelConfig(provider="google", model_name="models/gemma-4-31b-it"),
            baseline_variant=review_direct_transfer_variant,
            candidate_variants=(review_slot_translated_variant,),
        )

    if experiment_id == "EXP-131":
        review_translated_baseline_variant = PromptVariant(
            variant_id="review_translated_baseline_gpt5mini",
            lever_id="baseline",
            changed_field="none",
            description="gpt-5-mini에서 review-translated strict baseline prompt를 그대로 적용한 baseline입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_review_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 review_quote primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- product_name primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- cta primaryText는 8~10자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 저장, 방문, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- 지역명은 hookText, review_quote primaryText, product_name primaryText에는 넣지 마세요.\n"
                "- captions 3개 중 정확히 1개 caption에는 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- 위 caption에서 지역 표현을 '서울숲 근처', '서울숲 인근', '성수역', '근처', '동네' 같은 우회 표현으로 바꾸지 마세요.\n"
                "- 지역명이 들어간 hashtag는 정확히 1개만 쓰고, 그 hashtag는 '성수동' 문자열을 그대로 포함해야 합니다.\n"
                "- 긴 감상은 review_quote subText로 보내고, primaryText는 친구가 바로 보내는 한 줄처럼 짧게 유지하세요.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 믿고 갈 한 끼를 찾는 20~30대 방문객입니다.\n"
                "B급 감성 review는 친구가 채팅방에 바로 던지는 한 줄 제보처럼 들려야 합니다.\n"
                "review_quote는 짧고 말맛 있게, product_name은 다시 찾는 이유가 한 번에 보이게 쓰세요.\n"
                "cta는 감탄사보다 행동 단어를 앞쪽에 두고 짧게 마무리하세요."
            ),
        )
        review_surface_locked_variant = PromptVariant(
            variant_id="review_surface_locked_exact_region_anchor",
            lever_id="surface_lock",
            changed_field="slot_guidance",
            description="gpt-5-mini에서 nearby-location leakage를 막기 위해 caption/subText/sceneText surface를 더 강하게 잠그는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_review_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 review_quote primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- product_name primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- cta primaryText는 8~10자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 저장, 방문, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- captions 3개 중 정확히 1개 caption에만 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- 그 1개 caption을 제외한 다른 captions, hookText, ctaText, sceneText, subText, hashtags에는 위치 표현을 넣지 마세요.\n"
                "- 특히 '서울숲', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 landmark/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- region hashtag는 정확히 1개만 쓰고, 반드시 '#성수동'만 허용합니다.\n"
                "- product_name, review_quote, subText에는 위치 단서를 절대 넣지 말고 맛, 질감, 재방문 이유만 쓰세요.\n"
                "- 위치를 더 쓰고 싶어지면 그 자리를 메뉴 장점이나 재방문 이유로 바꾸세요.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 믿고 갈 한 끼를 찾는 20~30대 방문객입니다.\n"
                "B급 감성 review는 친구가 채팅방에 바로 던지는 한 줄 제보처럼 들려야 합니다.\n"
                "review_quote는 짧고 말맛 있게, product_name은 다시 찾는 이유가 한 번에 보이게 쓰세요.\n"
                "cta는 감탄사보다 행동 단어를 앞쪽에 두고 짧게 마무리하세요."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-131",
            experiment_title="GPT-5 Mini Review Strict Region Leakage Suppression",
            objective="T04 review, b_grade_fun, 실제 음식 사진에서 gpt-5-mini를 고정한 채 surface-locked exact region anchor를 추가하면 nearby-location leakage가 줄어드는지 확인합니다.",
            scenario=get_service_aligned_bgrade_review_scenario(),
            model=ModelConfig(provider="openai", model_name="gpt-5-mini"),
            baseline_variant=review_translated_baseline_variant,
            candidate_variants=(review_surface_locked_variant,),
        )

    if experiment_id == "EXP-146":
        promotion_shorter_copy_baseline_variant = PromptVariant(
            variant_id="promotion_strict_anchor_shorter_copy_off_baseline_gemma",
            lever_id="baseline",
            changed_field="none",
            description="Gemma 4에서 EXP-144 strict anchor shorterCopy=false prompt를 그대로 적용한 baseline입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_shorter_copy_off_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 14자 안팎으로 유지하세요.\n"
                "- benefit primaryText는 가능하면 12~14자 안쪽으로 쓰고, 14자를 넘기지 마세요.\n"
                "- urgency primaryText는 10자 안팎, cta primaryText는 8자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 방문, 저장, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option shorterCopy=false이므로 모든 문장을 억지로 한 줄 슬로건처럼 자르지 말고, 필요한 맥락은 subText와 caption으로 분리해 남기세요.\n"
                "- 대신 primaryText는 계속 poster headline처럼 짧아야 하며, 설명이 길어질수록 subText로 보내세요.\n"
                "- 가격, 할인, 세트 이점은 감춰도 되는 정보가 아니므로 benefit나 caption에서 자연스럽게 살리되, 같은 숫자나 혜택 문구를 여러 surface에 반복하지 마세요.\n"
                "- 지역명은 hookText와 scene primaryText에는 넣지 마세요.\n"
                "- captions 3개 중 정확히 1개 caption에는 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- 위 caption에서 지역 표현을 '서울숲 근처', '서울숲 인근', '성수역', '근처', '동네' 같은 우회 표현으로 바꾸지 마세요.\n"
                "- 지역명이 들어간 hashtag는 정확히 1개만 쓰고, 그 hashtag는 '성수동' 문자열을 그대로 포함해야 합니다.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "shorterCopy=false일 때는 모든 문장을 짧게 깎는 것보다 훅-혜택-행동 흐름이 자연스럽게 이어지도록 한 줄 보조 설명을 허용하세요.\n"
                "hook, benefit, urgency, cta는 각 장면에서 바로 읽히도록 짧고 직접적으로 유지하되, 설명이 필요하면 subText나 caption 한 줄로 정리하세요."
            ),
        )
        promotion_surface_locked_variant = PromptVariant(
            variant_id="promotion_surface_locked_nearby_leakage_suppression_gemma",
            lever_id="surface_lock",
            changed_field="slot_guidance",
            description="Gemma 4에서 subText/hashtags nearby leakage를 막기 위해 promotion strict anchor surface를 더 강하게 잠그는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_shorter_copy_off_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 14자 안팎으로 유지하세요.\n"
                "- benefit primaryText는 가능하면 12~14자 안쪽으로 쓰고, 14자를 넘기지 마세요.\n"
                "- urgency primaryText는 10자 안팎, cta primaryText는 8자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 방문, 저장, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option shorterCopy=false는 설명을 허용한다는 뜻이지 위치 설명을 늘리라는 뜻이 아닙니다.\n"
                "- captions 3개 중 정확히 1개 caption에만 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- region hashtag는 정확히 1개만 쓰고, 반드시 '#성수동'만 허용하세요.\n"
                "- '#성수동맛집', '#서울숲맛집', '#서울숲데이트'처럼 지역을 확장하거나 nearby landmark를 넣은 hashtag는 금지합니다.\n"
                "- 위 1개 caption과 '#성수동'을 제외한 다른 captions, hashtags, hookText, ctaText, sceneText, subText에는 위치 표현을 넣지 마세요.\n"
                "- 특히 '서울숲', '서울숲 근처', '서울숲 인근', '성수역', '근처', '인근', '동네', '앞', '옆', '골목', '핫플' 같은 nearby/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- subText에는 위치 단서를 절대 넣지 말고 메뉴 강점, 세트 구성, 할인 이유, 퇴근 후 한잔 상황만 쓰세요.\n"
                "- 가격, 할인, 세트 이점은 benefit/caption/subText에 자연스럽게 살리되 같은 숫자나 혜택 문구를 여러 surface에 반복하지 마세요.\n"
                "- 위치를 더 쓰고 싶어지면 그 자리를 메뉴 장점, 식감, 방문 이유로 바꾸세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "shorterCopy=false일 때는 설명을 한 줄 더 붙일 수 있지만, 그 설명은 메뉴 매력과 방문 이유에만 써야 합니다.\n"
                "지역을 더 쓰고 싶어지면 nearby landmark로 새지 말고, 그 자리를 맛, 구성, 할인 이유, 퇴근 후 보상감으로 채우세요."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-146",
            experiment_title="Gemma 4 Promotion Surface-Locked Nearby Leakage Suppression",
            objective="T02 promotion, b_grade_fun, highlightPrice=true, shorterCopy=false, emphasizeRegion=false에서 Gemma 4를 고정한 채 subText/hashtag surface lock을 추가하면 nearby-location leakage가 줄고 strict baseline repeatability가 개선되는지 확인합니다.",
            scenario=get_service_aligned_bgrade_shorter_copy_off_scenario(),
            model=ModelConfig(provider="google", model_name="models/gemma-4-31b-it"),
            baseline_variant=promotion_shorter_copy_baseline_variant,
            candidate_variants=(promotion_surface_locked_variant,),
        )

    if experiment_id == "EXP-148":
        promotion_highlight_price_off_baseline_variant = PromptVariant(
            variant_id="promotion_strict_anchor_highlight_price_off_baseline_gemma",
            lever_id="baseline",
            changed_field="none",
            description="Gemma 4에서 EXP-143 strict anchor highlightPrice=false prompt를 그대로 적용한 baseline입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_highlight_price_off_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 14자 안팎으로 유지하세요.\n"
                "- benefit primaryText는 가능하면 12~14자 안쪽으로 쓰고, 14자를 넘기지 마세요.\n"
                "- urgency primaryText는 10자 안팎, cta primaryText는 8자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 방문, 저장, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option highlightPrice=false이므로 가격 숫자나 할인폭을 hook, benefit, urgency의 주제처럼 앞세우지 마세요.\n"
                "- 혜택이 있더라도 가격 숫자보다 메뉴 강점, 식감, 구성, 방문 이유를 먼저 보이게 쓰세요.\n"
                "- 지역명은 hookText와 scene primaryText에는 넣지 마세요.\n"
                "- captions 3개 중 정확히 1개 caption에는 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- 위 caption에서 지역 표현을 '서울숲 근처', '서울숲 인근', '성수역', '근처', '동네' 같은 우회 표현으로 바꾸지 마세요.\n"
                "- 지역명이 들어간 hashtag는 정확히 1개만 쓰고, 그 hashtag는 '성수동' 문자열을 그대로 포함해야 합니다.\n"
                "- 긴 설명은 subText로 보내고, primaryText는 poster headline처럼 짧게 유지하세요.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "highlightPrice=false일 때는 할인 숫자를 밀기보다 메뉴 매력과 방문 이유가 먼저 읽히게 쓰세요.\n"
                "hook, benefit, urgency, cta는 각 장면에서 바로 읽히도록 짧고 직접적으로 쓰고, 가격을 억지로 비워서 심심해지지 않게 맛과 분위기 근거를 넣으세요."
            ),
        )
        promotion_surface_locked_variant = PromptVariant(
            variant_id="promotion_surface_locked_highlight_price_off_gemma",
            lever_id="surface_lock",
            changed_field="slot_guidance",
            description="Gemma 4에서 highlightPrice=false 조건의 nearby leakage와 price foreground drift를 함께 막기 위해 promotion strict anchor surface를 더 강하게 잠그는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_highlight_price_off_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 14자 안팎으로 유지하세요.\n"
                "- hookText와 hook primaryText는 절대 16자를 넘기지 마세요.\n"
                "- benefit primaryText는 가능하면 12~14자 안쪽으로 쓰고, 14자를 넘기지 마세요.\n"
                "- urgency primaryText는 10자 안팎, cta primaryText는 8자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 방문, 저장, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option highlightPrice=false는 가격 강조를 끄는 뜻이므로 hookText, benefit, urgency, captions, hashtags에서 가격 숫자, 할인폭, 특가, 할인, 가성비를 중심 훅처럼 앞세우지 마세요.\n"
                "- 가격 표현을 비우고 싶어지면 그 자리를 규카츠 식감, 육즙, 맥주 페어링, 퇴근 후 한 끼 이유로 채우세요.\n"
                "- captions 3개 중 정확히 1개 caption에만 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- region hashtag는 정확히 1개만 쓰고, 반드시 '#성수동'만 허용하세요.\n"
                "- '#성수동맛집', '#서울숲맛집', '#서울숲데이트', '#퇴근후성수', '#동네맛집'처럼 지역을 확장하거나 nearby 의미를 암시하는 hashtag는 금지합니다.\n"
                "- 위 1개 caption과 '#성수동'을 제외한 다른 captions, hashtags, hookText, ctaText, sceneText, subText에는 위치 표현을 넣지 마세요.\n"
                "- 특히 '서울숲', '서울숲 근처', '서울숲 인근', '성수역', '근처', '인근', '동네', '앞', '옆', '골목', '핫플' 같은 nearby/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- subText에는 위치 설명을 넣지 말고 메뉴 강점, 식감, 구성, 방문 이유, 맥주와의 페어링만 쓰세요.\n"
                "- 지역이나 가격을 더 쓰고 싶어지면 그 자리를 메뉴 장점, 식감, 재방문 이유로 바꾸세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "highlightPrice=false일 때는 할인 훅 대신 메뉴 매력과 방문 이유를 전면에 세워야 합니다.\n"
                "hook이 길어지면 감탄사보다 명사+질문 구조로 압축해서 첫 장면 headline이 바로 읽히게 유지하세요.\n"
                "지역 표현이 더 쓰고 싶어지면 nearby landmark로 새지 말고, 그 자리를 식감, 육즙, 페어링, 퇴근 후 보상감으로 채우세요."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-148",
            experiment_title="Gemma 4 Promotion Highlight Price Off Surface Lock",
            objective="T02 promotion, b_grade_fun, highlightPrice=false, shorterCopy=true, emphasizeRegion=false에서 Gemma 4를 고정한 채 subText/hashtag surface lock과 no-price-foreground constraint를 추가하면 nearby-location leakage와 price drift가 줄고 strict baseline repeatability가 개선되는지 확인합니다.",
            scenario=get_service_aligned_bgrade_highlight_price_off_scenario(),
            model=ModelConfig(provider="google", model_name="models/gemma-4-31b-it"),
            baseline_variant=promotion_highlight_price_off_baseline_variant,
            candidate_variants=(promotion_surface_locked_variant,),
        )

    if experiment_id == "EXP-152":
        promotion_shorter_copy_surface_lock_baseline_variant = PromptVariant(
            variant_id="promotion_surface_lock_shorter_copy_off_baseline_gemma",
            lever_id="baseline",
            changed_field="none",
            description="Gemma 4에서 promotion_surface_lock_shorter_copy_off prompt를 highlightPrice=false + shorterCopy=false scenario에 baseline으로 재사용합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_highlight_price_off_shorter_copy_off_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 14자 안팎으로 유지하세요.\n"
                "- benefit primaryText는 가능하면 12~14자 안쪽으로 쓰고, 14자를 넘기지 마세요.\n"
                "- urgency primaryText는 10자 안팎, cta primaryText는 8자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 방문, 저장, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option shorterCopy=false는 설명을 허용한다는 뜻이지 위치 설명을 늘리라는 뜻이 아닙니다.\n"
                "- captions 3개 중 정확히 1개 caption에만 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- region hashtag는 정확히 1개만 쓰고, 반드시 '#성수동'만 허용하세요.\n"
                "- '#성수동맛집', '#서울숲맛집', '#서울숲데이트'처럼 지역을 확장하거나 nearby landmark를 넣은 hashtag는 금지합니다.\n"
                "- 위 1개 caption과 '#성수동'을 제외한 다른 captions, hashtags, hookText, ctaText, sceneText, subText에는 위치 표현을 넣지 마세요.\n"
                "- 특히 '서울숲', '서울숲 근처', '서울숲 인근', '성수역', '근처', '인근', '동네', '앞', '옆', '골목', '핫플' 같은 nearby/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- subText에는 위치 단서를 절대 넣지 말고 메뉴 강점, 세트 구성, 할인 이유, 퇴근 후 한잔 상황만 쓰세요.\n"
                "- 가격, 할인, 세트 이점은 benefit/caption/subText에 자연스럽게 살리되 같은 숫자나 혜택 문구를 여러 surface에 반복하지 마세요.\n"
                "- 위치를 더 쓰고 싶어지면 그 자리를 메뉴 장점, 식감, 방문 이유로 바꾸세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "shorterCopy=false일 때는 설명을 한 줄 더 붙일 수 있지만, 그 설명은 메뉴 매력과 방문 이유에만 써야 합니다.\n"
                "지역을 더 쓰고 싶어지면 nearby landmark로 새지 말고, 그 자리를 맛, 구성, 할인 이유, 퇴근 후 보상감으로 채우세요."
            ),
        )
        promotion_combined_surface_locked_variant = PromptVariant(
            variant_id="promotion_surface_locked_highlight_price_off_shorter_copy_off_gemma",
            lever_id="surface_lock",
            changed_field="slot_guidance",
            description="Gemma 4에서 shorterCopy=false profile에 highlightPrice=false 조건을 추가해 no-price-foreground와 nearby leakage suppression을 함께 고정하는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_highlight_price_off_shorter_copy_off_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 14자 안팎으로 유지하세요.\n"
                "- hookText와 hook primaryText는 절대 16자를 넘기지 마세요.\n"
                "- benefit primaryText는 가능하면 12~14자 안쪽으로 쓰고, 14자를 넘기지 마세요.\n"
                "- urgency primaryText는 10자 안팎, cta primaryText는 8자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 방문, 저장, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option shorterCopy=false는 설명을 허용하지만, 그 설명도 가격 설명보다 메뉴 장점과 방문 이유를 먼저 보여야 합니다.\n"
                "- quick option highlightPrice=false이므로 가격 숫자, 할인폭, 특가, 할인, 가성비를 hookText, benefit, urgency, captions, hashtags의 중심 훅처럼 앞세우지 마세요.\n"
                "- 가격이나 혜택을 언급하더라도 raw 숫자나 퍼센트를 headline처럼 쓰지 말고, caption 또는 subText 한 줄 안의 보조 정보로만 처리하세요.\n"
                "- captions 3개 중 정확히 1개 caption에만 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- region hashtag는 정확히 1개만 쓰고, 반드시 '#성수동'만 허용하세요.\n"
                "- '#성수동맛집', '#서울숲맛집', '#서울숲데이트', '#퇴근후성수', '#동네맛집'처럼 지역을 확장하거나 nearby 의미를 암시하는 hashtag는 금지합니다.\n"
                "- '#오늘만할인', '#가성비', '#특가', '#할인중'처럼 가격 foreground 뉘앙스가 강한 hashtag도 금지합니다.\n"
                "- 위 1개 caption과 '#성수동'을 제외한 다른 captions, hashtags, hookText, ctaText, sceneText, subText에는 위치 표현을 넣지 마세요.\n"
                "- 특히 '서울숲', '서울숲 근처', '서울숲 인근', '성수역', '근처', '인근', '동네', '앞', '옆', '골목', '핫플' 같은 nearby/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- subText에는 위치 설명을 넣지 말고 메뉴 강점, 식감, 세트 구성, 방문 이유, 맥주 페어링만 쓰세요.\n"
                "- 가격 표현을 비우고 싶어지면 그 자리를 규카츠 식감, 육즙, 퇴근 후 보상감, 맥주와의 조합으로 채우세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "shorterCopy=false일 때는 설명이 한 줄 더 붙어도 되지만, highlightPrice=false일 때는 그 설명이 할인 숫자가 아니라 메뉴 매력과 방문 이유를 떠받쳐야 합니다.\n"
                "hook이 길어지면 감탄사보다 명사+질문 구조로 압축하고, 가격을 더 밀고 싶어지면 그 자리를 식감, 육즙, 구성, 페어링 근거로 바꾸세요."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-152",
            experiment_title="Gemma 4 Promotion Highlight Price Off Shorter Copy Off Surface Lock",
            objective="T02 promotion, b_grade_fun, highlightPrice=false, shorterCopy=false, emphasizeRegion=false에서 Gemma 4를 고정한 채 shorterCopy=false surface-lock profile에 no-price-foreground constraint를 더하면 combined option profile로 승격 가능한지 확인합니다.",
            scenario=get_service_aligned_bgrade_highlight_price_off_shorter_copy_off_scenario(),
            model=ModelConfig(provider="google", model_name="models/gemma-4-31b-it"),
            baseline_variant=promotion_shorter_copy_surface_lock_baseline_variant,
            candidate_variants=(promotion_combined_surface_locked_variant,),
        )

    if experiment_id == "EXP-156":
        new_menu_region_anchor_baseline_variant = PromptVariant(
            variant_id="new_menu_friendly_region_anchor_baseline_gpt5mini",
            lever_id="baseline",
            changed_field="none",
            description="gpt-5-mini에서 new_menu_friendly_strict_region_anchor prompt를 shorterCopy=true scenario에 baseline으로 재사용합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_new_menu_shorter_copy_region_anchor_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- product_name primaryText와 difference primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- cta primaryText는 8~10자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 확인, 주문, 저장, 방문 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option emphasizeRegion=true는 regionName을 더 분명하게 쓰라는 뜻이지, 상세 위치를 공개하라는 뜻이 아닙니다.\n"
                "- 문자열 '성수동'은 hookText에 1회, captions 3개 중 정확히 1개 caption에 1회, hashtags 중 정확히 1개 hashtag에 1회만 쓰세요.\n"
                "- 위 3곳을 제외한 다른 captions, hashtags, ctaText, sceneText, subText에는 지역 표현을 반복하지 마세요.\n"
                "- '서울숲', '서울숲 근처', '서울숲 인근', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 nearby/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- difference는 위치 설명 대신 맛, 질감, 재료 조합, 신메뉴 포인트만 남기세요.\n"
                "- 긴 메뉴 설명은 subText로 보내고, primaryText는 poster headline처럼 짧게 유지하세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 새로운 카페 메뉴를 찾는 20~30대 방문객입니다.\n"
                "friendly 톤은 과장된 B급보다 가볍게 권하는 한 줄 추천처럼 들려야 합니다.\n"
                "hook은 첫 공개 느낌이나 궁금증을 짧게 던지고, difference는 메뉴 포인트를 바로 이해되게 쓰세요.\n"
                "지역을 더 쓰고 싶어지면 추가 위치 정보로 새지 말고, 그 자리를 메뉴 특징이나 한 줄 추천 이유로 바꾸세요."
            ),
        )
        new_menu_shorter_copy_variant = PromptVariant(
            variant_id="new_menu_friendly_region_anchor_shorter_copy_gpt5mini",
            lever_id="shorter_copy",
            changed_field="slot_guidance",
            description="gpt-5-mini에서 new_menu strict region anchor를 유지한 채 shorterCopy=true budget을 더 강하게 명시하는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_new_menu_shorter_copy_region_anchor_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 10~12자 안팎으로 유지하고, 13자를 넘기지 마세요.\n"
                "- product_name primaryText와 difference primaryText는 10~12자 안팎으로 유지하고, 13자를 넘기지 마세요.\n"
                "- cta primaryText는 6~8자 안팎으로 유지하세요.\n"
                "- cta와 ctaText는 확인, 주문, 저장, 방문 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option shorterCopy=true이므로 설명을 길게 늘이지 말고, 각 장면에는 한 가지 정보만 남기세요.\n"
                "- subText를 쓰더라도 한 줄 보조 문구만 허용하고, 쉼표로 설명을 길게 잇지 마세요.\n"
                "- captions도 한 문장 한 포인트만 남기고, 긴 배경 설명이나 감탄사 반복을 넣지 마세요.\n"
                "- quick option emphasizeRegion=true는 regionName을 더 분명하게 쓰라는 뜻이지, 상세 위치를 공개하라는 뜻이 아닙니다.\n"
                "- 문자열 '성수동'은 hookText에 1회, captions 3개 중 정확히 1개 caption에 1회, hashtags 중 정확히 1개 hashtag에 1회만 쓰세요.\n"
                "- 위 3곳을 제외한 다른 captions, hashtags, ctaText, sceneText, subText에는 지역 표현을 반복하지 마세요.\n"
                "- '서울숲', '서울숲 근처', '서울숲 인근', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 nearby/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- difference는 위치 설명 대신 메뉴 특징, 맛, 조합만 짧게 남기고, 긴 부연 설명은 지우세요.\n"
                "- 더 쓰고 싶어지면 지역이나 배경 설명이 아니라 메뉴 포인트를 한 단어 더 선명하게 바꾸세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 새로운 카페 메뉴를 찾는 20~30대 방문객입니다.\n"
                "friendly 톤은 과장보다 가볍고 또렷한 추천처럼 들려야 합니다.\n"
                "shorterCopy=true일 때는 첫인상, 메뉴 포인트, 행동만 남기고 군더더기 설명은 빼는 편이 맞습니다.\n"
                "지역을 더 쓰고 싶어지면 상세 위치로 새지 말고, 그 자리를 메뉴 특징이나 한 줄 추천 이유로 바꾸세요."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-156",
            experiment_title="GPT-5 Mini New Menu Shorter Copy Region Anchor",
            objective="T01 new_menu, friendly, highlightPrice=false, shorterCopy=true, emphasizeRegion=true에서 gpt-5-mini를 고정한 채 existing strict region anchor prompt 위에 shorterCopy=true budget을 추가하면 option profile로 승격 가능한지 확인합니다.",
            scenario=get_new_menu_shorter_copy_region_anchor_scenario(),
            model=ModelConfig(provider="openai", model_name="gpt-5-mini"),
            baseline_variant=new_menu_region_anchor_baseline_variant,
            candidate_variants=(new_menu_shorter_copy_variant,),
        )

    if experiment_id == "EXP-165":
        new_menu_highlight_price_baseline_variant = PromptVariant(
            variant_id="new_menu_friendly_region_anchor_highlight_price_baseline_gpt5mini",
            lever_id="baseline",
            changed_field="none",
            description="gpt-5-mini에서 new_menu_friendly_strict_region_anchor prompt를 highlightPrice=true scenario에 baseline으로 재사용합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_new_menu_highlight_price_region_anchor_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- product_name primaryText와 difference primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- cta primaryText는 8~10자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 확인, 주문, 저장, 방문 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option emphasizeRegion=true는 regionName을 더 분명하게 쓰라는 뜻이지, 상세 위치를 공개하라는 뜻이 아닙니다.\n"
                "- 문자열 '성수동'은 hookText에 1회, captions 3개 중 정확히 1개 caption에 1회, hashtags 중 정확히 1개 hashtag에 1회만 쓰세요.\n"
                "- 위 3곳을 제외한 다른 captions, hashtags, ctaText, sceneText, subText에는 지역 표현을 반복하지 마세요.\n"
                "- '서울숲', '서울숲 근처', '서울숲 인근', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 nearby/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- difference는 위치 설명 대신 맛, 질감, 재료 조합, 신메뉴 포인트만 남기세요.\n"
                "- 긴 메뉴 설명은 subText로 보내고, primaryText는 poster headline처럼 짧게 유지하세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 새로운 카페 메뉴를 찾는 20~30대 방문객입니다.\n"
                "friendly 톤은 과장된 B급보다 가볍게 권하는 한 줄 추천처럼 들려야 합니다.\n"
                "hook은 첫 공개 느낌이나 궁금증을 짧게 던지고, difference는 메뉴 포인트를 바로 이해되게 쓰세요.\n"
                "지역을 더 쓰고 싶어지면 추가 위치 정보로 새지 말고, 그 자리를 메뉴 특징이나 한 줄 추천 이유로 바꾸세요."
            ),
        )
        new_menu_highlight_price_variant = PromptVariant(
            variant_id="new_menu_friendly_region_anchor_highlight_price_gpt5mini",
            lever_id="highlight_price",
            changed_field="slot_guidance",
            description="gpt-5-mini에서 new_menu strict region anchor를 유지한 채 highlightPrice=true를 가격 환각 없이 body 가치 포인트 강조로 해석하는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_new_menu_highlight_price_region_anchor_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- product_name primaryText와 difference primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- cta primaryText는 8~10자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 확인, 주문, 저장, 방문 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option highlightPrice=true는 body와 difference에서 가격 또는 가치 포인트를 더 또렷하게 보이게 정리하라는 뜻입니다.\n"
                "- 다만 입력에 명시된 가격 숫자, 할인폭, 세트 정보가 없으면 새로운 가격 숫자, 할인율, 특가 문구를 만들지 마세요.\n"
                "- 숫자가 없는 상황에서는 difference, subText, caption에서 신메뉴 구성, 재료 조합, 함께 주문할 이유, 한정 포인트를 가치 포인트처럼 더 선명하게 쓰세요.\n"
                "- '#가성비', '#특가', '#할인', '#세일', '#만원대'처럼 가격 foreground 뉘앙스를 새로 만드는 hashtag는 쓰지 마세요.\n"
                "- quick option emphasizeRegion=true는 regionName을 더 분명하게 쓰라는 뜻이지, 상세 위치를 공개하라는 뜻이 아닙니다.\n"
                "- 문자열 '성수동'은 hookText에 1회, captions 3개 중 정확히 1개 caption에 1회, hashtags 중 정확히 1개 hashtag에 1회만 쓰세요.\n"
                "- 위 3곳을 제외한 다른 captions, hashtags, ctaText, sceneText, subText에는 지역 표현을 반복하지 마세요.\n"
                "- '서울숲', '서울숲 근처', '서울숲 인근', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 nearby/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- difference는 위치 설명 대신 메뉴 특징, 조합, 가치 포인트만 남기고, 숫자 없는 가격 추측으로 채우지 마세요.\n"
                "- 긴 메뉴 설명은 subText로 보내고, primaryText는 poster headline처럼 짧게 유지하세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 새로운 카페 메뉴를 찾는 20~30대 방문객입니다.\n"
                "friendly 톤은 과장보다 가볍고 또렷한 추천처럼 들려야 합니다.\n"
                "highlightPrice=true라도 숫자 가격이 없는 입력에서는 가격을 지어내지 말고, 신메뉴를 왜 한번 시켜볼 만한지 가치 포인트를 더 분명하게 보여주는 편이 맞습니다.\n"
                "지역을 더 쓰고 싶어지면 상세 위치로 새지 말고, 그 자리를 메뉴 특징, 조합, 함께 주문할 이유로 바꾸세요."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-165",
            experiment_title="GPT-5 Mini New Menu Highlight Price Region Anchor",
            objective="T01 new_menu, friendly, highlightPrice=true, shorterCopy=false, emphasizeRegion=true에서 gpt-5-mini를 고정한 채 strict region anchor baseline 위에 no-price-hallucination value emphasis를 추가하면 option profile로 승격 가능한지 확인합니다.",
            scenario=get_new_menu_highlight_price_region_anchor_scenario(),
            model=ModelConfig(provider="openai", model_name="gpt-5-mini"),
            baseline_variant=new_menu_highlight_price_baseline_variant,
            candidate_variants=(new_menu_highlight_price_variant,),
        )

    if experiment_id == "EXP-169":
        new_menu_combined_baseline_variant = PromptVariant(
            variant_id="new_menu_friendly_region_anchor_shorter_copy_baseline_highlight_price_gpt5mini",
            lever_id="baseline",
            changed_field="none",
            description="gpt-5-mini에서 new_menu_friendly_region_anchor_shorter_copy prompt를 highlightPrice=true + shorterCopy=true scenario에 baseline으로 재사용합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_new_menu_highlight_price_shorter_copy_region_anchor_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 10~12자 안팎으로 유지하고, 13자를 넘기지 마세요.\n"
                "- product_name primaryText와 difference primaryText는 10~12자 안팎으로 유지하고, 13자를 넘기지 마세요.\n"
                "- cta primaryText는 6~8자 안팎으로 유지하세요.\n"
                "- cta와 ctaText는 확인, 주문, 저장, 방문 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option shorterCopy=true이므로 설명을 길게 늘이지 말고, 각 장면에는 한 가지 정보만 남기세요.\n"
                "- subText를 쓰더라도 한 줄 보조 문구만 허용하고, 쉼표로 설명을 길게 잇지 마세요.\n"
                "- captions도 한 문장 한 포인트만 남기고, 긴 배경 설명이나 감탄사 반복을 넣지 마세요.\n"
                "- quick option emphasizeRegion=true는 regionName을 더 분명하게 쓰라는 뜻이지, 상세 위치를 공개하라는 뜻이 아닙니다.\n"
                "- 문자열 '성수동'은 hookText에 1회, captions 3개 중 정확히 1개 caption에 1회, hashtags 중 정확히 1개 hashtag에 1회만 쓰세요.\n"
                "- 위 3곳을 제외한 다른 captions, hashtags, ctaText, sceneText, subText에는 지역 표현을 반복하지 마세요.\n"
                "- '서울숲', '서울숲 근처', '서울숲 인근', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 nearby/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- difference는 위치 설명 대신 메뉴 특징, 맛, 조합만 짧게 남기고, 긴 부연 설명은 지우세요.\n"
                "- 더 쓰고 싶어지면 지역이나 배경 설명이 아니라 메뉴 포인트를 한 단어 더 선명하게 바꾸세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 새로운 카페 메뉴를 찾는 20~30대 방문객입니다.\n"
                "friendly 톤은 과장보다 가볍고 또렷한 추천처럼 들려야 합니다.\n"
                "shorterCopy=true일 때는 첫인상, 메뉴 포인트, 행동만 남기고 군더더기 설명은 빼는 편이 맞습니다.\n"
                "지역을 더 쓰고 싶어지면 상세 위치로 새지 말고, 그 자리를 메뉴 특징이나 한 줄 추천 이유로 바꾸세요."
            ),
        )
        new_menu_combined_variant = PromptVariant(
            variant_id="new_menu_friendly_region_anchor_highlight_price_shorter_copy_gpt5mini",
            lever_id="highlight_price_shorter_copy",
            changed_field="slot_guidance",
            description="gpt-5-mini에서 new_menu shorterCopy profile 위에 highlightPrice=true를 숫자 가격 환각 없는 단일 가치 포인트 강조로 결합하는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_new_menu_highlight_price_shorter_copy_region_anchor_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 10~12자 안팎으로 유지하고, 13자를 넘기지 마세요.\n"
                "- product_name primaryText와 difference primaryText는 10~12자 안팎으로 유지하고, 13자를 넘기지 마세요.\n"
                "- cta primaryText는 6~8자 안팎으로 유지하세요.\n"
                "- cta와 ctaText는 확인, 주문, 저장, 방문 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option shorterCopy=true이므로 hook, product_name, difference, cta 각각 한 포인트만 남기고, 한 줄 안에 두 가지 메시지를 몰아넣지 마세요.\n"
                "- quick option highlightPrice=true는 difference와 subText에서 가격 또는 가치 포인트가 먼저 읽히게 정리하라는 뜻입니다.\n"
                "- 다만 입력에 명시된 가격 숫자, 할인폭, 세트 정보가 없으면 새로운 가격 숫자, 할인율, 특가, 세일, 가성비 문구를 만들지 마세요.\n"
                "- 숫자가 없는 상황에서는 신메뉴 구성, 재료 조합, 디저트와 함께 주문할 이유, 한 번 시켜볼 만한 포인트 중 딱 하나만 골라 difference와 caption에 짧게 남기세요.\n"
                "- subText를 쓰더라도 한 줄 보조 문구만 허용하고, 가치 포인트도 한 줄에 한 가지 근거만 남기세요.\n"
                "- captions도 각 한 문장 한 포인트만 남기고, 긴 배경 설명이나 감탄사 반복을 넣지 마세요.\n"
                "- '#가성비', '#특가', '#할인', '#세일', '#만원대'처럼 가격 foreground 뉘앙스를 새로 만드는 hashtag는 쓰지 마세요.\n"
                "- quick option emphasizeRegion=true는 regionName을 더 분명하게 쓰라는 뜻이지, 상세 위치를 공개하라는 뜻이 아닙니다.\n"
                "- 문자열 '성수동'은 hookText에 1회, captions 3개 중 정확히 1개 caption에 1회, hashtags 중 정확히 1개 hashtag에 1회만 쓰세요.\n"
                "- 위 3곳을 제외한 다른 captions, hashtags, ctaText, sceneText, subText에는 지역 표현을 반복하지 마세요.\n"
                "- '서울숲', '서울숲 근처', '서울숲 인근', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 nearby/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- difference는 위치 설명 대신 메뉴 특징 또는 가치 포인트 한 가지로만 채우고, 숫자 없는 가격 추측으로 채우지 마세요.\n"
                "- 더 쓰고 싶어지면 가격이나 위치를 늘리지 말고, 이미 고른 가치 포인트를 한 단어 더 선명하게 다듬으세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 새로운 카페 메뉴를 찾는 20~30대 방문객입니다.\n"
                "friendly 톤은 과장보다 가볍고 또렷한 추천처럼 들려야 합니다.\n"
                "shorterCopy=true와 highlightPrice=true가 같이 오면 길게 설명하는 대신, 왜 한번 시켜볼 만한지 한 줄 가치 포인트를 먼저 보이게 쓰는 편이 맞습니다.\n"
                "지역을 더 쓰고 싶어지면 상세 위치로 새지 말고, 그 자리를 메뉴 특징, 조합, 함께 주문할 이유 중 하나로 바꾸세요."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-169",
            experiment_title="GPT-5 Mini New Menu Highlight Price Shorter Copy Region Anchor",
            objective="T01 new_menu, friendly, highlightPrice=true, shorterCopy=true, emphasizeRegion=true에서 gpt-5-mini를 고정한 채 shorterCopy profile 위에 no-price-hallucination value emphasis를 결합하면 combined option profile로 승격 가능한지 확인합니다.",
            scenario=get_new_menu_highlight_price_shorter_copy_region_anchor_scenario(),
            model=ModelConfig(provider="openai", model_name="gpt-5-mini"),
            baseline_variant=new_menu_combined_baseline_variant,
            candidate_variants=(new_menu_combined_variant,),
        )

    if experiment_id == "EXP-173":
        review_shorter_copy_off_baseline_variant = PromptVariant(
            variant_id="review_surface_locked_shorter_copy_off_baseline_gpt5mini",
            lever_id="baseline",
            changed_field="none",
            description="gpt-5-mini에서 review_surface_locked_exact_region_anchor prompt를 shorterCopy=false scenario에 baseline으로 재사용합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_review_shorter_copy_off_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 review_quote primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- product_name primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- cta primaryText는 8~10자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 저장, 방문, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- captions 3개 중 정확히 1개 caption에만 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- 그 1개 caption을 제외한 다른 captions, hookText, ctaText, sceneText, subText, hashtags에는 위치 표현을 넣지 마세요.\n"
                "- 특히 '서울숲', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 landmark/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- region hashtag는 정확히 1개만 쓰고, 반드시 '#성수동'만 허용합니다.\n"
                "- product_name, review_quote, subText에는 위치 단서를 절대 넣지 말고 맛, 질감, 재방문 이유만 쓰세요.\n"
                "- 위치를 더 쓰고 싶어지면 그 자리를 메뉴 장점이나 재방문 이유로 바꾸세요.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 믿고 갈 한 끼를 찾는 20~30대 방문객입니다.\n"
                "B급 감성 review는 친구가 채팅방에 바로 던지는 한 줄 제보처럼 들려야 합니다.\n"
                "review_quote는 짧고 말맛 있게, product_name은 다시 찾는 이유가 한 번에 보이게 쓰세요.\n"
                "cta는 감탄사보다 행동 단어를 앞쪽에 두고 짧게 마무리하세요."
            ),
        )
        review_shorter_copy_off_variant = PromptVariant(
            variant_id="review_surface_locked_exact_region_anchor_shorter_copy_off",
            lever_id="shorter_copy_off",
            changed_field="slot_guidance",
            description="gpt-5-mini에서 review surface-lock을 유지한 채 shorterCopy=false 설명 여유를 재방문 이유 쪽으로만 허용하는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_review_shorter_copy_off_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 review_quote primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- product_name primaryText는 12~16자 안팎으로 유지하세요.\n"
                "- cta primaryText는 8~10자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 저장, 방문, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option shorterCopy=false는 설명을 한 줄 더 허용한다는 뜻이지, 위치나 감탄사를 늘리라는 뜻이 아닙니다.\n"
                "- review_quote나 subText에는 한 줄 정도의 추가 설명을 붙여도 되지만, 그 설명은 맛, 식감, 재방문 이유, 같이 곁들이기 좋은 이유만 다뤄야 합니다.\n"
                "- captions 3개 중 정확히 1개 caption에만 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- 그 1개 caption을 제외한 다른 captions, hookText, ctaText, sceneText, subText, hashtags에는 위치 표현을 넣지 마세요.\n"
                "- 특히 '서울숲', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 landmark/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- region hashtag는 정확히 1개만 쓰고, 반드시 '#성수동'만 허용합니다.\n"
                "- product_name, review_quote, subText에는 위치 단서를 절대 넣지 말고 맛, 질감, 재방문 이유만 쓰세요.\n"
                "- 긴 설명을 붙일 때도 한 surface에 한 가지 이유만 남기고, 같은 의미를 hook/caption/subText에서 반복하지 마세요.\n"
                "- 위치를 더 쓰고 싶어지면 그 자리를 메뉴 장점, 식감, 다시 찾는 이유로 바꾸세요.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 믿고 갈 한 끼를 찾는 20~30대 방문객입니다.\n"
                "B급 감성 review는 친구가 채팅방에 바로 던지는 한 줄 제보처럼 들려야 합니다.\n"
                "shorterCopy=false일 때도 장황한 후기보다, 왜 다시 갈지 한 줄 근거가 더 먼저 읽히는 편이 맞습니다.\n"
                "설명을 더 쓰고 싶어지면 위치 대신 식감, 만족감, 재주문 이유 쪽으로만 확장하세요."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-173",
            experiment_title="GPT-5 Mini Review Shorter Copy Off Surface Lock",
            objective="T04 review, b_grade_fun, highlightPrice=false, shorterCopy=false, emphasizeRegion=false에서 gpt-5-mini를 고정한 채 review surface-lock baseline 위에 shorterCopy=false 설명 여유를 추가하면 option profile로 승격 가능한지 확인합니다.",
            scenario=get_service_aligned_bgrade_review_shorter_copy_off_scenario(),
            model=ModelConfig(provider="openai", model_name="gpt-5-mini"),
            baseline_variant=review_shorter_copy_off_baseline_variant,
            candidate_variants=(review_shorter_copy_off_variant,),
        )

    if experiment_id == "EXP-177":
        review_highlight_price_shorter_copy_off_baseline_variant = PromptVariant(
            variant_id="review_surface_locked_highlight_price_shorter_copy_off_baseline_gpt5mini",
            lever_id="baseline",
            changed_field="none",
            description="gpt-5-mini에서 review_surface_locked_exact_region_anchor_shorter_copy_off prompt를 highlightPrice=true + shorterCopy=false scenario에 baseline으로 재사용합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_review_highlight_price_shorter_copy_off_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 review_quote primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- product_name primaryText는 12~16자 안팎으로 유지하세요.\n"
                "- cta primaryText는 8~10자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 저장, 방문, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option shorterCopy=false는 설명을 한 줄 더 허용한다는 뜻이지, 위치나 감탄사를 늘리라는 뜻이 아닙니다.\n"
                "- review_quote나 subText에는 한 줄 정도의 추가 설명을 붙여도 되지만, 그 설명은 맛, 식감, 재방문 이유, 같이 곁들이기 좋은 이유만 다뤄야 합니다.\n"
                "- captions 3개 중 정확히 1개 caption에만 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- 그 1개 caption을 제외한 다른 captions, hookText, ctaText, sceneText, subText, hashtags에는 위치 표현을 넣지 마세요.\n"
                "- 특히 '서울숲', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 landmark/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- region hashtag는 정확히 1개만 쓰고, 반드시 '#성수동'만 허용합니다.\n"
                "- product_name, review_quote, subText에는 위치 단서를 절대 넣지 말고 맛, 질감, 재방문 이유만 쓰세요.\n"
                "- 긴 설명을 붙일 때도 한 surface에 한 가지 이유만 남기고, 같은 의미를 hook/caption/subText에서 반복하지 마세요.\n"
                "- 위치를 더 쓰고 싶어지면 그 자리를 메뉴 장점, 식감, 다시 찾는 이유로 바꾸세요.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 믿고 갈 한 끼를 찾는 20~30대 방문객입니다.\n"
                "B급 감성 review는 친구가 채팅방에 바로 던지는 한 줄 제보처럼 들려야 합니다.\n"
                "shorterCopy=false일 때도 장황한 후기보다, 왜 다시 갈지 한 줄 근거가 더 먼저 읽히는 편이 맞습니다.\n"
                "설명을 더 쓰고 싶어지면 위치 대신 식감, 만족감, 재주문 이유 쪽으로만 확장하세요."
            ),
        )
        review_highlight_price_shorter_copy_off_variant = PromptVariant(
            variant_id="review_surface_locked_highlight_price_shorter_copy_off",
            lever_id="highlight_price",
            changed_field="slot_guidance",
            description="gpt-5-mini에서 review shorterCopy=false surface-lock을 유지한 채 highlightPrice=true를 숫자 환각 없는 가치 근거 foreground로 해석하는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_review_highlight_price_shorter_copy_off_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 review_quote primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- product_name primaryText는 12~16자 안팎으로 유지하세요.\n"
                "- cta primaryText는 8~10자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 저장, 방문, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option shorterCopy=false는 설명을 한 줄 더 허용한다는 뜻이지, 위치나 감탄사를 늘리라는 뜻이 아닙니다.\n"
                "- quick option highlightPrice=true는 review 템플릿에서 가격 숫자를 새로 쓰라는 뜻이 아니라, 한 끼 만족감이나 다시 갈 이유가 더 값어치 있게 느껴지도록 정리하라는 뜻입니다.\n"
                "- 입력에 가격 숫자, 할인율, 특가 문구가 없으면 새로운 숫자, 할인, 세일, 쿠폰, 가성비 문구를 만들지 마세요.\n"
                "- review_quote, product_name, subText 중 한 surface 정도에는 값어치가 느껴지는 이유를 먼저 읽히게 하되, 그 이유는 맛, 양감, 식감, 조합, 재방문 만족감 중 하나로만 설명하세요.\n"
                "- '돈값', '가성비', '특가' 같은 노골적 가격 키워드를 반복하지 말고, 만족감이나 또 시킬 이유가 자연스럽게 읽히는 문장으로 바꾸세요.\n"
                "- captions 3개 중 정확히 1개 caption에만 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- 그 1개 caption을 제외한 다른 captions, hookText, ctaText, sceneText, subText, hashtags에는 위치 표현을 넣지 마세요.\n"
                "- 특히 '서울숲', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 landmark/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- region hashtag는 정확히 1개만 쓰고, 반드시 '#성수동'만 허용합니다.\n"
                "- product_name, review_quote, subText에는 위치 단서를 절대 넣지 말고 맛, 질감, 재방문 이유만 쓰세요.\n"
                "- 긴 설명을 붙일 때도 한 surface에 한 가지 이유만 남기고, 같은 의미를 hook/caption/subText에서 반복하지 마세요.\n"
                "- 위치를 더 쓰고 싶어지면 그 자리를 메뉴 장점, 식감, 다시 찾는 이유로 바꾸세요.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 믿고 갈 한 끼를 찾는 20~30대 방문객입니다.\n"
                "B급 감성 review는 친구가 채팅방에 바로 던지는 한 줄 제보처럼 들려야 합니다.\n"
                "highlightPrice=true라도 리뷰 템플릿에서는 가격 숫자보다 왜 이 집이 값어치 있게 느껴졌는지 한 줄 근거가 먼저 읽혀야 합니다.\n"
                "가격을 더 쓰고 싶어지면 그 자리를 식감, 만족감, 다시 찾는 이유로 바꾸세요."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-177",
            experiment_title="GPT-5 Mini Review Highlight Price Shorter Copy Off Surface Lock",
            objective="T04 review, b_grade_fun, highlightPrice=true, shorterCopy=false, emphasizeRegion=false에서 gpt-5-mini를 고정한 채 review shorterCopy=false surface-lock 위에 no-price-hallucination value emphasis를 결합하면 option profile로 승격 가능한지 확인합니다.",
            scenario=get_service_aligned_bgrade_review_highlight_price_shorter_copy_off_scenario(),
            model=ModelConfig(provider="openai", model_name="gpt-5-mini"),
            baseline_variant=review_highlight_price_shorter_copy_off_baseline_variant,
            candidate_variants=(review_highlight_price_shorter_copy_off_variant,),
        )

    if experiment_id == "EXP-181":
        review_highlight_price_baseline_variant = PromptVariant(
            variant_id="review_surface_locked_highlight_price_baseline_gpt5mini",
            lever_id="baseline",
            changed_field="none",
            description="gpt-5-mini에서 review_surface_locked_exact_region_anchor prompt를 highlightPrice=true + shorterCopy=true scenario에 baseline으로 재사용합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_review_highlight_price_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 review_quote primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- product_name primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- cta primaryText는 8~10자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 저장, 방문, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- captions 3개 중 정확히 1개 caption에만 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- 그 1개 caption을 제외한 다른 captions, hookText, ctaText, sceneText, subText, hashtags에는 위치 표현을 넣지 마세요.\n"
                "- 특히 '서울숲', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 landmark/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- region hashtag는 정확히 1개만 쓰고, 반드시 '#성수동'만 허용합니다.\n"
                "- product_name, review_quote, subText에는 위치 단서를 절대 넣지 말고 맛, 질감, 재방문 이유만 쓰세요.\n"
                "- 위치를 더 쓰고 싶어지면 그 자리를 메뉴 장점이나 재방문 이유로 바꾸세요.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 믿고 갈 한 끼를 찾는 20~30대 방문객입니다.\n"
                "B급 감성 review는 친구가 채팅방에 바로 던지는 한 줄 제보처럼 들려야 합니다.\n"
                "review_quote는 짧고 말맛 있게, product_name은 다시 찾는 이유가 한 번에 보이게 쓰세요.\n"
                "cta는 감탄사보다 행동 단어를 앞쪽에 두고 짧게 마무리하세요."
            ),
        )
        review_highlight_price_variant = PromptVariant(
            variant_id="review_surface_locked_highlight_price",
            lever_id="highlight_price",
            changed_field="slot_guidance",
            description="gpt-5-mini에서 review surface-lock을 유지한 채 highlightPrice=true를 짧은 value foreground로 해석하는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_review_highlight_price_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 review_quote primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- product_name primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- cta primaryText는 8~10자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 저장, 방문, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option shorterCopy=true이므로 hook, review_quote, product_name, cta 각각 한 가지 정보만 짧게 남기세요.\n"
                "- subText를 쓰더라도 한 줄 보조 문구만 허용하고, 쉼표로 설명을 길게 잇지 마세요.\n"
                "- quick option highlightPrice=true는 review 템플릿에서 가격 숫자를 새로 쓰라는 뜻이 아니라, 만족감이나 다시 갈 이유가 더 값어치 있게 느껴지도록 정리하라는 뜻입니다.\n"
                "- 입력에 가격 숫자, 할인율, 특가 문구가 없으면 새로운 숫자, 할인, 세일, 쿠폰, 가성비 문구를 만들지 마세요.\n"
                "- review_quote, product_name, subText 중 한 surface 정도에는 값어치가 느껴지는 이유를 먼저 읽히게 하되, 그 이유는 맛, 식감, 양감, 조합, 재방문 만족감 중 하나로만 설명하세요.\n"
                "- '돈값', '가성비', '특가' 같은 노골적 가격 키워드를 반복하지 말고, 만족감이나 또 갈 이유가 자연스럽게 읽히는 문장으로 바꾸세요.\n"
                "- captions 3개 중 정확히 1개 caption에만 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- 그 1개 caption을 제외한 다른 captions, hookText, ctaText, sceneText, subText, hashtags에는 위치 표현을 넣지 마세요.\n"
                "- 특히 '서울숲', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 landmark/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- region hashtag는 정확히 1개만 쓰고, 반드시 '#성수동'만 허용합니다.\n"
                "- product_name, review_quote, subText에는 위치 단서를 절대 넣지 말고 맛, 질감, 재방문 이유만 쓰세요.\n"
                "- 긴 설명을 붙이고 싶어지면 그 자리를 더 짧은 만족감 근거 한 줄로 줄이세요.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 믿고 갈 한 끼를 찾는 20~30대 방문객입니다.\n"
                "B급 감성 review는 친구가 채팅방에 바로 던지는 한 줄 제보처럼 들려야 합니다.\n"
                "highlightPrice=true라도 리뷰 템플릿에서는 가격 숫자보다 왜 이 집이 값어치 있게 느껴졌는지 짧게 먼저 읽혀야 합니다.\n"
                "문장이 길어지면 가격을 더 쓰지 말고 만족감 근거를 한 줄로 압축하세요."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-181",
            experiment_title="GPT-5 Mini Review Highlight Price Surface Lock",
            objective="T04 review, b_grade_fun, highlightPrice=true, shorterCopy=true, emphasizeRegion=false에서 gpt-5-mini를 고정한 채 review surface-lock 위에 no-price-hallucination value emphasis를 결합하면 option profile로 승격 가능한지 확인합니다.",
            scenario=get_service_aligned_bgrade_review_highlight_price_scenario(),
            model=ModelConfig(provider="openai", model_name="gpt-5-mini"),
            baseline_variant=review_highlight_price_baseline_variant,
            candidate_variants=(review_highlight_price_variant,),
        )

    if experiment_id == "EXP-213":
        review_region_baseline_variant = PromptVariant(
            variant_id="review_surface_locked_region_baseline_gpt5mini",
            lever_id="baseline",
            changed_field="none",
            description="gpt-5-mini에서 review_surface_locked_exact_region_anchor prompt를 emphasizeRegion=true scenario에 baseline으로 재사용합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_review_region_emphasis_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 review_quote primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- product_name primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- cta primaryText는 8~10자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 저장, 방문, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option emphasizeRegion=true는 regionName을 더 분명하게 쓰라는 뜻이지, 상세 위치를 공개하라는 뜻이 아닙니다.\n"
                "- 문자열 '성수동'은 captions 3개 중 정확히 1개 caption에 1회, hashtags 중 정확히 1개 hashtag에 1회만 쓰세요.\n"
                "- 위 2곳을 제외한 다른 captions, hookText, review_quote primaryText, product_name primaryText, ctaText, sceneText, subText에는 지역 표현을 넣지 마세요.\n"
                "- region hashtag는 정확히 1개만 쓰고, 반드시 '#성수동'만 허용합니다.\n"
                "- '서울숲', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 landmark/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- product_name, review_quote, subText에는 위치 단서를 절대 넣지 말고 맛, 질감, 재방문 이유만 쓰세요.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 믿고 갈 한 끼를 찾는 20~30대 방문객입니다.\n"
                "B급 감성 review는 친구가 채팅방에 바로 던지는 한 줄 제보처럼 들려야 합니다.\n"
                "emphasizeRegion=true여도 review 본문을 지역 설명으로 채우기보다, 메뉴 만족감과 다시 갈 이유가 먼저 읽혀야 합니다.\n"
                "지역을 더 쓰고 싶어지면 상세 위치로 새지 말고, 더 짧고 또렷한 한 줄 제보로 압축하세요."
            ),
        )
        review_region_anchor_variant = PromptVariant(
            variant_id="review_surface_locked_region_anchor",
            lever_id="region_anchor",
            changed_field="slot_guidance",
            description="gpt-5-mini에서 review surface-lock을 유지한 채 emphasizeRegion=true를 hookText first-anchor로만 올리는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_review_region_emphasis_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 review_quote primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- product_name primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- cta primaryText는 8~10자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 저장, 방문, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option shorterCopy=true이므로 hook, review_quote, product_name, cta 각각 한 가지 정보만 짧게 남기세요.\n"
                "- quick option emphasizeRegion=true이므로 regionName은 hookText에서만 분명하게 드러나게 쓰세요.\n"
                "- 문자열 '성수동'은 hookText에 1회, hashtags 중 정확히 1개 hashtag에 1회만 쓰고, captions에는 넣지 마세요.\n"
                "- hookText와 '#성수동'을 제외한 다른 captions, review_quote primaryText, product_name primaryText, ctaText, sceneText, subText, hashtags에는 지역 표현을 넣지 마세요.\n"
                "- region hashtag는 정확히 1개만 쓰고, 반드시 '#성수동'만 허용합니다.\n"
                "- '서울숲', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 landmark/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- product_name, review_quote, subText에는 위치 단서를 절대 넣지 말고 맛, 질감, 재방문 이유만 쓰세요.\n"
                "- 지역을 더 쓰고 싶어지면 nearby landmark로 확장하지 말고, hook 한 줄의 지역 anchor를 더 또렷하게 다듬으세요.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 믿고 갈 한 끼를 찾는 20~30대 방문객입니다.\n"
                "B급 감성 review는 친구가 채팅방에 바로 던지는 한 줄 제보처럼 들려야 합니다.\n"
                "emphasizeRegion=true일 때도 좋은 방식은 첫 훅에서만 성수동 anchor를 짧게 주고, 본문은 계속 메뉴 만족감에 집중하는 것입니다.\n"
                "지역 훅 하나와 재방문 이유 하나를 분리해 읽히게 정리하세요."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-213",
            experiment_title="GPT-5 Mini Review Region Anchor",
            objective="T04 review, b_grade_fun, highlightPrice=false, shorterCopy=true, emphasizeRegion=true에서 gpt-5-mini를 고정한 채 review surface-lock baseline 위에 safe region anchor를 추가하면 option profile로 승격 가능한지 확인합니다.",
            scenario=get_service_aligned_bgrade_review_region_emphasis_scenario(),
            model=ModelConfig(provider="openai", model_name="gpt-5-mini"),
            baseline_variant=review_region_baseline_variant,
            candidate_variants=(review_region_anchor_variant,),
        )

    if experiment_id == "EXP-215":
        review_shorter_copy_off_region_baseline_variant = PromptVariant(
            variant_id="review_surface_locked_shorter_copy_off_region_baseline_gpt5mini",
            lever_id="baseline",
            changed_field="none",
            description="gpt-5-mini에서 review_surface_locked_exact_region_anchor_shorter_copy_off prompt를 emphasizeRegion=true scenario에 baseline으로 재사용합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_review_shorter_copy_off_region_emphasis_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 review_quote primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- product_name primaryText는 12~16자 안팎으로 유지하세요.\n"
                "- cta primaryText는 8~10자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 저장, 방문, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option shorterCopy=false는 설명을 한 줄 더 허용한다는 뜻이지, 위치나 감탄사를 늘리라는 뜻이 아닙니다.\n"
                "- review_quote나 subText에는 한 줄 정도의 추가 설명을 붙여도 되지만, 그 설명은 맛, 식감, 재방문 이유, 같이 곁들이기 좋은 이유만 다뤄야 합니다.\n"
                "- quick option emphasizeRegion=true는 regionName을 더 분명하게 쓰라는 뜻이지, 상세 위치를 공개하라는 뜻이 아닙니다.\n"
                "- 문자열 '성수동'은 captions 3개 중 정확히 1개 caption에 1회, hashtags 중 정확히 1개 hashtag에 1회만 쓰세요.\n"
                "- 위 2곳을 제외한 다른 captions, hookText, review_quote primaryText, product_name primaryText, ctaText, sceneText, subText에는 지역 표현을 넣지 마세요.\n"
                "- region hashtag는 정확히 1개만 쓰고, 반드시 '#성수동'만 허용합니다.\n"
                "- '서울숲', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 landmark/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- product_name, review_quote, subText에는 위치 단서를 절대 넣지 말고 맛, 질감, 재방문 이유만 쓰세요.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 믿고 갈 한 끼를 찾는 20~30대 방문객입니다.\n"
                "B급 감성 review는 친구가 채팅방에 바로 던지는 한 줄 제보처럼 들려야 합니다.\n"
                "shorterCopy=false일 때도 설명 여유는 위치가 아니라 맛, 만족감, 재방문 이유를 붙이는 데만 써야 합니다.\n"
                "지역을 더 쓰고 싶어지면 훅을 더 짧고 선명하게 다듬는 편이 맞습니다."
            ),
        )
        review_shorter_copy_off_region_anchor_variant = PromptVariant(
            variant_id="review_surface_locked_shorter_copy_off_region_anchor",
            lever_id="region_anchor",
            changed_field="slot_guidance",
            description="gpt-5-mini에서 review shorterCopy=false surface-lock을 유지한 채 emphasizeRegion=true를 hookText first-anchor로만 올리는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_review_shorter_copy_off_region_emphasis_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 review_quote primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- product_name primaryText는 12~16자 안팎으로 유지하세요.\n"
                "- cta primaryText는 8~10자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 저장, 방문, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option shorterCopy=false는 설명을 허용하지만, 그 설명은 위치 확장이 아니라 맛, 식감, 재방문 이유에만 쓰세요.\n"
                "- quick option emphasizeRegion=true이므로 regionName은 hookText에서만 분명하게 드러나게 쓰세요.\n"
                "- 문자열 '성수동'은 hookText에 1회, hashtags 중 정확히 1개 hashtag에 1회만 쓰고, captions에는 넣지 마세요.\n"
                "- hookText와 '#성수동'을 제외한 다른 captions, review_quote primaryText, product_name primaryText, ctaText, sceneText, subText, hashtags에는 지역 표현을 넣지 마세요.\n"
                "- region hashtag는 정확히 1개만 쓰고, 반드시 '#성수동'만 허용합니다.\n"
                "- '서울숲', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 landmark/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- product_name, review_quote, subText에는 위치 단서를 절대 넣지 말고 맛, 질감, 재방문 이유만 쓰세요.\n"
                "- 지역을 더 쓰고 싶어지면 nearby landmark로 확장하지 말고, hook 한 줄의 지역 anchor를 더 또렷하게 다듬으세요.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 믿고 갈 한 끼를 찾는 20~30대 방문객입니다.\n"
                "B급 감성 review는 친구가 채팅방에 바로 던지는 한 줄 제보처럼 들려야 합니다.\n"
                "shorterCopy=false여도 상세 위치를 늘리는 것은 방향이 아니고, 설명 여유는 재방문 이유와 만족감 근거에 써야 합니다.\n"
                "지역 훅 하나와 맛 근거 한 줄을 분리해 읽히게 정리하세요."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-215",
            experiment_title="GPT-5 Mini Review Shorter Copy Off Region Anchor",
            objective="T04 review, b_grade_fun, highlightPrice=false, shorterCopy=false, emphasizeRegion=true에서 gpt-5-mini를 고정한 채 review shorterCopy=false surface-lock 위에 safe region anchor를 추가하면 option profile로 승격 가능한지 확인합니다.",
            scenario=get_service_aligned_bgrade_review_shorter_copy_off_region_emphasis_scenario(),
            model=ModelConfig(provider="openai", model_name="gpt-5-mini"),
            baseline_variant=review_shorter_copy_off_region_baseline_variant,
            candidate_variants=(review_shorter_copy_off_region_anchor_variant,),
        )

    if experiment_id == "EXP-217":
        review_highlight_price_shorter_copy_off_region_baseline_variant = PromptVariant(
            variant_id="review_surface_locked_highlight_price_shorter_copy_off_region_baseline_gpt5mini",
            lever_id="baseline",
            changed_field="none",
            description="gpt-5-mini에서 review_surface_locked_highlight_price_shorter_copy_off prompt를 emphasizeRegion=true scenario에 baseline으로 재사용합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_review_highlight_price_shorter_copy_off_region_emphasis_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 review_quote primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- product_name primaryText는 12~16자 안팎으로 유지하세요.\n"
                "- cta primaryText는 8~10자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 저장, 방문, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option shorterCopy=false는 설명을 한 줄 더 허용한다는 뜻이지, 위치나 감탄사를 늘리라는 뜻이 아닙니다.\n"
                "- quick option highlightPrice=true는 review 템플릿에서 가격 숫자를 새로 쓰라는 뜻이 아니라, 한 끼 만족감이나 다시 갈 이유가 더 값어치 있게 느껴지도록 정리하라는 뜻입니다.\n"
                "- 입력에 가격 숫자, 할인율, 특가 문구가 없으면 새로운 숫자, 할인, 세일, 쿠폰, 가성비 문구를 만들지 마세요.\n"
                "- review_quote, product_name, subText 중 한 surface 정도에는 값어치가 느껴지는 이유를 먼저 읽히게 하되, 그 이유는 맛, 양감, 식감, 조합, 재방문 만족감 중 하나로만 설명하세요.\n"
                "- quick option emphasizeRegion=true는 regionName을 더 분명하게 쓰라는 뜻이지, 상세 위치를 공개하라는 뜻이 아닙니다.\n"
                "- 문자열 '성수동'은 captions 3개 중 정확히 1개 caption에 1회, hashtags 중 정확히 1개 hashtag에 1회만 쓰세요.\n"
                "- 위 2곳을 제외한 다른 captions, hookText, review_quote primaryText, product_name primaryText, ctaText, sceneText, subText에는 지역 표현을 넣지 마세요.\n"
                "- region hashtag는 정확히 1개만 쓰고, 반드시 '#성수동'만 허용합니다.\n"
                "- '서울숲', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 landmark/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 믿고 갈 한 끼를 찾는 20~30대 방문객입니다.\n"
                "B급 감성 review는 친구가 채팅방에 바로 던지는 한 줄 제보처럼 들려야 합니다.\n"
                "highlightPrice=true와 shorterCopy=false가 같이 와도 지역보다 값어치가 느껴지는 이유와 재방문 만족감이 먼저 읽혀야 합니다.\n"
                "지역을 더 쓰고 싶어지면 훅을 다듬고, 설명 여유는 만족감 근거에만 쓰세요."
            ),
        )
        review_highlight_price_shorter_copy_off_region_anchor_variant = PromptVariant(
            variant_id="review_surface_locked_highlight_price_shorter_copy_off_region_anchor",
            lever_id="region_anchor",
            changed_field="slot_guidance",
            description="gpt-5-mini에서 review highlight-price shorterCopy=false surface-lock을 유지한 채 emphasizeRegion=true를 hookText first-anchor로만 올리는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_review_highlight_price_shorter_copy_off_region_emphasis_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 review_quote primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- product_name primaryText는 12~16자 안팎으로 유지하세요.\n"
                "- cta primaryText는 8~10자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 저장, 방문, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option shorterCopy=false는 설명을 허용하지만, 그 설명은 위치 확장이 아니라 만족감 근거와 재방문 이유에만 쓰세요.\n"
                "- quick option highlightPrice=true는 가격 숫자를 새로 쓰라는 뜻이 아니라, 값어치가 느껴지는 이유를 더 앞세우라는 뜻입니다.\n"
                "- 입력에 가격 숫자, 할인율, 특가 문구가 없으면 새로운 숫자, 할인, 세일, 쿠폰, 가성비 문구를 만들지 마세요.\n"
                "- quick option emphasizeRegion=true이므로 regionName은 hookText에서만 분명하게 드러나게 쓰세요.\n"
                "- 문자열 '성수동'은 hookText에 1회, hashtags 중 정확히 1개 hashtag에 1회만 쓰고, captions에는 넣지 마세요.\n"
                "- hookText와 '#성수동'을 제외한 다른 captions, review_quote primaryText, product_name primaryText, ctaText, sceneText, subText, hashtags에는 지역 표현을 넣지 마세요.\n"
                "- region hashtag는 정확히 1개만 쓰고, 반드시 '#성수동'만 허용합니다.\n"
                "- '서울숲', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 landmark/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- product_name, review_quote, subText에는 위치 단서를 절대 넣지 말고 맛, 질감, 재방문 이유만 쓰세요.\n"
                "- 지역을 더 쓰고 싶어지면 nearby landmark로 확장하지 말고, hook 한 줄의 지역 anchor를 더 또렷하게 다듬으세요.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 믿고 갈 한 끼를 찾는 20~30대 방문객입니다.\n"
                "B급 감성 review는 친구가 채팅방에 바로 던지는 한 줄 제보처럼 들려야 합니다.\n"
                "값어치가 느껴지는 이유를 먼저 읽히게 하되, 지역 강조는 첫 훅 한 줄로만 처리하는 편이 맞습니다.\n"
                "설명 여유는 가격이나 위치보다 만족감 근거를 더 또렷하게 적는 데 쓰세요."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-217",
            experiment_title="GPT-5 Mini Review Highlight Price Shorter Copy Off Region Anchor",
            objective="T04 review, b_grade_fun, highlightPrice=true, shorterCopy=false, emphasizeRegion=true에서 gpt-5-mini를 고정한 채 review highlight-price shorterCopy=false surface-lock 위에 safe region anchor를 추가하면 option profile로 승격 가능한지 확인합니다.",
            scenario=get_service_aligned_bgrade_review_highlight_price_shorter_copy_off_region_emphasis_scenario(),
            model=ModelConfig(provider="openai", model_name="gpt-5-mini"),
            baseline_variant=review_highlight_price_shorter_copy_off_region_baseline_variant,
            candidate_variants=(review_highlight_price_shorter_copy_off_region_anchor_variant,),
        )

    if experiment_id == "EXP-219":
        review_highlight_price_region_baseline_variant = PromptVariant(
            variant_id="review_surface_locked_highlight_price_region_baseline_gpt5mini",
            lever_id="baseline",
            changed_field="none",
            description="gpt-5-mini에서 review_surface_locked_highlight_price prompt를 emphasizeRegion=true scenario에 baseline으로 재사용합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_review_highlight_price_region_emphasis_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 review_quote primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- product_name primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- cta primaryText는 8~10자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 저장, 방문, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option shorterCopy=true이므로 hook, review_quote, product_name, cta 각각 한 가지 정보만 짧게 남기세요.\n"
                "- quick option highlightPrice=true는 review 템플릿에서 가격 숫자를 새로 쓰라는 뜻이 아니라, 만족감이나 다시 갈 이유가 더 값어치 있게 느껴지도록 정리하라는 뜻입니다.\n"
                "- 입력에 가격 숫자, 할인율, 특가 문구가 없으면 새로운 숫자, 할인, 세일, 쿠폰, 가성비 문구를 만들지 마세요.\n"
                "- review_quote, product_name, subText 중 한 surface 정도에는 값어치가 느껴지는 이유를 먼저 읽히게 하되, 그 이유는 맛, 식감, 양감, 조합, 재방문 만족감 중 하나로만 설명하세요.\n"
                "- quick option emphasizeRegion=true는 regionName을 더 분명하게 쓰라는 뜻이지, 상세 위치를 공개하라는 뜻이 아닙니다.\n"
                "- 문자열 '성수동'은 captions 3개 중 정확히 1개 caption에 1회, hashtags 중 정확히 1개 hashtag에 1회만 쓰세요.\n"
                "- 위 2곳을 제외한 다른 captions, hookText, review_quote primaryText, product_name primaryText, ctaText, sceneText, subText에는 지역 표현을 넣지 마세요.\n"
                "- region hashtag는 정확히 1개만 쓰고, 반드시 '#성수동'만 허용합니다.\n"
                "- '서울숲', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 landmark/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 믿고 갈 한 끼를 찾는 20~30대 방문객입니다.\n"
                "B급 감성 review는 친구가 채팅방에 바로 던지는 한 줄 제보처럼 들려야 합니다.\n"
                "shorterCopy=true와 highlightPrice=true가 같이 오면 짧은 만족감 근거 한 줄이 먼저 읽혀야 하고, 지역은 본문이 아니라 훅 한 줄에서만 처리하는 편이 맞습니다.\n"
                "가격이나 위치 대신 만족감 근거를 한 줄로 압축하세요."
            ),
        )
        review_highlight_price_region_anchor_variant = PromptVariant(
            variant_id="review_surface_locked_highlight_price_region_anchor",
            lever_id="region_anchor",
            changed_field="slot_guidance",
            description="gpt-5-mini에서 review highlight-price surface-lock을 유지한 채 emphasizeRegion=true를 hookText first-anchor로만 올리는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_review_highlight_price_region_emphasis_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 review_quote primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- product_name primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- cta primaryText는 8~10자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 저장, 방문, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option shorterCopy=true이므로 hook, review_quote, product_name, cta 각각 한 가지 정보만 짧게 남기세요.\n"
                "- quick option highlightPrice=true는 가격 숫자를 새로 쓰라는 뜻이 아니라, 값어치가 느껴지는 이유를 더 앞세우라는 뜻입니다.\n"
                "- 입력에 가격 숫자, 할인율, 특가 문구가 없으면 새로운 숫자, 할인, 세일, 쿠폰, 가성비 문구를 만들지 마세요.\n"
                "- quick option emphasizeRegion=true이므로 regionName은 hookText에서만 분명하게 드러나게 쓰세요.\n"
                "- 문자열 '성수동'은 hookText에 1회, hashtags 중 정확히 1개 hashtag에 1회만 쓰고, captions에는 넣지 마세요.\n"
                "- hookText와 '#성수동'을 제외한 다른 captions, review_quote primaryText, product_name primaryText, ctaText, sceneText, subText, hashtags에는 지역 표현을 넣지 마세요.\n"
                "- region hashtag는 정확히 1개만 쓰고, 반드시 '#성수동'만 허용합니다.\n"
                "- '서울숲', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 landmark/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- product_name, review_quote, subText에는 위치 단서를 절대 넣지 말고 맛, 질감, 재방문 이유만 쓰세요.\n"
                "- 지역을 더 쓰고 싶어지면 nearby landmark로 확장하지 말고, hook 한 줄의 지역 anchor를 더 또렷하게 다듬으세요.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 믿고 갈 한 끼를 찾는 20~30대 방문객입니다.\n"
                "B급 감성 review는 친구가 채팅방에 바로 던지는 한 줄 제보처럼 들려야 합니다.\n"
                "짧은 만족감 근거 한 줄과 첫 훅의 지역 anchor만 남기고, 본문에서는 계속 메뉴 만족감이 먼저 읽히게 만드는 편이 맞습니다.\n"
                "지역 훅과 값어치 근거를 분리해 읽히게 정리하세요."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-219",
            experiment_title="GPT-5 Mini Review Highlight Price Region Anchor",
            objective="T04 review, b_grade_fun, highlightPrice=true, shorterCopy=true, emphasizeRegion=true에서 gpt-5-mini를 고정한 채 review highlight-price surface-lock 위에 safe region anchor를 추가하면 option profile로 승격 가능한지 확인합니다.",
            scenario=get_service_aligned_bgrade_review_highlight_price_region_emphasis_scenario(),
            model=ModelConfig(provider="openai", model_name="gpt-5-mini"),
            baseline_variant=review_highlight_price_region_baseline_variant,
            candidate_variants=(review_highlight_price_region_anchor_variant,),
        )

    if experiment_id == "EXP-185":
        new_menu_minimal_region_baseline_variant = PromptVariant(
            variant_id="new_menu_friendly_strict_region_anchor_baseline_region_off_gpt5mini",
            lever_id="baseline",
            changed_field="none",
            description="gpt-5-mini에서 new_menu strict region anchor prompt를 emphasizeRegion=false scenario에 baseline으로 재사용합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_new_menu_minimal_region_anchor_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- product_name primaryText와 difference primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- cta primaryText는 8~10자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 확인, 주문, 저장, 방문 중 하나의 행동 단어로 시작하세요.\n"
                "- 지역 기준면은 hookText 1회, captions 3개 중 정확히 1개 caption 1회, hashtags 중 정확히 1개 hashtag 1회로 유지하세요.\n"
                "- 위 3곳을 제외한 다른 captions, hashtags, ctaText, sceneText, subText에는 지역 표현을 반복하지 마세요.\n"
                "- region hashtag는 정확히 1개만 쓰고, 반드시 '#성수동'만 허용합니다.\n"
                "- '서울숲', '서울숲 근처', '서울숲 인근', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 nearby/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- difference와 subText는 위치 설명 대신 메뉴 특징, 질감, 조합, 신메뉴 포인트만 남기세요.\n"
                "- 위치를 더 쓰고 싶어지면 그 자리를 메뉴 특징이나 한 줄 추천 이유로 바꾸세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 새로운 카페 메뉴를 찾는 20~30대 방문객입니다.\n"
                "friendly 톤은 과장된 B급보다 가볍게 권하는 한 줄 추천처럼 들려야 합니다.\n"
                "hook은 첫 공개 느낌이나 궁금증을 짧게 던지고, difference는 메뉴 포인트를 바로 이해되게 쓰세요.\n"
                "지역을 더 쓰고 싶어지면 상세 위치로 새지 말고, 그 자리를 메뉴 특징이나 한 줄 추천 이유로 바꾸세요."
            ),
        )
        new_menu_minimal_region_variant = PromptVariant(
            variant_id="new_menu_friendly_minimal_region_anchor_gpt5mini",
            lever_id="region_minimal_anchor",
            changed_field="slot_guidance",
            description="gpt-5-mini에서 new_menu strict region anchor를 유지하되 emphasizeRegion=false에 맞춰 hook 지역명을 제거하고 caption 1개 + hashtag 1개만 남기는 minimal anchor variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_new_menu_minimal_region_anchor_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- product_name primaryText와 difference primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- cta primaryText는 8~10자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 확인, 주문, 저장, 방문 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option emphasizeRegion=false이므로 hookText, hook primaryText, sceneText, subText, ctaText에는 지역명을 넣지 마세요.\n"
                "- 대신 copy-rule의 region slot 최소치를 맞추기 위해 captions 3개 중 정확히 1개 caption에만 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- hashtags는 총 5~8개를 유지하세요.\n"
                "- hashtags에는 region hashtag를 정확히 1개만 쓰고, 반드시 '#성수동'만 허용하세요.\n"
                "- 나머지 4~7개 hashtag는 메뉴명, 맛, 디저트 조합, 카테고리 중심의 non-region hashtag로 채우세요.\n"
                "- 위 2곳을 제외한 다른 captions와 hashtags에는 지역명을 반복하지 마세요.\n"
                "- '#성수동맛집' 같은 확장형 지역 hashtag는 쓰지 마세요.\n"
                "- '서울숲', '서울숲 근처', '서울숲 인근', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 nearby/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- difference와 subText는 위치 설명 대신 메뉴 특징, 질감, 재료 조합, 오늘 시켜볼 이유만 남기세요.\n"
                "- hook은 지역보다 신메뉴 자체의 첫인상이나 궁금증을 먼저 보여주세요.\n"
                "- 위치를 더 쓰고 싶어지면 그 자리를 메뉴 특징이나 한 줄 추천 이유로 바꾸세요."
            ),
            audience_guidance=(
                "타깃 고객은 새로운 카페 메뉴를 가볍게 저장해 두려는 20~30대 방문객입니다.\n"
                "friendly 톤은 지역 제보보다 메뉴 추천이 먼저 읽히는 편이 맞습니다.\n"
                "emphasizeRegion=false에서는 hook을 지역명으로 시작하지 말고, 첫 공개 느낌이나 궁금증을 메뉴 중심으로 짧게 던지세요.\n"
                "지역 기준면은 caption 한 줄과 '#성수동' 하나로만 남기고, 나머지 hashtag와 문장은 신메뉴 이유와 조합 설명에 써야 합니다."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-185",
            experiment_title="GPT-5 Mini New Menu Minimal Region Anchor",
            objective="T01 new_menu, friendly, highlightPrice=false, shorterCopy=false, emphasizeRegion=false에서 gpt-5-mini를 고정한 채 strict region anchor baseline을 minimal region anchor로 낮추면 option profile로 승격 가능한지 확인합니다.",
            scenario=get_new_menu_minimal_region_anchor_scenario(),
            model=ModelConfig(provider="openai", model_name="gpt-5-mini"),
            baseline_variant=new_menu_minimal_region_baseline_variant,
            candidate_variants=(new_menu_minimal_region_variant,),
        )

    if experiment_id == "EXP-189":
        new_menu_minimal_region_shorter_copy_baseline_variant = PromptVariant(
            variant_id="new_menu_friendly_minimal_region_anchor_baseline_shorter_copy_gpt5mini",
            lever_id="baseline",
            changed_field="none",
            description="gpt-5-mini에서 new_menu_friendly_minimal_region_anchor prompt를 shorterCopy=true + emphasizeRegion=false scenario에 baseline으로 재사용합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_new_menu_shorter_copy_minimal_region_anchor_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- product_name primaryText와 difference primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- cta primaryText는 8~10자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 확인, 주문, 저장, 방문 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option emphasizeRegion=false이므로 hookText, hook primaryText, sceneText, subText, ctaText에는 지역명을 넣지 마세요.\n"
                "- captions 3개 중 정확히 1개 caption에만 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- hashtags는 총 5~8개를 유지하고, region hashtag는 정확히 '#성수동' 1개만 허용하세요.\n"
                "- 나머지 hashtag는 메뉴명, 맛, 디저트 조합, 카테고리 중심 non-region hashtag로 채우세요.\n"
                "- 위 2곳을 제외한 다른 captions와 hashtags에는 지역명을 반복하지 마세요.\n"
                "- '#성수동맛집' 같은 확장형 지역 hashtag는 쓰지 마세요.\n"
                "- '서울숲', '서울숲 근처', '서울숲 인근', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 nearby/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- difference와 subText는 위치 설명 대신 메뉴 특징, 질감, 재료 조합, 오늘 시켜볼 이유만 남기세요.\n"
                "- hook은 지역보다 신메뉴 자체의 첫인상이나 궁금증을 먼저 보여주세요.\n"
                "- 위치를 더 쓰고 싶어지면 그 자리를 메뉴 특징이나 한 줄 추천 이유로 바꾸세요."
            ),
            audience_guidance=(
                "타깃 고객은 새로운 카페 메뉴를 가볍게 저장해 두려는 20~30대 방문객입니다.\n"
                "friendly 톤은 지역 제보보다 메뉴 추천이 먼저 읽히는 편이 맞습니다.\n"
                "지역 기준면은 caption 한 줄과 '#성수동' 하나로만 남기고, 나머지 hashtag와 문장은 신메뉴 이유와 조합 설명에 써야 합니다.\n"
                "hook은 지역명보다 메뉴 첫인상과 궁금증을 우선해 짧게 던지세요."
            ),
        )
        new_menu_minimal_region_shorter_copy_variant = PromptVariant(
            variant_id="new_menu_friendly_minimal_region_anchor_shorter_copy_gpt5mini",
            lever_id="shorter_copy",
            changed_field="slot_guidance",
            description="gpt-5-mini에서 new_menu minimal region anchor를 유지한 채 shorterCopy=true를 각 surface 한 포인트 압축으로 해석하는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_new_menu_shorter_copy_minimal_region_anchor_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 10~12자 안팎으로 유지하고, 13자를 넘기지 마세요.\n"
                "- product_name primaryText와 difference primaryText는 10~12자 안팎으로 유지하고, 13자를 넘기지 마세요.\n"
                "- cta primaryText는 6~8자 안팎으로 유지하세요.\n"
                "- cta와 ctaText는 확인, 주문, 저장, 방문 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option shorterCopy=true이므로 hook, product_name, difference, cta 각각 한 가지 정보만 남기고 설명을 길게 늘이지 마세요.\n"
                "- subText를 쓰더라도 한 줄 보조 문구만 허용하고, 쉼표로 설명을 길게 잇지 마세요.\n"
                "- captions도 한 문장 한 포인트만 남기고, 긴 배경 설명이나 감탄사 반복을 넣지 마세요.\n"
                "- quick option emphasizeRegion=false이므로 hookText, hook primaryText, sceneText, subText, ctaText에는 지역명을 넣지 마세요.\n"
                "- captions 3개 중 정확히 1개 caption에만 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- hashtags는 총 5~8개를 유지하고, region hashtag는 정확히 '#성수동' 1개만 허용하세요.\n"
                "- 나머지 hashtag는 메뉴명, 맛, 디저트 조합, 카테고리 중심 non-region hashtag로 채우세요.\n"
                "- 위 2곳을 제외한 다른 captions와 hashtags에는 지역명을 반복하지 마세요.\n"
                "- '#성수동맛집' 같은 확장형 지역 hashtag는 쓰지 마세요.\n"
                "- '서울숲', '서울숲 근처', '서울숲 인근', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 nearby/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- difference는 위치 설명 대신 메뉴 특징, 맛, 조합 한 가지로만 짧게 남기세요.\n"
                "- 더 쓰고 싶어지면 지역이나 배경 설명이 아니라 메뉴 포인트를 한 단어 더 선명하게 바꾸세요."
            ),
            audience_guidance=(
                "타깃 고객은 새로운 카페 메뉴를 가볍게 저장해 두려는 20~30대 방문객입니다.\n"
                "friendly 톤은 지역 제보보다 메뉴 추천이 먼저 읽히는 편이 맞습니다.\n"
                "shorterCopy=true에서는 지역 기준면을 줄이는 것이 아니라, 지역 외 문장을 메뉴 중심 한 포인트로 더 짧게 압축하는 편이 맞습니다.\n"
                "hook은 지역명보다 메뉴 첫인상과 궁금증을 짧게 던지세요."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-189",
            experiment_title="GPT-5 Mini New Menu Shorter Copy Minimal Region Anchor",
            objective="T01 new_menu, friendly, highlightPrice=false, shorterCopy=true, emphasizeRegion=false에서 gpt-5-mini를 고정한 채 minimal region anchor baseline 위에 shorterCopy=true 압축을 추가하면 option profile로 승격 가능한지 확인합니다.",
            scenario=get_new_menu_shorter_copy_minimal_region_anchor_scenario(),
            model=ModelConfig(provider="openai", model_name="gpt-5-mini"),
            baseline_variant=new_menu_minimal_region_shorter_copy_baseline_variant,
            candidate_variants=(new_menu_minimal_region_shorter_copy_variant,),
        )

    if experiment_id == "EXP-193":
        new_menu_minimal_region_highlight_price_baseline_variant = PromptVariant(
            variant_id="new_menu_friendly_minimal_region_anchor_baseline_highlight_price_gpt5mini",
            lever_id="baseline",
            changed_field="none",
            description="gpt-5-mini에서 new_menu_friendly_minimal_region_anchor prompt를 highlightPrice=true + emphasizeRegion=false scenario에 baseline으로 재사용합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_new_menu_highlight_price_minimal_region_anchor_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- product_name primaryText와 difference primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- cta primaryText는 8~10자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 확인, 주문, 저장, 방문 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option emphasizeRegion=false이므로 hookText, hook primaryText, sceneText, subText, ctaText에는 지역명을 넣지 마세요.\n"
                "- captions 3개 중 정확히 1개 caption에만 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- hashtags는 총 5~8개를 유지하고, region hashtag는 정확히 '#성수동' 1개만 허용하세요.\n"
                "- 나머지 hashtag는 메뉴명, 맛, 디저트 조합, 카테고리 중심 non-region hashtag로 채우세요.\n"
                "- 위 2곳을 제외한 다른 captions와 hashtags에는 지역명을 반복하지 마세요.\n"
                "- '#성수동맛집' 같은 확장형 지역 hashtag는 쓰지 마세요.\n"
                "- '서울숲', '서울숲 근처', '서울숲 인근', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 nearby/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- difference와 subText는 위치 설명 대신 메뉴 특징, 질감, 재료 조합, 오늘 시켜볼 이유만 남기세요.\n"
                "- hook은 지역보다 신메뉴 자체의 첫인상이나 궁금증을 먼저 보여주세요.\n"
                "- 위치를 더 쓰고 싶어지면 그 자리를 메뉴 특징이나 한 줄 추천 이유로 바꾸세요."
            ),
            audience_guidance=(
                "타깃 고객은 새로운 카페 메뉴를 가볍게 저장해 두려는 20~30대 방문객입니다.\n"
                "friendly 톤은 지역 제보보다 메뉴 추천이 먼저 읽히는 편이 맞습니다.\n"
                "지역 기준면은 caption 한 줄과 '#성수동' 하나로만 남기고, 나머지 hashtag와 문장은 신메뉴 이유와 조합 설명에 써야 합니다.\n"
                "hook은 지역명보다 메뉴 첫인상과 궁금증을 우선해 짧게 던지세요."
            ),
        )
        new_menu_minimal_region_highlight_price_variant = PromptVariant(
            variant_id="new_menu_friendly_minimal_region_anchor_highlight_price_gpt5mini",
            lever_id="highlight_price",
            changed_field="slot_guidance",
            description="gpt-5-mini에서 new_menu minimal region anchor를 유지한 채 highlightPrice=true를 숫자 환각 없는 value foreground로 해석하는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_new_menu_highlight_price_minimal_region_anchor_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- product_name primaryText와 difference primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- cta primaryText는 8~10자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 확인, 주문, 저장, 방문 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option highlightPrice=true는 가격 숫자를 새로 쓰라는 뜻이 아니라, 이 메뉴를 왜 한번 시켜볼 만한지 가치 포인트를 더 또렷하게 보이게 정리하라는 뜻입니다.\n"
                "- 입력에 가격 숫자, 할인폭, 세트 정보가 없으면 새로운 가격 숫자, 할인율, 특가, 세일, 가성비 문구를 만들지 마세요.\n"
                "- 숫자가 없는 상황에서는 difference, subText, caption에서 재료 조합, 질감, 함께 주문할 이유, 한정 포인트 중 하나를 가치 포인트처럼 더 선명하게 쓰세요.\n"
                "- '#가성비', '#특가', '#할인', '#세일', '#만원대'처럼 가격 foreground 뉘앙스를 새로 만드는 hashtag는 쓰지 마세요.\n"
                "- quick option emphasizeRegion=false이므로 hookText, hook primaryText, sceneText, subText, ctaText에는 지역명을 넣지 마세요.\n"
                "- captions 3개 중 정확히 1개 caption에만 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- hashtags는 총 5~8개를 유지하고, region hashtag는 정확히 '#성수동' 1개만 허용하세요.\n"
                "- 나머지 hashtag는 메뉴명, 맛, 디저트 조합, 카테고리 중심 non-region hashtag로 채우세요.\n"
                "- 위 2곳을 제외한 다른 captions와 hashtags에는 지역명을 반복하지 마세요.\n"
                "- '#성수동맛집' 같은 확장형 지역 hashtag는 쓰지 마세요.\n"
                "- '서울숲', '서울숲 근처', '서울숲 인근', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 nearby/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- difference와 subText는 위치 설명 대신 메뉴 특징, 질감, 조합, 가치 포인트만 남기고 숫자 없는 가격 추측으로 채우지 마세요.\n"
                "- hook은 지역보다 신메뉴 자체의 첫인상이나 궁금증을 먼저 보여주세요.\n"
                "- 위치를 더 쓰고 싶어지면 그 자리를 메뉴 특징이나 한 줄 추천 이유로 바꾸세요."
            ),
            audience_guidance=(
                "타깃 고객은 새로운 카페 메뉴를 가볍게 저장해 두려는 20~30대 방문객입니다.\n"
                "friendly 톤은 지역 제보보다 메뉴 추천이 먼저 읽히는 편이 맞습니다.\n"
                "highlightPrice=true라도 가격 숫자 없는 카페 신메뉴에서는 가격을 지어내지 말고, 왜 한번 시켜볼 만한지 가치 포인트를 먼저 읽히게 쓰는 편이 맞습니다.\n"
                "지역 기준면은 caption 한 줄과 '#성수동' 하나로만 남기고, 나머지는 메뉴 이유와 조합 설명에 써야 합니다."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-193",
            experiment_title="GPT-5 Mini New Menu Highlight Price Minimal Region Anchor",
            objective="T01 new_menu, friendly, highlightPrice=true, shorterCopy=false, emphasizeRegion=false에서 gpt-5-mini를 고정한 채 minimal region anchor baseline 위에 no-price-hallucination value emphasis를 추가하면 option profile로 승격 가능한지 확인합니다.",
            scenario=get_new_menu_highlight_price_minimal_region_anchor_scenario(),
            model=ModelConfig(provider="openai", model_name="gpt-5-mini"),
            baseline_variant=new_menu_minimal_region_highlight_price_baseline_variant,
            candidate_variants=(new_menu_minimal_region_highlight_price_variant,),
        )

    if experiment_id == "EXP-197":
        new_menu_minimal_region_combined_baseline_variant = PromptVariant(
            variant_id="new_menu_friendly_minimal_region_anchor_shorter_copy_baseline_highlight_price_gpt5mini",
            lever_id="baseline",
            changed_field="none",
            description="gpt-5-mini에서 new_menu_friendly_minimal_region_anchor_shorter_copy prompt를 highlightPrice=true + shorterCopy=true + emphasizeRegion=false scenario에 baseline으로 재사용합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_new_menu_highlight_price_shorter_copy_minimal_region_anchor_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 10~12자 안팎으로 유지하고, 13자를 넘기지 마세요.\n"
                "- product_name primaryText와 difference primaryText는 10~12자 안팎으로 유지하고, 13자를 넘기지 마세요.\n"
                "- cta primaryText는 6~8자 안팎으로 유지하세요.\n"
                "- cta와 ctaText는 확인, 주문, 저장, 방문 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option shorterCopy=true이므로 hook, product_name, difference, cta 각각 한 가지 정보만 남기고 설명을 길게 늘이지 마세요.\n"
                "- subText를 쓰더라도 한 줄 보조 문구만 허용하고, 쉼표로 설명을 길게 잇지 마세요.\n"
                "- captions도 한 문장 한 포인트만 남기고, 긴 배경 설명이나 감탄사 반복을 넣지 마세요.\n"
                "- quick option emphasizeRegion=false이므로 hookText, hook primaryText, sceneText, subText, ctaText에는 지역명을 넣지 마세요.\n"
                "- captions 3개 중 정확히 1개 caption에만 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- hashtags는 총 5~8개를 유지하고, region hashtag는 정확히 '#성수동' 1개만 허용하세요.\n"
                "- 나머지 hashtag는 메뉴명, 맛, 디저트 조합, 카테고리 중심 non-region hashtag로 채우세요.\n"
                "- 위 2곳을 제외한 다른 captions와 hashtags에는 지역명을 반복하지 마세요.\n"
                "- '#성수동맛집' 같은 확장형 지역 hashtag는 쓰지 마세요.\n"
                "- '서울숲', '서울숲 근처', '서울숲 인근', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 nearby/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- difference는 위치 설명 대신 메뉴 특징, 맛, 조합 한 가지로만 짧게 남기세요.\n"
                "- 더 쓰고 싶어지면 지역이나 배경 설명이 아니라 메뉴 포인트를 한 단어 더 선명하게 바꾸세요."
            ),
            audience_guidance=(
                "타깃 고객은 새로운 카페 메뉴를 가볍게 저장해 두려는 20~30대 방문객입니다.\n"
                "friendly 톤은 지역 제보보다 메뉴 추천이 먼저 읽히는 편이 맞습니다.\n"
                "shorterCopy=true에서는 지역 기준면을 줄이는 것이 아니라, 지역 외 문장을 메뉴 중심 한 포인트로 더 짧게 압축하는 편이 맞습니다.\n"
                "hook은 지역명보다 메뉴 첫인상과 궁금증을 짧게 던지세요."
            ),
        )
        new_menu_minimal_region_combined_variant = PromptVariant(
            variant_id="new_menu_friendly_minimal_region_anchor_highlight_price_shorter_copy_gpt5mini",
            lever_id="highlight_price_shorter_copy",
            changed_field="slot_guidance",
            description="gpt-5-mini에서 new_menu minimal region shorter-copy profile 위에 highlightPrice=true를 숫자 가격 환각 없는 단일 value foreground로 결합하는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_new_menu_highlight_price_shorter_copy_minimal_region_anchor_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 10~12자 안팎으로 유지하고, 13자를 넘기지 마세요.\n"
                "- product_name primaryText와 difference primaryText는 10~12자 안팎으로 유지하고, 13자를 넘기지 마세요.\n"
                "- cta primaryText는 6~8자 안팎으로 유지하세요.\n"
                "- cta와 ctaText는 확인, 주문, 저장, 방문 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option shorterCopy=true이므로 hook, product_name, difference, cta 각각 한 포인트만 남기고, 한 줄 안에 두 가지 메시지를 몰아넣지 마세요.\n"
                "- quick option highlightPrice=true는 가격 숫자를 새로 쓰라는 뜻이 아니라, 이 메뉴를 왜 한번 시켜볼 만한지 가치 포인트를 먼저 읽히게 정리하라는 뜻입니다.\n"
                "- 입력에 가격 숫자, 할인폭, 세트 정보가 없으면 새로운 가격 숫자, 할인율, 특가, 세일, 가성비 문구를 만들지 마세요.\n"
                "- 숫자가 없는 상황에서는 신메뉴 구성, 재료 조합, 디저트와 함께 주문할 이유, 첫 한입 포인트 중 딱 하나만 골라 difference와 caption에 짧게 남기세요.\n"
                "- subText를 쓰더라도 한 줄 보조 문구만 허용하고, 가치 포인트도 한 줄에 한 가지 근거만 남기세요.\n"
                "- captions도 각 한 문장 한 포인트만 남기고, 긴 배경 설명이나 감탄사 반복을 넣지 마세요.\n"
                "- '#가성비', '#특가', '#할인', '#세일', '#만원대'처럼 가격 foreground 뉘앙스를 새로 만드는 hashtag는 쓰지 마세요.\n"
                "- quick option emphasizeRegion=false이므로 hookText, hook primaryText, sceneText, subText, ctaText에는 지역명을 넣지 마세요.\n"
                "- captions 3개 중 정확히 1개 caption에만 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- hashtags는 총 5~8개를 유지하고, region hashtag는 정확히 '#성수동' 1개만 허용하세요.\n"
                "- 나머지 hashtag는 메뉴명, 맛, 디저트 조합, 카테고리 중심 non-region hashtag로 채우세요.\n"
                "- 위 2곳을 제외한 다른 captions와 hashtags에는 지역명을 반복하지 마세요.\n"
                "- '#성수동맛집' 같은 확장형 지역 hashtag는 쓰지 마세요.\n"
                "- '서울숲', '서울숲 근처', '서울숲 인근', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 nearby/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- difference는 위치 설명 대신 메뉴 특징 또는 가치 포인트 한 가지로만 채우고, 숫자 없는 가격 추측으로 채우지 마세요.\n"
                "- 더 쓰고 싶어지면 가격이나 위치를 늘리지 말고, 이미 고른 가치 포인트를 한 단어 더 선명하게 다듬으세요."
            ),
            audience_guidance=(
                "타깃 고객은 새로운 카페 메뉴를 가볍게 저장해 두려는 20~30대 방문객입니다.\n"
                "friendly 톤은 지역 제보보다 메뉴 추천이 먼저 읽히는 편이 맞습니다.\n"
                "shorterCopy=true와 highlightPrice=true가 같이 오면 길게 설명하는 대신, 왜 한번 시켜볼 만한지 한 줄 가치 포인트를 먼저 보이게 쓰는 편이 맞습니다.\n"
                "지역 기준면은 caption 한 줄과 '#성수동' 하나로만 남기고, 나머지는 메뉴 이유와 조합 설명에 써야 합니다."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-197",
            experiment_title="GPT-5 Mini New Menu Highlight Price Shorter Copy Minimal Region Anchor",
            objective="T01 new_menu, friendly, highlightPrice=true, shorterCopy=true, emphasizeRegion=false에서 gpt-5-mini를 고정한 채 minimal region shorter-copy profile 위에 no-price-hallucination value foreground를 결합하면 option profile로 승격 가능한지 확인합니다.",
            scenario=get_new_menu_highlight_price_shorter_copy_minimal_region_anchor_scenario(),
            model=ModelConfig(provider="openai", model_name="gpt-5-mini"),
            baseline_variant=new_menu_minimal_region_combined_baseline_variant,
            candidate_variants=(new_menu_minimal_region_combined_variant,),
        )

    if experiment_id == "EXP-158":
        promotion_combined_region_baseline_variant = PromptVariant(
            variant_id="promotion_surface_lock_highlight_price_off_shorter_copy_off_region_baseline_gemma",
            lever_id="baseline",
            changed_field="none",
            description="Gemma 4에서 promotion_surface_lock_highlight_price_off_shorter_copy_off prompt를 emphasizeRegion=true scenario에 baseline으로 재사용합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_highlight_price_off_shorter_copy_off_region_emphasis_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 14자 안팎으로 유지하세요.\n"
                "- hookText와 hook primaryText는 절대 16자를 넘기지 마세요.\n"
                "- benefit primaryText는 가능하면 12~14자 안쪽으로 쓰고, 14자를 넘기지 마세요.\n"
                "- urgency primaryText는 10자 안팎, cta primaryText는 8자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 방문, 저장, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option shorterCopy=false는 설명을 허용하지만, 그 설명도 가격 설명보다 메뉴 장점과 방문 이유를 먼저 보여야 합니다.\n"
                "- quick option highlightPrice=false이므로 가격 숫자, 할인폭, 특가, 할인, 가성비를 hookText, benefit, urgency, captions, hashtags의 중심 훅처럼 앞세우지 마세요.\n"
                "- 가격이나 혜택을 언급하더라도 raw 숫자나 퍼센트를 headline처럼 쓰지 말고, caption 또는 subText 한 줄 안의 보조 정보로만 처리하세요.\n"
                "- captions 3개 중 정확히 1개 caption에만 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- region hashtag는 정확히 1개만 쓰고, 반드시 '#성수동'만 허용하세요.\n"
                "- '#성수동맛집', '#서울숲맛집', '#서울숲데이트', '#퇴근후성수', '#동네맛집'처럼 지역을 확장하거나 nearby 의미를 암시하는 hashtag는 금지합니다.\n"
                "- '#오늘만할인', '#가성비', '#특가', '#할인중'처럼 가격 foreground 뉘앙스가 강한 hashtag도 금지합니다.\n"
                "- 위 1개 caption과 '#성수동'을 제외한 다른 captions, hashtags, hookText, ctaText, sceneText, subText에는 위치 표현을 넣지 마세요.\n"
                "- 특히 '서울숲', '서울숲 근처', '서울숲 인근', '성수역', '근처', '인근', '동네', '앞', '옆', '골목', '핫플' 같은 nearby/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- subText에는 위치 설명을 넣지 말고 메뉴 강점, 식감, 세트 구성, 방문 이유, 맥주 페어링만 쓰세요.\n"
                "- 가격 표현을 비우고 싶어지면 그 자리를 규카츠 식감, 육즙, 퇴근 후 보상감, 맥주와의 조합으로 채우세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "shorterCopy=false일 때는 설명이 한 줄 더 붙어도 되지만, highlightPrice=false일 때는 그 설명이 할인 숫자가 아니라 메뉴 매력과 방문 이유를 떠받쳐야 합니다.\n"
                "hook이 길어지면 감탄사보다 명사+질문 구조로 압축하고, 가격을 더 밀고 싶어지면 그 자리를 식감, 육즙, 구성, 페어링 근거로 바꾸세요."
            ),
        )
        promotion_combined_region_anchor_variant = PromptVariant(
            variant_id="promotion_surface_locked_highlight_price_off_shorter_copy_off_region_anchor_gemma",
            lever_id="region_anchor",
            changed_field="slot_guidance",
            description="Gemma 4에서 combined no-price + shorterCopy=false profile 위에 emphasizeRegion=true용 exact region anchor를 추가하는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_highlight_price_off_shorter_copy_off_region_emphasis_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 14자 안팎으로 유지하세요.\n"
                "- hookText와 hook primaryText는 절대 16자를 넘기지 마세요.\n"
                "- benefit primaryText는 가능하면 12~14자 안쪽으로 쓰고, 14자를 넘기지 마세요.\n"
                "- urgency primaryText는 10자 안팎, cta primaryText는 8자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 방문, 저장, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option shorterCopy=false는 설명을 허용하지만, 그 설명도 가격 설명보다 메뉴 장점과 방문 이유를 먼저 보여야 합니다.\n"
                "- quick option highlightPrice=false이므로 가격 숫자, 할인폭, 특가, 할인, 가성비를 hookText, benefit, urgency, captions, hashtags의 중심 훅처럼 앞세우지 마세요.\n"
                "- quick option emphasizeRegion=true이므로 regionName은 첫 장면 hookText와 hook primaryText에서만 분명하게 드러나게 쓰세요.\n"
                "- 문자열 '성수동'은 hookText/hook primaryText 계열에 1회, hashtags 중 정확히 1개 hashtag에 1회만 쓰고, captions에는 넣지 마세요.\n"
                "- region hashtag는 정확히 1개만 쓰고, 반드시 '#성수동'만 허용하세요.\n"
                "- '#성수동맛집', '#서울숲맛집', '#서울숲데이트', '#퇴근후성수', '#동네맛집'처럼 지역을 확장하거나 nearby 의미를 암시하는 hashtag는 금지합니다.\n"
                "- '#오늘만할인', '#가성비', '#특가', '#할인중'처럼 가격 foreground 뉘앙스가 강한 hashtag도 금지합니다.\n"
                "- hookText/hook primaryText와 '#성수동'을 제외한 다른 captions, hashtags, ctaText, sceneText, subText에는 위치 표현을 넣지 마세요.\n"
                "- 특히 '서울숲', '서울숲 근처', '서울숲 인근', '성수역', '근처', '인근', '동네', '앞', '옆', '골목', '핫플' 같은 nearby/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- subText에는 위치 설명을 넣지 말고 메뉴 강점, 식감, 세트 구성, 방문 이유, 맥주 페어링만 쓰세요.\n"
                "- 지역을 더 쓰고 싶어지면 nearby landmark로 확장하지 말고, hook 한 줄의 지역 anchor를 더 또렷하게 다듬으세요.\n"
                "- 가격 표현을 비우고 싶어지면 그 자리를 규카츠 식감, 육즙, 퇴근 후 보상감, 맥주와의 조합으로 채우세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "emphasizeRegion=true일 때도 상세 위치를 늘어놓는 것이 아니라, 첫 훅에서만 성수동 anchor를 분명히 보여주는 편이 맞습니다.\n"
                "shorterCopy=false일 때도 위치 설명을 늘리지 말고, 설명 여유는 메뉴 매력과 방문 이유에만 쓰세요."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-158",
            experiment_title="Gemma 4 Promotion Highlight Price Off Shorter Copy Off Region Anchor",
            objective="T02 promotion, b_grade_fun, highlightPrice=false, shorterCopy=false, emphasizeRegion=true에서 Gemma 4를 고정한 채 combined no-price + shorterCopy=false profile 위에 safe region anchor를 추가하면 option profile로 승격 가능한지 확인합니다.",
            scenario=get_service_aligned_bgrade_highlight_price_off_shorter_copy_off_region_emphasis_scenario(),
            model=ModelConfig(provider="google", model_name="models/gemma-4-31b-it"),
            baseline_variant=promotion_combined_region_baseline_variant,
            candidate_variants=(promotion_combined_region_anchor_variant,),
        )

    if experiment_id == "EXP-201":
        promotion_highlight_price_off_region_baseline_variant = PromptVariant(
            variant_id="promotion_surface_lock_highlight_price_off_region_baseline_gemma",
            lever_id="baseline",
            changed_field="none",
            description="Gemma 4에서 promotion_surface_lock_highlight_price_off prompt를 emphasizeRegion=true scenario에 baseline으로 재사용합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_highlight_price_off_region_emphasis_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 14자 안팎으로 유지하세요.\n"
                "- hookText와 hook primaryText는 절대 16자를 넘기지 마세요.\n"
                "- benefit primaryText는 가능하면 12~14자 안쪽으로 쓰고, 14자를 넘기지 마세요.\n"
                "- urgency primaryText는 10자 안팎, cta primaryText는 8자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 방문, 저장, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option shorterCopy=true이므로 설명을 길게 늘이지 말고, 각 scene과 caption에는 한 가지 포인트만 남기세요.\n"
                "- quick option highlightPrice=false는 가격 강조를 끄는 뜻이므로 hookText, benefit, urgency, captions, hashtags에서 가격 숫자, 할인폭, 특가, 할인, 가성비를 중심 훅처럼 앞세우지 마세요.\n"
                "- 가격 표현을 비우고 싶어지면 그 자리를 규카츠 식감, 육즙, 맥주 페어링, 퇴근 후 한 끼 이유로 채우세요.\n"
                "- captions 3개 중 정확히 1개 caption에만 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- region hashtag는 정확히 1개만 쓰고, 반드시 '#성수동'만 허용하세요.\n"
                "- '#성수동맛집', '#서울숲맛집', '#서울숲데이트', '#퇴근후성수', '#동네맛집'처럼 지역을 확장하거나 nearby 의미를 암시하는 hashtag는 금지합니다.\n"
                "- 위 1개 caption과 '#성수동'을 제외한 다른 captions, hashtags, hookText, ctaText, sceneText, subText에는 위치 표현을 넣지 마세요.\n"
                "- 특히 '서울숲', '서울숲 근처', '서울숲 인근', '성수역', '근처', '인근', '동네', '앞', '옆', '골목', '핫플' 같은 nearby/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- subText에는 위치 설명을 넣지 말고 메뉴 강점, 식감, 방문 이유, 맥주와의 조합만 쓰세요.\n"
                "- 위치를 더 쓰고 싶어지면 nearby landmark로 새지 말고, 그 자리를 메뉴 장점이나 방문 이유 한 줄로 바꾸세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "highlightPrice=false와 shorterCopy=true가 같이 오면 할인 숫자를 비운 자리도 식감, 한입 포인트, 방문 이유 같은 짧은 근거로 채워야 합니다.\n"
                "짧게 쓸수록 지역보다 메뉴 첫인상과 한 끼 이유가 먼저 읽히게 정리하세요."
            ),
        )
        promotion_highlight_price_off_region_anchor_variant = PromptVariant(
            variant_id="promotion_surface_locked_highlight_price_off_region_anchor_gemma",
            lever_id="region_anchor",
            changed_field="slot_guidance",
            description="Gemma 4에서 highlightPrice=false surface-lock profile 위에 emphasizeRegion=true용 first-hook region anchor를 추가하는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_highlight_price_off_region_emphasis_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 14자 안팎으로 유지하세요.\n"
                "- hookText와 hook primaryText는 절대 16자를 넘기지 마세요.\n"
                "- benefit primaryText는 가능하면 12~14자 안쪽으로 쓰고, 14자를 넘기지 마세요.\n"
                "- urgency primaryText는 10자 안팎, cta primaryText는 8자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 방문, 저장, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option shorterCopy=true이므로 hook, benefit, urgency, cta, captions 각각 한 가지 메시지만 남기고 설명을 길게 늘이지 마세요.\n"
                "- quick option highlightPrice=false는 가격 강조를 끄는 뜻이므로 hookText, benefit, urgency, captions, hashtags에서 가격 숫자, 할인폭, 특가, 할인, 가성비를 중심 훅처럼 앞세우지 마세요.\n"
                "- quick option emphasizeRegion=true이므로 regionName은 첫 장면 hookText와 hook primaryText에서만 분명하게 드러나게 쓰세요.\n"
                "- 문자열 '성수동'은 hookText/hook primaryText 계열에 1회, hashtags 중 정확히 1개 hashtag에 1회만 쓰고, captions에는 넣지 마세요.\n"
                "- region hashtag는 정확히 1개만 쓰고, 반드시 '#성수동'만 허용하세요.\n"
                "- '#성수동맛집', '#서울숲맛집', '#서울숲데이트', '#퇴근후성수', '#동네맛집'처럼 지역을 확장하거나 nearby 의미를 암시하는 hashtag는 금지합니다.\n"
                "- hookText/hook primaryText와 '#성수동'을 제외한 다른 captions, hashtags, ctaText, sceneText, subText에는 위치 표현을 넣지 마세요.\n"
                "- 특히 '서울숲', '서울숲 근처', '서울숲 인근', '성수역', '근처', '인근', '동네', '앞', '옆', '골목', '핫플' 같은 nearby/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- subText에는 위치 설명을 넣지 말고 메뉴 강점, 식감, 방문 이유, 맥주와의 조합만 쓰세요.\n"
                "- 지역을 더 쓰고 싶어지면 nearby landmark로 확장하지 말고, hook 한 줄의 지역 anchor를 더 또렷하게 다듬으세요.\n"
                "- 가격 표현을 비우고 싶어지면 그 자리를 규카츠 식감, 육즙, 맥주 페어링, 퇴근 후 한 끼 이유로 채우세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "emphasizeRegion=true여도 상세 위치를 늘어놓는 것이 아니라, 첫 훅에서만 성수동 anchor를 짧게 박는 편이 맞습니다.\n"
                "짧게 쓸수록 지역 훅 하나와 메뉴 포인트 하나를 분리해 읽히게 정리하세요."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-201",
            experiment_title="Gemma 4 Promotion Highlight Price Off Region Anchor",
            objective="T02 promotion, b_grade_fun, highlightPrice=false, shorterCopy=true, emphasizeRegion=true에서 Gemma 4를 고정한 채 no-price surface-lock profile 위에 safe region anchor를 추가하면 option profile로 승격 가능한지 확인합니다.",
            scenario=get_service_aligned_bgrade_highlight_price_off_region_emphasis_scenario(),
            model=ModelConfig(provider="google", model_name="models/gemma-4-31b-it"),
            baseline_variant=promotion_highlight_price_off_region_baseline_variant,
            candidate_variants=(promotion_highlight_price_off_region_anchor_variant,),
        )

    if experiment_id == "EXP-205":
        promotion_shorter_copy_off_region_baseline_variant = PromptVariant(
            variant_id="promotion_surface_lock_shorter_copy_off_region_baseline_gemma",
            lever_id="baseline",
            changed_field="none",
            description="Gemma 4에서 promotion_surface_lock_shorter_copy_off prompt를 emphasizeRegion=true scenario에 baseline으로 재사용합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_shorter_copy_off_region_emphasis_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 14자 안팎으로 유지하세요.\n"
                "- benefit primaryText는 가능하면 12~14자 안쪽으로 쓰고, 14자를 넘기지 마세요.\n"
                "- urgency primaryText는 10자 안팎, cta primaryText는 8자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 방문, 저장, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option shorterCopy=false이므로 모든 문장을 억지로 한 줄 슬로건처럼 자르지 말고, 필요한 맥락은 subText와 caption으로 분리해 남기세요.\n"
                "- 대신 primaryText는 계속 poster headline처럼 짧아야 하며, 설명이 길어질수록 subText로 보내세요.\n"
                "- highlightPrice=true라도 입력에 가격 숫자, 할인폭, 세트 정보가 없으면 새로운 숫자 가격, 할인율, 특가 문구를 만들지 마세요.\n"
                "- 숫자 근거가 없을 때는 메뉴 강점, 세트감, 맥주 페어링, 퇴근 후 보상감 같은 value foreground만 살리세요.\n"
                "- captions 3개 중 정확히 1개 caption에만 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- region hashtag는 정확히 1개만 쓰고, 반드시 '#성수동'만 허용하세요.\n"
                "- '#성수동맛집', '#서울숲맛집', '#서울숲데이트', '#퇴근후성수', '#동네맛집'처럼 지역을 확장하거나 nearby 의미를 암시하는 hashtag는 금지합니다.\n"
                "- 위 1개 caption과 '#성수동'을 제외한 다른 captions, hashtags, hookText, ctaText, sceneText, subText에는 위치 표현을 넣지 마세요.\n"
                "- 특히 '서울숲', '서울숲 근처', '서울숲 인근', '성수역', '근처', '인근', '동네', '앞', '옆', '골목', '핫플' 같은 nearby/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- subText에는 위치 설명을 넣지 말고 메뉴 강점, 식감, 세트 구성, 방문 이유, 맥주 페어링만 쓰세요.\n"
                "- 가격을 더 밀고 싶어지면 숫자를 만들지 말고, 그 자리를 퇴근 후 보상 한 끼 이유나 페어링 근거로 바꾸세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "shorterCopy=false일 때는 설명이 한 줄 더 붙어도 되지만, 그 설명은 위치가 아니라 메뉴 매력과 방문 이유를 떠받쳐야 합니다.\n"
                "highlightPrice=true도 숫자 가격을 억지로 만들기보다, 왜 이 한상이 바로 읽히는지를 먼저 보여주는 편이 맞습니다."
            ),
        )
        promotion_shorter_copy_off_region_anchor_variant = PromptVariant(
            variant_id="promotion_surface_locked_shorter_copy_off_region_anchor_gemma",
            lever_id="region_anchor",
            changed_field="slot_guidance",
            description="Gemma 4에서 shorterCopy=false surface-lock profile 위에 emphasizeRegion=true용 first-hook region anchor를 추가하는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_shorter_copy_off_region_emphasis_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 14자 안팎으로 유지하세요.\n"
                "- hookText와 hook primaryText는 절대 16자를 넘기지 마세요.\n"
                "- benefit primaryText는 가능하면 12~14자 안쪽으로 쓰고, 14자를 넘기지 마세요.\n"
                "- urgency primaryText는 10자 안팎, cta primaryText는 8자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 방문, 저장, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option shorterCopy=false는 설명을 허용하지만, 그 설명은 위치 확장이 아니라 메뉴 강점, 세트감, 방문 이유에만 쓰세요.\n"
                "- quick option highlightPrice=true라도 입력에 가격 숫자, 할인폭, 세트 정보가 없으면 새로운 숫자 가격, 할인율, 특가 문구를 만들지 마세요.\n"
                "- quick option emphasizeRegion=true이므로 regionName은 첫 장면 hookText와 hook primaryText에서만 분명하게 드러나게 쓰세요.\n"
                "- 문자열 '성수동'은 hookText/hook primaryText 계열에 1회, hashtags 중 정확히 1개 hashtag에 1회만 쓰고, captions에는 넣지 마세요.\n"
                "- region hashtag는 정확히 1개만 쓰고, 반드시 '#성수동'만 허용하세요.\n"
                "- '#성수동맛집', '#서울숲맛집', '#서울숲데이트', '#퇴근후성수', '#동네맛집'처럼 지역을 확장하거나 nearby 의미를 암시하는 hashtag는 금지합니다.\n"
                "- '#오늘만할인', '#가성비', '#특가', '#할인중'처럼 숫자 가격 환각을 유도하는 hashtag는 새로 만들지 마세요.\n"
                "- hookText/hook primaryText와 '#성수동'을 제외한 다른 captions, hashtags, ctaText, sceneText, subText에는 위치 표현을 넣지 마세요.\n"
                "- 특히 '서울숲', '서울숲 근처', '서울숲 인근', '성수역', '근처', '인근', '동네', '앞', '옆', '골목', '핫플' 같은 nearby/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- subText에는 위치 설명을 넣지 말고 메뉴 강점, 식감, 세트 구성, 방문 이유, 맥주 페어링만 쓰세요.\n"
                "- 지역을 더 쓰고 싶어지면 nearby landmark로 확장하지 말고, hook 한 줄의 지역 anchor를 더 또렷하게 다듬으세요.\n"
                "- 가격이나 혜택을 더 보이고 싶어지면 raw 숫자가 아니라 퇴근 후 보상감, 한상 구성, 페어링 이유 같은 value foreground로 바꾸세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "emphasizeRegion=true일 때도 상세 위치를 늘어놓는 것이 아니라, 첫 훅에서만 성수동 anchor를 짧게 박는 편이 맞습니다.\n"
                "shorterCopy=false일 때 생기는 설명 여유는 위치가 아니라 메뉴 매력과 재방문 이유에 써야 합니다."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-205",
            experiment_title="Gemma 4 Promotion Shorter Copy Off Region Anchor",
            objective="T02 promotion, b_grade_fun, highlightPrice=true, shorterCopy=false, emphasizeRegion=true에서 Gemma 4를 고정한 채 shorterCopy=false surface-lock profile 위에 safe region anchor를 추가하면 option profile로 승격 가능한지 확인합니다.",
            scenario=get_service_aligned_bgrade_shorter_copy_off_region_emphasis_scenario(),
            model=ModelConfig(provider="google", model_name="models/gemma-4-31b-it"),
            baseline_variant=promotion_shorter_copy_off_region_baseline_variant,
            candidate_variants=(promotion_shorter_copy_off_region_anchor_variant,),
        )

    if experiment_id == "EXP-209":
        promotion_region_baseline_variant = PromptVariant(
            variant_id="promotion_surface_lock_region_baseline_gemma",
            lever_id="baseline",
            changed_field="none",
            description="Gemma 4에서 active promotion baseline 원칙을 emphasizeRegion=true scenario에 baseline으로 재사용합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_region_emphasis_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 14자 안팎으로 유지하세요.\n"
                "- benefit primaryText는 가능하면 12~14자 안쪽으로 쓰고, 14자를 넘기지 마세요.\n"
                "- urgency primaryText는 10자 안팎, cta primaryText는 8자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 방문, 저장, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option shorterCopy=true이므로 hook, benefit, urgency, cta, captions 각각 한 가지 메시지만 남기고 설명을 길게 늘이지 마세요.\n"
                "- quick option highlightPrice=true라도 입력에 가격 숫자, 할인폭, 세트 정보가 없으면 새로운 숫자 가격, 할인율, 특가 문구를 만들지 마세요.\n"
                "- 숫자 근거가 없는 상황에서는 메뉴 구성, 육즙, 맥주 페어링, 퇴근 후 보상감 같은 value foreground를 한 줄로 압축하세요.\n"
                "- captions 3개 중 정확히 1개 caption에만 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- region hashtag는 정확히 1개만 쓰고, 반드시 '#성수동'만 허용하세요.\n"
                "- '#성수동맛집', '#서울숲맛집', '#서울숲데이트', '#퇴근후성수', '#동네맛집'처럼 지역을 확장하거나 nearby 의미를 암시하는 hashtag는 금지합니다.\n"
                "- 위 1개 caption과 '#성수동'을 제외한 다른 captions, hashtags, hookText, ctaText, sceneText, subText에는 위치 표현을 넣지 마세요.\n"
                "- 특히 '서울숲', '서울숲 근처', '서울숲 인근', '성수역', '근처', '인근', '동네', '앞', '옆', '골목', '핫플' 같은 nearby/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- subText에는 위치 설명을 넣지 말고 메뉴 강점, 식감, 방문 이유, 맥주와의 조합만 쓰세요.\n"
                "- 지역을 더 쓰고 싶어지면 nearby landmark로 새지 말고, 그 자리를 메뉴 포인트 한 줄로 정리하세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "기본 promotion 축에서는 짧고 직접적인 headline이 먼저 읽혀야 하고, value 포인트도 숫자보다 한상 이유가 먼저 보이는 편이 맞습니다.\n"
                "짧게 쓸수록 장면마다 메시지를 하나만 남기고, 나머지는 caption이나 hashtag로 흩뿌리지 마세요."
            ),
        )
        promotion_region_anchor_variant = PromptVariant(
            variant_id="promotion_surface_locked_region_anchor_gemma",
            lever_id="region_anchor",
            changed_field="slot_guidance",
            description="Gemma 4에서 default promotion baseline 위에 emphasizeRegion=true용 first-hook region anchor를 추가하는 variant입니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_region_emphasis_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 14자 안팎으로 유지하세요.\n"
                "- hookText와 hook primaryText는 절대 16자를 넘기지 마세요.\n"
                "- benefit primaryText는 가능하면 12~14자 안쪽으로 쓰고, 14자를 넘기지 마세요.\n"
                "- urgency primaryText는 10자 안팎, cta primaryText는 8자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 방문, 저장, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option shorterCopy=true이므로 hook, benefit, urgency, cta, captions 각각 한 가지 메시지만 남기고, 한 줄 안에 두 가지 메시지를 몰아넣지 마세요.\n"
                "- quick option highlightPrice=true라도 입력에 가격 숫자, 할인폭, 세트 정보가 없으면 새로운 숫자 가격, 할인율, 특가 문구를 만들지 마세요.\n"
                "- 숫자 근거가 없는 상황에서는 메뉴 구성, 육즙, 맥주 페어링, 퇴근 후 보상감 같은 value foreground를 한 줄로 압축하세요.\n"
                "- quick option emphasizeRegion=true이므로 regionName은 첫 장면 hookText와 hook primaryText에서만 분명하게 드러나게 쓰세요.\n"
                "- 문자열 '성수동'은 hookText/hook primaryText 계열에 1회, hashtags 중 정확히 1개 hashtag에 1회만 쓰고, captions에는 넣지 마세요.\n"
                "- region hashtag는 정확히 1개만 쓰고, 반드시 '#성수동'만 허용하세요.\n"
                "- '#성수동맛집', '#서울숲맛집', '#서울숲데이트', '#퇴근후성수', '#동네맛집'처럼 지역을 확장하거나 nearby 의미를 암시하는 hashtag는 금지합니다.\n"
                "- '#오늘만할인', '#가성비', '#특가', '#할인중'처럼 숫자 가격 환각을 유도하는 hashtag는 새로 만들지 마세요.\n"
                "- hookText/hook primaryText와 '#성수동'을 제외한 다른 captions, hashtags, ctaText, sceneText, subText에는 위치 표현을 넣지 마세요.\n"
                "- 특히 '서울숲', '서울숲 근처', '서울숲 인근', '성수역', '근처', '인근', '동네', '앞', '옆', '골목', '핫플' 같은 nearby/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- subText에는 위치 설명을 넣지 말고 메뉴 강점, 식감, 방문 이유, 맥주와의 조합만 쓰세요.\n"
                "- 지역을 더 쓰고 싶어지면 nearby landmark로 확장하지 말고, hook 한 줄의 지역 anchor를 더 또렷하게 다듬으세요.\n"
                "- 가치 포인트를 더 보이고 싶어지면 raw 숫자가 아니라 메뉴 조합, 식감, 페어링, 퇴근 후 보상감으로 바꾸세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "emphasizeRegion=true일 때도 좋은 방식은 상세 위치를 늘리는 것이 아니라, 첫 훅에서만 성수동 anchor를 짧고 강하게 보이게 하는 것입니다.\n"
                "짧게 쓸수록 지역 anchor 하나와 메뉴 가치 포인트 하나를 분리해 읽히게 정리하세요."
            ),
        )
        return ExperimentDefinition(
            experiment_id="EXP-209",
            experiment_title="Gemma 4 Promotion Region Anchor",
            objective="T02 promotion, b_grade_fun, highlightPrice=true, shorterCopy=true, emphasizeRegion=true에서 Gemma 4를 고정한 채 default promotion baseline 위에 safe region anchor를 추가하면 option profile로 승격 가능한지 확인합니다.",
            scenario=get_service_aligned_bgrade_region_emphasis_scenario(),
            model=ModelConfig(provider="google", model_name="models/gemma-4-31b-it"),
            baseline_variant=promotion_region_baseline_variant,
            candidate_variants=(promotion_region_anchor_variant,),
        )

    raise ValueError(f"unsupported experiment id: {experiment_id}")


def get_model_comparison_definition(experiment_id: str = "EXP-23") -> ModelComparisonDefinition:
    common_role = "당신은 한국 지역 소상공인용 SNS 광고 카피를 구조화된 슬롯에 맞춰 작성하는 한국어 카피라이터입니다."

    if experiment_id == "EXP-23":
        fixed_prompt_variant = PromptVariant(
            variant_id="fixed_b_grade_tone_guidance",
            lever_id="model",
            changed_field="model_only",
            description="T02 promotion에서 효과가 좋았던 B급 톤 가이드를 고정하고 모델만 비교합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "hook, benefit, urgency, cta는 각 장면에서 바로 읽히도록 짧고 직접적으로 쓰세요.\n"
                "추상 표현인 '분위기를 보여드립니다', '구성했습니다' 같은 문장은 피하고, 혜택·기간감·행동 단어를 앞쪽에 배치하세요."
            ),
        )
        return ModelComparisonDefinition(
            experiment_id="EXP-23",
            experiment_title="Service-Aligned Promotion Cross-Provider Model Comparison",
            objective="T02 promotion, b_grade_fun, 실제 음식 사진, 고정된 B급 tone guidance 조건에서 cross-provider 모델만 바꿨을 때 카피와 scene-plan 품질 차이를 비교합니다.",
            scenario=get_service_aligned_bgrade_scenario(),
            prompt_variant=fixed_prompt_variant,
            models=(
                ModelConfig(provider="google", model_name="models/gemma-4-31b-it"),
                ModelConfig(provider="openai", model_name="gpt-5-mini"),
                ModelConfig(provider="openai", model_name="gpt-4.1-mini"),
            ),
        )

    if experiment_id == "EXP-24":
        fixed_prompt_variant = PromptVariant(
            variant_id="fixed_b_grade_tone_guidance",
            lever_id="model",
            changed_field="model_only",
            description="T02 promotion에서 효과가 좋았던 B급 톤 가이드를 고정하고 Google 계열 모델만 비교합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "hook, benefit, urgency, cta는 각 장면에서 바로 읽히도록 짧고 직접적으로 쓰세요.\n"
                "추상 표현인 '분위기를 보여드립니다', '구성했습니다' 같은 문장은 피하고, 혜택·기간감·행동 단어를 앞쪽에 배치하세요."
            ),
        )
        return ModelComparisonDefinition(
            experiment_id="EXP-24",
            experiment_title="Service-Aligned Promotion Google Model Comparison",
            objective="T02 promotion, b_grade_fun, 실제 음식 사진, 고정된 B급 tone guidance 조건에서 Google 계열 모델(Gemma/Gemini)만 바꿨을 때 카피와 scene-plan 품질 차이를 비교합니다.",
            scenario=get_service_aligned_bgrade_scenario(),
            prompt_variant=fixed_prompt_variant,
            models=(
                ModelConfig(provider="google", model_name="models/gemma-4-31b-it"),
                ModelConfig(provider="google", model_name="models/gemini-2.5-flash"),
                ModelConfig(provider="google", model_name="models/gemini-2.5-flash-lite"),
            ),
        )

    if experiment_id == "EXP-25":
        fixed_prompt_variant = PromptVariant(
            variant_id="fixed_b_grade_tone_guidance",
            lever_id="model",
            changed_field="model_only",
            description="T02 promotion에서 효과가 좋았던 B급 톤 가이드를 고정하고, 현재 계정에서 사용 가능한 OpenAI 모델과 Gemma 4만 비교합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "hook, benefit, urgency, cta는 각 장면에서 바로 읽히도록 짧고 직접적으로 쓰세요.\n"
                "추상 표현인 '분위기를 보여드립니다', '구성했습니다' 같은 문장은 피하고, 혜택·기간감·행동 단어를 앞쪽에 배치하세요."
            ),
        )
        return ModelComparisonDefinition(
            experiment_id="EXP-25",
            experiment_title="Service-Aligned Promotion OpenAI-Available Model Comparison",
            objective="T02 promotion, b_grade_fun, 실제 음식 사진, 고정된 B급 tone guidance 조건에서 현재 계정에서 사용 가능한 OpenAI 모델(gpt-5-mini, gpt-5-nano)과 Gemma 4를 비교합니다.",
            scenario=get_service_aligned_bgrade_scenario(),
            prompt_variant=fixed_prompt_variant,
            models=(
                ModelConfig(provider="google", model_name="models/gemma-4-31b-it"),
                ModelConfig(provider="openai", model_name="gpt-5-mini"),
                ModelConfig(provider="openai", model_name="gpt-5-nano"),
            ),
        )

    if experiment_id == "EXP-26":
        fixed_prompt_variant = PromptVariant(
            variant_id="fixed_review_region_repeat_guidance",
            lever_id="model",
            changed_field="model_only",
            description="T04 review에서 이미 확인했던 지역 반복 제약 프롬프트를 고정하고 모델만 비교합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                "지역명은 hookText, captions, hashtags를 모두 합쳐 총 2회 이하로만 사용하세요.\n"
                "이미 해시태그에 지역명이 들어가면 본문 계열에서는 최대 1회만 더 허용됩니다.\n"
                "review_quote와 product_name에는 지역명을 억지로 반복하지 말고, 꼭 필요할 때만 한 번 쓰세요."
            ),
            audience_guidance="추가 지시 없음. 스타일 기본값만 따르세요.",
        )
        return ModelComparisonDefinition(
            experiment_id="EXP-26",
            experiment_title="Service-Aligned Review Model Comparison",
            objective="T04 review, b_grade_fun, 실제 음식 사진, 고정된 review region repeat guidance 조건에서 Gemma 4와 gpt-5-mini를 비교합니다.",
            scenario=get_service_aligned_bgrade_review_scenario(),
            prompt_variant=fixed_prompt_variant,
            models=(
                ModelConfig(provider="google", model_name="models/gemma-4-31b-it"),
                ModelConfig(provider="openai", model_name="gpt-5-mini"),
            ),
        )

    if experiment_id == "EXP-29":
        fixed_prompt_variant = PromptVariant(
            variant_id="fixed_b_grade_tone_guidance_text_only_hf",
            lever_id="model",
            changed_field="model_only",
            description="T02 promotion에서 효과가 좋았던 B급 tone guidance를 유지하되, Hugging Face text-only 오픈소스 모델만 비교합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "hook, benefit, urgency, cta는 각 장면에서 바로 읽히도록 짧고 직접적으로 쓰세요.\n"
                "추상 표현인 '분위기를 보여드립니다', '구성했습니다' 같은 문장은 피하고, 혜택·기간감·행동 단어를 앞쪽에 배치하세요.\n"
                "이번 비교는 Hugging Face text-only 경로이므로 이미지 자체를 해석하지 말고, 입력된 업종/목적/스타일/자산 파일명만 근거로 작성하세요."
            ),
        )
        return ModelComparisonDefinition(
            experiment_id="EXP-29",
            experiment_title="Hugging Face Open-Source Text Model Comparison",
            objective="T02 promotion, b_grade_fun 시나리오에서 Hugging Face router로 실제 통과한 오픈소스 text 모델만 비교해 copy generation 후보군을 확장합니다.",
            scenario=get_service_aligned_bgrade_scenario(),
            prompt_variant=fixed_prompt_variant,
            models=(
                ModelConfig(provider="huggingface", model_name="Qwen/Qwen3-4B-Instruct-2507"),
                ModelConfig(provider="huggingface", model_name="Qwen/Qwen3.5-27B"),
            ),
        )

    if experiment_id == "EXP-30":
        fixed_prompt_variant = PromptVariant(
            variant_id="fixed_b_grade_tone_guidance_local_ollama",
            lever_id="model",
            changed_field="model_only",
            description="T02 promotion에서 효과가 좋았던 B급 tone guidance를 유지하고, 현재 로컬 Ollama에 이미 설치된 모델만 비교합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "hook, benefit, urgency, cta는 각 장면에서 바로 읽히도록 짧고 직접적으로 쓰세요.\n"
                "추상 표현인 '분위기를 보여드립니다', '구성했습니다' 같은 문장은 피하고, 혜택·기간감·행동 단어를 앞쪽에 배치하세요.\n"
                "한국어 출력에서 깨짐(�, 이상한 라틴 문자 조합)이 생기지 않도록 자연스러운 한국어 문장만 사용하세요."
            ),
        )
        return ModelComparisonDefinition(
            experiment_id="EXP-30",
            experiment_title="Local Ollama Model Comparison On 4080 Super",
            objective="RTX 4080 Super 16GB / RAM 64GB 환경에서 이미 설치된 로컬 Ollama 모델만 비교해, 현재 프로젝트 copy generation에 바로 투입 가능한 로컬 후보를 고릅니다.",
            scenario=get_service_aligned_bgrade_scenario(),
            prompt_variant=fixed_prompt_variant,
            models=(
                ModelConfig(provider="ollama", model_name="gemma3:12b"),
                ModelConfig(provider="ollama", model_name="exaone3.5:7.8b"),
                ModelConfig(provider="ollama", model_name="llama3.1:8b"),
                ModelConfig(provider="ollama", model_name="mistral-small3.1:24b-instruct-2503-q4_K_M"),
            ),
        )

    if experiment_id == "EXP-101":
        fixed_prompt_variant = PromptVariant(
            variant_id="fixed_reference_hook_pack_guidance",
            lever_id="model",
            changed_field="model_only",
            description="T02 promotion에서 reference-derived hook guidance를 고정하고 모델만 비교합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_scenario())}"
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "hook, benefit, urgency, cta는 각 장면에서 바로 읽히도록 짧고 직접적으로 쓰세요.\n"
                "추상 표현인 '분위기를 보여드립니다', '구성했습니다' 같은 문장은 피하고, 혜택·기간감·행동 단어를 앞쪽에 배치하세요."
            ),
        )
        return ModelComparisonDefinition(
            experiment_id="EXP-101",
            experiment_title="Reference Hook Pack Cross-Provider Model Comparison",
            objective="T02 promotion, b_grade_fun, 실제 음식 사진, 고정된 reference hook guidance 조건에서 모델만 바꿨을 때 hook 직접성, scene 길이, CTA 안정성 차이를 비교합니다.",
            scenario=get_service_aligned_bgrade_scenario(),
            prompt_variant=fixed_prompt_variant,
            models=(
                ModelConfig(provider="google", model_name="models/gemma-4-31b-it"),
                ModelConfig(provider="google", model_name="models/gemini-2.5-flash"),
                ModelConfig(provider="openai", model_name="gpt-5-mini"),
                ModelConfig(provider="openai", model_name="gpt-5-nano"),
            ),
        )

    if experiment_id == "EXP-105":
        fixed_prompt_variant = PromptVariant(
            variant_id="fixed_reference_hook_region_anchor_budget",
            lever_id="model",
            changed_field="model_only",
            description="reference hook guidance에 region anchor와 length budget을 함께 고정하고 Gemma 4와 gpt-5-mini만 비교합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 14자 안팎으로 유지하세요.\n"
                "- benefit primaryText는 16자 안팎, urgency primaryText는 10자 안팎, cta primaryText는 8자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 방문, 저장, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- 지역명은 hookText와 scene primaryText에는 넣지 마세요.\n"
                "- 지역명은 captions 중 정확히 1개 문장에 1회만 넣으세요.\n"
                "- 지역명이 들어간 hashtag는 정확히 1개만 쓰세요.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요.\n"
                "- subText에는 보조 설명을 넣되, primaryText보다 길어도 괜찮습니다."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "hook, benefit, urgency, cta는 각 장면에서 바로 읽히도록 짧고 직접적으로 쓰세요.\n"
                "추상 표현인 '분위기를 보여드립니다', '구성했습니다' 같은 문장은 피하고, 혜택·기간감·행동 단어를 앞쪽에 배치하세요."
            ),
        )
        return ModelComparisonDefinition(
            experiment_id="EXP-105",
            experiment_title="Reference Hook Region Anchor Budget Comparison",
            objective="T02 promotion, b_grade_fun, 실제 음식 사진에서 reference hook guidance와 region anchor/length budget을 함께 고정했을 때 Gemma 4와 gpt-5-mini 중 누가 더 render-ready한 결과를 내는지 비교합니다.",
            scenario=get_service_aligned_bgrade_scenario(),
            prompt_variant=fixed_prompt_variant,
            models=(
                ModelConfig(provider="google", model_name="models/gemma-4-31b-it"),
                ModelConfig(provider="openai", model_name="gpt-5-mini"),
            ),
        )

    if experiment_id == "EXP-108":
        fixed_prompt_variant = PromptVariant(
            variant_id="fixed_reference_hook_strict_anchor_and_benefit_budget",
            lever_id="model",
            changed_field="model_only",
            description="reference hook guidance에 exact region anchor와 tighter benefit budget을 함께 고정하고 Gemma 4와 gpt-5-mini만 비교합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 14자 안팎으로 유지하세요.\n"
                "- benefit primaryText는 가능하면 12~14자 안쪽으로 쓰고, 14자를 넘기지 마세요.\n"
                "- urgency primaryText는 10자 안팎, cta primaryText는 8자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 방문, 저장, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- 지역명은 hookText와 scene primaryText에는 넣지 마세요.\n"
                "- captions 3개 중 정확히 1개 caption에는 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- 위 caption에서 지역 표현을 '서울숲 근처', '서울숲 인근', '성수역', '근처', '동네' 같은 우회 표현으로 바꾸지 마세요.\n"
                "- 지역명이 들어간 hashtag는 정확히 1개만 쓰고, 그 hashtag는 '성수동' 문자열을 그대로 포함해야 합니다.\n"
                "- 긴 혜택 설명은 benefit subText로 보내고, primaryText는 poster headline처럼 짧게 유지하세요.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "hook, benefit, urgency, cta는 각 장면에서 바로 읽히도록 짧고 직접적으로 쓰세요.\n"
                "추상 표현인 '분위기를 보여드립니다', '구성했습니다' 같은 문장은 피하고, 혜택·기간감·행동 단어를 앞쪽에 배치하세요."
            ),
        )
        return ModelComparisonDefinition(
            experiment_id="EXP-108",
            experiment_title="Reference Hook Strict Anchor Benefit Budget Comparison",
            objective="T02 promotion, b_grade_fun, 실제 음식 사진에서 exact region anchor와 tighter benefit budget을 함께 고정했을 때 Gemma 4와 gpt-5-mini 중 누가 더 production-near한 결과를 내는지 비교합니다.",
            scenario=get_service_aligned_bgrade_scenario(),
            prompt_variant=fixed_prompt_variant,
            models=(
                ModelConfig(provider="google", model_name="models/gemma-4-31b-it"),
                ModelConfig(provider="openai", model_name="gpt-5-mini"),
            ),
        )

    if experiment_id == "EXP-129":
        fixed_prompt_variant = PromptVariant(
            variant_id="fixed_review_baseline_transfer_translated",
            lever_id="model",
            changed_field="model_only",
            description="T04 review에서 promotion strict baseline 원칙을 review slot 구조로 번역한 prompt를 고정하고 Gemma 4와 gpt-5-mini를 비교합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_review_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 review_quote primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- product_name primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- cta primaryText는 8~10자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 저장, 방문, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- 지역명은 hookText, review_quote primaryText, product_name primaryText에는 넣지 마세요.\n"
                "- captions 3개 중 정확히 1개 caption에는 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- 위 caption에서 지역 표현을 '서울숲 근처', '서울숲 인근', '성수역', '근처', '동네' 같은 우회 표현으로 바꾸지 마세요.\n"
                "- 지역명이 들어간 hashtag는 정확히 1개만 쓰고, 그 hashtag는 '성수동' 문자열을 그대로 포함해야 합니다.\n"
                "- 긴 감상은 review_quote subText로 보내고, primaryText는 친구가 바로 보내는 한 줄처럼 짧게 유지하세요.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 믿고 갈 한 끼를 찾는 20~30대 방문객입니다.\n"
                "B급 감성 review는 친구가 채팅방에 바로 던지는 한 줄 제보처럼 들려야 합니다.\n"
                "review_quote는 짧고 말맛 있게, product_name은 다시 찾는 이유가 한 번에 보이게 쓰세요.\n"
                "cta는 감탄사보다 행동 단어를 앞쪽에 두고 짧게 마무리하세요."
            ),
        )
        return ModelComparisonDefinition(
            experiment_id="EXP-129",
            experiment_title="Review Baseline Transfer Fallback Model Comparison",
            objective="T04 review, b_grade_fun, 실제 음식 사진에서 review-translated baseline prompt를 고정했을 때 Gemma 4와 gpt-5-mini 중 누가 fallback 가능한 수준으로 production-near한 결과를 내는지 비교합니다.",
            scenario=get_service_aligned_bgrade_review_scenario(),
            prompt_variant=fixed_prompt_variant,
            models=(
                ModelConfig(provider="google", model_name="models/gemma-4-31b-it"),
                ModelConfig(provider="openai", model_name="gpt-5-mini"),
            ),
        )

    if experiment_id == "EXP-130":
        fixed_prompt_variant = PromptVariant(
            variant_id="fixed_review_baseline_transfer_translated",
            lever_id="model",
            changed_field="model_only",
            description="T04 review에서 review-translated strict baseline prompt를 고정하고 Gemma 4, gpt-4.1-mini, gpt-5-mini를 fallback 후보 관점으로 비교합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_review_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 review_quote primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- product_name primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- cta primaryText는 8~10자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 저장, 방문, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- 지역명은 hookText, review_quote primaryText, product_name primaryText에는 넣지 마세요.\n"
                "- captions 3개 중 정확히 1개 caption에는 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- 위 caption에서 지역 표현을 '서울숲 근처', '서울숲 인근', '성수역', '근처', '동네' 같은 우회 표현으로 바꾸지 마세요.\n"
                "- 지역명이 들어간 hashtag는 정확히 1개만 쓰고, 그 hashtag는 '성수동' 문자열을 그대로 포함해야 합니다.\n"
                "- 긴 감상은 review_quote subText로 보내고, primaryText는 친구가 바로 보내는 한 줄처럼 짧게 유지하세요.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 믿고 갈 한 끼를 찾는 20~30대 방문객입니다.\n"
                "B급 감성 review는 친구가 채팅방에 바로 던지는 한 줄 제보처럼 들려야 합니다.\n"
                "review_quote는 짧고 말맛 있게, product_name은 다시 찾는 이유가 한 번에 보이게 쓰세요.\n"
                "cta는 감탄사보다 행동 단어를 앞쪽에 두고 짧게 마무리하세요."
            ),
        )
        return ModelComparisonDefinition(
            experiment_id="EXP-130",
            experiment_title="Review Strict Fallback Candidate Sweep",
            objective="T04 review, b_grade_fun, 실제 음식 사진에서 strict review baseline prompt를 고정했을 때 Gemma 4, gpt-4.1-mini, gpt-5-mini 중 누가 fallback 가능한 수준으로 strict region policy와 길이 budget을 지키는지 비교합니다.",
            scenario=get_service_aligned_bgrade_review_scenario(),
            prompt_variant=fixed_prompt_variant,
            models=(
                ModelConfig(provider="google", model_name="models/gemma-4-31b-it"),
                ModelConfig(provider="openai", model_name="gpt-4.1-mini"),
                ModelConfig(provider="openai", model_name="gpt-5-mini"),
            ),
        )

    if experiment_id == "EXP-223":
        fixed_prompt_variant = PromptVariant(
            variant_id="fixed_review_surface_locked_exact_region_anchor",
            lever_id="model",
            changed_field="model_only",
            description="T04 review에서 현재 채택한 surface-locked exact region anchor prompt를 고정하고 Gemma 4와 gpt-5-mini를 비교합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_review_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 review_quote primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- product_name primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- cta primaryText는 8~10자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 저장, 방문, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- captions 3개 중 정확히 1개 caption에만 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- 그 1개 caption을 제외한 다른 captions, hookText, ctaText, sceneText, subText, hashtags에는 위치 표현을 넣지 마세요.\n"
                "- 특히 '서울숲', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 landmark/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- region hashtag는 정확히 1개만 쓰고, 반드시 '#성수동'만 허용합니다.\n"
                "- product_name, review_quote, subText에는 위치 단서를 절대 넣지 말고 맛, 질감, 재방문 이유만 쓰세요.\n"
                "- 위치를 더 쓰고 싶어지면 그 자리를 메뉴 장점이나 재방문 이유로 바꾸세요.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 믿고 갈 한 끼를 찾는 20~30대 방문객입니다.\n"
                "B급 감성 review는 친구가 채팅방에 바로 던지는 한 줄 제보처럼 들려야 합니다.\n"
                "review_quote는 짧고 말맛 있게, product_name은 다시 찾는 이유가 한 번에 보이게 쓰세요.\n"
                "cta는 감탄사보다 행동 단어를 앞쪽에 두고 짧게 마무리하세요."
            ),
        )
        return ModelComparisonDefinition(
            experiment_id="EXP-223",
            experiment_title="Review Surface Lock Current Baseline Model Comparison",
            objective="T04 review, b_grade_fun, 실제 음식 사진에서 현재 채택한 surface-locked exact region anchor prompt를 고정했을 때 Gemma 4와 gpt-5-mini 중 누가 strict fallback 기준에 더 안정적으로 맞는지 확인합니다.",
            scenario=get_service_aligned_bgrade_review_scenario(),
            prompt_variant=fixed_prompt_variant,
            models=(
                ModelConfig(provider="google", model_name="models/gemma-4-31b-it"),
                ModelConfig(provider="openai", model_name="gpt-5-mini"),
            ),
        )

    if experiment_id == "EXP-135":
        fixed_prompt_variant = PromptVariant(
            variant_id="fixed_new_menu_strict_region_anchor",
            lever_id="model",
            changed_field="model_only",
            description="T01 new_menu에서 promotion strict baseline 원칙을 new_menu slot 구조와 emphasizeRegion=true 조건으로 번역한 prompt를 고정하고 Gemma 4와 gpt-5-mini를 비교합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_default_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- product_name primaryText와 difference primaryText는 12~14자 안팎으로 유지하세요.\n"
                "- cta primaryText는 8~10자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 확인, 주문, 저장, 방문 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option emphasizeRegion=true는 regionName을 더 분명하게 쓰라는 뜻이지, 상세 위치를 공개하라는 뜻이 아닙니다.\n"
                "- 문자열 '성수동'은 hookText에 1회, captions 3개 중 정확히 1개 caption에 1회, hashtags 중 정확히 1개 hashtag에 1회만 쓰세요.\n"
                "- 위 3곳을 제외한 다른 captions, hashtags, ctaText, sceneText, subText에는 지역 표현을 반복하지 마세요.\n"
                "- '서울숲', '서울숲 근처', '서울숲 인근', '성수역', '근처', '인근', '동네', '핫플', '앞' 같은 nearby/detail-location 표현은 모든 surface에서 금지합니다.\n"
                "- difference는 위치 설명 대신 맛, 질감, 재료 조합, 신메뉴 포인트만 남기세요.\n"
                "- 긴 메뉴 설명은 subText로 보내고, primaryText는 poster headline처럼 짧게 유지하세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 새로운 카페 메뉴를 찾는 20~30대 방문객입니다.\n"
                "friendly 톤은 과장된 B급보다 가볍게 권하는 한 줄 추천처럼 들려야 합니다.\n"
                "hook은 첫 공개 느낌이나 궁금증을 짧게 던지고, difference는 메뉴 포인트를 바로 이해되게 쓰세요.\n"
                "지역을 더 쓰고 싶어지면 추가 위치 정보로 새지 말고, 그 자리를 메뉴 특징이나 한 줄 추천 이유로 바꾸세요."
            ),
        )
        return ModelComparisonDefinition(
            experiment_id="EXP-135",
            experiment_title="New Menu Strict Region Anchor Coverage Comparison",
            objective="T01 new_menu, friendly, emphasizeRegion=true, 실제 카페 이미지에서 promotion strict baseline 원칙을 번역한 prompt를 고정했을 때 Gemma 4와 gpt-5-mini 중 누가 strict location policy와 길이 budget을 지키며 baseline coverage 후보가 되는지 비교합니다.",
            scenario=get_default_scenario(),
            prompt_variant=fixed_prompt_variant,
            models=(
                ModelConfig(provider="google", model_name="models/gemma-4-31b-it"),
                ModelConfig(provider="openai", model_name="gpt-5-mini"),
            ),
        )

    if experiment_id == "EXP-143":
        fixed_prompt_variant = PromptVariant(
            variant_id="fixed_promotion_strict_anchor_no_price_highlight",
            lever_id="model",
            changed_field="model_only",
            description="T02 promotion에서 main baseline strict prompt를 유지하되 highlightPrice=false 조건을 명시하고 Gemma 4와 gpt-5-mini를 비교합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_highlight_price_off_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 14자 안팎으로 유지하세요.\n"
                "- benefit primaryText는 가능하면 12~14자 안쪽으로 쓰고, 14자를 넘기지 마세요.\n"
                "- urgency primaryText는 10자 안팎, cta primaryText는 8자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 방문, 저장, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option highlightPrice=false이므로 가격 숫자나 할인폭을 hook, benefit, urgency의 주제처럼 앞세우지 마세요.\n"
                "- 혜택이 있더라도 가격 숫자보다 메뉴 강점, 식감, 구성, 방문 이유를 먼저 보이게 쓰세요.\n"
                "- 지역명은 hookText와 scene primaryText에는 넣지 마세요.\n"
                "- captions 3개 중 정확히 1개 caption에는 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- 위 caption에서 지역 표현을 '서울숲 근처', '서울숲 인근', '성수역', '근처', '동네' 같은 우회 표현으로 바꾸지 마세요.\n"
                "- 지역명이 들어간 hashtag는 정확히 1개만 쓰고, 그 hashtag는 '성수동' 문자열을 그대로 포함해야 합니다.\n"
                "- 긴 설명은 subText로 보내고, primaryText는 poster headline처럼 짧게 유지하세요.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "highlightPrice=false일 때는 할인 숫자를 밀기보다 메뉴 매력과 방문 이유가 먼저 읽히게 쓰세요.\n"
                "hook, benefit, urgency, cta는 각 장면에서 바로 읽히도록 짧고 직접적으로 쓰고, 가격을 억지로 비워서 심심해지지 않게 맛과 분위기 근거를 넣으세요."
            ),
        )
        return ModelComparisonDefinition(
            experiment_id="EXP-143",
            experiment_title="Promotion Strict Anchor Highlight Price Off Coverage Comparison",
            objective="T02 promotion, b_grade_fun, highlightPrice=false, shorterCopy=true, emphasizeRegion=false 조건에서 strict anchor baseline 원칙을 유지했을 때 Gemma 4와 gpt-5-mini 중 누가 가격 비강조 quick option coverage 후보가 되는지 비교합니다.",
            scenario=get_service_aligned_bgrade_highlight_price_off_scenario(),
            prompt_variant=fixed_prompt_variant,
            models=(
                ModelConfig(provider="google", model_name="models/gemma-4-31b-it"),
                ModelConfig(provider="openai", model_name="gpt-5-mini"),
            ),
        )

    if experiment_id == "EXP-144":
        fixed_prompt_variant = PromptVariant(
            variant_id="fixed_promotion_strict_anchor_no_shorter_copy",
            lever_id="model",
            changed_field="model_only",
            description="T02 promotion에서 main baseline strict prompt를 유지하되 shorterCopy=false 조건을 명시하고 Gemma 4와 gpt-5-mini를 비교합니다.",
            role_instruction=common_role,
            slot_guidance=(
                "sceneText와 subText에는 템플릿의 각 textRole에 맞는 문구를 채우세요. "
                "같은 의미를 기계적으로 반복하지 말고, 광고 문맥에 맞게 자연스럽게 작성하세요.\n"
                f"{build_reference_hook_guidance(DEFAULT_TEMPLATE_SPEC_ROOT, get_service_aligned_bgrade_shorter_copy_off_scenario())}\n"
                "추가 output constraint:\n"
                "- hookText와 hook primaryText는 14자 안팎으로 유지하세요.\n"
                "- benefit primaryText는 가능하면 12~14자 안쪽으로 쓰고, 14자를 넘기지 마세요.\n"
                "- urgency primaryText는 10자 안팎, cta primaryText는 8자 안팎으로 쓰세요.\n"
                "- cta와 ctaText는 방문, 저장, 확인, 예약 중 하나의 행동 단어로 시작하세요.\n"
                "- quick option shorterCopy=false이므로 모든 문장을 억지로 한 줄 슬로건처럼 자르지 말고, 필요한 맥락은 subText와 caption으로 분리해 남기세요.\n"
                "- 대신 primaryText는 계속 poster headline처럼 짧아야 하며, 설명이 길어질수록 subText로 보내세요.\n"
                "- 가격, 할인, 세트 이점은 감춰도 되는 정보가 아니므로 benefit나 caption에서 자연스럽게 살리되, 같은 숫자나 혜택 문구를 여러 surface에 반복하지 마세요.\n"
                "- 지역명은 hookText와 scene primaryText에는 넣지 마세요.\n"
                "- captions 3개 중 정확히 1개 caption에는 문자열 '성수동'을 그대로 1회 넣으세요.\n"
                "- 위 caption에서 지역 표현을 '서울숲 근처', '서울숲 인근', '성수역', '근처', '동네' 같은 우회 표현으로 바꾸지 마세요.\n"
                "- 지역명이 들어간 hashtag는 정확히 1개만 쓰고, 그 hashtag는 '성수동' 문자열을 그대로 포함해야 합니다.\n"
                "- 다른 captions와 hashtags에는 지역명을 반복하지 마세요."
            ),
            audience_guidance=(
                "타깃 고객은 성수동에서 퇴근 후 한 끼나 가볍게 한잔할 곳을 찾는 20~30대 방문객입니다.\n"
                "B급 감성은 조잡함이 아니라 동네 전단지처럼 바로 읽히는 생활 밀착형 과장 톤입니다.\n"
                "shorterCopy=false일 때는 모든 문장을 짧게 깎는 것보다 훅-혜택-행동 흐름이 자연스럽게 이어지도록 한 줄 보조 설명을 허용하세요.\n"
                "hook, benefit, urgency, cta는 각 장면에서 바로 읽히도록 짧고 직접적으로 유지하되, 설명이 필요하면 subText나 caption 한 줄로 정리하세요."
            ),
        )
        return ModelComparisonDefinition(
            experiment_id="EXP-144",
            experiment_title="Promotion Strict Anchor Shorter Copy Off Coverage Comparison",
            objective="T02 promotion, b_grade_fun, highlightPrice=true, shorterCopy=false, emphasizeRegion=false 조건에서 strict anchor baseline 원칙을 유지했을 때 Gemma 4와 gpt-5-mini 중 누가 비압축 quick option coverage 후보가 되는지 비교합니다.",
            scenario=get_service_aligned_bgrade_shorter_copy_off_scenario(),
            prompt_variant=fixed_prompt_variant,
            models=(
                ModelConfig(provider="google", model_name="models/gemma-4-31b-it"),
                ModelConfig(provider="openai", model_name="gpt-5-mini"),
            ),
        )

    raise ValueError(f"unsupported model comparison id: {experiment_id}")


def load_experiment_context(template_spec_root: Path, scenario: ScenarioSpec) -> dict[str, Any]:
    template = load_template(template_spec_root, scenario.template_id)
    style = load_style(template_spec_root, scenario.style_id)
    copy_rule = load_copy_rule(template_spec_root, scenario.purpose)
    return {
        "template": template,
        "style": style,
        "copy_rule": copy_rule,
    }


def load_reference_hook_pack(template_spec_root: Path) -> dict[str, Any]:
    hook_pack_path = template_spec_root / "manifests" / "reference-hook-pack-v1.json"
    return json.loads(hook_pack_path.read_text(encoding="utf-8"))


def select_reference_hook_candidates(template_spec_root: Path, scenario: ScenarioSpec, max_candidates: int = 3) -> list[dict[str, Any]]:
    hook_pack = load_reference_hook_pack(template_spec_root)
    candidates: list[dict[str, Any]] = []
    for hook in hook_pack.get("hooks", []):
        if scenario.purpose not in hook.get("supportedPurposes", []):
            continue
        if scenario.template_id not in hook.get("supportedTemplates", []):
            continue
        if scenario.style_id not in hook.get("supportedStyles", []):
            continue
        candidates.append(hook)
    return candidates[:max_candidates]


def build_reference_hook_guidance(template_spec_root: Path, scenario: ScenarioSpec, max_candidates: int = 3) -> str:
    candidates = select_reference_hook_candidates(template_spec_root, scenario, max_candidates=max_candidates)
    if not candidates:
        return "추가 hook 후보 없음. 기본 슬롯 지시만 따르세요."

    lines = [
        "아래 reference-derived hook 후보의 문장 구조를 우선 참고하세요.",
        "문장을 그대로 복사하지 말고, 현재 자산과 목적에 맞게 같은 구조로 다시 작성하세요.",
        "hookText와 첫 장면 primaryText는 14자 안팎의 짧은 한 줄로 유지하세요.",
        "hook은 혜택, 궁금증, 방문 이유 중 하나가 바로 보이게 시작하세요.",
        "body slot은 hook을 반복 설명하지 말고, 구체 정보로 바로 이어지게 작성하세요.",
        "cta는 감탄보다 저장, 방문, 확인 같은 행동 단어를 앞쪽에 두세요.",
        "",
        "[reference hook candidates]",
    ]
    for hook in candidates:
        lines.append(
            f"- {hook['hookId']} ({hook['patternId']}): {hook['primaryLine']} | notes: {hook['notes']}"
        )
    return "\n".join(lines)


def build_deterministic_reference_bundle(template_spec_root: Path, scenario: ScenarioSpec) -> dict[str, Any]:
    context = load_experiment_context(template_spec_root, scenario)
    project = {
        "business_type": scenario.business_type,
        "purpose": scenario.purpose,
        "region_name": scenario.region_name,
    }
    processed_assets = [{"source": path, "vertical": path, "square": path} for path in scenario.asset_paths]
    return _build_copy_bundle(
        project,
        context["template"],
        context["copy_rule"],
        scenario.style_id,
        scenario.quick_options,
        scenario.quick_options,
        processed_assets,
    )


def build_prompt_package(template_spec_root: Path, scenario: ScenarioSpec, variant: PromptVariant) -> dict[str, str]:
    context = load_experiment_context(template_spec_root, scenario)
    template = context["template"]
    style = context["style"]
    copy_rule = context["copy_rule"]
    text_roles = list(dict.fromkeys(scene["textRole"] for scene in template["scenes"]))
    region_policy = copy_rule["regionPolicy"]
    caption_rules = copy_rule["captionRules"]
    asset_names = ", ".join(path.name for path in scenario.asset_paths)
    scene_text_lines = ['  "sceneText": {']
    for index, role in enumerate(text_roles):
        suffix = "," if index < len(text_roles) - 1 else ""
        scene_text_lines.append(f'    "{role}": "string"{suffix}')
    scene_text_lines.append("  },")
    sub_text_lines = ['  "subText": {']
    for index, role in enumerate(text_roles):
        suffix = "," if index < len(text_roles) - 1 else ""
        sub_text_lines.append(f'    "{role}": "string"{suffix}')
    sub_text_lines.append("  }")

    system_instruction = "\n".join(
        [
            variant.role_instruction,
            "출력은 오직 JSON 객체 하나만 반환하세요.",
            "입력에 없는 사실, 가격, 운영 시간, 후기 평점은 추측하지 마세요.",
            "한국어만 사용하고, 읽자마자 이해되는 짧은 광고 문장으로 작성하세요.",
        ]
    )
    user_prompt = "\n".join(
        [
            "[고정 입력 조건]",
            f"- 업종: {scenario.business_type}",
            f"- 목적: {scenario.purpose}",
            f"- 스타일: {scenario.style_id}",
            f"- 지역명: {scenario.region_name}",
            f"- 상세 위치: {scenario.detail_location or '없음'}",
            f"- 템플릿: {template['templateId']} / {template['title']}",
            f"- 자산 세트: {asset_names}",
            f"- quick options: {json.dumps(scenario.quick_options, ensure_ascii=False)}",
            "",
            "[템플릿/카피 규칙]",
            f"- 필수 textRole 순서: {', '.join(copy_rule['structure'])}",
            f"- 이번 템플릿에 실제로 필요한 textRole: {', '.join(text_roles)}",
            f"- 지역 반영: 제목/본문/해시태그 중 최소 {region_policy['minSlots']}개 영역에 반영, 지역명 총 반복은 {region_policy['maxRepeat']}회 이하",
            f"- 캡션 수: 정확히 {caption_rules['minOptions']}개",
            f"- 캡션 최대 길이: {caption_rules['maxLength']}자",
            f"- 해시태그 수: 5~8개",
            f"- 스타일 톤: {style['textTone']}",
            "",
            "[타깃 고객/톤 지시]",
            variant.audience_guidance,
            "",
            "[슬롯 지시]",
            variant.slot_guidance,
            "",
            "[필수 출력 JSON shape]",
            '{',
            '  "hookText": "string",',
            '  "captions": ["string", "string", "string"],',
            '  "hashtags": ["#string"],',
            '  "ctaText": "string",',
            *scene_text_lines,
            *sub_text_lines,
            '}',
        ]
    )
    return {
        "system_instruction": system_instruction,
        "user_prompt": user_prompt,
    }


def run_experiment(
    experiment: ExperimentDefinition,
    template_spec_root: Path = DEFAULT_TEMPLATE_SPEC_ROOT,
    artifact_root: Path = DEFAULT_ARTIFACT_ROOT,
    api_key_env: str = "GEMINI_API_KEY",
) -> dict[str, Any]:
    artifact_root.mkdir(parents=True, exist_ok=True)
    context = load_experiment_context(template_spec_root, experiment.scenario)
    deterministic_bundle = build_deterministic_reference_bundle(template_spec_root, experiment.scenario)
    deterministic_evaluation = evaluate_copy_bundle(
        deterministic_bundle,
        experiment.scenario,
        context["template"],
        context["copy_rule"],
    )

    results: list[dict[str, Any]] = [
        {
            "variant_id": "deterministic_reference",
            "lever_id": "reference",
            "changed_field": None,
            "description": "현재 production deterministic baseline 참조 결과입니다.",
            "provider": "deterministic",
            "model_name": "rule_based_copy_builder",
            "latency_ms": 0,
            "prompt": None,
            "output": deterministic_bundle,
            "evaluation": deterministic_evaluation,
            "scene_plan": build_scene_plan_preview(template_spec_root, experiment.scenario, deterministic_bundle),
            "scene_plan_metrics": evaluate_scene_plan_preview(template_spec_root, experiment.scenario, deterministic_bundle),
            "korean_integrity": evaluate_korean_integrity(deterministic_bundle),
        }
    ]

    variants = (experiment.baseline_variant, *experiment.candidate_variants)
    for variant in variants:
        prompt_package = build_prompt_package(template_spec_root, experiment.scenario, variant)
        started = time.perf_counter()
        try:
            output = generate_copy_bundle_with_model(
                model=experiment.model,
                prompt_package=prompt_package,
                asset_paths=experiment.scenario.asset_paths,
                api_key_env=api_key_env,
            )
            latency_ms = int((time.perf_counter() - started) * 1000)
            results.append(
                {
                    "variant_id": variant.variant_id,
                    "lever_id": variant.lever_id,
                    "changed_field": variant.changed_field,
                    "description": variant.description,
                    "provider": experiment.model.provider,
                    "model_name": experiment.model.model_name,
                    "latency_ms": latency_ms,
                    "prompt": prompt_package,
                    "output": output,
                    "evaluation": evaluate_copy_bundle(
                        output,
                        experiment.scenario,
                        context["template"],
                        context["copy_rule"],
                    ),
                    "scene_plan": build_scene_plan_preview(template_spec_root, experiment.scenario, output),
                    "scene_plan_metrics": evaluate_scene_plan_preview(template_spec_root, experiment.scenario, output),
                    "korean_integrity": evaluate_korean_integrity(output),
                    "error": None,
                }
            )
        except Exception as exc:  # noqa: BLE001
            latency_ms = int((time.perf_counter() - started) * 1000)
            sanitized_error = sanitize_error_message(str(exc))
            results.append(
                {
                    "variant_id": variant.variant_id,
                    "lever_id": variant.lever_id,
                    "changed_field": variant.changed_field,
                    "description": variant.description,
                    "provider": experiment.model.provider,
                    "model_name": experiment.model.model_name,
                    "latency_ms": latency_ms,
                    "prompt": prompt_package,
                    "output": {},
                    "evaluation": {
                        "required_roles": [],
                        "region_slot_hits": 0,
                        "region_repeat_count": 0,
                        "audience_cue_count": 0,
                        "caption_count": 0,
                        "hashtag_count": 0,
                        "distinct_scene_lines": 0,
                        "failed_checks": [f"request failed: {sanitized_error}"],
                        "passed_checks": 0,
                        "score": 0.0,
                    },
                    "scene_plan": None,
                    "scene_plan_metrics": {
                        "scene_count": 0,
                        "max_text_per_scene": 0,
                        "over_limit_scene_ids": [],
                        "repeated_copy_scene_ids": [],
                        "closing_cta_actionable": False,
                        "headline_lengths": {},
                    },
                    "korean_integrity": empty_korean_integrity_metrics(),
                    "error": sanitized_error,
                }
            )

    artifact = {
        "experiment_id": experiment.experiment_id,
        "experiment_title": experiment.experiment_title,
        "objective": experiment.objective,
        "scenario": serialize_scenario(experiment.scenario),
        "model": asdict(experiment.model),
        "results": results,
        "comparison": summarize_results(results),
    }
    artifact_name = slugify(f"{experiment.experiment_id}-{experiment.experiment_title}")
    artifact_path = artifact_root / f"{artifact_name}.json"
    artifact_path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")
    artifact["artifact_path"] = str(artifact_path)
    return artifact


def run_model_comparison_experiment(
    experiment: ModelComparisonDefinition,
    template_spec_root: Path = DEFAULT_TEMPLATE_SPEC_ROOT,
    artifact_root: Path = DEFAULT_ARTIFACT_ROOT,
) -> dict[str, Any]:
    artifact_root.mkdir(parents=True, exist_ok=True)
    context = load_experiment_context(template_spec_root, experiment.scenario)
    deterministic_bundle = build_deterministic_reference_bundle(template_spec_root, experiment.scenario)
    deterministic_evaluation = evaluate_copy_bundle(
        deterministic_bundle,
        experiment.scenario,
        context["template"],
        context["copy_rule"],
    )
    prompt_package = build_prompt_package(template_spec_root, experiment.scenario, experiment.prompt_variant)

    results: list[dict[str, Any]] = [
        {
            "variant_id": "deterministic_reference",
            "lever_id": "reference",
            "changed_field": None,
            "description": "현재 production deterministic baseline 참조 결과입니다.",
            "provider": "deterministic",
            "model_name": "rule_based_copy_builder",
            "latency_ms": 0,
            "prompt": None,
            "output": deterministic_bundle,
            "evaluation": deterministic_evaluation,
            "scene_plan": build_scene_plan_preview(template_spec_root, experiment.scenario, deterministic_bundle),
            "scene_plan_metrics": evaluate_scene_plan_preview(template_spec_root, experiment.scenario, deterministic_bundle),
            "korean_integrity": evaluate_korean_integrity(deterministic_bundle),
        }
    ]

    for model in experiment.models:
        started = time.perf_counter()
        try:
            output = generate_copy_bundle_with_model(
                model=model,
                prompt_package=prompt_package,
                asset_paths=experiment.scenario.asset_paths,
                api_key_env=resolve_api_key_env(model.provider),
            )
            latency_ms = int((time.perf_counter() - started) * 1000)
            results.append(
                {
                    "variant_id": slugify(f"{model.provider}-{model.model_name}"),
                    "lever_id": "model",
                    "changed_field": "model",
                    "description": f"{model.provider}:{model.model_name} 비교 결과",
                    "provider": model.provider,
                    "model_name": model.model_name,
                    "latency_ms": latency_ms,
                    "prompt": prompt_package,
                    "output": output,
                    "evaluation": evaluate_copy_bundle(
                        output,
                        experiment.scenario,
                        context["template"],
                        context["copy_rule"],
                    ),
                    "scene_plan": build_scene_plan_preview(template_spec_root, experiment.scenario, output),
                    "scene_plan_metrics": evaluate_scene_plan_preview(template_spec_root, experiment.scenario, output),
                    "korean_integrity": evaluate_korean_integrity(output),
                    "error": None,
                }
            )
        except Exception as exc:  # noqa: BLE001
            latency_ms = int((time.perf_counter() - started) * 1000)
            sanitized_error = sanitize_error_message(str(exc))
            results.append(
                {
                    "variant_id": slugify(f"{model.provider}-{model.model_name}"),
                    "lever_id": "model",
                    "changed_field": "model",
                    "description": f"{model.provider}:{model.model_name} 비교 결과",
                    "provider": model.provider,
                    "model_name": model.model_name,
                    "latency_ms": latency_ms,
                    "prompt": prompt_package,
                    "output": {},
                    "evaluation": {
                        "required_roles": [],
                        "region_slot_hits": 0,
                        "region_repeat_count": 0,
                        "audience_cue_count": 0,
                        "caption_count": 0,
                        "hashtag_count": 0,
                        "distinct_scene_lines": 0,
                        "failed_checks": [f"request failed: {sanitized_error}"],
                        "passed_checks": 0,
                        "score": 0.0,
                    },
                    "scene_plan": None,
                    "scene_plan_metrics": {
                        "scene_count": 0,
                        "max_text_per_scene": 0,
                        "over_limit_scene_ids": [],
                        "repeated_copy_scene_ids": [],
                        "closing_cta_actionable": False,
                        "headline_lengths": {},
                    },
                    "korean_integrity": empty_korean_integrity_metrics(),
                    "error": sanitized_error,
                }
            )

    artifact = {
        "experiment_id": experiment.experiment_id,
        "experiment_title": experiment.experiment_title,
        "objective": experiment.objective,
        "scenario": serialize_scenario(experiment.scenario),
        "prompt_variant": asdict(experiment.prompt_variant),
        "models": [asdict(model) for model in experiment.models],
        "results": results,
        "comparison": summarize_results(results),
    }
    artifact_name = slugify(f"{experiment.experiment_id}-{experiment.experiment_title}")
    artifact_path = artifact_root / f"{artifact_name}.json"
    artifact_path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")
    artifact["artifact_path"] = str(artifact_path)
    return artifact


def serialize_scenario(scenario: ScenarioSpec) -> dict[str, Any]:
    return {
        "scenario_id": scenario.scenario_id,
        "business_type": scenario.business_type,
        "purpose": scenario.purpose,
        "style_id": scenario.style_id,
        "region_name": scenario.region_name,
        "detail_location": scenario.detail_location,
        "template_id": scenario.template_id,
        "asset_paths": [str(path) for path in scenario.asset_paths],
        "quick_options": scenario.quick_options,
    }


def generate_copy_bundle_with_google_model(
    model: ModelConfig,
    prompt_package: dict[str, str],
    asset_paths: tuple[Path, ...],
    api_key_env: str = "GEMINI_API_KEY",
) -> dict[str, Any]:
    result = generate_copy_bundle_with_google_model_with_meta(
        model=model,
        prompt_package=prompt_package,
        asset_paths=asset_paths,
        api_key_env=api_key_env,
    )
    return result["output"]


def _is_retryable_google_transport_error(exc: Exception) -> bool:
    if isinstance(exc, (TimeoutError, socket.timeout)):
        return True
    if isinstance(exc, urllib.error.URLError):
        return isinstance(exc.reason, (TimeoutError, socket.timeout))
    return False


def generate_copy_bundle_with_google_model_with_meta(
    model: ModelConfig,
    prompt_package: dict[str, str],
    asset_paths: tuple[Path, ...],
    api_key_env: str = "GEMINI_API_KEY",
    request_timeout_sec: int = 60,
    max_retries: int = 0,
    retry_backoff_sec: float = 0.0,
) -> dict[str, Any]:
    api_key = os.environ.get(api_key_env)
    if not api_key:
        raise RuntimeError(f"{api_key_env} is not set")

    request_parts = [{"text": prompt_package["user_prompt"]}]
    for path in asset_paths:
        request_parts.append(
            {
                "inline_data": {
                    "mime_type": infer_mime_type(path),
                    "data": base64.b64encode(path.read_bytes()).decode("ascii"),
                }
            }
        )

    body = {
        "systemInstruction": {
            "parts": [
                {
                    "text": prompt_package["system_instruction"],
                }
            ]
        },
        "contents": [
            {
                "role": "user",
                "parts": request_parts,
            }
        ],
        "generationConfig": {
            "temperature": model.temperature,
            "topP": model.top_p,
            "maxOutputTokens": model.max_output_tokens,
            "responseMimeType": "application/json",
        },
    }

    url = f"https://generativelanguage.googleapis.com/v1beta/{model.model_name}:generateContent?key={api_key}"
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    attempt = 0
    while True:
        attempt += 1
        try:
            with urllib.request.urlopen(request, timeout=request_timeout_sec) as response:
                payload = json.load(response)
            break
        except urllib.error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(sanitize_error_message(f"google model request failed: {exc.code} {detail}")) from exc
        except Exception as exc:  # noqa: BLE001
            if _is_retryable_google_transport_error(exc) and attempt <= max_retries:
                if retry_backoff_sec > 0:
                    time.sleep(retry_backoff_sec * attempt)
                continue
            raise RuntimeError(
                sanitize_error_message(
                    f"google model transport failed after {attempt} attempt(s): {exc}"
                )
            ) from exc

    candidates = payload.get("candidates") or []
    if not candidates:
        raise RuntimeError(f"model returned no candidates: {json.dumps(payload, ensure_ascii=False)}")

    parts = candidates[0].get("content", {}).get("parts", [])
    text = "".join(part.get("text", "") for part in parts if "text" in part).strip()
    if not text:
        raise RuntimeError(f"model returned empty text: {json.dumps(payload, ensure_ascii=False)}")
    return {
        "output": parse_json_object(text),
        "requestMeta": {
            "provider": "google",
            "modelName": model.model_name,
            "timeoutSec": request_timeout_sec,
            "maxRetries": max_retries,
            "retryBackoffSec": retry_backoff_sec,
            "attemptCount": attempt,
            "retriesUsed": max(0, attempt - 1),
        },
    }


def resolve_api_key_env(provider: str) -> str:
    if provider == "google":
        return "GEMINI_API_KEY"
    if provider == "openai":
        return "OPENAI_API_KEY"
    if provider == "huggingface":
        return "HF_TOKEN"
    if provider == "ollama":
        return "OLLAMA_HOST"
    raise ValueError(f"unsupported provider: {provider}")


def generate_copy_bundle_with_model(
    model: ModelConfig,
    prompt_package: dict[str, str],
    asset_paths: tuple[Path, ...],
    api_key_env: str,
) -> dict[str, Any]:
    if model.provider == "google":
        return generate_copy_bundle_with_google_model(
            model=model,
            prompt_package=prompt_package,
            asset_paths=asset_paths,
            api_key_env=api_key_env,
        )
    if model.provider == "openai":
        return generate_copy_bundle_with_openai_model(
            model=model,
            prompt_package=prompt_package,
            asset_paths=asset_paths,
            api_key_env=api_key_env,
        )
    if model.provider == "huggingface":
        return generate_copy_bundle_with_huggingface_model(
            model=model,
            prompt_package=prompt_package,
            asset_paths=asset_paths,
            api_key_env=api_key_env,
        )
    if model.provider == "ollama":
        return generate_copy_bundle_with_ollama_model(
            model=model,
            prompt_package=prompt_package,
            asset_paths=asset_paths,
            api_key_env=api_key_env,
        )
    raise ValueError(f"unsupported provider: {model.provider}")


def generate_copy_bundle_with_openai_model(
    model: ModelConfig,
    prompt_package: dict[str, str],
    asset_paths: tuple[Path, ...],
    api_key_env: str = "OPENAI_API_KEY",
) -> dict[str, Any]:
    api_key = os.environ.get(api_key_env)
    if not api_key:
        raise RuntimeError(f"{api_key_env} is not set")

    content: list[dict[str, Any]] = [{"type": "input_text", "text": prompt_package["user_prompt"]}]
    for path in asset_paths:
        mime_type = infer_mime_type(path)
        encoded = base64.b64encode(path.read_bytes()).decode("ascii")
        content.append(
            {
                "type": "input_image",
                "image_url": f"data:{mime_type};base64,{encoded}",
            }
        )

    body = {
        "model": model.model_name,
        "instructions": prompt_package["system_instruction"],
        "input": [
            {
                "role": "user",
                "content": content,
            }
        ],
        "max_output_tokens": model.max_output_tokens,
        "text": {
            "format": {
                "type": "json_object",
            },
            "verbosity": "low" if model.model_name.startswith("gpt-5") else "medium",
        },
    }
    if model.model_name.startswith("gpt-5"):
        body["reasoning"] = {
            "effort": "minimal",
        }

    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(sanitize_error_message(f"openai model request failed: {exc.code} {detail}")) from exc

    text = extract_openai_response_text(payload)
    if not text:
        raise RuntimeError(f"openai model returned empty text: {json.dumps(payload, ensure_ascii=False)}")
    return parse_json_object(text)


def generate_copy_bundle_with_huggingface_model(
    model: ModelConfig,
    prompt_package: dict[str, str],
    asset_paths: tuple[Path, ...],
    api_key_env: str = "HF_TOKEN",
) -> dict[str, Any]:
    api_key = os.environ.get(api_key_env) or os.environ.get("HUGGINGFACE_HUB_TOKEN")
    if not api_key:
        raise RuntimeError(f"{api_key_env} is not set")

    asset_names = ", ".join(path.name for path in asset_paths)
    text_prompt = (
        f"{prompt_package['system_instruction']}\n\n"
        f"참고 자산 파일명: {asset_names}\n\n"
        f"{prompt_package['user_prompt']}"
    )
    body = {
        "model": model.model_name,
        "messages": [
            {
                "role": "user",
                "content": text_prompt,
            }
        ],
        "max_tokens": model.max_output_tokens,
    }

    request = urllib.request.Request(
        "https://router.huggingface.co/v1/chat/completions",
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(sanitize_error_message(f"huggingface model request failed: {exc.code} {detail}")) from exc

    try:
        text = str(payload["choices"][0]["message"]["content"]).strip()
    except (KeyError, IndexError, TypeError) as exc:
        raise RuntimeError(f"huggingface model returned unexpected payload: {json.dumps(payload, ensure_ascii=False)}") from exc

    text = strip_think_blocks(text)
    if not text:
        raise RuntimeError(f"huggingface model returned empty text: {json.dumps(payload, ensure_ascii=False)}")
    return parse_json_object(text)


def generate_copy_bundle_with_ollama_model(
    model: ModelConfig,
    prompt_package: dict[str, str],
    asset_paths: tuple[Path, ...],
    api_key_env: str = "OLLAMA_HOST",
) -> dict[str, Any]:
    base_url = (os.environ.get(api_key_env) or OLLAMA_DEFAULT_HOST).rstrip("/")
    supports_vision = ollama_supports_vision(model.model_name, base_url)
    user_message: dict[str, Any] = {
        "role": "user",
        "content": prompt_package["user_prompt"],
    }
    if supports_vision:
        user_message["images"] = [base64.b64encode(path.read_bytes()).decode("ascii") for path in asset_paths]
    else:
        asset_names = ", ".join(path.name for path in asset_paths)
        user_message["content"] = (
            f"참고 자산 파일명: {asset_names}\n\n"
            f"{prompt_package['user_prompt']}\n\n"
            "이 모델은 이번 경로에서 이미지를 직접 해석하지 못할 수 있으므로, 업종/목적/스타일/지역과 자산 파일명만 근거로 작성하세요."
        )

    body = {
        "model": model.model_name,
        "stream": False,
        "format": "json",
        "messages": [
            {
                "role": "system",
                "content": prompt_package["system_instruction"],
            },
            user_message,
        ],
        "options": {
            "temperature": model.temperature,
            "top_p": model.top_p,
            "num_predict": model.max_output_tokens,
        },
    }
    request = urllib.request.Request(
        f"{base_url}/api/chat",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=600) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"ollama model request failed: {exc.code} {detail}") from exc

    try:
        text = str(payload["message"]["content"]).strip()
    except (KeyError, TypeError) as exc:
        raise RuntimeError(f"ollama model returned unexpected payload: {json.dumps(payload, ensure_ascii=False)}") from exc

    text = strip_think_blocks(text)
    if not text:
        raise RuntimeError(f"ollama model returned empty text: {json.dumps(payload, ensure_ascii=False)}")
    return parse_json_object(text)


def ollama_supports_vision(model_name: str, base_url: str) -> bool:
    body = {"model": model_name}
    request = urllib.request.Request(
        f"{base_url}/api/show",
        data=json.dumps(body).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=60) as response:
            payload = json.load(response)
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"ollama show request failed: {exc.code} {detail}") from exc

    capabilities = payload.get("capabilities", [])
    return isinstance(capabilities, list) and "vision" in capabilities


def strip_think_blocks(text: str) -> str:
    without_think = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()
    return without_think.strip()


def empty_korean_integrity_metrics() -> dict[str, Any]:
    return {
        "hangul_char_count": 0,
        "contains_replacement_char": False,
        "suspicious_markers": [],
        "is_suspected_broken": False,
    }


def evaluate_korean_integrity(copy_bundle: dict[str, Any]) -> dict[str, Any]:
    texts = collect_text_values(copy_bundle)
    combined = " ".join(texts)
    suspicious_markers = [marker for marker in MOJIBAKE_MARKERS if marker in combined]
    return {
        "hangul_char_count": len(re.findall(r"[가-힣]", combined)),
        "contains_replacement_char": "�" in combined,
        "suspicious_markers": suspicious_markers,
        "is_suspected_broken": bool(suspicious_markers),
    }


def collect_text_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list):
        texts: list[str] = []
        for item in value:
            texts.extend(collect_text_values(item))
        return texts
    if isinstance(value, dict):
        texts = []
        for item in value.values():
            texts.extend(collect_text_values(item))
        return texts
    return []


def extract_openai_response_text(payload: dict[str, Any]) -> str:
    if isinstance(payload.get("output_text"), str) and payload["output_text"].strip():
        return payload["output_text"].strip()

    texts: list[str] = []
    for output in payload.get("output", []):
        if not isinstance(output, dict):
            continue
        for content in output.get("content", []):
            if not isinstance(content, dict):
                continue
            text_value = content.get("text")
            if isinstance(text_value, str) and text_value.strip():
                texts.append(text_value.strip())

    return "\n".join(texts).strip()


def parse_json_object(raw_text: str) -> dict[str, Any]:
    stripped = raw_text.strip()
    if stripped.startswith("```"):
        stripped = stripped.strip("`")
        if stripped.startswith("json"):
            stripped = stripped[4:].strip()
    try:
        parsed = json.loads(stripped)
    except json.JSONDecodeError as exc:
        for index in sorted({position for position, char in enumerate(stripped) if char == "{"}, reverse=True):
            try:
                parsed = json.loads(stripped[index:])
                break
            except json.JSONDecodeError:
                continue
        else:
            raise RuntimeError(f"invalid JSON response: {raw_text}") from exc
    if not isinstance(parsed, dict):
        raise RuntimeError(f"expected JSON object, got: {type(parsed)!r}")
    return parsed


def infer_mime_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix in {".jpg", ".jpeg"}:
        return "image/jpeg"
    if suffix == ".webp":
        return "image/webp"
    return "image/png"


def evaluate_copy_bundle(bundle: dict[str, Any], scenario: ScenarioSpec, template: dict[str, Any], copy_rule: dict[str, Any]) -> dict[str, Any]:
    failed_checks: list[str] = []
    required_roles = list(dict.fromkeys(scene["textRole"] for scene in template["scenes"]))
    scene_text = bundle.get("sceneText") if isinstance(bundle.get("sceneText"), dict) else {}
    sub_text = bundle.get("subText") if isinstance(bundle.get("subText"), dict) else {}
    captions = bundle.get("captions") if isinstance(bundle.get("captions"), list) else []
    hashtags = bundle.get("hashtags") if isinstance(bundle.get("hashtags"), list) else []
    hook_text = str(bundle.get("hookText", "")).strip()
    cta_text = str(bundle.get("ctaText", "")).strip()

    if not hook_text:
        failed_checks.append("hookText is empty")
    if len(captions) != copy_rule["captionRules"]["minOptions"]:
        failed_checks.append(f"caption count mismatch: expected {copy_rule['captionRules']['minOptions']}, got {len(captions)}")
    if captions and max(len(str(caption)) for caption in captions) > copy_rule["captionRules"]["maxLength"]:
        failed_checks.append("caption length exceeded max limit")
    if len(hashtags) < 5 or len(hashtags) > 8:
        failed_checks.append("hashtag count is outside 5~8")
    if not cta_text:
        failed_checks.append("ctaText is empty")
    if cta_text and not any(keyword in cta_text for keyword in REGION_ACTION_KEYWORDS):
        failed_checks.append("ctaText lacks explicit action keyword")
    if len(set(str(caption).strip() for caption in captions if str(caption).strip())) != len(captions):
        failed_checks.append("captions contain duplicates")
    if len(set(str(tag).strip() for tag in hashtags if str(tag).strip())) != len(hashtags):
        failed_checks.append("hashtags contain duplicates")
    if any(not str(tag).startswith("#") for tag in hashtags):
        failed_checks.append("hashtags must start with #")

    missing_scene_roles = [role for role in required_roles if not str(scene_text.get(role, "")).strip()]
    if missing_scene_roles:
        failed_checks.append(f"sceneText missing roles: {', '.join(missing_scene_roles)}")
    missing_sub_roles = [role for role in required_roles if not str(sub_text.get(role, "")).strip()]
    if missing_sub_roles:
        failed_checks.append(f"subText missing roles: {', '.join(missing_sub_roles)}")

    region_slot_hits = count_region_slot_hits(bundle, scenario.region_name)
    region_repeat_count = count_region_mentions(bundle, scenario.region_name)
    detail_location_policy_id = resolve_detail_location_policy_id(copy_rule, scenario)
    detail_location_policy_surfaces = resolve_detail_location_policy_surfaces(copy_rule, scenario)
    detail_location_leaks_by_surface = count_detail_location_leaks_by_surface(bundle, scenario)
    detail_location_leak_count = sum(
        int(detail_location_leaks_by_surface.get(surface, 0)) for surface in detail_location_policy_surfaces
    )
    audience_cue_count = count_audience_context_mentions(bundle)
    if region_slot_hits < copy_rule["regionPolicy"]["minSlots"]:
        failed_checks.append("region appears in fewer than required areas")
    if region_repeat_count > copy_rule["regionPolicy"]["maxRepeat"]:
        failed_checks.append("region repeated more than allowed")
    if detail_location_leak_count > 0:
        failed_checks.append("nearby location leaked into strict region budget")

    distinct_scene_lines = len({str(scene_text.get(role, "")).strip() for role in required_roles if str(scene_text.get(role, "")).strip()})
    if distinct_scene_lines < max(2, len(required_roles) - 1):
        failed_checks.append("sceneText variety is too low")

    total_checks = 15 if detail_location_policy_surfaces else 14
    passed_checks = max(0, total_checks - len(failed_checks))
    return {
        "required_roles": required_roles,
        "region_slot_hits": region_slot_hits,
        "region_repeat_count": region_repeat_count,
        "detail_location_policy_id": detail_location_policy_id,
        "detail_location_policy_surfaces": list(detail_location_policy_surfaces),
        "detail_location_leak_count": detail_location_leak_count,
        "detail_location_leaks_by_surface": detail_location_leaks_by_surface,
        "audience_cue_count": audience_cue_count,
        "caption_count": len(captions),
        "hashtag_count": len(hashtags),
        "distinct_scene_lines": distinct_scene_lines,
        "failed_checks": failed_checks,
        "passed_checks": passed_checks,
        "score": round((passed_checks / total_checks) * 100, 1),
    }


def build_scene_plan_preview(template_spec_root: Path, scenario: ScenarioSpec, bundle: dict[str, Any]) -> dict[str, Any]:
    context = load_experiment_context(template_spec_root, scenario)
    processed_assets = [{"vertical": path, "square": path} for path in scenario.asset_paths]
    project = {
        "business_type": scenario.business_type,
        "purpose": scenario.purpose,
        "region_name": scenario.region_name,
    }
    return build_scene_plan(
        project=project,
        template=context["template"],
        style=context["style"],
        copy_bundle=bundle,
        processed_assets=processed_assets,
        storage_root=ROOT_DIR,
    )


def evaluate_scene_plan_preview(template_spec_root: Path, scenario: ScenarioSpec, bundle: dict[str, Any]) -> dict[str, Any]:
    scene_plan = build_scene_plan_preview(template_spec_root, scenario, bundle)
    style = load_experiment_context(template_spec_root, scenario)["style"]
    max_text_per_scene = int(style.get("rules", {}).get("maxTextPerScene", 0) or 0)

    over_limit_scene_ids: list[str] = []
    repeated_copy_scene_ids: list[str] = []
    headline_lengths: dict[str, int] = {}

    for scene in scene_plan["scenes"]:
        primary_text = str(scene["copy"]["primaryText"]).strip()
        secondary_text = str(scene["copy"]["secondaryText"]).strip()
        headline_lengths[scene["sceneId"]] = len(primary_text)
        if max_text_per_scene and len(primary_text) > max_text_per_scene:
            over_limit_scene_ids.append(scene["sceneId"])
        if scene["sceneRole"] != "closing" and normalize(primary_text) == normalize(secondary_text):
            repeated_copy_scene_ids.append(scene["sceneId"])

    closing_scene = next((scene for scene in scene_plan["scenes"] if scene["sceneRole"] == "closing"), None)
    closing_cta_text = str(closing_scene["copy"]["primaryText"]).strip() if closing_scene else ""
    return {
        "scene_count": scene_plan["sceneCount"],
        "max_text_per_scene": max_text_per_scene,
        "headline_lengths": headline_lengths,
        "over_limit_scene_ids": over_limit_scene_ids,
        "repeated_copy_scene_ids": repeated_copy_scene_ids,
        "closing_cta_actionable": bool(closing_cta_text and any(keyword in closing_cta_text for keyword in REGION_ACTION_KEYWORDS)),
    }


def count_region_slot_hits(bundle: dict[str, Any], region_name: str) -> int:
    normalized_region = normalize(region_name)
    hook_hit = normalized_region in normalize(str(bundle.get("hookText", "")))
    caption_hit = any(normalized_region in normalize(str(caption)) for caption in bundle.get("captions", []))
    hashtag_hit = any(normalized_region in normalize(str(tag)) for tag in bundle.get("hashtags", []))
    return sum(int(hit) for hit in (hook_hit, caption_hit, hashtag_hit))


def count_region_mentions(bundle: dict[str, Any], region_name: str) -> int:
    normalized_region = normalize(region_name)
    total = 0
    candidates = [str(bundle.get("hookText", "")), str(bundle.get("ctaText", ""))]
    candidates.extend(str(item) for item in bundle.get("captions", []))
    candidates.extend(str(item) for item in bundle.get("hashtags", []))
    for value in candidates:
        total += normalize(value).count(normalized_region)
    return total


def count_detail_location_leaks(bundle: dict[str, Any], scenario: ScenarioSpec) -> int:
    if not should_enforce_detail_location_guard(scenario):
        return 0
    return sum(count_detail_location_leaks_by_surface(bundle, scenario).values())


def should_enforce_detail_location_guard(scenario: ScenarioSpec) -> bool:
    return bool(scenario.detail_location)


def extract_detail_location_aliases(detail_location: str | None) -> tuple[str, ...]:
    if not detail_location:
        return ()

    aliases: list[str] = []
    normalized_detail = normalize(detail_location)
    if normalized_detail:
        aliases.append(normalized_detail)
        stripped = normalized_detail
        for token in DETAIL_LOCATION_GENERIC_TOKENS:
            if stripped.endswith(token):
                stripped = stripped[: -len(token)]
                break
        if stripped and stripped != normalized_detail and len(stripped) >= 2:
            aliases.append(stripped)

    for token in re.split(r"\s+", detail_location.strip()):
        normalized_token = normalize(token)
        if not normalized_token or normalized_token in DETAIL_LOCATION_GENERIC_TOKENS:
            continue
        if len(normalized_token) >= 2:
            aliases.append(normalized_token)

    seen: list[str] = []
    for alias in aliases:
        if alias not in seen:
            seen.append(alias)
    return tuple(seen)


def count_detail_location_leaks_by_surface(bundle: dict[str, Any], scenario: ScenarioSpec) -> dict[str, int]:
    aliases = extract_detail_location_aliases(scenario.detail_location)
    if not aliases:
        return {}

    leaks: dict[str, int] = {}
    for surface, values in collect_bundle_surface_texts(bundle).items():
        surface_leaks = 0
        for value in values:
            normalized_value = normalize(value)
            if any(alias in normalized_value for alias in aliases):
                surface_leaks += 1
        if surface_leaks > 0:
            leaks[surface] = surface_leaks
    return leaks


def resolve_detail_location_policy_surfaces(copy_rule: dict[str, Any], scenario: ScenarioSpec) -> tuple[str, ...]:
    if not should_enforce_detail_location_guard(scenario):
        return ()

    policy = copy_rule.get("locationPolicy") if isinstance(copy_rule, dict) else None
    if isinstance(policy, dict):
        configured_surfaces = []
        for surface in policy.get("forbiddenDetailLocationSurfaces", []):
            if isinstance(surface, str) and surface in LOCATION_POLICY_SURFACES and surface not in configured_surfaces:
                configured_surfaces.append(surface)
        if configured_surfaces:
            return tuple(configured_surfaces)

    return LOCATION_POLICY_SURFACES


def resolve_detail_location_policy_id(copy_rule: dict[str, Any], scenario: ScenarioSpec) -> str | None:
    if not should_enforce_detail_location_guard(scenario):
        return None

    policy = copy_rule.get("locationPolicy") if isinstance(copy_rule, dict) else None
    if isinstance(policy, dict):
        policy_id = policy.get("policyId")
        if isinstance(policy_id, str) and policy_id.strip():
            return policy_id

    return "strict_all_surfaces"


def collect_bundle_surface_texts(bundle: dict[str, Any]) -> dict[str, tuple[str, ...]]:
    scene_text = bundle.get("sceneText") if isinstance(bundle.get("sceneText"), dict) else {}
    sub_text = bundle.get("subText") if isinstance(bundle.get("subText"), dict) else {}
    return {
        "hookText": (str(bundle.get("hookText", "")),),
        "ctaText": (str(bundle.get("ctaText", "")),),
        "captions": tuple(str(item) for item in bundle.get("captions", [])),
        "hashtags": tuple(str(item) for item in bundle.get("hashtags", [])),
        "sceneText": tuple(str(item) for item in scene_text.values()),
        "subText": tuple(str(item) for item in sub_text.values()),
    }


def iter_bundle_text_values(bundle: dict[str, Any]) -> tuple[str, ...]:
    values: list[str] = []
    for surface_values in collect_bundle_surface_texts(bundle).values():
        values.extend(surface_values)
    return tuple(values)


def count_audience_context_mentions(bundle: dict[str, Any]) -> int:
    joined = " ".join(
        [
            str(bundle.get("hookText", "")),
            str(bundle.get("ctaText", "")),
            *[str(item) for item in bundle.get("captions", [])],
        ]
    )
    normalized = normalize(joined)
    return sum(normalized.count(keyword) for keyword in AUDIENCE_CONTEXT_KEYWORDS)


def normalize(value: str) -> str:
    return value.replace(" ", "").replace("\n", "").lower()


def slugify(value: str) -> str:
    lowered = value.lower().replace(" ", "-").replace("/", "-")
    cleaned = "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in lowered)
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-")


def summarize_results(results: list[dict[str, Any]]) -> dict[str, Any]:
    rows = []
    for item in results:
        evaluation = item["evaluation"]
        scene_plan_metrics = item.get("scene_plan_metrics", {})
        rows.append(
                {
                    "variant_id": item["variant_id"],
                    "provider": item["provider"],
                    "model_name": item["model_name"],
                    "latency_ms": item["latency_ms"],
                "score": evaluation["score"],
                "audience_cue_count": evaluation["audience_cue_count"],
                "over_limit_scene_ids": scene_plan_metrics.get("over_limit_scene_ids", []),
                "repeated_copy_scene_ids": scene_plan_metrics.get("repeated_copy_scene_ids", []),
                "closing_cta_actionable": scene_plan_metrics.get("closing_cta_actionable"),
                    "failed_checks": evaluation["failed_checks"],
                    "hookText": item["output"].get("hookText"),
                    "ctaText": item["output"].get("ctaText"),
                    "error": item.get("error"),
                }
            )
    return {"rows": rows}
