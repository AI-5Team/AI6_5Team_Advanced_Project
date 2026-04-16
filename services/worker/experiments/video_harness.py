from __future__ import annotations

import json
from dataclasses import asdict, dataclass
from pathlib import Path

from PIL import Image, ImageColor, ImageDraw, ImageEnhance, ImageFilter, ImageOps

from services.worker.renderers.media import CANVAS_SIZE, create_scene_image, render_video
from services.worker.utils.runtime import ensure_dir, load_font


ROOT_DIR = Path(__file__).resolve().parents[3]
DEFAULT_ARTIFACT_ROOT = ROOT_DIR / "docs" / "experiments" / "artifacts"


@dataclass(frozen=True)
class VideoScenario:
    scenario_id: str
    style_id: str
    template_id: str
    asset_paths: tuple[Path, ...]
    scene_specs: tuple[dict, ...]


@dataclass(frozen=True)
class VideoVariant:
    variant_id: str
    lever_id: str
    description: str
    overlay_mode: str
    headline_font_size: int
    badge_count: int
    accent_block_count: int
    stroke_enabled: bool
    rotated_elements: int
    opening_focus: str = "default"
    scene_text_overrides: dict[str, dict[str, str]] | None = None


@dataclass(frozen=True)
class VideoExperimentDefinition:
    experiment_id: str
    title: str
    objective: str
    scenario: VideoScenario
    baseline_variant: VideoVariant
    candidate_variants: tuple[VideoVariant, ...]


