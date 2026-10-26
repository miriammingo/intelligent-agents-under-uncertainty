# Intelligent Agents under Uncertainty 🤖

This project explores different approaches to **autonomous decision-making under uncertainty**, combining classical Artificial Intelligence techniques with probabilistic reasoning and Markov Decision Processes.

The project consists of three scenarios in which an autonomous agent must reason about its environment, plan its actions and make decisions with incomplete or uncertain information.

## 🧠 Approaches

### 1. Logical Agent

The first agent operates in a partially observable grid environment where dangerous cells are initially unknown.

Using the percepts collected while exploring the environment, the agent:

- Identifies safe and potentially dangerous cells
- Maintains a representation of the known environment
- Uses logical deductions to update its knowledge
- Applies **Breadth-First Search (BFS)** to navigate through known safe areas

### 2. Bayesian Agent

The second approach introduces uncertainty explicitly through probability.

The agent maintains probability maps for different elements of the environment and updates them as new percepts are observed.

Main components include:

- Prior probability distributions
- Bayesian probability updates
- Risk estimation for unexplored cells
- Probability maps representing uncertainty
- **A\*** search combining accumulated risk and Manhattan distance

This allows the agent to choose paths that balance reaching its objective with avoiding uncertain or dangerous areas.

### 3. Markov Decision Process

The final scenario models decision-making in a stochastic environment using a **Markov Decision Process (MDP)**.

The environment includes probabilistic transitions caused by a river current, meaning that the result of an action is not always deterministic.

The solution implements:

- States and actions
- Transition probabilities
- Rewards
- Discount factor
- Bellman updates
- **Value Iteration**
- Extraction of the optimal policy
- Simulation of the resulting policy

## 🛠️ Technologies

- Python
- NumPy
- Search algorithms
- Bayesian inference
- Markov Decision Processes
- Dynamic programming

## 📂 Project Structure

```text
intelligent-agents-under-uncertainty/
│
├── kurtz.py        # Logical reasoning agent and BFS navigation
├── palacio.py      # Bayesian agent and risk-based A* search
├── river_mdp.py    # MDP, Value Iteration and optimal policy
├── report/
│   └── project-report.pdf
└── README.md
```

## 📄 Project Report

A detailed explanation of the methodology and results is available in the [project report](report/project-report.pdf).

## 👩‍💻 Author

**Míriam Mingo Revuelta**  
Mathematical Engineering and Artificial Intelligence  
Universidad Pontificia Comillas – ICAI
