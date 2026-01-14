import pandas as pd
import numpy as np

# Define the number of samples to generate
num_samples = 20000

# Define clear profiles for destinations
destination_profiles = {
    'Paris': {'Interet': 'Culture', 'Climat': 'Tempéré', 'Budget': 3000},
    'Tokyo': {'Interet': 'Culture', 'Climat': 'Tempéré', 'Budget': 7000},
    'New York': {'Interet': 'Ville', 'Climat': 'Tempéré', 'Budget': 6000},
    'Bali': {'Interet': 'Plage', 'Climat': 'Chaud', 'Budget': 1500},
    'Rome': {'Interet': 'Culture', 'Climat': 'Chaud', 'Budget': 2500},
    'Le Caire': {'Interet': 'Culture', 'Climat': 'Chaud', 'Budget': 1200},
    'Rio de Janeiro': {'Interet': 'Plage', 'Climat': 'Chaud', 'Budget': 2000},
    'Sydney': {'Interet': 'Ville', 'Climat': 'Chaud', 'Budget': 5000},
    'Barcelone': {'Interet': 'Plage', 'Climat': 'Chaud', 'Budget': 2200},
    'Londres': {'Interet': 'Ville', 'Climat': 'Froid', 'Budget': 3500}
}

# Define user feature distributions
interests = ['Culture', 'Ville', 'Plage', 'Aventure', 'Nature']
climates = ['Tempéré', 'Chaud', 'Froid']

def get_best_destination(user_profile, dest_profiles):
    """
    Calculates a compatibility score between a user and destinations,
    and returns the best match.
    """
    scores = {}
    for dest, profile in dest_profiles.items():
        score = 0
        # Interest match (high importance)
        if user_profile['Interet'] == profile['Interet']:
            score += 10
        # Climate match (medium importance)
        if user_profile['Climat'] == profile['Climat']:
            score += 5
        # Budget proximity (lower importance)
        budget_diff = abs(user_profile['Budget'] - profile['Budget'])
        score += max(0, 5 - budget_diff / 500) # Score decreases as budget difference grows
        scores[dest] = score

    # Return the destination with the highest score
    return max(scores, key=scores.get)

# Generate user data and assign the best destination
data = []
for _ in range(num_samples):
    user = {
        'Age': np.random.randint(18, 70),
        'Budget': np.random.randint(1000, 8000),
        'Interet': np.random.choice(interests),
        'Duree': np.random.randint(3, 21),
        'Climat': np.random.choice(climates)
    }

    destination = get_best_destination(user, destination_profiles)

    user['Destination'] = destination
    data.append(user)

# Create DataFrame and save to CSV
df = pd.DataFrame(data)
df.to_csv('tourisme_dataset.csv', index=False)

print(f"Generated {len(df)} unique and consistent travel profiles.")
print("Dataset 'tourisme_dataset.csv' created successfully.")