def get_video_experiment_definition(experiment_id: str = "EXP-03") -> VideoExperimentDefinition:
    exp03_scenario = VideoScenario(
        scenario_id="scenario-cafe-promotion-b-grade-fixed-copy",
        style_id="b_grade_fun",
        template_id="T02",
        asset_paths=(
            ROOT_DIR / "samples" / "input" / "cafe" / "cafe-latte-01.png",
            ROOT_DIR / "samples" / "input" / "cafe" / "cafe-dessert-02.png",
        ),
        scene_specs=(
            {
                "scene_id": "s1",
                "duration_sec": 1.3,
                "primary_text": "오늘만 텐션 폭발",
                "secondary_text": "성수동 한정 / 혜택 경보",
                "badge_text": "HOOK",
                "asset_index": 0,
            },
            {
                "scene_id": "s2",
                "duration_sec": 1.7,
                "primary_text": "딸기라떼 1+1",
                "secondary_text": "친구랑 오면 더 이득",
                "badge_text": "혜택",
                "asset_index": 1,
            },
            {
                "scene_id": "s3",
                "duration_sec": 1.8,
                "primary_text": "지금 안 오면 손해",
                "secondary_text": "오후 2시-5시까지만",
                "badge_text": "긴급",
                "asset_index": 0,
            },
            {
                "scene_id": "s4",
                "duration_sec": 1.6,
                "primary_text": "성수동으로 바로 뛰어오세요",
                "secondary_text": "스크롤 멈추고 매장 체크",
                "badge_text": "CTA",
                "asset_index": 1,
            },
        ),
    )
    exp03_baseline = VideoVariant(
        variant_id="baseline_card_overlay",
        lever_id="overlay_layout",
        description="현재 production renderer가 사용하는 카드형 오버레이 baseline입니다.",
        overlay_mode="card_panel",
        headline_font_size=58,
        badge_count=1,
        accent_block_count=2,
        stroke_enabled=False,
        rotated_elements=0,
    )
    flyer = VideoVariant(
        variant_id="bgrade_flyer_overlay",
        lever_id="overlay_layout",
        description="형광 전단지 느낌의 B급 오버레이 variant입니다.",
        overlay_mode="flyer_poster",
        headline_font_size=84,
        badge_count=3,
        accent_block_count=6,
        stroke_enabled=True,
        rotated_elements=2,
    )
    if experiment_id == "EXP-03":
        return VideoExperimentDefinition(
            experiment_id="EXP-03",
            title="B-grade Video Layout Experiment",
            objective="같은 B급 카피와 같은 자산 조건에서 카드형 오버레이보다 전단지형 B급 오버레이가 더 강한 화면 인상을 만드는지 확인합니다.",
            scenario=exp03_scenario,
            baseline_variant=exp03_baseline,
            candidate_variants=(flyer,),
        )

    if experiment_id == "EXP-04":
        exp04_scenario = VideoScenario(
            scenario_id="scenario-cafe-promotion-owner-made-reference",
            style_id="b_grade_fun",
            template_id="T02",
            asset_paths=exp03_scenario.asset_paths,
            scene_specs=(
                {
                    "scene_id": "s1",
                    "duration_sec": 1.3,
                    "primary_text": "오늘만!! 딸기라떼",
                    "secondary_text": "4,500원 / 성수동 한정",
                    "badge_text": "HOOK",
                    "asset_index": 0,
                },
                {
                    "scene_id": "s2",
                    "duration_sec": 1.7,
                    "primary_text": "실화?? 1+1",
                    "secondary_text": "친구랑 오면 더 이득",
                    "badge_text": "혜택",
                    "asset_index": 1,
                },
                {
                    "scene_id": "s3",
                    "duration_sec": 1.8,
                    "primary_text": "지금 안 오면 손해",
                    "secondary_text": "오후 2시-5시 긴급 할인",
                    "badge_text": "긴급",
                    "asset_index": 0,
                },
                {
                    "scene_id": "s4",
                    "duration_sec": 1.6,
                    "primary_text": "사장님이 직접 부름",
                    "secondary_text": "성수동 카페 오세요~~",
                    "badge_text": "CTA",
                    "asset_index": 1,
                },
            ),
        )
        owner_made = VideoVariant(
            variant_id="owner_made_safe_zone",
            lever_id="product_visibility_protection",
            description="docs/sample의 Style A 레퍼런스를 참고한, 상품 보호형 사장님 제작 느낌 variant입니다.",
            overlay_mode="owner_made_safe",
            headline_font_size=76,
            badge_count=2,
            accent_block_count=4,
            stroke_enabled=True,
            rotated_elements=1,
        )
        return VideoExperimentDefinition(
            experiment_id="EXP-04",
            title="Owner-made Safe-zone Layout Experiment",
            objective="B급 감성은 유지하면서 상품 가시성을 더 살릴 수 있는지, owner-made reference 레이아웃을 비교합니다.",
            scenario=exp04_scenario,
            baseline_variant=flyer,
            candidate_variants=(owner_made,),
        )

    if experiment_id == "EXP-05":
        exp05_scenario = VideoScenario(
            scenario_id="scenario-restaurant-promotion-handdrawn-real-photos",
            style_id="b_grade_fun",
            template_id="T02",
            asset_paths=(
                ROOT_DIR / "docs" / "sample" / "음식사진샘플(타코야키).jpg",
                ROOT_DIR / "docs" / "sample" / "음식사진샘플(맥주).jpg",
            ),
            scene_specs=(
                {
                    "scene_id": "s1",
                    "duration_sec": 1.3,
                    "primary_text": "오늘만!! 타코야키",
                    "secondary_text": "맥주랑 같이 가면 미쳤다",
                    "badge_text": "HOOK",
                    "asset_index": 0,
                },
                {
                    "scene_id": "s2",
                    "duration_sec": 1.7,
                    "primary_text": "타코야키+맥주 각이다",
                    "secondary_text": "퇴근길 1차 바로 가능",
                    "badge_text": "조합",
                    "asset_index": 1,
                },
                {
                    "scene_id": "s3",
                    "duration_sec": 1.8,
                    "primary_text": "지금 안 먹으면 손해",
                    "secondary_text": "겉바속촉 / 시원한 한잔",
                    "badge_text": "긴급",
                    "asset_index": 0,
                },
                {
                    "scene_id": "s4",
                    "duration_sec": 1.6,
                    "primary_text": "타코야키 먹으러 바로 오세요",
                    "secondary_text": "성수동 말고 어디 감?",
                    "badge_text": "CTA",
                    "asset_index": 1,
                },
            ),
        )
        hand_drawn = VideoVariant(
            variant_id="hand_drawn_menu_board",
            lever_id="visual_style_reference",
            description="docs/sample/손그림샘플.png를 참고한 손그림 메뉴판형 variant입니다.",
            overlay_mode="hand_drawn_menu",
            headline_font_size=66,
            badge_count=4,
            accent_block_count=5,
            stroke_enabled=True,
            rotated_elements=3,
        )
        owner_made_real = VideoVariant(
            variant_id="owner_made_real_photo",
            lever_id="visual_style_reference",
            description="실제 음식 사진 기반 owner-made baseline입니다.",
            overlay_mode="owner_made_safe",
            headline_font_size=76,
            badge_count=2,
            accent_block_count=4,
            stroke_enabled=True,
            rotated_elements=1,
        )
        return VideoExperimentDefinition(
            experiment_id="EXP-05",
            title="Hand-drawn Reference With Real Food Photos",
            objective="실제 음식 사진에 손그림 메뉴판 스타일을 입혔을 때 owner-made baseline보다 더 잘 맞는지 확인합니다.",
            scenario=exp05_scenario,
            baseline_variant=owner_made_real,
            candidate_variants=(hand_drawn,),
        )

    if experiment_id == "EXP-06":
        exp06_scenario = VideoScenario(
            scenario_id="scenario-restaurant-promotion-service-aligned-opening-priority",
            style_id="b_grade_fun",
            template_id="T02",
            asset_paths=(
                ROOT_DIR / "docs" / "sample" / "음식사진샘플(규카츠).jpg",
                ROOT_DIR / "docs" / "sample" / "음식사진샘플(맥주).jpg",
            ),
            scene_specs=(
                {
                    "scene_id": "s1",
                    "duration_sec": 1.4,
                    "primary_text": "오늘만 2천원↓",
                    "secondary_text": "규카츠 세트 특가",
                    "badge_text": "혜택",
                    "asset_index": 0,
                },
                {
                    "scene_id": "s2",
                    "duration_sec": 1.6,
                    "primary_text": "겉바속촉 규카츠",
                    "secondary_text": "맥주 한잔까지 같이 각",
                    "badge_text": "메뉴",
                    "asset_index": 0,
                },
                {
                    "scene_id": "s3",
                    "duration_sec": 1.6,
                    "primary_text": "오늘 저녁까지만",
                    "secondary_text": "퇴근길 방문 타이밍 잡기 좋음",
                    "badge_text": "긴급",
                    "asset_index": 1,
                },
                {
                    "scene_id": "s4",
                    "duration_sec": 1.6,
                    "primary_text": "지금 바로 저장 말고 방문",
                    "secondary_text": "인스타 업로드용 CTA도 바로 가능",
                    "badge_text": "CTA",
                    "asset_index": 1,
                },
            ),
        )
        benefit_first = VideoVariant(
            variant_id="owner_made_benefit_first",
            lever_id="opening_scene_priority",
            description="프로모션 목적에 맞춰 첫 씬을 혜택 우선으로 여는 service-aligned baseline입니다.",
            overlay_mode="owner_made_safe",
            headline_font_size=76,
            badge_count=2,
            accent_block_count=4,
            stroke_enabled=True,
            rotated_elements=1,
            opening_focus="benefit_first",
        )
        menu_first = VideoVariant(
            variant_id="owner_made_menu_first",
            lever_id="opening_scene_priority",
            description="같은 구성에서 첫 씬만 메뉴 우선으로 바꾼 variant입니다.",
            overlay_mode="owner_made_safe",
            headline_font_size=76,
            badge_count=2,
            accent_block_count=4,
            stroke_enabled=True,
            rotated_elements=1,
            opening_focus="menu_first",
            scene_text_overrides={
                "s1": {
                    "primary_text": "겉바 규카츠",
                    "secondary_text": "오늘만 2천원↓ / 세트 특가",
                    "badge_text": "메뉴",
                }
            },
        )
        return VideoExperimentDefinition(
            experiment_id="EXP-06",
            title="Service-aligned B-grade Promotion Opening Priority",
            objective="Phase 1 핵심 서비스 루프 기준에서 promotion 템플릿의 첫 씬을 혜택 우선으로 열지, 메뉴 우선으로 열지 비교합니다.",
            scenario=exp06_scenario,
            baseline_variant=benefit_first,
            candidate_variants=(menu_first,),
        )

    if experiment_id == "EXP-07":
        exp07_scenario = VideoScenario(
            scenario_id="scenario-restaurant-promotion-visual-baseline-rebuild",
            style_id="b_grade_fun",
            template_id="T02",
            asset_paths=(
                ROOT_DIR / "docs" / "sample" / "음식사진샘플(규카츠).jpg",
                ROOT_DIR / "docs" / "sample" / "음식사진샘플(맥주).jpg",
            ),
            scene_specs=(
                {
                    "scene_id": "s1",
                    "duration_sec": 1.4,
                    "primary_text": "오늘만 2천원↓",
                    "secondary_text": "규카츠 세트 특가",
                    "badge_text": "혜택",
                    "asset_index": 0,
                },
                {
                    "scene_id": "s2",
                    "duration_sec": 1.6,
                    "primary_text": "겉바속촉 규카츠",
                    "secondary_text": "맥주 한잔까지 같이 각",
                    "badge_text": "메뉴",
                    "asset_index": 0,
                },
                {
                    "scene_id": "s3",
                    "duration_sec": 1.6,
                    "primary_text": "오늘 저녁까지만",
                    "secondary_text": "퇴근길 방문 타이밍 잡기 좋음",
                    "badge_text": "긴급",
                    "asset_index": 1,
                },
                {
                    "scene_id": "s4",
                    "duration_sec": 1.6,
                    "primary_text": "지금 바로 저장 말고 방문",
                    "secondary_text": "인스타 업로드용 CTA도 바로 가능",
                    "badge_text": "CTA",
                    "asset_index": 1,
                },
            ),
        )
        legacy = VideoVariant(
            variant_id="legacy_owner_made_safe",
            lever_id="baseline_rebuild",
            description="기존 fixed-position owner-made renderer baseline입니다.",
            overlay_mode="owner_made_safe",
            headline_font_size=76,
            badge_count=2,
            accent_block_count=4,
            stroke_enabled=True,
            rotated_elements=1,
            opening_focus="benefit_first",
        )
        rebuilt = VideoVariant(
            variant_id="structured_bgrade_v2",
            lever_id="baseline_rebuild",
            description="text fit, safe zone, footer CTA를 다시 설계한 rebuilt baseline입니다.",
            overlay_mode="structured_bgrade_v2",
            headline_font_size=64,
            badge_count=3,
            accent_block_count=5,
            stroke_enabled=True,
            rotated_elements=0,
            opening_focus="benefit_first",
        )
        return VideoExperimentDefinition(
            experiment_id="EXP-07",
            title="Visual Baseline Rebuild Before OVAT",
            objective="OVAT 재개 전에 텍스트 overflow와 겹침을 줄이는 새로운 baseline renderer를 검증합니다.",
            scenario=exp07_scenario,
            baseline_variant=legacy,
            candidate_variants=(rebuilt,),
        )

    if experiment_id == "EXP-08":
        exp08_scenario = VideoScenario(
            scenario_id="scenario-multi-photo-validation-structured-bgrade-v2",
            style_id="b_grade_fun",
            template_id="T02",
            asset_paths=(
                ROOT_DIR / "docs" / "sample" / "음식사진샘플(규카츠).jpg",
                ROOT_DIR / "docs" / "sample" / "음식사진샘플(라멘).jpg",
                ROOT_DIR / "docs" / "sample" / "음식사진샘플(순두부짬뽕).jpg",
                ROOT_DIR / "docs" / "sample" / "음식사진샘플(장어덮밥).jpg",
                ROOT_DIR / "docs" / "sample" / "음식사진샘플(타코야키).jpg",
            ),
            scene_specs=(
                {"scene_id": "s1", "duration_sec": 1.2, "primary_text": "오늘만 2천원↓", "secondary_text": "규카츠 세트 특가", "badge_text": "혜택", "asset_index": 0},
                {"scene_id": "s2", "duration_sec": 1.2, "primary_text": "면추가 무료", "secondary_text": "라멘 점심 특가", "badge_text": "혜택", "asset_index": 1},
                {"scene_id": "s3", "duration_sec": 1.2, "primary_text": "맵칼한 점심딜", "secondary_text": "순두부짬뽕 바로", "badge_text": "혜택", "asset_index": 2},
                {"scene_id": "s4", "duration_sec": 1.2, "primary_text": "보양식 오늘 할인", "secondary_text": "장어덮밥 특선", "badge_text": "혜택", "asset_index": 3},
                {"scene_id": "s5", "duration_sec": 1.2, "primary_text": "타코야키 세트딜", "secondary_text": "맥주 조합 바로", "badge_text": "혜택", "asset_index": 4},
            ),
        )
        rebuilt = VideoVariant(
            variant_id="structured_bgrade_v2_multi_photo",
            lever_id="multi_photo_validation",
            description="structured_bgrade_v2를 실제 음식 사진 5세트에 적용해 baseline 안정성을 확인합니다.",
            overlay_mode="structured_bgrade_v2",
            headline_font_size=64,
            badge_count=3,
            accent_block_count=5,
            stroke_enabled=True,
            rotated_elements=0,
            opening_focus="benefit_first",
        )
        return VideoExperimentDefinition(
            experiment_id="EXP-08",
            title="Structured B-grade V2 Multi-photo Validation",
            objective="새 baseline이 실제 음식 사진 다건에서도 overflow와 겹침 없이 유지되는지 확인합니다.",
            scenario=exp08_scenario,
            baseline_variant=rebuilt,
            candidate_variants=(),
        )

    raise ValueError(f"unsupported video experiment id: {experiment_id}")


