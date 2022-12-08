import shooter


if __name__ == '__main__':
    position = (128, 128)
    destination = (1080, 512)
    vector = shooter.direction(position, destination)
    print(f'angle from {position} to {destination}: {vector}')
    vx, vy = vector
    px, py = position
    while px < 1080 and py < 512:
        px += 8*vx
        py += 8*vy
    print(f'travel: {int(px), int(py)}')
