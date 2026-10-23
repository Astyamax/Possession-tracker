"""nearest tracked player."""

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "BAR-ATH_tactical_atd.txt"
OUTPUT = ROOT / "src" / "output" / "BAR-ATH_tactical_nearest_team.csv"
N_FRAMES = 199_319
HOME_TRACKS = 24  # Barcelona occupies ATD tracks 1..24; Athletic occupies 25..46.


def point(field):
    x, y, _ = field.split(",", 2)
    return None if x == "NaN" else (float(x), float(y))


def nearest_team(players, ball):
    ball = point(ball)
    if ball is None:
        return "X"  # The ball is unavailable, so this method abstains.

    closest = (float("inf"), "X")
    for track, player in enumerate(players):
        player = point(player)
        if player is None:
            continue
        distance = (player[0] - ball[0]) ** 2 + (player[1] - ball[1]) ** 2
        if distance < closest[0]:
            closest = distance, "H" if track < HOME_TRACKS else "A"
    return closest[1]


def main():
    with INPUT.open(encoding="utf-8") as source, OUTPUT.open(
        "w", encoding="utf-8", newline=""
    ) as destination:
        writer = csv.writer(destination)
        writer.writerow(("frame", "label"))

        count = 0
        for count, line in enumerate(source, start=1):
            source_frame, players, ball = line.rstrip().split(":")
            if int(source_frame) != count:
                raise ValueError(f"Unexpected source frame {source_frame}")
            writer.writerow((count - 1, nearest_team(players.split(";"), ball)))

    if count != N_FRAMES:
        raise ValueError(f"Expected {N_FRAMES} frames, found {count}")


if __name__ == "__main__":
    main()