def run_video_experiment(
    experiment: VideoExperimentDefinition,
    artifact_root: Path = DEFAULT_ARTIFACT_ROOT,
) -> dict:
    scenario_root = artifact_root / slugify(f"{experiment.experiment_id}-{experiment.title}")
    ensure_dir(scenario_root)

    results = []
    for variant in (experiment.baseline_variant, *experiment.candidate_variants):
        variant_root = scenario_root / variant.variant_id
        scenes_root = variant_root / "scenes"
        ensure_dir(scenes_root)

        rendered_scenes: list[tuple[Path, float]] = []
        first_scene_path: str | None = None
        rendered_scene_specs: list[dict] = []
        for scene in experiment.scenario.scene_specs:
            resolved_scene = resolve_scene_spec(scene, variant)
            output_path = scenes_root / f"{resolved_scene['scene_id']}.png"
            asset_path = experiment.scenario.asset_paths[resolved_scene["asset_index"]]
            render_scene_variant(
                variant=variant,
                output_path=output_path,
                asset_path=asset_path,
                primary_text=resolved_scene["primary_text"],
                secondary_text=resolved_scene["secondary_text"],
                badge_text=resolved_scene["badge_text"],
            )
            rendered_scenes.append((output_path, float(resolved_scene["duration_sec"])))
            rendered_scene_specs.append(resolved_scene)
            if first_scene_path is None:
                first_scene_path = str(output_path)

        video_path = variant_root / "preview.mp4"
        render_video(rendered_scenes, video_path)

        results.append(
            {
                "variant": asdict(variant),
                "video_path": str(video_path),
                "first_scene_path": first_scene_path,
                "rendered_scene_specs": rendered_scene_specs,
                "evaluation": evaluate_video_variant(variant, rendered_scene_specs),
            }
        )

    artifact = {
        "experiment_id": experiment.experiment_id,
        "title": experiment.title,
        "objective": experiment.objective,
        "scenario": {
            "scenario_id": experiment.scenario.scenario_id,
            "style_id": experiment.scenario.style_id,
            "template_id": experiment.scenario.template_id,
            "asset_paths": [str(path) for path in experiment.scenario.asset_paths],
            "scene_specs": list(experiment.scenario.scene_specs),
        },
        "results": results,
    }
    artifact_path = scenario_root / "summary.json"
    artifact_path.write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")
    artifact["artifact_path"] = str(artifact_path)
    return artifact


