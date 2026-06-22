import torch

FILE = "stats.pth"

data = torch.load(
    FILE,
    map_location="cpu",
    weights_only=False
)

print("Before:")

for key, value in data.items():

    if "epsilon" in key.lower():

        print(key, value)

# -------------------------
# Change epsilon values
# -------------------------

if "player1_epsilon" in data:
    data["player1_epsilon"] = 1.0

if "player2_epsilon" in data:
    data["player2_epsilon"] = 1.0


torch.save(
    data,
    FILE
)

