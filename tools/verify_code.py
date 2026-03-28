#!/usr/bin/env python3
"""
ตัวตรวจสอบรหัสยืนยัน ต้นคิด (Tonkid Verification Code Validator)

ใช้สำหรับอาจารย์ตรวจสอบว่ารหัสยืนยันที่นักศึกษาส่งมาถูกต้องหรือไม่
รองรับทั้งการตรวจทีละรหัส และตรวจจากไฟล์ CSV แบบ batch

สูตร V code (ใช้ตาราง lookup — ไม่มีการคูณ):
  ตารางค่าลับ:
  | คะแนน | เกณฑ์1 | เกณฑ์2 | เกณฑ์3 | เกณฑ์4 | เกณฑ์5 |
  |   1   |   3    |   7    |   2    |   9    |   5    |
  |   2   |   8    |   1    |   6    |   4    |   9    |
  |   3   |   5    |   9    |   8    |   2    |   3    |
  |   4   |   1    |   4    |   3    |   7    |   6    |
  lookup_sum = ผลรวมค่าจากตาราง 5 เกณฑ์
  id_sum     = ผลรวมของเลข 4 ตัวท้ายรหัสนักศึกษา
  raw        = lookup_sum + id_sum + จำนวนรอบ
  V          = 2 หลักสุดท้ายของ raw

การใช้งาน:
  python verify_code.py TK-5678-44334-5R-0C-V16-D26
  python verify_code.py --csv input.csv --output results.csv
  python verify_code.py --interactive
"""

import re
import sys
import csv
import argparse
from dataclasses import dataclass
from typing import Optional


# ตารางค่าลับสำหรับคำนวณ V code (ห้ามเปลี่ยน!)
# LOOKUP_TABLE[คะแนน] = [เกณฑ์1, เกณฑ์2, เกณฑ์3, เกณฑ์4, เกณฑ์5]
LOOKUP_TABLE = {
    1: [3, 7, 2, 9, 5],
    2: [8, 1, 6, 4, 9],
    3: [5, 9, 8, 2, 3],
    4: [1, 4, 3, 7, 6],
}

# ชื่อเกณฑ์ 5 ตัว
CRITERIA_NAMES = [
    "วิเคราะห์ประเด็น",
    "หลักฐาน",
    "มุมมอง",
    "เชื่อมโยง",
    "สรุป",
]

# Regex สำหรับ parse verification code
CODE_PATTERN = re.compile(
    r"^TK-(\d{4})-(\d{5})-(\d+)R-(\d+)C-V(\d{2})-D26$"
)


@dataclass
class VerificationResult:
    """ผลการตรวจสอบรหัสยืนยัน"""
    code: str
    valid: bool
    student_id: str = ""
    scores: list = None
    total_score: int = 0
    rounds: int = 0
    copy_count: int = 0
    v_code_given: int = 0
    v_code_expected: int = 0
    error: str = ""


def calculate_v_code(scores: list[int], id_digits: str, rounds: int) -> int:
    """คำนวณ V code จากคะแนน, รหัส, และจำนวนรอบ (ใช้ตาราง lookup)"""
    # ขั้น 1: หาค่าจากตาราง แล้วรวมกัน
    lookup_sum = sum(LOOKUP_TABLE[s][i] for i, s in enumerate(scores))

    # ขั้น 2: id digit sum
    id_sum = sum(int(d) for d in id_digits)

    # ขั้น 3: raw = lookup_sum + id_sum + rounds
    raw = lookup_sum + id_sum + rounds

    # ขั้น 4: last 2 digits
    v = raw % 100

    return v


