class LCG:
    def __init__(self, seed):
        self.modulus = 2**31 - 1
        self.multiplier = 48271
        self.increment = 0
        self.seed = seed

    def next(self):
        self.seed = (self.multiplier * self.seed + self.increment) % self.modulus
        return self.seed

# Определяем классы для игрока и NPC
class Character:
    def __init__(self, name, hp, mp, arm, dmg):
        self.name = name
        self.hp = hp
        self.mp = mp
        self.arm = arm
        self.dmg = dmg

    def attack(self, target):
        damage_dealt = max(0, self.dmg - target.arm)
        target.hp -= damage_dealt
        return damage_dealt

class Player(Character):
    def __init__(self, name):
        super().__init__(name, hp=100, mp=50, arm=5, dmg=10)
        self.quests = {}  # Dictionary to track quests (quest_name: completed status (True/False))

class Enemy(Character):
    def __init__(self):
        super().__init__("Противник", hp=50, mp=0, arm=2, dmg=8)

class Rat(Character):
    def __init__(self):
        super().__init__("Крыса", hp=5, mp=0, arm=0, dmg=3)

# Определяем Задания и локации
class Quest:
    def __init__(self, name, description, location, requirements=None, reward_message="Задание выполнено!"):
        self.name = name
        self.description = description
        self.location = location  # Локация, где квест должен быть выполнен
        self.requirements = requirements  # Словарь требуемых предметов (например 3 травы, 2 шкуры)
        self.reward_message = reward_message
        self.completed = False

    def is_complete(self, player):
        if self.requirements:
            for item, count in self.requirements.items():
                if player.inventory.get(item, 0) < count: 
                    return False
        return True

class Location:
    def __init__(self, name, grid, buildings=None, quests=None, enemy_count=0, rat_count=0):
        self.name = name
        self.grid = grid  
        self.buildings = buildings or [] 
        self.quests = quests or []  # Список заданий
        self.enemy_count = enemy_count
        self.rat_count = rat_count

# Utility-функции

def generate_map(size):
    return [['.' for _ in range(size)] for _ in range(size)]

def render_map(location, player_pos, enemies_pos=None):
    game_map = location.grid  
    building_found = False

    for y in range(len(game_map)):
        for x in range(len(game_map[y])):
            building_here = False
            if location.buildings:
                for building_x, building_y, description in location.buildings:
                    if (x, y) == (building_x, building_y):
                        building_here = True
                        break
            if (x, y) == player_pos:
                print('P', end=' ') # Персонаж ("герой")

                if building_here and not building_found:
                    building_found = True

            elif enemies_pos and (x, y) in enemies_pos: # Несколько противников
                print('E', end=' ')  # Противник
            else:
                print(game_map[y][x], end=' ')
        print()
    print()

    # Рендер построек
    if location.buildings:
        for building_x, building_y, description in location.buildings:
            if (building_x, building_y) == player_pos:
                print(f"Ты сейчас около: {description}") # Взаимодействие с постройками
    # Рендер квестов (Если)
    if location.quests:
        for quest in location.quests:
            if not quest.completed:
                print(f"Задание: {quest.name} - {quest.description}")
    print()

def check_collision(pos, game_map):
    x, y = pos
    if x < 0 or y < 0 or x >= len(game_map) or y >= len(game_map[0]):
        return True
    return False

def move_enemy_towards_player(enemy_pos, player_pos):
    enemy_x, enemy_y = enemy_pos
    player_x, player_y = player_pos

    if enemy_x < player_x:
        enemy_x += 1
    elif enemy_x > player_x:
        enemy_x -= 1

    if enemy_y < player_y:
        enemy_y += 1
    elif enemy_y > player_y:
        enemy_y -= 1

    return (enemy_x, enemy_y)


# Сетап локаций и заданий
hub_grid = [
    ['.', '.', '.', '.', '.'],  # д означает Маленький домик (домик)
    ['.', 'д', 'Д', '.', '.'],  # Д означает Большой дом (дом)
    ['.', 'Т', 'P', 'М', '.'],  # P означает Player ("герой")
    ['.', '.', 'H', '.', '.'],  # H означает Ратуша (ратуша)
    ['.', '.', '.', '.', '.']   # Т означает Твой дом (твой дом)
]                               # М означает Магазин (магазин)
hub_buildings = [
    (1, 1, "Маленький домик"),
    (2, 1, "Большой дом"),
    (2, 2, "Твой дом"),
    (3, 1, "Магазин"),
    (2, 3, "Ратуша")
]
# Задания в хабе (могут быть добавлены позднее)
hub_quests = []
hub = Location("хаб", hub_grid, hub_buildings, hub_quests)


