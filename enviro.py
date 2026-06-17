# 0 = empty
# 1 = blue
# 2 = red
board = [
 [0,0,0,0,2,0,0,0,0],
 [0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0],
 [0,0,0,0,0,0,0,0,0],
 [0,0,0,0,1,0,0,0,0]
]

# The AI can choose:
# 0 = move up
# 1 = move down
# 2 = move left
# 3 = move right

# Rewards
# win  = +100
# lose = -100
# move closer to goal = +1
# move away from goal = -1
# illegal move = -5
reward = 0 
if blue_wins:
    reward = 100

elif red_wins:
    reward = -100

else:
    reward = distance_before - distance_after