import pandas as pd
import numpy as np

# Define the number of samples to generate
num_samples = 20000

# Define clear profiles for destinations
destination_profiles = {
    # Existing destinations
    'Paris': {'Interet': 'Culture', 'Climat': 'Tempéré', 'Budget': 3000, 'Activite': 'Musée'},
    'Tokyo': {'Interet': 'Culture', 'Climat': 'Tempéré', 'Budget': 7000, 'Activite': 'Gastronomie'},
    'New York': {'Interet': 'Ville', 'Climat': 'Tempéré', 'Budget': 6000, 'Activite': 'Shopping'},
    'Bali': {'Interet': 'Plage', 'Climat': 'Chaud', 'Budget': 1500, 'Activite': 'Surf'},
    'Rome': {'Interet': 'Culture', 'Climat': 'Chaud', 'Budget': 2500, 'Activite': 'Histoire'},
    'Le Caire': {'Interet': 'Culture', 'Climat': 'Chaud', 'Budget': 1200, 'Activite': 'Histoire'},
    'Rio de Janeiro': {'Interet': 'Plage', 'Climat': 'Chaud', 'Budget': 2000, 'Activite': 'Carnaval'},
    'Sydney': {'Interet': 'Ville', 'Climat': 'Chaud', 'Budget': 5000, 'Activite': 'Opéra'},
    'Barcelone': {'Interet': 'Plage', 'Climat': 'Chaud', 'Budget': 2200, 'Activite': 'Architecture'},
    'Londres': {'Interet': 'Ville', 'Climat': 'Froid', 'Budget': 3500, 'Activite': 'Musée'},

    # Added destinations
    'Kyoto': {'Interet': 'Culture', 'Climat': 'Tempéré', 'Budget': 6500, 'Activite': 'Histoire'},
    'Bangkok': {'Interet': 'Ville', 'Climat': 'Chaud', 'Budget': 1800, 'Activite': 'Gastronomie'},
    'Dubai': {'Interet': 'Ville', 'Climat': 'Désertique', 'Budget': 8000, 'Activite': 'Shopping'},
    'Istanbul': {'Interet': 'Culture', 'Climat': 'Tempéré', 'Budget': 2800, 'Activite': 'Histoire'},
    'Marrakech': {'Interet': 'Culture', 'Climat': 'Chaud', 'Budget': 1300, 'Activite': 'Shopping'},
    'Reykjavik': {'Interet': 'Nature', 'Climat': 'Froid', 'Budget': 4500, 'Activite': 'Aurores boréales'},
    'Queenstown': {'Interet': 'Aventure', 'Climat': 'Froid', 'Budget': 5500, 'Activite': 'Ski'},
    'Machu Picchu': {'Interet': 'Aventure', 'Climat': 'Tempéré', 'Budget': 3200, 'Activite': 'Randonnée'},
    'Santorin': {'Interet': 'Plage', 'Climat': 'Chaud', 'Budget': 3800, 'Activite': 'Photographie'},
    'Prague': {'Interet': 'Culture', 'Climat': 'Froid', 'Budget': 2000, 'Activite': 'Histoire'},
    'Amsterdam': {'Interet': 'Ville', 'Climat': 'Froid', 'Budget': 3200, 'Activite': 'Musée'},
    'Le Cap': {'Interet': 'Nature', 'Climat': 'Tempéré', 'Budget': 4000, 'Activite': 'Randonnée'},
    'Buenos Aires': {'Interet': 'Culture', 'Climat': 'Tempéré', 'Budget': 2500, 'Activite': 'Tango'},
    'Séoul': {'Interet': 'Ville', 'Climat': 'Tempéré', 'Budget': 6000, 'Activite': 'Shopping'},
    'Hanoï': {'Interet': 'Culture', 'Climat': 'Chaud', 'Budget': 1500, 'Activite': 'Gastronomie'},
    'Venise': {'Interet': 'Culture', 'Climat': 'Tempéré', 'Budget': 3500, 'Activite': 'Romance'},
    'Mexico': {'Interet': 'Culture', 'Climat': 'Tempéré', 'Budget': 2200, 'Activite': 'Histoire'},
    'Lisbonne': {'Interet': 'Ville', 'Climat': 'Tempéré', 'Budget': 2300, 'Activite': 'Gastronomie'},
    'Vienne': {'Interet': 'Culture', 'Climat': 'Froid', 'Budget': 3000, 'Activite': 'Musique'},
    'Berlin': {'Interet': 'Ville', 'Climat': 'Froid', 'Budget': 2800, 'Activite': 'Histoire'},
}

# Define user feature distributions
interests = ['Culture', 'Ville', 'Plage', 'Aventure', 'Nature', 'Gastronomie', 'Shopping', 'Histoire']
climates = ['Tempéré', 'Chaud', 'Froid', 'Désertique']
travel_types = ['Solo', 'Couple', 'Famille', 'Amis']
seasons = ['Printemps', 'Été', 'Automne', 'Hiver']
nationalities = ['Français', 'Américain', 'Chinois', 'Allemand', 'Japonais', 'Britannique', 'Indien', 'Brésilien', 'Canadien', 'Australien']
activities = ['Musée', 'Gastronomie', 'Shopping', 'Surf', 'Histoire', 'Carnaval', 'Opéra', 'Architecture', 'Aurores boréales', 'Ski', 'Randonnée', 'Photographie', 'Tango', 'Romance', 'Musique']

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
        # Activity match
        if user_profile['Activite'] == profile['Activite']:
            score += 8
        # Budget proximity (lower importance)
        budget_diff = abs(user_profile['Budget'] - profile['Budget'])
        score += max(0, 5 - budget_diff / 500) # Score decreases as budget difference grows
        scores[dest] = score

    # Return the destination with the highest score
    return max(scores, key=scores.get)

# Generate user data and assign the best destination
data = []
for i in range(num_samples):
    user = {
        'Age': np.random.randint(18, 70),
        'Budget': np.random.randint(1000, 8000),
        'Interet': np.random.choice(interests),
        'Duree': np.random.randint(3, 21),
        'Climat': np.random.choice(climates),
        'Type_Voyage': np.random.choice(travel_types),
        'Saison': np.random.choice(seasons),
        'Nationalite': np.random.choice(nationalities),
        'Activite': np.random.choice(activities)
    }

    # Introduce some noise and inconsistencies
    if i % 10 == 0:
        user['Interet'] = 'Cultuer' # Typo
    if i % 20 == 0:
        user['Budget'] = np.nan # Missing value
    if i % 50 == 0:
        # Create a duplicate entry
        data.append(user.copy())

    destination = get_best_destination(user, destination_profiles)
    user['Destination'] = destination
    data.append(user)

# Create DataFrame and save to CSV
df = pd.DataFrame(data)
df.to_csv('tourisme_dataset.csv', index=False)

print(f"Generated {len(df)} travel profiles with some inconsistencies.")
print("Dataset 'tourisme_dataset.csv' created successfully.")
