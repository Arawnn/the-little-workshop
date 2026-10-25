from collections import deque

# TODO 1: Créer une file vide
events = deque()
# TODO 2: Ajouter move_to, inspect et repair
events.append('move_to')
events.append('inspect')
events.append('repair')

# TODO 3: Consommer les événements avec while
# et afficher chaque événement
while events:
  event = events.popleft()
  print(f"Processing {event}")

  
  if event == 'repair':
    events.append('idle')


# TODO 4: Afficher le message final
print("Simulation complete!")