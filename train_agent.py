from keras.models import Sequential
from keras.layers import Dense
from rl.agents.dqn import DQNAgent
from rl.memory import SequentialMemory
from rl.policy import EpsGreedyQPolicy
from tic_tac_toe import TicTacToe

# Define the neural network architecture for the DQN agents
def build_model(input_shape, num_actions):
    model = Sequential()
    model.add(Dense(64, activation='relu', input_shape=input_shape))
    model.add(Dense(64, activation='relu'))
    model.add(Dense(num_actions, activation='linear'))
    return model

env = TicTacToe()
# Initialize the agents
input_shape = env.observation_space.shape
num_actions = env.action_space.n
model = build_model(input_shape, num_actions)

memory = SequentialMemory(limit=10000, window_length=1)
policy = EpsGreedyQPolicy(eps=0.1)  # Exploration policy

agent1 = DQNAgent(model=model, nb_actions=num_actions, memory=memory, nb_steps_warmup=100,
                  target_model_update=1e-2, policy=policy)
agent2 = DQNAgent(model=model, nb_actions=num_actions, memory=memory, nb_steps_warmup=100,
                  target_model_update=1e-2, policy=policy)

agent1.compile(optimizer='adam', metrics=['mae'])
agent2.compile(optimizer='adam', metrics=['mae'])

num_episodes = 1000  # Adjust as needed

num_episodes = 1000  # Adjust as needed

for episode in range(num_episodes):
    state = env.reset()
    done = False

    while not done:
        if env.current_player == 1:
            action = agent1.act(state)
        else:
            action = agent2.act(state)

        next_state, reward, done, _ = env.step(action)

        # Update the agents' memories and train them separately
        if env.current_player == 1:
            agent1.memory.append(state, action, reward, next_state, done)
            agent1.train()
        else:
            agent2.memory.append(state, action, reward, next_state, done)
            agent2.train()

        state = next_state

    # Print episode information (optional)
    print(f"Episode {episode + 1}: Agent 1 reward = {reward} | Agent 2 reward = {-reward}")

# Save the trained models
agent1.save_weights('agent1_weights.h5f')
agent2.save_weights('agent2_weights.h5f')


# Save the trained models
agent1.save_weights('agent1_weights.h5f')
agent2.save_weights('agent2_weights.h5f')