def resolve_scene_spec(scene: dict, variant: VideoVariant) -> dict:
    resolved = dict(scene)
    if not variant.scene_text_overrides:
        return resolved
    scene_override = variant.scene_text_overrides.get(scene["scene_id"])
    if scene_override:
        resolved.update(scene_override)
    return resolved


def render_scene_variant(
    variant: VideoVariant,
    output_path: Path,
    asset_path: Path,
    primary_text: str,
    secondary_text: str,
    badge_text: str,
) -> None:
    if variant.overlay_mode == "card_panel":
        create_scene_image(
            output_path,
            asset_path,
            primary_text,
            secondary_text,
            "b_grade_fun",
            badge_text=badge_text,
        )
        return
    if variant.overlay_mode == "flyer_poster":
        create_flyer_scene_image(output_path, asset_path, primary_text, secondary_text, badge_text)
        return
    if variant.overlay_mode == "owner_made_safe":
        create_owner_made_scene_image(output_path, asset_path, primary_text, secondary_text)
        return
    if variant.overlay_mode == "structured_bgrade_v2":
        create_structured_bgrade_scene_image(output_path, asset_path, primary_text, secondary_text, badge_text)
        return
    if variant.overlay_mode == "hand_drawn_menu":
        create_hand_drawn_menu_scene_image(output_path, asset_path, primary_text, secondary_text)
        return
    raise ValueError(f"unsupported overlay mode: {variant.overlay_mode}")


def create_flyer_scene_image(
    output_path: Path,
    asset_path: Path,
    primary_text: str,
    secondary_text: str,
    badge_text: str,
) -> None:
    ensure_dir(output_path.parent)
    base = Image.open(asset_path).convert("RGB").resize(CANVAS_SIZE, Image.Resampling.LANCZOS)
    base = ImageEnhance.Contrast(base).enhance(1.2)
    base = ImageEnhance.Color(base).enhance(1.25)
    canvas = base.convert("RGBA")
    overlay = Image.new("RGBA", CANVAS_SIZE, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)

    yellow = ImageColor.getrgb("#FFF200")
    hot_pink = ImageColor.getrgb("#FF4FB3")
    cyan = ImageColor.getrgb("#67F5FF")
    black = (18, 18, 18)
    white = (255, 255, 255)

    draw.rectangle((0, 0, CANVAS_SIZE[0], CANVAS_SIZE[1]), fill=(0, 0, 0, 36))
    draw.rectangle((24, 34, CANVAS_SIZE[0] - 24, 188), fill=yellow + (255,), outline=black, width=8)
    draw.rectangle((38, 1020, CANVAS_SIZE[0] - 38, 1234), fill=black + (228,), outline=yellow, width=8)
    draw.rectangle((0, 922, CANVAS_SIZE[0], 980), fill=hot_pink + (238,))
    draw.rectangle((0, 980, CANVAS_SIZE[0], 1018), fill=cyan + (225,))

    sticker = Image.new("RGBA", (214, 88), (0, 0, 0, 0))
    sticker_draw = ImageDraw.Draw(sticker)
    sticker_draw.rounded_rectangle((0, 0, 214, 88), radius=18, fill=hot_pink + (255,), outline=black, width=6)
    sticker_draw.text((24, 24), "B급 특가", font=load_font(28, bold=True), fill=black)
    sticker = sticker.rotate(-8, expand=True)
    overlay.alpha_composite(sticker, dest=(34, 214))

    badge = Image.new("RGBA", (180, 78), (0, 0, 0, 0))
    badge_draw = ImageDraw.Draw(badge)
    badge_draw.rounded_rectangle((0, 0, 180, 78), radius=16, fill=yellow + (255,), outline=black, width=5)
    badge_draw.text((28, 20), badge_text, font=load_font(26, bold=True), fill=black)
    badge = badge.rotate(7, expand=True)
    overlay.alpha_composite(badge, dest=(498, 210))

    burst = Image.new("RGBA", (164, 164), (0, 0, 0, 0))
    burst_draw = ImageDraw.Draw(burst)
    burst_draw.regular_polygon((82, 82, 66), n_sides=10, rotation=18, fill=cyan + (255,), outline=black, width=5)
    burst_draw.text((42, 60), "한정", font=load_font(24, bold=True), fill=black)
    overlay.alpha_composite(burst, dest=(550, 90))

    headline_font = load_font(84, bold=True)
    sub_font = load_font(38, bold=True)
    footer_font = load_font(28, bold=True)

    headline_box = (56, 286, CANVAS_SIZE[0] - 56, 888)
    draw.multiline_text(
        (headline_box[0], headline_box[1]),
        balance_text(primary_text, 9),
        font=headline_font,
        fill=yellow,
        stroke_width=8,
        stroke_fill=black,
        spacing=8,
    )
    draw.multiline_text(
        (headline_box[0] + 8, headline_box[1] + 8),
        balance_text(primary_text, 9),
        font=headline_font,
        fill=hot_pink,
        stroke_width=0,
        spacing=8,
    )
    draw.multiline_text(
        (66, 1048),
        balance_text(secondary_text, 14),
        font=sub_font,
        fill=white,
        stroke_width=2,
        stroke_fill=black,
        spacing=4,
    )
    draw.text((70, 932), "지금 멈추면 손해", font=load_font(28, bold=True), fill=black)
    draw.text((440, 942), "형광 경고 자막", font=load_font(24, bold=True), fill=black)
    draw.text((62, 1190), "성수동 / 오늘만 / 저장 말고 바로 방문", font=footer_font, fill=yellow)

    merged = Image.alpha_composite(canvas, overlay)
    merged.convert("RGB").save(output_path)


