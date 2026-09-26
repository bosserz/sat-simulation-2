"""Convert an adaptive mock exam package (sat-exam-prep/<set>/mock_exam.json)
into the app's full-test format and copy its figures into static/.

    python3 import_adaptive_mock.py sat-exam-prep/oct_2026 "Digital SAT Mock Test (Oct 2026)" oct_2026

Writes database/mock_tests/<slug>.json and static/images/mock_tests/<slug>/.
Module 2 questions carry a `variant` ("medium" or "hard"); the app picks one
per section from the module 1 score and the thresholds in `routing`.
"""
import html
import json
import os
import shutil
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BLANK_HTML = '<span aria-hidden="true" class="blank">______</span><span class="sr-only">blank</span>'
SECTION_TYPES = {"rw": "verbal", "math": "math"}


def _text(value):
    return (value or "").replace("______", BLANK_HTML)


def _figure_html(figure, image_dir):
    name = os.path.basename(figure.get("svg") or figure["src"])
    alt = html.escape(figure.get("alt", ""), quote=True)
    return f'<img class="sat-figure" src="/static/{image_dir}/{name}" alt="{alt}">'


def _passage_html(q, image_dir):
    parts = []
    if q.get("intro"):
        parts.append(f"<p><em>{_text(q['intro'])}</em></p>")
    for p in q.get("passages") or []:
        parts.append(f"<p><strong>{p['label']}</strong></p><p>{_text(p['text'])}</p>")
    if q.get("passage"):
        parts.append(f"<p>{_text(q['passage'])}</p>")
    if q.get("notes"):
        items = "".join(f"<li>{_text(n)}</li>" for n in q["notes"])
        parts.append(f"<ul>{items}</ul>")
    if q.get("figure"):
        parts.append(_figure_html(q["figure"], image_dir))
    return "".join(parts) or None


def _convert_question(q, qtype, module, variant, question_id, image_dir):
    choices = q.get("choices") or []
    options = [_text(c["text"]) for c in choices]
    if choices:
        by_label = {c["label"]: _text(c["text"]) for c in choices}
        correct = by_label[q["answer"]]
    else:
        correct = q.get("accepted_answers") or [q["answer"]]

    stem = _text(q["stem"])
    if qtype == "math":
        passage = None
        question = stem
        if q.get("figure"):
            question = _figure_html(q["figure"], image_dir) + f"<p>{stem}</p>"
    else:
        passage = _passage_html(q, image_dir)
        question = stem

    return {
        "question_id": question_id,
        "source_id": q["id"],
        "type": qtype,
        "module": module,
        "variant": variant,
        "domain": q["domain"],
        "skill": q["skill"],
        "level": q["difficulty"].title(),
        "passage": passage,
        "question": question,
        "options": options,
        "correct_answer": correct,
        "explanation": q.get("explanation"),
        "image": None,
        "equation": None,
    }


def convert(source_dir, name, slug):
    with open(os.path.join(source_dir, "mock_exam.json")) as f:
        exam = json.load(f)

    image_dir = f"images/mock_tests/{slug}"
    questions, routing = [], {}
    for section in sorted(exam["sections"], key=lambda s: s["order"]):
        qtype = SECTION_TYPES[section["id"]]
        route = section["routing"]
        routing[qtype] = {"threshold": route["threshold"]}
        for module in section["modules"]:
            if module["stage"] == 1:
                variant = None
            elif module["id"] == route["if_at_least_threshold"]:
                variant = "hard"
            elif module["id"] == route["otherwise"]:
                variant = "medium"
            else:
                raise ValueError(f"Module {module['id']} is not a routing target")
            for q in module["questions"]:
                questions.append(_convert_question(
                    q, qtype, module["stage"], variant, len(questions) + 1, image_dir
                ))

    out_dir = os.path.join(BASE_DIR, "database", "mock_tests")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"{slug}.json")
    with open(out_path, "w") as f:
        json.dump({"name": name, "routing": routing, "questions": questions}, f, indent=2, ensure_ascii=False)
        f.write("\n")

    fig_src = os.path.join(source_dir, "figures")
    fig_dst = os.path.join(BASE_DIR, "static", image_dir)
    os.makedirs(fig_dst, exist_ok=True)
    copied = 0
    for fname in sorted(os.listdir(fig_src)):
        if fname.endswith(".svg"):
            shutil.copy2(os.path.join(fig_src, fname), fig_dst)
            copied += 1

    print(f"Wrote {len(questions)} questions to {os.path.relpath(out_path, BASE_DIR)}")
    print(f"Copied {copied} figures to static/{image_dir}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        sys.exit(__doc__)
    convert(sys.argv[1], sys.argv[2], sys.argv[3])
