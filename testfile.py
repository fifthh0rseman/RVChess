"""
В данном методе после каждого взаимодействия агента со средой
возвращается числовое вознаграждение.
"""

import numpy as np
from collections import defaultdict

from ValueIteration import value_iteration


def advance(numPolicies, dirichletPosterior, numStates, numActions,
            NgParams, horizon):
    """
    Для каждой выбранной среды запускает value_iteration,
    чтобы получить оптимальные numPolicies с учетом выбранной динамики и вознаграждений
    """

    policies = []
    rewardModels = []

    for i in range(numPolicies):

        dynamicsAndDirichletPosteriorSample = []

        for state in range(numStates):

            dummySample_ = []

            for action in range(numActions):
                dummySample_.append(np.random.dirichlet(dirichletPosterior[state][action]))

            dynamicsAndDirichletPosteriorSample.append(dummySample_)

        sampleRewards = np.empty((numStates, numActions))

        for s in range(numStates):
            for a in range(numActions):
                gamma_sample = np.random.gamma(NgParams[s, a, 2], 1 / NgParams[s, a, 3])
                sampleRewards[s, a] = np.random.normal(NgParams[s, a, 0],
                                                       (NgParams[s, a, 1] * gamma_sample) ** (-0.5))

        policies.append(value_iteration(dynamicsAndDirichletPosteriorSample, sampleRewards, numStates,
                                        numActions, epsilon=0,
                                        H=horizon)[0])
        rewardModels.append(sampleRewards)

    return policies, rewardModels


def DPSRL(horizon, NgPriorParams, env, numIter, dirichletPrior=1,
          seed=None):
    """
      1) horizon - количество state/action пар в каждом эпизоде обучения
      2) NgPriorParams: гиперпараметры для модели нормального или гамма
        распределения, используется для поощрения. Например:
        [mu0, k0, alpha0, beta0]
      3) env: окружение RL
      4) numIter: кол-во итераций алгоритма
      5) dirichletPrior: установка приора для модели транзитной динамики.
        Рассматривается марковская модель.
        Для каждой пары state/action устанавливается как
        dirichletPrior * np.ones(numStates), где numStates -
        кол-во состояний в марковском процессе.
      6) seed - отвечает за случайную генерацию числа


    Возвращает вектор вознаграждений, полученных при выполнении алгоритма.
    Это либо общее вознаграждение от каждого развертывания траектории,
    либо вознаграждение за каждый шаг, предпринятый в среде
    (какое из них - определяется параметром env).
    """

    if seed is not None:
        np.random.seed(seed)

    numStates = env.numStates
    numActions = env.numActions

    dirichletPosterior = defaultdict(lambda: defaultdict(lambda: dirichletPrior * np.ones(numStates)))

    NgParams = np.tile(NgPriorParams, (numStates, numActions, 1))

    # Сколько раз посещена каждая пара
    visitCounts = np.zeros((numStates, numActions))

    # Вознаграждения
    rewards = defaultdict(lambda: [])

    numPolicies = 1  # Number of policies to sample per learning iteration

    # Сохраняем результаты
    if env.store_episode_reward:  # общая награда для траектории
        rewards = np.empty(numIter * numPolicies)
    else:  # или награда на каждом шагу траектории
        rewards = np.empty(numIter * horizon * numPolicies)

    rewardCount = 0  # счетчик количества доступных наград

    for iteration in range(numIter):

        print('PSRL: iteration %i' % (iteration + 1))

        policies, rewardModels = advance(numPolicies, dirichletPosterior,
                                         numStates, numActions, NgParams, horizon)

        for policy in policies:

            state = env.reset()

            for t in range(horizon):

                action = np.random.choice(numActions, p=policy[t, state, :])

                next_state, reward, done, = env.step(action)

                # На каждом шаге обновляем dirichletPosterior:
                dirichletPosterior[state][action][next_state] += 1

                # Обновляем количество посещений:
                visitCounts[state][action] += 1

                # Сохраняем результаты
                rewards[state, action].append(reward)

                if not env.storeEpisodeReward:
                    rewards[rewardCount] = env.getStepReward(state,
                                                             action, next_state)
                    rewardCount += 1

                if done:
                    break

                state = next_state

            if env.store_episode_reward:
                rewards[rewardCount] = env.get_trajectory_return()
                rewardCount += 1

        NgParams = feedbackNG(NgPriorParams, visitCounts, rewards,
                              numStates, numActions)

    return rewards


def feedbackNG(NgPriorParams, visitCounts, rewards, numStates,
               numActions):
    """
    Обновляет апостериорное вознаграждение, основываясь на остальных параметрах
    """
    NgParams = np.empty((numStates, numActions, 4))

    mu0 = NgPriorParams[0]
    k0 = NgPriorParams[1]
    alpha0 = NgPriorParams[2]
    beta0 = NgPriorParams[3]

    for s in range(numStates):
        for a in range(numActions):

            n = visitCounts[s, a]

            if n == 0:
                NgParams[s, a] = NgPriorParams
                continue

            samples = np.array(rewards[s, a])
            avg = np.mean(samples)

            NgParams[s, a, 0] = (k0 * mu0 + n * avg) / (k0 + n)
            NgParams[s, a, 1] = k0 + n
            NgParams[s, a, 2] = alpha0 + n / 2
            NgParams[s, a, 3] = beta0 + 0.5 * np.sum((samples - avg) ** 2) + k0 * n * (avg - mu0) ** 2 / (2 * (k0 + n))

    return NgParams