def create_owner_made_scene_image(
    output_path: Path,
    asset_path: Path,
    primary_text: str,
    secondary_text: str,
) -> None:
    ensure_dir(output_path.parent)
    base = Image.open(asset_path).convert("RGB").resize(CANVAS_SIZE, Image.Resampling.LANCZOS)
    base = ImageEnhance.Contrast(base).enhance(1.1)
    canvas = Image.new("RGBA", CANVAS_SIZE, (250, 248, 240, 255))
    draw = ImageDraw.Draw(canvas)

    white_card = Image.new("RGBA", (520, 720), (255, 255, 255, 255))
    card_draw = ImageDraw.Draw(white_card)
    card_draw.rounded_rectangle((0, 0, 520, 720), radius=28, fill=(255, 255, 255, 255))
    image_crop = base.resize((470, 640), Image.Resampling.LANCZOS)
    white_card.alpha_composite(image_crop.convert("RGBA"), dest=(24, 34))
    white_card = white_card.rotate(-6, expand=True)
    canvas.alpha_composite(white_card, dest=(34, 74))

    yellow = ImageColor.getrgb("#E6FF19")
    black = (14, 14, 14)
    red = ImageColor.getrgb("#FF2C20")

    text = balance_text(primary_text, 7)
    draw.multiline_text(
        (420, 120),
        text,
        font=load_font(76, bold=True),
        fill=yellow,
        stroke_width=6,
        stroke_fill=black,
        spacing=2,
    )
    draw.multiline_text(
        (424, 124),
        text,
        font=load_font(76, bold=True),
        fill=yellow,
        stroke_width=0,
        spacing=2,
    )

    price_label = secondary_text.split("/")[0].strip()
    draw.text(
        (460, 432),
        price_label,
        font=load_font(70, bold=True),
        fill=yellow,
        stroke_width=6,
        stroke_fill=black,
    )
    draw.ellipse((420, 410, 712, 568), outline=red, width=8)
    draw.ellipse((432, 422, 700, 556), outline=red, width=6)
    draw.arc((408, 396, 720, 576), start=15, end=336, fill=red, width=7)

    footer_note = "사장님이 직접 쓴 느낌"
    footer_cta = "저장 말고 바로 방문"
    draw.text((256, 1056), footer_note, font=load_font(28, bold=True), fill=black)
    draw.text((292, 1102), footer_cta, font=load_font(28, bold=True), fill=black)
    draw.line((612, 1058, 664, 1012), fill=black, width=4)
    draw.line((664, 1012, 684, 1030), fill=black, width=4)
    draw.line((664, 1012, 648, 994), fill=black, width=4)

    canvas.convert("RGB").save(output_path)