lake_grid = [
    ['W', 'W', 'W', '.', '.'],  # W означает Water (вода)
    ['W', 'W', 'W', '.', '.'],
    ['.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.']
]
# Квест: сбор трав
gather_herbs_quest = Quest("Собрать травы", "Собери 3 травы.", "озеро", requirements=None, reward_message="Ты собрал травы! А так красиво было.")
lake_quests = [gather_herbs_quest]
lake = Location("озеро", lake_grid, quests=lake_quests)


forest_grid = [
    ['.', '.', '.', '.', '.'],  # T означает Tree (дерево)
    ['T', 'T', 'T', '.', '.'],
    ['T', 'T', '.', '.', '.'],
    ['T', 'T', '.', 'T', 'T'],
    ['T', 'T', '.', 'T', 'T']
]
# Квест: снятие шкур
skin_quest = Quest("Сбор шкур", "Собери две шкуры животных", "лес", requirements=None, reward_message="Ты успешно снял шкуры. Жестоко...")
forest_quests = [skin_quest]
forest = Location("лес", forest_grid, quests=forest_quests)


swamp_grid = [
    ['.', '.', '.', '.', '.'],  # S означает Swamp (болото)
    ['W', 'W', 'R', '.', '.'],  # R означает Rat (крыса)
    ['.', 'T', '.', 'R', '.'],  # W означает Water (вода)
    ['.', 'T', 'R', '.', '.'],
    ['.', 'T', '.', '.', '.']
]
# Квест: убить крыс
kill_rats_quest = Quest("Убить крыс", "Убить три крысы", "болото", reward_message="Ты убил всех крыс! Надеюсь, оно того стоило.")
swamp_quests = [kill_rats_quest]
swamp = Location("болото", swamp_grid, quests=swamp_quests, enemy_count=0, rat_count=3)


#  Словарь локаций
locations = {
    "хаб": hub,
    "озеро": lake,
    "лес": forest,
    "болото": swamp
}