def parse_and_verify(code: str, skip_vcode: bool = False) -> VerificationResult:
    """Parse รหัสยืนยันและตรวจสอบ V code (หรือข้ามถ้า skip_vcode=True)"""
    code = code.strip()

    match = CODE_PATTERN.match(code)
    if not match:
        return VerificationResult(
            code=code, valid=False,
            error="รูปแบบรหัสไม่ถูกต้อง (ต้องเป็น TK-XXXX-XXXXX-XR-XC-VXX-D26)"
        )

    student_id = match.group(1)
    scores_str = match.group(2)
    rounds = int(match.group(3))
    copy_count = int(match.group(4))
    v_given = int(match.group(5))

    # แยกคะแนน 5 ตัว
    scores = [int(c) for c in scores_str]

    # ตรวจว่าคะแนนแต่ละตัวอยู่ในช่วง 1-4
    for i, s in enumerate(scores):
        if s < 1 or s > 4:
            return VerificationResult(
                code=code, valid=False,
                error=f"คะแนนเกณฑ์ที่ {i+1} ({CRITERIA_NAMES[i]}) = {s} ไม่อยู่ในช่วง 1-4"
            )

    # ตรวจจำนวนรอบ
    if rounds not in (5, 6):
        return VerificationResult(
            code=code, valid=False,
            error=f"จำนวนรอบ = {rounds} ไม่ปกติ (ควรเป็น 5 หรือ 6)"
        )

    # คำนวณ V code ที่ถูกต้อง
    v_expected = calculate_v_code(scores, student_id, rounds)

    if skip_vcode:
        # ข้าม V code — ถือว่าผ่านถ้า format/scores/rounds ถูก
        return VerificationResult(
            code=code,
            valid=True,
            student_id=student_id,
            scores=scores,
            total_score=sum(scores),
            rounds=rounds,
            copy_count=copy_count,
            v_code_given=v_given,
            v_code_expected=v_expected,
            error="ข้าม V code (สูตรเก่า)"
        )

    is_valid = (v_given == v_expected)

    return VerificationResult(
        code=code,
        valid=is_valid,
        student_id=student_id,
        scores=scores,
        total_score=sum(scores),
        rounds=rounds,
        copy_count=copy_count,
        v_code_given=v_given,
        v_code_expected=v_expected,
        error="" if is_valid else f"V code ไม่ตรง: ได้ V{v_given:02d} แต่ควรเป็น V{v_expected:02d} → อาจเป็นรหัสปลอม!"
    )


def format_result(result: VerificationResult) -> str:
    """แสดงผลการตรวจสอบแบบสวยงาม"""
    lines = []
    lines.append(f"  รหัส: {result.code}")

    if result.error and not result.student_id:
        lines.append(f"  ❌ {result.error}")
        return "\n".join(lines)

    if result.valid and result.error == "ข้าม V code (สูตรเก่า)":
        status = "✅ ผ่าน (ข้าม V)"
    elif result.valid:
        status = "✅ ถูกต้อง"
    else:
        status = "❌ ไม่ถูกต้อง"
    lines.append(f"  สถานะ: {status}")
    lines.append(f"  รหัส นศ. 4 ตัวท้าย: {result.student_id}")

    # แสดงคะแนนรายเกณฑ์
    score_parts = []
    for name, score in zip(CRITERIA_NAMES, result.scores):
        score_parts.append(f"{name}={score}")
    lines.append(f"  คะแนน: {', '.join(score_parts)}")
    lines.append(f"  คะแนนรวม: {result.total_score}/20")
    lines.append(f"  จำนวนรอบ: {result.rounds} {'(มีทบทวน)' if result.rounds == 6 else ''}")
    lines.append(f"  การคัดลอก: {result.copy_count} ครั้ง")
    lines.append(f"  V code: V{result.v_code_given:02d} (คาดหวัง: V{result.v_code_expected:02d})")

    if result.error:
        lines.append(f"  ⚠️  {result.error}")

    return "\n".join(lines)