def create_structured_bgrade_scene_image(
    output_path: Path,
    asset_path: Path,
    primary_text: str,
    secondary_text: str,
    badge_text: str,
) -> None:
    ensure_dir(output_path.parent)
    base = Image.open(asset_path).convert("RGB")
    background = ImageOps.fit(base, CANVAS_SIZE, method=Image.Resampling.LANCZOS)
    background = background.filter(ImageFilter.GaussianBlur(radius=8))
    background = ImageEnhance.Color(background).enhance(0.72)
    background = ImageEnhance.Contrast(background).enhance(0.86)
    background = ImageEnhance.Brightness(background).enhance(0.72)

    canvas = background.convert("RGBA")
    paper = Image.new("RGBA", CANVAS_SIZE, (246, 239, 228, 214))
    canvas = Image.alpha_composite(canvas, paper)
    draw = ImageDraw.Draw(canvas)

    yellow = ImageColor.getrgb("#E9FF25")
    black = ImageColor.getrgb("#121212")
    red = ImageColor.getrgb("#FF3B30")
    white = ImageColor.getrgb("#FFFDF8")
    purple = ImageColor.getrgb("#2A1147")
    beige = ImageColor.getrgb("#FFF4DE")

    photo_card_box = (34, 76, 350, 958)
    panel_box = (374, 86, 680, 940)
    footer_box = (44, 1022, 676, 1212)
    footer_cta_box = (76, 1116, 644, 1184)
    badge_box = (396, 110, 574, 168)
    headline_box = (396, 198, 658, 500)
    secondary_box = (396, 552, 658, 712)
    note_box = (396, 762, 658, 852)

    draw_shadowed_card(draw, (photo_card_box[0] + 10, photo_card_box[1] + 16, photo_card_box[2] + 10, photo_card_box[3] + 16), radius=30, fill=(0, 0, 0, 55))
    draw.rounded_rectangle(photo_card_box, radius=30, fill=white, outline=black, width=4)

    photo = ImageOps.fit(
        base,
        (photo_card_box[2] - photo_card_box[0] - 28, photo_card_box[3] - photo_card_box[1] - 28),
        method=Image.Resampling.LANCZOS,
    )
    canvas.alpha_composite(photo.convert("RGBA"), dest=(photo_card_box[0] + 14, photo_card_box[1] + 14))

    draw.rounded_rectangle(panel_box, radius=28, fill=purple + (246,), outline=black, width=4)
    draw.rounded_rectangle(footer_box, radius=32, fill=beige + (250,), outline=black, width=4)
    draw.rounded_rectangle(footer_cta_box, radius=26, fill=black + (255,), outline=yellow, width=3)
    draw.rounded_rectangle(badge_box, radius=18, fill=yellow + (255,), outline=black, width=3)

    badge_block = fit_text_block(draw, badge_text, badge_box, max_font_size=28, min_font_size=20, bold=True, max_lines=1, prefer_fewer_lines=False)
    draw_block(draw, badge_block, fill=black)

    headline_block = fit_text_block(draw, primary_text, headline_box, max_font_size=62, min_font_size=32, bold=True, max_lines=3)
    draw_block(draw, headline_block, fill=yellow, stroke_fill=black, stroke_width=5, shadow_offset=(4, 4), shadow_fill=black)

    draw.rounded_rectangle(secondary_box, radius=26, fill=white + (255,), outline=black, width=3)
    secondary_block = fit_text_block(draw, secondary_text, inset_box(secondary_box, 18), max_font_size=44, min_font_size=22, bold=True, max_lines=3)
    draw_block(draw, secondary_block, fill=black)
    draw_scribble_oval(draw, expand_box(secondary_box, 8, 10), red, width=4)

    note_block = fit_text_block(draw, "사장님 손글씨", note_box, max_font_size=28, min_font_size=18, bold=True, max_lines=2, prefer_fewer_lines=False)
    draw_block(draw, note_block, fill=white)

    cta_block = fit_text_block(draw, "저장 말고 바로 방문", footer_cta_box, max_font_size=38, min_font_size=24, bold=True, max_lines=1, prefer_fewer_lines=False)
    draw_block(draw, cta_block, fill=yellow)

    sub_note_block = fit_text_block(draw, "인스타 업로드용 결과물 기준", (78, 1052, 642, 1100), max_font_size=24, min_font_size=16, bold=True, max_lines=1, prefer_fewer_lines=False)
    draw_block(draw, sub_note_block, fill=black)

    # Light B-grade accent without touching the product zone.
    draw.text((84, 88), "오늘만", font=load_font(22, bold=True), fill=red)
    draw.line((610, 980, 654, 952), fill=black, width=4)
    draw.line((654, 952, 676, 972), fill=black, width=4)
    draw.line((654, 952, 650, 920), fill=black, width=4)

    canvas.convert("RGB").save(output_path)


