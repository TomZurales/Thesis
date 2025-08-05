import optuna

def objective(trial):
    x_int1 = trial.suggest_int('x_int1', 1, 10)
    x_float1 = trial.suggest_float('x_float1', 0.0, 1.0)
    x_int2 = trial.suggest_int('x_int2', 1, 10)
    x_float2 = trial.suggest_float('x_float2', 0.0, 2.0)

    # Replace with your objective
    return (x_int1 - 3)**2 + (x_float1 - 0.75)**2 + (x_int2 - 7)**2 + (x_float2 - 1.5)**2

study = optuna.create_study(direction='minimize')
study.optimize(objective, n_trials=100)

print(study.best_params)