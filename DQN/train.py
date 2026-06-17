for episode in range(episodes):

    state = env.reset()

    done = False

    total_reward = 0

    while not done:


        
        
        if random.random() < epsilon:

            action = random.randint(0,3)

        else:

            with torch.no_grad():

                q = policy_net(
                    torch.FloatTensor(state)
                )

                action = q.argmax().item()

        next_state,reward,done = env.step(action)

        memory.push(
            state,
            action,
            reward,
            next_state,
            done
        )

        state = next_state

        total_reward += reward

        if len(memory) > batch_size:

            states,actions,rewards,next_states,dones = \
                memory.sample(batch_size)

            states = torch.FloatTensor(states)
            actions = torch.LongTensor(actions)

            rewards = torch.FloatTensor(rewards)
            next_states = torch.FloatTensor(next_states)

            dones = torch.FloatTensor(dones)

            q_values = policy_net(states)

            current_q = q_values.gather(
                1,
                actions.unsqueeze(1)
            ).squeeze()

            next_q = target_net(
                next_states
            ).max(1)[0]

            target_q = rewards + gamma * next_q * (1-dones)

            loss = F.mse_loss(
                current_q,
                target_q.detach()
            )

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

    epsilon = max(
        epsilon_min,
        epsilon * epsilon_decay
    )

    if episode % 100 == 0:

        target_net.load_state_dict(
            policy_net.state_dict()
        )

        print(
            f"Episode={episode}",
            f"Reward={total_reward:.2f}",
            f"Epsilon={epsilon:.3f}"
        )