# Игровая логика
def main():
    rat_kill_count = 0

    print("Добро пожаловать!")
    player_name = input("Как твоё имя? ")
    player = Player(player_name)
    player.inventory = {} # Инвентарь

    current_location_name = 'хаб'
    current_location = locations[current_location_name]

    lcg = LCG(42)

    player_pos = (0, 0)

    def get_random_position(location):
      x = lcg.next() % len(location.grid[0])
      y = lcg.next() % len(location.grid)
      return (x,y)

    def generate_enemies(location, num_enemies, num_rats):
        enemies = []
        for _ in range(num_enemies):
            enemies.append(Enemy())  # Создание противника
        for _ in range(num_rats):
            enemies.append(Rat()) # Создание противника-крысы
        return enemies
    

    # Функция случайной позиции в локации
    def get_random_enemy_positions(location, num_enemies, num_rats):
        enemy_positions = []
        for _ in range(num_enemies):
            enemy_positions.append((lcg.next() % len(location.grid[0]), lcg.next() % len(location.grid))) # Добавление противника
        for _ in range(num_rats):
            enemy_positions.append((lcg.next() % len(location.grid[0]), lcg.next() % len(location.grid))) # Добавление противника-крысы
        return enemy_positions

    enemies = generate_enemies(current_location, current_location.enemy_count, current_location.rat_count)
    enemies_pos = get_random_enemy_positions(current_location, current_location.enemy_count, current_location.rat_count)

    while True:
        render_map(current_location, player_pos, enemies_pos)
        print(f"{player.name} Здоровье: {player.hp}, Силы: {player.mp}")

        # Проверка выполненности квестов
        for quest in current_location.quests:
            if not quest.completed:
                if current_location.name == quest.location:
                  # Проверка выполненности квестов, используя логику квестов
                  if quest.is_complete(player):
                      quest.completed = True
                      print(quest.reward_message)
                      # Награда

        action = input("Действия: (w/a/s/d для перемещения, f-атака, i-взаимодействие, q-выход из игры, локации): ").lower()

        if action == 'q':
            print("Спасибо за игру!")
            break
        
        if action in locations:  # Проверка, если ввод - название локации
            new_location_name = action
            new_location = locations[new_location_name]

            # Проверка на коллизию ПЕРЕД переходом на другую локацию
            current_location_name = new_location_name
            current_location = new_location
            player_pos = (0, 0)

            print(f"Ты переместился на локацию : {current_location_name}")
            continue

        if action == 'локации':
            print(f"Список доступных локаций : хаб, озеро, лес, болото")
            continue

        if action == 'w':
            new_pos = (player_pos[0], player_pos[1] - 1)
        elif action == 's':
            new_pos = (player_pos[0], player_pos[1] + 1)
        elif action == 'a':
            new_pos = (player_pos[0] - 1, player_pos[1])
        elif action == 'd':
            new_pos = (player_pos[0] + 1, player_pos[1])
        elif action == 'f':
            # Логика атаки
            attacked = False
            for i, enemy_pos in enumerate(enemies_pos):
                if player_pos == enemy_pos:
                    damage = player.attack(enemies[i])
                    print(f"{player.name} атакует {enemies[i].name} и наносит {damage} урона.")
                    if enemies[i].hp <=0:
                        print("Ты успешно убил противника! Выживает сильнейший!!!")
                        if isinstance(enemies[i], Rat): # Проверка на то, что это крыса
                            print("Ты убил крысу.")
                            player.inventory["Хвост крысы"] = player.inventory.get("Хвост крысы", 0) + 1
                        del enemies[i] # Удаляем мертвого противника
                        del enemies_pos[i] # Удаляем позицию мертвого противника
                        attacked = True
                        break

            if not attacked:
                print("Здесь некого атаковать.")
                continue

            if not enemies:
                print("Ты убил всех крыс!")

        elif action == 'i':
            # Логика интеракции
            if current_location.buildings:
                for building_x, building_y, description in current_location.buildings:
                    if (building_x, building_y) == player_pos:
                        print(f"Взаимодействие с: {description}")
                        # Специфические взаимодействия
                        if description == "Маленький домик":
                            print("Ты вошёл в небольшой дом")
                        elif description == "Ратуша":
                            print("Ты в ратуше.")
                        elif description == "Магазин":
                            print("Ты смотришь на вывеску около магазина. Приходит понимание, что магазин закрыт.")
                        elif description == "Большой дом":
                            print("Ты у большого дома")
                        elif description == "Твой дом":
                            print("Ты в своём доме")
                        # Дополнительные взаимодействия
            if current_location.quests: # Проверка на наличие квестов в локации
              for quest in current_location.quests:
                  if not quest.completed: # Проверка на выполненность квеста
                    # (Возможность ввода логики завершения квестов)
                    if current_location.name == "озеро" and quest.name == "Сбор трав":
                      if player_pos == (3, 0): 
                            print("Ты собрал некоторые травы.")
                            player.inventory["Травы"] = player.inventory.get("Травы", 0) + 1
                            if quest.is_complete(player):
                              quest.completed = True
                              print(quest.reward_message)
                    elif current_location.name == "лес" and quest.name == "Сбор шкур":
                      if player_pos == (0,1):
                        print("Ты снял шкуру.")
                        player.inventory["Шкура"] = player.inventory.get("Шкура", 0) + 1
                        if quest.is_complete(player):
                          quest.completed = True
                          print(quest.reward_message)
                    elif current_location.name == 'болото' and quest.name == 'Убить крыс':
                        if rat_kill_count == 3:
                            quest.completed = True
                            print(quest.reward_message)
        else:
            print("Некорректное действие.")
            continue

        if action in ('w', 'a', 's', 'd'):
            # Проверка коллизии ПЕРЕД перемещением
            new_pos = (player_pos[0] + (1 if action == 'd' else -1 if action == 'a' else 0)), player_pos[1] + (1 if action == 's' else -1 if action == 'w' else 0)
            
            if not check_collision(new_pos, current_location.grid):
                player_pos = new_pos

                for i, enemy_pos in enumerate(enemies_pos):
                    enemies_pos[i] = move_enemy_towards_player(enemy_pos, player_pos)
            
            else:

                print("Ты не можешь переместиться сюда.")

                # Проверка K.O. (game over)
                if player.hp <= 0:
                    print("Ты умер!")
                    break

        # Проверка на победу в игре (все квесты выполнены)
        all_quests_complete = True
        for location_name, location in locations.items():
            for quest in location.quests:
                if not quest.completed:
                    all_quests_complete = False
                    break
            if not all_quests_complete:
              break

        if all_quests_complete and current_location_name == "хаб" and player_pos == (2, 3): # Проверка, если игрок находится внутри Ратуши.
              print("Ты завершил все задания и завершил игру!")
              break
    print("Игра закончена.")


if __name__ == "__main__":
    main()