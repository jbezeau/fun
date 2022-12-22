import actions


class MockCharacter:
    def __init__(self):
        self.stats = {actions.FIGHT: 6, actions.SHOOT: 4, actions.PWR: 6, actions.RES: 4}
        self.a_frame = 3
        self.a_speed = 0.1


if __name__ == '__main__':
    guy = MockCharacter()
    guy2 = MockCharacter()

    actions.punch(guy, guy2)