def create_hand_drawn_menu_scene_image(
    output_path: Path,
    asset_path: Path,
    primary_text: str,
    secondary_text: str,
) -> None:
    ensure_dir(output_path.parent)
    cream = ImageColor.getrgb("#F7EECF")
    brown = ImageColor.getrgb("#8A4E2A")
    orange = ImageColor.getrgb("#E98A2C")
    navy = ImageColor.getrgb("#24305E")
    red = ImageColor.getrgb("#CC3A2A")
    teal = ImageColor.getrgb("#5A908A")

    canvas = Image.new("RGBA", CANVAS_SIZE, cream + (255,))
    draw = ImageDraw.Draw(canvas)
    photo = Image.open(asset_path).convert("RGB").resize((248, 248), Image.Resampling.LANCZOS)

    # Hand-drawn border
    for offset in range(0, 16, 4):
        draw.rounded_rectangle(
            (18 + offset, 18 + offset, CANVAS_SIZE[0] - 18 - offset, CANVAS_SIZE[1] - 18 - offset),
            radius=20,
            outline=brown,
            width=3,
        )

    # Photo plate
    frame_center = (CANVAS_SIZE[0] // 2, 230)
    draw.ellipse((frame_center[0] - 150, frame_center[1] - 150, frame_center[0] + 150, frame_center[1] + 150), fill=(255, 255, 255), outline=navy, width=5)
    plate = Image.new("RGBA", (270, 270), (0, 0, 0, 0))
    plate_draw = ImageDraw.Draw(plate)
    plate_draw.ellipse((4, 4, 266, 266), fill=(255, 255, 255, 255), outline=navy, width=5)
    mask = Image.new("L", (270, 270), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((10, 10, 260, 260), fill=255)
    photo_masked = Image.new("RGBA", (270, 270), (0, 0, 0, 0))
    photo_masked.paste(photo.resize((250, 250), Image.Resampling.LANCZOS).convert("RGBA"), (10, 10), mask.crop((10, 10, 260, 260)))
    plate.alpha_composite(photo_masked)
    canvas.alpha_composite(plate, dest=(frame_center[0] - 135, frame_center[1] - 135))

    # Doodle stars
    draw.text((86, 104), "best!", font=load_font(30, bold=True), fill=teal)
    draw.text((112, 68), "★", font=load_font(26, bold=True), fill=orange)
    draw.text((136, 84), "★", font=load_font(20, bold=True), fill=red)
    draw.text((568, 366), "★", font=load_font(24, bold=True), fill=navy)
    draw.text((598, 394), "★", font=load_font(16, bold=True), fill=orange)

    # Headline label
    label = Image.new("RGBA", (360, 86), (0, 0, 0, 0))
    label_draw = ImageDraw.Draw(label)
    label_draw.rectangle((0, 0, 360, 86), fill=orange + (255,), outline=brown, width=5)
    label_draw.multiline_text((20, 14), balance_text(primary_text, 8), font=load_font(54, bold=True), fill=navy, spacing=0)
    label = label.rotate(-3, expand=True)
    canvas.alpha_composite(label, dest=(182, 412))

    # Price/info tag
    draw.rounded_rectangle((170, 560, 550, 650), radius=24, fill=(255, 247, 230, 255), outline=red, width=5)
    draw.multiline_text((194, 580), balance_text(secondary_text, 11), font=load_font(34, bold=True), fill=red, spacing=4)

    # Store sketch block
    draw.rectangle((204, 742, 516, 928), outline=teal, width=4)
    for x in range(204, 516, 22):
        draw.line((x, 742, x, 928), fill=(190, 190, 190), width=1)
    for y in range(742, 928, 22):
        draw.line((204, y, 516, y), fill=(190, 190, 190), width=1)
    draw.rectangle((290, 812, 432, 900), outline=brown, width=4)
    draw.text((328, 846), "가게", font=load_font(28, bold=True), fill=brown)
    draw.arc((528, 740, 640, 858), 210, 340, fill=navy, width=4)
    draw.arc((76, 770, 168, 856), 20, 160, fill=teal, width=4)

    # Footer menu notes
    draw.text((68, 1004), "타코야키", font=load_font(42, bold=True), fill=navy)
    draw.text((68, 1054), "맥주랑 같이 가면 딱", font=load_font(34, bold=True), fill=brown)
    draw.text((68, 1120), "손그림 메뉴판 감성 / 실사 음식 사진 혼합", font=load_font(26, bold=True), fill=red)

    canvas.convert("RGB").save(output_path)


def fit_text_block(
    draw: ImageDraw.ImageDraw,
    text: str,
    box: tuple[int, int, int, int],
    *,
    max_font_size: int,
    min_font_size: int,
    bold: bool,
    max_lines: int,
    spacing: int = 6,
    prefer_fewer_lines: bool = True,
) -> dict:
    max_width = box[2] - box[0]
    max_height = box[3] - box[1]
    best_candidate: dict | None = None
    best_line_count = 99
    best_font_size = -1
    for font_size in range(max_font_size, min_font_size - 1, -2):
        font = load_font(font_size, bold=bold)
        lines = wrap_text_by_pixels(draw, text, font, max_width)
        if len(lines) > max_lines:
            continue
        text_value = "\n".join(lines)
        bbox = draw.multiline_textbbox((0, 0), text_value, font=font, spacing=spacing, stroke_width=0)
        width = bbox[2] - bbox[0]
        height = bbox[3] - bbox[1]
        if width <= max_width and height <= max_height:
            x = box[0] + (max_width - width) // 2
            y = box[1] + (max_height - height) // 2
            candidate = {"text": text_value, "font": font, "position": (x, y), "spacing": spacing, "font_size": font_size}
            if not prefer_fewer_lines:
                return candidate
            line_count = len(lines)
            if line_count < best_line_count or (line_count == best_line_count and font_size > best_font_size):
                best_candidate = candidate
                best_line_count = line_count
                best_font_size = font_size

    if best_candidate is not None:
        return best_candidate

    font = load_font(min_font_size, bold=bold)
    lines = wrap_text_by_pixels(draw, text, font, max_width)
    if len(lines) > max_lines:
        lines = lines[: max_lines - 1] + [truncate_to_width(draw, lines[max_lines - 1], font, max_width)]
    text_value = "\n".join(lines)
    bbox = draw.multiline_textbbox((0, 0), text_value, font=font, spacing=spacing, stroke_width=0)
    width = bbox[2] - bbox[0]
    height = bbox[3] - bbox[1]
    x = box[0] + max((max_width - width) // 2, 0)
    y = box[1] + max((max_height - height) // 2, 0)
    return {"text": text_value, "font": font, "position": (x, y), "spacing": spacing, "font_size": min_font_size}


def wrap_text_by_pixels(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    raw_lines = text.splitlines() or [text]
    wrapped_lines: list[str] = []
    for raw_line in raw_lines:
        wrapped_lines.extend(wrap_single_line_by_words(draw, raw_line, font, max_width))
    return wrapped_lines or [text]


def wrap_single_line_by_words(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    words = [word for word in text.split(" ") if word]
    if not words:
        return [text]

    lines: list[str] = []
    current = ""
    for word in words:
        word_segments = split_word_to_width(draw, word, font, max_width)
        for index, segment in enumerate(word_segments):
            spacer = "" if index > 0 or not current else " "
            candidate = f"{current}{spacer}{segment}" if current else segment
            bbox = draw.textbbox((0, 0), candidate, font=font)
            width = bbox[2] - bbox[0]
            if width <= max_width or not current:
                current = candidate
            else:
                lines.append(current.rstrip())
                current = segment
    if current.strip():
        lines.append(current.rstrip())
    return lines or [text]


def split_word_to_width(draw: ImageDraw.ImageDraw, word: str, font, max_width: int) -> list[str]:
    bbox = draw.textbbox((0, 0), word, font=font)
    width = bbox[2] - bbox[0]
    if width <= max_width:
        return [word]

    pieces: list[str] = []
    current = ""
    for char in word:
        candidate = f"{current}{char}"
        bbox = draw.textbbox((0, 0), candidate, font=font)
        width = bbox[2] - bbox[0]
        if width <= max_width or not current:
            current = candidate
        else:
            pieces.append(current)
            current = char
    if current:
        pieces.append(current)
    return pieces or [word]


def truncate_to_width(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> str:
    candidate = text.rstrip()
    while candidate:
        bbox = draw.textbbox((0, 0), f"{candidate}…", font=font)
        if bbox[2] - bbox[0] <= max_width:
            return f"{candidate}…"
        candidate = candidate[:-1]
    return "…"


def draw_block(
    draw: ImageDraw.ImageDraw,
    block: dict,
    *,
    fill: tuple[int, int, int],
    stroke_fill: tuple[int, int, int] | None = None,
    stroke_width: int = 0,
    shadow_offset: tuple[int, int] | None = None,
    shadow_fill: tuple[int, int, int] | None = None,
) -> None:
    x, y = block["position"]
    if shadow_offset and shadow_fill:
        draw.multiline_text(
            (x + shadow_offset[0], y + shadow_offset[1]),
            block["text"],
            font=block["font"],
            fill=shadow_fill,
            spacing=block["spacing"],
        )
    draw.multiline_text(
        (x, y),
        block["text"],
        font=block["font"],
        fill=fill,
        spacing=block["spacing"],
        stroke_width=stroke_width,
        stroke_fill=stroke_fill,
        align="center",
    )


def draw_shadowed_card(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], *, radius: int, fill: tuple[int, int, int, int]) -> None:
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def draw_scribble_oval(draw: ImageDraw.ImageDraw, box: tuple[int, int, int, int], color: tuple[int, int, int], *, width: int) -> None:
    draw.ellipse(box, outline=color, width=width)
    draw.ellipse((box[0] + 10, box[1] + 6, box[2] - 6, box[3] - 8), outline=color, width=max(2, width - 1))
    draw.arc((box[0] - 8, box[1] + 4, box[2] + 6, box[3] - 2), start=12, end=334, fill=color, width=max(2, width - 1))


def inset_box(box: tuple[int, int, int, int], padding: int) -> tuple[int, int, int, int]:
    return (box[0] + padding, box[1] + padding, box[2] - padding, box[3] - padding)


def expand_box(box: tuple[int, int, int, int], x_padding: int, y_padding: int) -> tuple[int, int, int, int]:
    return (box[0] - x_padding, box[1] - y_padding, box[2] + x_padding, box[3] + y_padding)


def balance_text(text: str, max_chars: int) -> str:
    words = text.split()
    if len(words) == 1 and len(text) > max_chars:
        return "\n".join(text[i : i + max_chars] for i in range(0, len(text), max_chars))
    lines: list[str] = []
    current = ""
    for word in words:
        candidate = word if not current else f"{current} {word}"
        if len(candidate) <= max_chars or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return "\n".join(lines)


def evaluate_video_variant(variant: VideoVariant, rendered_scene_specs: list[dict]) -> dict:
    first_scene = rendered_scene_specs[0]
    last_scene = rendered_scene_specs[-1]
    first_primary = str(first_scene["primary_text"])
    first_secondary = str(first_scene["secondary_text"])
    last_primary = str(last_scene["primary_text"])
    last_secondary = str(last_scene["secondary_text"])

    benefit_keywords = ("오늘만", "할인", "특가", "1+1", "아낌", "무료", "이득")
    menu_keywords = ("규카츠", "맥주", "타코야키", "라멘", "짬뽕", "커피", "아이스크림", "세트")
    cta_keywords = ("방문", "오세요", "지금", "바로", "저장 말고")

    primary_has_benefit = contains_any(first_primary, benefit_keywords)
    secondary_has_benefit = contains_any(first_secondary, benefit_keywords)
    primary_has_menu = contains_any(first_primary, menu_keywords)
    secondary_has_menu = contains_any(first_secondary, menu_keywords)
    cta_visible = contains_any(last_primary, cta_keywords) or contains_any(last_secondary, cta_keywords)

    bgrade_signal_score = (
        min(3, variant.badge_count) * 15
        + min(6, variant.accent_block_count) * 6
        + min(2, variant.rotated_elements) * 12
        + (16 if variant.stroke_enabled else 0)
        + min(90, variant.headline_font_size) * 0.2
    )
    product_visibility_score = {
        "card_panel": 82.0,
        "flyer_poster": 48.0,
        "owner_made_safe": 88.0,
        "hand_drawn_menu": 84.0,
        "structured_bgrade_v2": 94.0,
    }[variant.overlay_mode]
    handdrawn_signal_score = {
        "card_panel": 4.0,
        "flyer_poster": 18.0,
        "owner_made_safe": 26.0,
        "hand_drawn_menu": 92.0,
        "structured_bgrade_v2": 18.0,
    }[variant.overlay_mode]
    layout_integrity_score = {
        "card_panel": 72.0,
        "flyer_poster": 38.0,
        "owner_made_safe": 44.0,
        "hand_drawn_menu": 70.0,
        "structured_bgrade_v2": 94.0,
    }[variant.overlay_mode]
    promotion_message_score = min(
        100.0,
        56.0
        + (28.0 if primary_has_benefit else 0.0)
        + (12.0 if secondary_has_benefit else 0.0)
        + (4.0 if variant.opening_focus == "benefit_first" else 0.0),
    )
    menu_clarity_score = min(
        100.0,
        56.0
        + (28.0 if primary_has_menu else 0.0)
        + (12.0 if secondary_has_menu else 0.0)
        + (4.0 if variant.opening_focus == "menu_first" else 0.0),
    )
    cta_clarity_score = 88.0 if cta_visible else 42.0
    service_loop_fit_score = round(
        promotion_message_score * 0.4
        + menu_clarity_score * 0.2
        + product_visibility_score * 0.2
        + cta_clarity_score * 0.1
        + layout_integrity_score * 0.1,
        1,
    )
    return {
        "bgrade_signal_score": round(bgrade_signal_score, 1),
        "product_visibility_score": product_visibility_score,
        "handdrawn_signal_score": handdrawn_signal_score,
        "layout_integrity_score": layout_integrity_score,
        "promotion_message_score": promotion_message_score,
        "menu_clarity_score": menu_clarity_score,
        "cta_clarity_score": cta_clarity_score,
        "service_loop_fit_score": service_loop_fit_score,
        "headline_font_size": variant.headline_font_size,
        "badge_count": variant.badge_count,
        "accent_block_count": variant.accent_block_count,
        "stroke_enabled": variant.stroke_enabled,
        "rotated_elements": variant.rotated_elements,
        "overlay_mode": variant.overlay_mode,
        "opening_focus": variant.opening_focus,
    }


def contains_any(text: str, keywords: tuple[str, ...]) -> bool:
    return any(keyword in text for keyword in keywords)


def slugify(value: str) -> str:
    lowered = value.lower().replace(" ", "-").replace("/", "-")
    cleaned = "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in lowered)
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-")
