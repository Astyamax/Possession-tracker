"""Export nearest-team labels while ignoring short possession switches.

Usage: python src/export_nearest_team_threshold.py 50
"""

import csv
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "BAR-ATH_tactical_atd.txt"
N_FRAMES = 199_319
HOME_TRACKS = 24
MIN_POSSESSION_FRAMES = int(sys.argv[1]) if len(sys.argv) == 2 else 50
OUTPUT = ROOT / "src" / "output" / f"BAR-ATH_tactical_nearest_team_threshold_{MIN_POSSESSION_FRAMES}.csv"


def point(field):
    x, y, _ = field.split(",", 2)
    return None if x == "NaN" else (float(x), float(y))


def nearest_team(players, ball):
    ball = point(ball)
    if ball is None:
        return "X"

    closest = (float("inf"), "X")
    for track, player in enumerate(players):
        player = point(player)
        if player is None:
            continue
        distance = (player[0] - ball[0]) ** 2 + (player[1] - ball[1]) ** 2
        if distance < closest[0]:
            closest = distance, "H" if track < HOME_TRACKS else "A"
    return closest[1]


def labels_from_tracking():
    labels = []
    with INPUT.open(encoding="utf-8") as source:
        for frame, line in enumerate(source):
            source_frame, players, ball = line.rstrip().split(":")
            if int(source_frame) != frame + 1:
                raise ValueError(f"Unexpected source frame {source_frame}")
            labels.append(nearest_team(players.split(";"), ball))

    if len(labels) != N_FRAMES:
        raise ValueError(f"Expected {N_FRAMES} frames, found {len(labels)}")
    return labels


def remove_short_switches(labels):
    filtered = labels.copy()
    confirmed_team = "X"
    start = 0

    while start < len(labels):
        end = start + 1
        while end < len(labels) and labels[end] == labels[start]:
            end += 1

        team = labels[start]
        if team in ("H", "A"):
            if team == confirmed_team or end - start >= MIN_POSSESSION_FRAMES:
                confirmed_team = team
            else:
                filtered[start:end] = [confirmed_team] * (end - start)
        start = end

    return filtered


def main():
    if MIN_POSSESSION_FRAMES < 1:
        raise ValueError("The threshold must be at least 1 frame")

    labels = remove_short_switches(labels_from_tracking())
    with OUTPUT.open("w", encoding="utf-8", newline="") as destination:
        writer = csv.writer(destination)
        writer.writerow(("frame", "label"))
        writer.writerows(enumerate(labels))


if __name__ == "__main__":
    main()