def process_csv(input_path: str, output_path: str, skip_vcode: bool = False):
    """ตรวจสอบรหัสจากไฟล์ CSV แบบ batch"""
    results = []

    with open(input_path, "r", encoding="utf-8") as f:
        reader = csv.reader(f)
        header = next(reader, None)

        # หา column ที่มีรหัสยืนยัน (TK-)
        code_col = None
        if header:
            for i, h in enumerate(header):
                if "TK-" in h or "รหัส" in h.lower() or "code" in h.lower() or "verification" in h.lower():
                    code_col = i
                    break

        # ถ้าหา column ไม่เจอ ลองหา TK- ใน data
        if code_col is None and header:
            for i, val in enumerate(header):
                if val.startswith("TK-"):
                    code_col = i
                    results.append(parse_and_verify(val, skip_vcode))
                    break

        if code_col is None:
            code_col = 0  # default to first column

        for row in reader:
            if len(row) > code_col:
                cell = row[code_col].strip()
                if cell.startswith("TK-"):
                    results.append(parse_and_verify(cell, skip_vcode))

    # สรุปผล
    valid_count = sum(1 for r in results if r.valid)
    invalid_count = sum(1 for r in results if not r.valid)

    print(f"\n{'='*60}")
    print(f"  ผลการตรวจสอบ: {len(results)} รหัส")
    print(f"  ✅ ถูกต้อง: {valid_count}")
    print(f"  ❌ ไม่ถูกต้อง: {invalid_count}")
    print(f"{'='*60}\n")

    # แสดงรหัสที่ไม่ถูกต้อง
    if invalid_count > 0:
        print("รหัสที่ไม่ถูกต้อง:")
        for r in results:
            if not r.valid:
                print(format_result(r))
                print()

    # เขียนผลลัพธ์เป็น CSV
    with open(output_path, "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "รหัสยืนยัน", "สถานะ", "รหัส_นศ",
            "วิเคราะห์ประเด็น", "หลักฐาน", "มุมมอง", "เชื่อมโยง", "สรุป",
            "คะแนนรวม", "จำนวนรอบ", "การคัดลอก",
            "V_ที่ได้", "V_ที่ถูกต้อง", "หมายเหตุ"
        ])
        for r in results:
            scores = r.scores or [0, 0, 0, 0, 0]
            writer.writerow([
                r.code,
                "ผ่าน (ข้าม V)" if (r.valid and r.error == "ข้าม V code (สูตรเก่า)") else ("ถูกต้อง" if r.valid else "ไม่ถูกต้อง"),
                r.student_id,
                *scores,
                r.total_score,
                r.rounds,
                r.copy_count,
                f"V{r.v_code_given:02d}" if r.student_id else "",
                f"V{r.v_code_expected:02d}" if r.student_id else "",
                r.error
            ])

    print(f"📁 บันทึกผลลัพธ์ที่: {output_path}")


def interactive_mode():
    """โหมดตรวจสอบทีละรหัส"""
    print("\n" + "=" * 60)
    print("  🔍 ตัวตรวจสอบรหัสยืนยัน ต้นคิด")
    print("  พิมพ์รหัสยืนยันเพื่อตรวจสอบ หรือ 'q' เพื่อออก")
    print("=" * 60)

    while True:
        print()
        code = input("  รหัสยืนยัน: ").strip()
        if code.lower() in ("q", "quit", "exit", "ออก"):
            print("  👋 ลาก่อน!")
            break
        if not code:
            continue

        result = parse_and_verify(code)
        print()
        print(format_result(result))


def main():
    parser = argparse.ArgumentParser(
        description="ตัวตรวจสอบรหัสยืนยัน ต้นคิด (Tonkid V-Code Validator)"
    )
    parser.add_argument(
        "code", nargs="?",
        help="รหัสยืนยัน เช่น TK-5678-44334-5R-0C-V16-D26"
    )
    parser.add_argument(
        "--csv", metavar="INPUT",
        help="ไฟล์ CSV ที่มีรหัสยืนยัน (batch mode)"
    )
    parser.add_argument(
        "--output", metavar="OUTPUT", default="results.csv",
        help="ไฟล์ CSV สำหรับบันทึกผลลัพธ์ (default: results.csv)"
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true",
        help="โหมดตรวจสอบทีละรหัส"
    )
    parser.add_argument(
        "--skip-vcode", action="store_true",
        help="ข้าม V code (สำหรับรหัสรอบเก่าที่ LLM คำนวณผิด) — ยังดึงคะแนน/ID/รอบได้"
    )

    args = parser.parse_args()

    if args.csv:
        process_csv(args.csv, args.output, skip_vcode=args.skip_vcode)
    elif args.interactive:
        interactive_mode()
    elif args.code:
        result = parse_and_verify(args.code, skip_vcode=args.skip_vcode)
        print()
        print(format_result(result))
        print()
        sys.exit(0 if result.valid else 1)
    else:
        # ถ้าไม่มี argument → interactive mode
        interactive_mode()


if __name__ == "__main__":
    main()
